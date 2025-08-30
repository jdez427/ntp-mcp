#!/usr/bin/env python3
"""NTP MCP Server - Secure time synchronization with enhanced security filtering"""

import asyncio
import ntplib
from datetime import datetime, timezone
import pytz
import os
import logging
import re
import ipaddress
import time
from typing import Optional, Tuple, List, Dict, Any
from collections import deque, OrderedDict
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# Configure logging properly
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ntp-server")

# Create server instance
server = Server("ntp-server")

# Security: Approved NTP servers whitelist
APPROVED_NTP_SERVERS = [
    # Global public servers
    "pool.ntp.org",
    "time.google.com",
    "time.cloudflare.com",
    "time.nist.gov",
    "time.windows.com",
    "time.apple.com",
    "ntp.ubuntu.com",
    
    # Regional pools
    "0.pool.ntp.org",
    "1.pool.ntp.org", 
    "2.pool.ntp.org",
    "3.pool.ntp.org",
    "north-america.pool.ntp.org",
    "europe.pool.ntp.org",
    "asia.pool.ntp.org",
    "oceania.pool.ntp.org",
    "south-america.pool.ntp.org",
    "africa.pool.ntp.org",
    
    # US pools
    "0.us.pool.ntp.org",
    "1.us.pool.ntp.org",
    "2.us.pool.ntp.org",
    "3.us.pool.ntp.org",
    
    # EU pools
    "0.europe.pool.ntp.org",
    "1.europe.pool.ntp.org",
    "2.europe.pool.ntp.org",
    "3.europe.pool.ntp.org",
]

# Pre-compute lowercase set for performance
APPROVED_SERVERS_LOWER = {s.lower() for s in APPROVED_NTP_SERVERS}

# Security: Combined regex pattern for efficiency (single pass instead of 10)
# Blocks: Untrusted domains and security-risk patterns
BLOCKED_PATTERN = re.compile(
    r'(?:'
    r'\.(?:ru|su|by|kz)(?:\.|$)|'  # TLD blocking: .ru, .su, .by, .kz
    r'(?:^|\.)(?:ru\.|belarus|kremlin|yandex|mail\.ru|vk\.com)'  # Specific services
    r')',
    re.IGNORECASE
)

# Constants
DEFAULT_NTP_TIMEOUT = 5  # seconds - Standard timeout for NTP requests
MAX_REQUESTS_PER_MINUTE = 60  # Rate limit: 1 req/sec average (burst allowed)
CACHE_TTL = 30  # seconds - Balance between performance and freshness
# Cache size calculation:
# - Average response size: ~200 bytes (Date/Time/Timezone/Server/Source)
# - Target memory usage: ~20KB maximum for cache
# - 100 entries * 200 bytes = 20KB (acceptable memory footprint)
MAX_CACHE_SIZE = 100  # Optimized for memory vs hit rate balance

# Rate limiting with deque for O(1) operations
# Using deque without maxlen to manually control cleanup based on time window
request_times: deque = deque()
# Note: MCP servers handle one request at a time via stdio - no locks needed

# Response cache using OrderedDict for O(1) LRU eviction
response_cache: OrderedDict[str, Tuple[str, float]] = OrderedDict()

def is_rate_limited() -> bool:
    """Check if rate limit has been exceeded using efficient deque.
    
    Note: No async/locking needed as MCP servers are single-threaded stdio.
    """
    current_time = time.time()
    
    # Remove old requests (older than 60 seconds)
    while request_times and current_time - request_times[0] >= 60:
        request_times.popleft()
    
    if len(request_times) >= MAX_REQUESTS_PER_MINUTE:
        return True
    
    request_times.append(current_time)
    return False

def get_cached_response(server: str) -> Optional[str]:
    """Get cached response if available and not expired.
    
    Uses normalized server name as key to prevent cache poisoning.
    """
    # Normalize server name to prevent cache poisoning
    cache_key = server.lower().strip().rstrip('.')
    
    if cache_key in response_cache:
        response, timestamp = response_cache[cache_key]
        if time.time() - timestamp < CACHE_TTL:
            # Move to end to mark as recently used
            response_cache.move_to_end(cache_key)
            return response
        else:
            del response_cache[cache_key]
    return None

def cache_response(server: str, response: str) -> None:
    """Cache a response with O(1) LRU eviction.
    
    Uses OrderedDict for efficient oldest-entry removal.
    Normalizes server names to prevent cache poisoning attacks.
    """
    # Normalize server name to prevent cache poisoning
    cache_key = server.lower().strip().rstrip('.')
    
    # Implement O(1) cache size limit with OrderedDict
    if len(response_cache) >= MAX_CACHE_SIZE:
        # Remove oldest entry - O(1) operation with OrderedDict
        response_cache.popitem(last=False)
    
    response_cache[cache_key] = (response, time.time())

def is_valid_ip(ip_str: str) -> Tuple[bool, str]:
    """Validate IP address (both IPv4 and IPv6)."""
    try:
        # Try to parse as IP address
        ip = ipaddress.ip_address(ip_str)
        
        # Block all direct IPs for security
        return False, f"Direct IP addresses not allowed for security reasons (detected {type(ip).__name__})"
    except ValueError:
        # Not an IP address
        return True, "Not an IP address"

def format_ntp_error(error_type: str, exc: Exception, logger) -> str:
    """Format NTP error messages consistently (DRY principle)."""
    msg = f"{error_type}: {exc}"
    logger.warning(f"{msg}, falling back to local time")
    return msg

def is_server_allowed(server_name: str) -> Tuple[bool, str]:
    """Check if an NTP server is allowed based on security rules."""
    server_lower = server_name.lower().strip()
    
    # First check if it's an IP address
    is_not_ip, ip_reason = is_valid_ip(server_lower)
    if not is_not_ip:
        return False, ip_reason
    
    # Check against combined blocked pattern (single regex pass)
    if BLOCKED_PATTERN.search(server_lower):
        return False, f"Server '{server_name}' blocked: matches security pattern"
    
    # Check if in approved list (using pre-computed set)
    if server_lower in APPROVED_SERVERS_LOWER:
        return True, f"Server '{server_name}' is in approved list"
    
    # Default deny for unknown servers
    return False, f"Server '{server_name}' not in approved list (security policy: default deny)"

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="get_current_time",
            description="Get the current time from an NTP server specified by NTP_SERVER env var (default 'pool.ntp.org'), in time zone specified by TZ env var (default system local)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="list_approved_servers",
            description="List all approved NTP servers that can be used",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((ntplib.NTPException, OSError, asyncio.TimeoutError)),
    reraise=True
)
async def get_ntp_time_with_retry(ntp_server: str) -> float:
    """Get NTP time with retry logic for specific exceptions."""
    c = ntplib.NTPClient()
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None, 
        lambda: c.request(ntp_server, timeout=DEFAULT_NTP_TIMEOUT)
    )
    return response.tx_time

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Optional[Dict[str, Any]] = None
) -> List[types.TextContent]:
    """Handle tool calls."""
    
    if name == "list_approved_servers":
        servers_list = "\n".join(f"• {server}" for server in APPROVED_NTP_SERVERS)
        return [
            types.TextContent(
                type="text",
                text=f"Approved NTP Servers:\n{servers_list}\n\nNote: Untrusted domains and direct IP addresses are blocked for security."
            )
        ]
    
    if name != "get_current_time":
        raise ValueError(f"Unknown tool: {name}")
    
    # Get NTP server from environment variable with validation
    requested_server = os.getenv('NTP_SERVER', 'pool.ntp.org').strip()
    
    # Handle empty server name edge case
    if not requested_server:
        return [
            types.TextContent(
                type="text",
                text="Error: Server name cannot be empty"
            )
        ]
    
    # Validate server name with IDN support
    try:
        # Convert IDN to ASCII (punycode) for validation
        ascii_server = requested_server.encode('idna').decode('ascii')
        if len(ascii_server) > 255 or not re.match(r'^[a-zA-Z0-9._-]+$', ascii_server):
            return [
                types.TextContent(
                    type="text",
                    text="Error: Invalid server name format"
                )
            ]
        # Use the ASCII version for all operations
        requested_server = ascii_server
    except (UnicodeError, UnicodeDecodeError):
        return [
            types.TextContent(
                type="text",
                text="Error: Invalid server name encoding (IDN conversion failed)"
            )
        ]
    
    # Security check FIRST (before rate limiting to prevent bypass)
    allowed, reason = is_server_allowed(requested_server)
    if not allowed:
        logger.warning(f"Blocked NTP server request: {reason}")
        return [
            types.TextContent(
                type="text",
                text=f"Security Error: {reason}\n\nPlease use one of the approved servers. Use 'list_approved_servers' tool to see the list."
            )
        ]
    
    # Check rate limiting AFTER security validation
    if is_rate_limited():
        return [
            types.TextContent(
                type="text",
                text="Error: Rate limit exceeded. Please wait before making another request."
            )
        ]
    
    # Check cache first (no async needed)
    cached_response = get_cached_response(requested_server)
    if cached_response:
        logger.info(f"Returning cached response for {requested_server}")
        return [
            types.TextContent(
                type="text",
                text=cached_response + "\n(cached)"
            )
        ]
    
    logger.info(f"Using approved NTP server: {requested_server}")
    
    # Get time zone from environment variable
    tz_name = os.getenv('TZ')
    if tz_name:
        try:
            tz = pytz.timezone(tz_name)
        except pytz.UnknownTimeZoneError:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error: Unknown time zone: {tz_name}"
                )
            ]
    else:
        tz = None  # Use system's local time zone if TZ is not set

    # Initialize error_msg with proper type hint
    error_msg: Optional[str] = None
    
    try:
        # Attempt to get time from NTP server with retry
        tx_time = await get_ntp_time_with_retry(requested_server)
        utc_dt = datetime.fromtimestamp(tx_time, timezone.utc)
        
        # Convert to desired time zone or system's local time zone
        if tz:
            local_dt = utc_dt.astimezone(tz)
        else:
            local_dt = utc_dt.astimezone()  # System's local time zone
        
        # Format the time according to the requested format
        date_str = local_dt.strftime("%Y-%m-%d")
        time_str = local_dt.strftime("%H:%M:%S")
        # Optimize timezone string formatting
        timezone_str = local_dt.strftime("%Z") or str(local_dt.tzinfo)
        
        result = f"Date:{date_str}\nTime:{time_str}\nTimezone:{timezone_str}\nNTP Server:{requested_server}\nSource:NTP"
        logger.info(f"NTP time retrieved: {result}")
        
        # Cache the response
        cache_response(requested_server, result)
        
    except ntplib.NTPException as e:
        # Specific NTP error handling
        error_msg = format_ntp_error("NTP protocol error", e, logger)
    except OSError as e:
        # Network/OS error handling
        error_msg = format_ntp_error("Network error", e, logger)
    except asyncio.TimeoutError:
        # Timeout handling
        error_msg = f"NTP timeout after {DEFAULT_NTP_TIMEOUT}s"
        logger.warning(f"{error_msg}, falling back to local time")
    except Exception as e:
        # Unexpected errors (should be rare now)
        error_msg = f"Unexpected error: {e}"
        logger.error(f"{error_msg}, falling back to local time")
    else:
        # Success - return the result
        return [
            types.TextContent(
                type="text",
                text=result
            )
        ]
    
    # Handle all error cases - fall back to local time
    try:
        if tz:
            # If TZ is set, get local time in that time zone
            local_dt = datetime.now(tz)
        else:
            # Otherwise, get system's local time with its time zone
            utc_now = datetime.now(timezone.utc)
            local_dt = utc_now.astimezone()
        
        # Format the time according to the requested format
        date_str = local_dt.strftime("%Y-%m-%d")
        time_str = local_dt.strftime("%H:%M:%S")
        # Optimize timezone string formatting
        timezone_str = local_dt.strftime("%Z") or str(local_dt.tzinfo)
        
        # IMPORTANT: Notify user this is a fallback
        result = f"Date:{date_str}\nTime:{time_str}\nTimezone:{timezone_str}\nSource:LOCAL SYSTEM (NTP unavailable: {error_msg})"
        
    except Exception as e2:
        # If all else fails, return an error
        result = f"Error: Failed to get time - {str(e2)}"
        logger.error(f"Failed to get time: {str(e2)}")
    
    return [
        types.TextContent(
            type="text",
            text=result
        )
    ]

async def main():
    """Run the server using stdio."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ntp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())