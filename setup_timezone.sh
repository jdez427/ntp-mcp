#!/bin/bash
# NTP-MCP Timezone Auto-Configuration Script
# Automatically detects system timezone and configures MCP settings

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🌍 NTP-MCP Timezone Configuration${NC}"
echo "=================================="
echo ""

# Detect system timezone
detect_timezone() {
    # Method 1: Try timedatectl (most reliable on modern Linux)
    if command -v timedatectl &> /dev/null; then
        TZ=$(timedatectl show -p Timezone --value 2>/dev/null || true)
        if [ -n "$TZ" ]; then
            echo "$TZ"
            return
        fi
    fi
    
    # Method 2: Check /etc/timezone
    if [ -f /etc/timezone ]; then
        TZ=$(cat /etc/timezone 2>/dev/null || true)
        if [ -n "$TZ" ]; then
            echo "$TZ"
            return
        fi
    fi
    
    # Method 3: Check TZ environment variable
    if [ -n "${TZ:-}" ]; then
        echo "$TZ"
        return
    fi
    
    # Method 4: Try to read from /etc/localtime symlink
    if [ -L /etc/localtime ]; then
        TZ=$(readlink /etc/localtime | sed 's|.*/zoneinfo/||')
        if [ -n "$TZ" ]; then
            echo "$TZ"
            return
        fi
    fi
    
    # Default to UTC if we can't detect
    echo "UTC"
}

# Get system timezone
SYSTEM_TZ=$(detect_timezone)
echo -e "${GREEN}✓${NC} Detected system timezone: ${YELLOW}$SYSTEM_TZ${NC}"

# Default NTP server (can be overridden)
DEFAULT_NTP_SERVER="time.cloudflare.com"

# Parse command line arguments
NTP_SERVER="${1:-$DEFAULT_NTP_SERVER}"

if [ "$#" -gt 0 ]; then
    echo -e "${GREEN}✓${NC} Using specified NTP server: ${YELLOW}$NTP_SERVER${NC}"
else
    echo -e "${GREEN}✓${NC} Using default NTP server: ${YELLOW}$NTP_SERVER${NC}"
fi

# Find Claude config file location
find_claude_config() {
    # Common locations for Claude config
    local config_paths=(
        "$HOME/.config/claude/claude_desktop_config.json"
        "$HOME/.claude/config.json"
        "$HOME/Library/Application Support/Claude/claude_desktop_config.json"  # macOS
        "$APPDATA/Claude/claude_desktop_config.json"  # Windows (if in WSL)
    )
    
    for path in "${config_paths[@]}"; do
        if [ -f "$path" ]; then
            echo "$path"
            return
        fi
    done
    
    # If not found, check if user has CLAUDE_CONFIG_PATH set
    if [ -n "${CLAUDE_CONFIG_PATH:-}" ] && [ -f "$CLAUDE_CONFIG_PATH" ]; then
        echo "$CLAUDE_CONFIG_PATH"
        return
    fi
    
    return 1
}

# Update or create MCP config
update_mcp_config() {
    local config_file="$1"
    local tz="$2"
    local ntp="$3"
    
    # Backup existing config
    if [ -f "$config_file" ]; then
        cp "$config_file" "${config_file}.backup.$(date +%Y%m%d_%H%M%S)"
        echo -e "${GREEN}✓${NC} Backed up existing config"
    fi
    
    # Check if config exists and has mcpServers section
    if [ -f "$config_file" ]; then
        # Use Python to safely update JSON
        python3 << EOF
import json
import sys

config_file = "$config_file"
tz = "$tz"
ntp = "$ntp"

try:
    with open(config_file, 'r') as f:
        config = json.load(f)
except:
    config = {}

# Ensure mcpServers exists
if 'mcpServers' not in config:
    config['mcpServers'] = {}

# Update or add ntp-server configuration
if 'ntp-server' not in config['mcpServers']:
    config['mcpServers']['ntp-server'] = {
        'command': '/home/jeff/mcp-ntp/launch_ntpmcp.sh'
    }

# Add or update env section
if 'env' not in config['mcpServers']['ntp-server']:
    config['mcpServers']['ntp-server']['env'] = {}

config['mcpServers']['ntp-server']['env']['TZ'] = tz
config['mcpServers']['ntp-server']['env']['NTP_SERVER'] = ntp

# Write back
with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print(f"Updated: TZ={tz}, NTP_SERVER={ntp}")
EOF
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓${NC} Successfully updated MCP configuration"
            return 0
        else
            echo -e "${RED}✗${NC} Failed to update configuration"
            return 1
        fi
    else
        # Create new config
        cat > "$config_file" << EOF
{
  "mcpServers": {
    "ntp-server": {
      "command": "/home/jeff/mcp-ntp/launch_ntpmcp.sh",
      "env": {
        "TZ": "$tz",
        "NTP_SERVER": "$ntp"
      }
    }
  }
}
EOF
        echo -e "${GREEN}✓${NC} Created new configuration file"
    fi
}

# Try to find and update Claude config
echo ""
echo "Looking for Claude configuration..."
if CONFIG_PATH=$(find_claude_config); then
    echo -e "${GREEN}✓${NC} Found config at: $CONFIG_PATH"
    update_mcp_config "$CONFIG_PATH" "$SYSTEM_TZ" "$NTP_SERVER"
else
    echo -e "${YELLOW}⚠${NC} Claude config not found. Creating local MCP config..."
    
    # Create a local config that can be referenced
    LOCAL_CONFIG="$HOME/.config/ntp-mcp/config.json"
    mkdir -p "$(dirname "$LOCAL_CONFIG")"
    update_mcp_config "$LOCAL_CONFIG" "$SYSTEM_TZ" "$NTP_SERVER"
    
    echo ""
    echo -e "${YELLOW}📝 Next Steps:${NC}"
    echo "1. Add this to your Claude configuration:"
    echo ""
    cat "$LOCAL_CONFIG"
    echo ""
    echo "2. Or set environment variables before starting Claude:"
    echo "   export TZ='$SYSTEM_TZ'"
    echo "   export NTP_SERVER='$NTP_SERVER'"
fi

# Also update the launch script as a fallback
LAUNCH_SCRIPT="/home/jeff/mcp-ntp/launch_ntpmcp.sh"
if [ -f "$LAUNCH_SCRIPT" ]; then
    echo ""
    echo "Updating launch script defaults..."
    # Update the export lines in launch script
    sed -i.bak "s|export TZ=.*|export TZ=\"\${TZ:-$SYSTEM_TZ}\"|" "$LAUNCH_SCRIPT"
    sed -i "s|export NTP_SERVER=.*|export NTP_SERVER=\"\${NTP_SERVER:-$NTP_SERVER}\"|" "$LAUNCH_SCRIPT"
    echo -e "${GREEN}✓${NC} Updated launch script defaults"
fi

echo ""
echo -e "${GREEN}🎉 Configuration Complete!${NC}"
echo ""
echo "Summary:"
echo "  Timezone: $SYSTEM_TZ"
echo "  NTP Server: $NTP_SERVER"
echo ""
echo "The NTP-MCP will now use your system's timezone automatically."
echo ""
echo "To use a different NTP server, run:"
echo "  $0 <ntp-server>"
echo "Example:"
echo "  $0 time.google.com"
echo ""
echo -e "${GREEN}Start Claude to use the updated configuration!${NC}"