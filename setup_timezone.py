#!/usr/bin/env python3
"""
NTP-MCP Timezone Auto-Configuration Script v2
Safely configures NTP-MCP with automatic detection and Claude integration
"""

import json
import os
import sys
import subprocess
import platform
import shutil
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

# ANSI color codes
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
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

def check_claude_cli() -> bool:
    """Check if Claude CLI is available"""
    try:
        result = subprocess.run(
            ["which", "claude"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False

def get_ntp_mcp_status() -> str:
    """Get current NTP MCP installation status"""
    if not check_claude_cli():
        return "no_cli"
    
    try:
        result = subprocess.run(
            ["claude", "mcp", "list"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return "cli_error"
        
        # Look for ntp in the output
        for line in result.stdout.splitlines():
            if line.startswith("ntp:"):
                if "✓ Connected" in line:
                    return "connected"
                elif "✗ Failed" in line:
                    return "failed"
                else:
                    return "unknown"
        
        return "not_installed"
    except Exception as e:
        print_color(f"Error checking MCP status: {e}", YELLOW)
        return "error"

def remove_ntp_mcp() -> bool:
    """Remove existing NTP MCP installation"""
    try:
        subprocess.run(
            ["claude", "mcp", "remove", "--scope", "user", "ntp"],
            capture_output=True,
            text=True
        )
        return True
    except:
        return False

def add_ntp_mcp(launch_script: Path) -> bool:
    """Add NTP MCP to Claude"""
    try:
        result = subprocess.run(
            ["claude", "mcp", "add", "--scope", "user", "ntp", "bash", str(launch_script)],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print_color(f"Error adding MCP: {e}", RED)
        return False

def verify_ntp_connection() -> bool:
    """Verify NTP MCP is connected"""
    time.sleep(2)  # Give it a moment to connect
    
    try:
        result = subprocess.run(
            ["claude", "mcp", "list"],
            capture_output=True,
            text=True
        )
        
        return "ntp" in result.stdout and "✓ Connected" in result.stdout
    except:
        return False

def fix_line_endings(file_path: Path):
    """Fix Windows line endings in shell scripts"""
    if not file_path.exists():
        return
    
    try:
        content = file_path.read_bytes()
        # Replace CRLF with LF
        content = content.replace(b'\r\n', b'\n')
        file_path.write_bytes(content)
    except Exception as e:
        print_color(f"Warning: Could not fix line endings: {e}", YELLOW)

def update_launch_script(launch_script: Path, timezone: str, ntp_server: str):
    """Update the launch script with new defaults"""
    if not launch_script.exists():
        return False
    
    try:
        # Fix line endings first
        fix_line_endings(launch_script)
        
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
        return True
    except Exception as e:
        print_color(f"⚠ Could not update launch script: {e}", YELLOW)
        return False

def show_manual_config(launch_script: Path, timezone: str, ntp_server: str):
    """Show manual configuration for Claude Desktop"""
    config = {
        "mcpServers": {
            "ntp": {
                "command": "bash",
                "args": [str(launch_script)],
                "env": {
                    "TZ": timezone,
                    "NTP_SERVER": ntp_server
                }
            }
        }
    }
    
    print()
    print("Add this to your Claude Desktop configuration:")
    print(json.dumps(config, indent=2))

def main():
    """Main setup function"""
    
    print_color("🌍 NTP-MCP Timezone Configuration v2", GREEN)
    print("=" * 40)
    print()
    
    # Get script directory
    script_dir = Path(__file__).parent.resolve()
    launch_script = script_dir / "launch_ntpmcp.sh"
    
    # Check if launch script exists
    if not launch_script.exists():
        print_color(f"❌ Error: launch_ntpmcp.sh not found in {script_dir}", RED)
        print("Please run this script from the ntp-mcp directory")
        return 1
    
    # Detect system timezone
    system_tz = detect_system_timezone()
    print_color(f"✓ Detected system timezone: {system_tz}", GREEN)
    
    # Get NTP server from command line or use default
    ntp_server = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_NTP_SERVER
    
    # Validate NTP server (optional warning)
    if ntp_server not in APPROVED_SERVERS:
        print_color(f"⚠ Note: '{ntp_server}' is not in the pre-approved list", YELLOW)
        print("Pre-approved servers:", ", ".join(APPROVED_SERVERS))
        response = input("Continue? (Y/n): ")
        if response.lower() == 'n':
            print("Setup cancelled")
            return 0
    
    print_color(f"✓ Using NTP server: {ntp_server}", GREEN)
    print()
    
    # Update launch script with detected values
    print("Updating launch script defaults...")
    if update_launch_script(launch_script, system_tz, ntp_server):
        print_color("✓ Launch script updated", GREEN)
    print()
    
    # Check Claude CLI availability
    if not check_claude_cli():
        print_color("⚠ Claude CLI not found.", YELLOW)
        print()
        print("To install the NTP-MCP manually, run:")
        print_color(f"claude mcp add --scope user ntp bash {launch_script}", BLUE)
        print()
        print("Or add to your Claude Desktop config:")
        show_manual_config(launch_script, system_tz, ntp_server)
        return 0
    
    # Check current installation status
    print("Checking NTP-MCP installation status...")
    status = get_ntp_mcp_status()
    
    if status == "connected":
        print_color("✓ NTP-MCP is already installed and connected!", GREEN)
        print()
        response = input("Would you like to update it with new settings? (y/N): ")
        if response.lower() == 'y':
            print("Updating NTP-MCP configuration...")
            remove_ntp_mcp()
            time.sleep(1)
            if add_ntp_mcp(launch_script):
                print_color("✓ NTP-MCP updated successfully!", GREEN)
            else:
                print_color("❌ Failed to update NTP-MCP", RED)
                return 1
        else:
            print("Keeping existing configuration.")
    
    elif status == "failed":
        print_color("⚠ NTP-MCP is installed but failed to connect.", YELLOW)
        print("Reinstalling with corrected configuration...")
        remove_ntp_mcp()
        time.sleep(1)
        if add_ntp_mcp(launch_script):
            print_color("✓ NTP-MCP reinstalled successfully!", GREEN)
        else:
            print_color("❌ Failed to reinstall NTP-MCP", RED)
            return 1
    
    elif status == "not_installed":
        print_color("→ NTP-MCP not found. Installing...", BLUE)
        if add_ntp_mcp(launch_script):
            print_color("✓ NTP-MCP installed successfully!", GREEN)
        else:
            print_color("❌ Failed to install NTP-MCP", RED)
            return 1
    
    elif status == "no_cli":
        print_color("❌ Claude CLI not available", RED)
        show_manual_config(launch_script, system_tz, ntp_server)
        return 1
    
    else:
        print_color("⚠ Unknown status. Attempting installation...", YELLOW)
        # Try to add, if it fails try remove then add
        if not add_ntp_mcp(launch_script):
            print_color("Note: MCP might already be installed. Trying to update...", YELLOW)
            remove_ntp_mcp()
            time.sleep(1)
            if add_ntp_mcp(launch_script):
                print_color("✓ NTP-MCP configuration complete!", GREEN)
            else:
                print_color("❌ Failed to configure NTP-MCP", RED)
                return 1
    
    # Verify installation
    print()
    print("Verifying installation...")
    if verify_ntp_connection():
        print_color("✅ SUCCESS! NTP-MCP is connected and working!", GREEN)
    else:
        print_color("⚠ Please restart Claude to complete the setup.", YELLOW)
    
    # Summary
    print()
    print_color("🎉 Configuration Complete!", GREEN)
    print()
    print("Summary:")
    print(f"  Timezone: {system_tz}")
    print(f"  NTP Server: {ntp_server}")
    print(f"  Installation: {script_dir}")
    print()
    print("The NTP-MCP will use these settings automatically.")
    print()
    print("To change settings, run:")
    print(f"  python3 {sys.argv[0]} <ntp-server>")
    print("Example:")
    print(f"  python3 {sys.argv[0]} time.google.com")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())