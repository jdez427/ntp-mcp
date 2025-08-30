#!/usr/bin/env python3
"""
NTP-MCP Timezone Auto-Configuration Script
Automatically detects system timezone and configures MCP settings
"""

import json
import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# ANSI color codes
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'  # No Color

# Default NTP servers (approved list)
APPROVED_SERVERS = [
    "time.cloudflare.com",
    "time.google.com",
    "pool.ntp.org",
    "time.nist.gov",
    "time.windows.com",
    "time.apple.com",
]

DEFAULT_NTP_SERVER = "time.cloudflare.com"

def print_color(message: str, color: str = NC):
    """Print colored message"""
    print(f"{color}{message}{NC}")

def detect_system_timezone() -> str:
    """Detect the system's timezone"""
    
    # Method 1: Try using tzlocal (most reliable)
    try:
        import tzlocal
        tz = tzlocal.get_localzone_name()
        if tz:
            return tz
    except ImportError:
        pass
    
    # Method 2: Check timedatectl on Linux
    if platform.system() == "Linux":
        try:
            result = subprocess.run(
                ["timedatectl", "show", "-p", "Timezone", "--value"],
                capture_output=True,
                text=True,
                check=True
            )
            tz = result.stdout.strip()
            if tz:
                return tz
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    
    # Method 3: Check /etc/timezone
    if Path("/etc/timezone").exists():
        try:
            tz = Path("/etc/timezone").read_text().strip()
            if tz:
                return tz
        except:
            pass
    
    # Method 4: Check TZ environment variable
    if os.environ.get("TZ"):
        return os.environ["TZ"]
    
    # Method 5: Try to get from /etc/localtime symlink
    if Path("/etc/localtime").is_symlink():
        try:
            tz_path = os.readlink("/etc/localtime")
            # Extract timezone from path like /usr/share/zoneinfo/America/New_York
            if "zoneinfo/" in tz_path:
                return tz_path.split("zoneinfo/")[-1]
        except:
            pass
    
    # Default to UTC
    print_color("⚠ Could not detect system timezone, defaulting to UTC", YELLOW)
    return "UTC"

def find_claude_config() -> Optional[Path]:
    """Find Claude configuration file"""
    
    # Common config locations
    config_paths = [
        Path.home() / ".config" / "claude" / "claude_desktop_config.json",
        Path.home() / ".claude" / "config.json",
        Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json",  # macOS
    ]
    
    # Add Windows path if in WSL or Windows
    if platform.system() == "Windows" or "microsoft" in platform.uname().release.lower():
        appdata = os.environ.get("APPDATA")
        if appdata:
            config_paths.append(Path(appdata) / "Claude" / "claude_desktop_config.json")
    
    # Check CLAUDE_CONFIG_PATH environment variable
    if os.environ.get("CLAUDE_CONFIG_PATH"):
        config_paths.insert(0, Path(os.environ["CLAUDE_CONFIG_PATH"]))
    
    # Find first existing config
    for path in config_paths:
        if path.exists():
            return path
    
    return None

def update_claude_config(config_path: Path, timezone: str, ntp_server: str) -> bool:
    """Update Claude configuration with NTP-MCP settings"""
    
    # Backup existing config
    if config_path.exists():
        backup_path = config_path.with_suffix(f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        shutil.copy2(config_path, backup_path)
        print_color(f"✓ Backed up config to {backup_path.name}", GREEN)
    
    # Load or create config
    config: Dict[str, Any] = {}
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            print_color("⚠ Existing config is invalid JSON, creating new", YELLOW)
    
    # Ensure mcpServers section exists
    if 'mcpServers' not in config:
        config['mcpServers'] = {}
    
    # Update ntp-server configuration
    config['mcpServers']['ntp-server'] = {
        'command': '/home/jeff/mcp-ntp/launch_ntpmcp.sh',
        'env': {
            'TZ': timezone,
            'NTP_SERVER': ntp_server
        }
    }
    
    # Write updated config
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    return True

def create_local_config(timezone: str, ntp_server: str) -> Path:
    """Create a local configuration file for manual integration"""
    
    local_config_dir = Path.home() / ".config" / "ntp-mcp"
    local_config_dir.mkdir(parents=True, exist_ok=True)
    local_config_path = local_config_dir / "config.json"
    
    config = {
        "mcpServers": {
            "ntp-server": {
                "command": "/home/jeff/mcp-ntp/launch_ntpmcp.sh",
                "env": {
                    "TZ": timezone,
                    "NTP_SERVER": ntp_server
                }
            }
        }
    }
    
    with open(local_config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    return local_config_path

def update_launch_script(timezone: str, ntp_server: str):
    """Update the launch script with new defaults"""
    
    launch_script = Path("/home/jeff/mcp-ntp/launch_ntpmcp.sh")
    if not launch_script.exists():
        return
    
    try:
        content = launch_script.read_text()
        
        # Update TZ line
        import re
        content = re.sub(
            r'export TZ=.*',
            f'export TZ="${{TZ:-{timezone}}}"',
            content
        )
        
        # Update NTP_SERVER line
        content = re.sub(
            r'export NTP_SERVER=.*',
            f'export NTP_SERVER="${{NTP_SERVER:-{ntp_server}}}"',
            content
        )
        
        launch_script.write_text(content)
        print_color("✓ Updated launch script defaults", GREEN)
    except Exception as e:
        print_color(f"⚠ Could not update launch script: {e}", YELLOW)

def main():
    """Main setup function"""
    
    print_color("🌍 NTP-MCP Timezone Configuration", GREEN)
    print("=" * 40)
    print()
    
    # Detect system timezone
    system_tz = detect_system_timezone()
    print_color(f"✓ Detected system timezone: {system_tz}", GREEN)
    
    # Get NTP server from command line or use default
    ntp_server = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_NTP_SERVER
    
    # Validate NTP server
    if ntp_server not in APPROVED_SERVERS:
        print_color(f"⚠ Warning: '{ntp_server}' is not in the approved server list", YELLOW)
        print("Approved servers:", ", ".join(APPROVED_SERVERS))
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled")
            return
    
    print_color(f"✓ Using NTP server: {ntp_server}", GREEN)
    print()
    
    # Find and update Claude config
    print("Looking for Claude configuration...")
    config_path = find_claude_config()
    
    if config_path:
        print_color(f"✓ Found config at: {config_path}", GREEN)
        if update_claude_config(config_path, system_tz, ntp_server):
            print_color("✓ Successfully updated Claude configuration", GREEN)
    else:
        print_color("⚠ Claude config not found, creating local config...", YELLOW)
        local_config = create_local_config(system_tz, ntp_server)
        print_color(f"✓ Created local config at: {local_config}", GREEN)
        print()
        print_color("📝 Next Steps:", YELLOW)
        print("1. Add the following to your Claude configuration:")
        print()
        with open(local_config) as f:
            print(f.read())
        print()
        print("2. Or set environment variables before starting Claude:")
        print(f"   export TZ='{system_tz}'")
        print(f"   export NTP_SERVER='{ntp_server}'")
    
    # Update launch script
    print()
    update_launch_script(system_tz, ntp_server)
    
    # Summary
    print()
    print_color("🎉 Configuration Complete!", GREEN)
    print()
    print("Summary:")
    print(f"  Timezone: {system_tz}")
    print(f"  NTP Server: {ntp_server}")
    print()
    print("The NTP-MCP will now use your system's timezone automatically.")
    print()
    print("To use a different NTP server, run:")
    print(f"  python3 {sys.argv[0]} <ntp-server>")
    print("Example:")
    print(f"  python3 {sys.argv[0]} time.google.com")
    print()
    print_color("Start Claude to use the updated configuration!", GREEN)

if __name__ == "__main__":
    main()