#!/bin/bash
# NTP-MCP Timezone Auto-Configuration Script v2
# Safely configures NTP-MCP with automatic detection and Claude integration

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}🌍 NTP-MCP Timezone Configuration v2${NC}"
echo "======================================"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

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

# Check if Claude CLI is available
check_claude_cli() {
    if command -v claude &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Check if NTP MCP is already installed
check_ntp_installed() {
    if ! check_claude_cli; then
        return 2  # Claude CLI not available
    fi
    
    # Check if ntp is in the MCP list
    if claude mcp list 2>/dev/null | grep -q "^ntp:"; then
        return 0  # Found
    else
        return 1  # Not found
    fi
}

# Get current NTP MCP status
get_ntp_status() {
    local status_line=$(claude mcp list 2>/dev/null | grep "^ntp:" || true)
    if [ -n "$status_line" ]; then
        if echo "$status_line" | grep -q "✓ Connected"; then
            echo "connected"
        elif echo "$status_line" | grep -q "✗ Failed"; then
            echo "failed"
        else
            echo "unknown"
        fi
    else
        echo "not_installed"
    fi
}

# Main configuration
main() {
    # Get system timezone
    SYSTEM_TZ=$(detect_timezone)
    echo -e "${GREEN}✓${NC} Detected system timezone: ${YELLOW}$SYSTEM_TZ${NC}"
    
    # Default NTP server (can be overridden)
    DEFAULT_NTP_SERVER="time.cloudflare.com"
    NTP_SERVER="${1:-$DEFAULT_NTP_SERVER}"
    
    if [ "$#" -gt 0 ]; then
        echo -e "${GREEN}✓${NC} Using specified NTP server: ${YELLOW}$NTP_SERVER${NC}"
    else
        echo -e "${GREEN}✓${NC} Using default NTP server: ${YELLOW}$NTP_SERVER${NC}"
    fi
    
    echo ""
    
    # Update launch script with detected values
    LAUNCH_SCRIPT="$SCRIPT_DIR/launch_ntpmcp.sh"
    if [ -f "$LAUNCH_SCRIPT" ]; then
        echo "Updating launch script defaults..."
        # Fix line endings first
        sed -i 's/\r$//' "$LAUNCH_SCRIPT" 2>/dev/null || true
        # Update the export lines
        sed -i.bak "s|export TZ=.*|export TZ=\"\${TZ:-$SYSTEM_TZ}\"|" "$LAUNCH_SCRIPT"
        sed -i "s|export NTP_SERVER=.*|export NTP_SERVER=\"\${NTP_SERVER:-$NTP_SERVER}\"|" "$LAUNCH_SCRIPT"
        echo -e "${GREEN}✓${NC} Updated launch script defaults"
        echo ""
    fi
    
    # Check Claude CLI availability
    if ! check_claude_cli; then
        echo -e "${YELLOW}⚠${NC} Claude CLI not found."
        echo ""
        echo "To install the NTP-MCP manually, run:"
        echo -e "${BLUE}claude mcp add --scope user ntp bash $LAUNCH_SCRIPT${NC}"
        echo ""
        echo "Or add to your Claude Desktop config:"
        show_manual_config
        return
    fi
    
    # Check current installation status
    echo "Checking NTP-MCP installation status..."
    NTP_STATUS=$(get_ntp_status)
    
    case "$NTP_STATUS" in
        "connected")
            echo -e "${GREEN}✓${NC} NTP-MCP is already installed and connected!"
            echo ""
            echo -e "${YELLOW}Would you like to update it with new settings? (y/N):${NC}"
            read -r response
            if [[ "$response" =~ ^[Yy]$ ]]; then
                echo "Updating NTP-MCP configuration..."
                claude mcp remove --scope user ntp 2>/dev/null || true
                sleep 1
                claude mcp add --scope user ntp bash "$LAUNCH_SCRIPT"
                echo -e "${GREEN}✓${NC} NTP-MCP updated successfully!"
            else
                echo "Keeping existing configuration."
            fi
            ;;
            
        "failed")
            echo -e "${YELLOW}⚠${NC} NTP-MCP is installed but failed to connect."
            echo "Reinstalling with corrected configuration..."
            claude mcp remove --scope user ntp 2>/dev/null || true
            sleep 1
            claude mcp add --scope user ntp bash "$LAUNCH_SCRIPT"
            echo -e "${GREEN}✓${NC} NTP-MCP reinstalled successfully!"
            ;;
            
        "not_installed")
            echo -e "${BLUE}→${NC} NTP-MCP not found. Installing..."
            claude mcp add --scope user ntp bash "$LAUNCH_SCRIPT"
            echo -e "${GREEN}✓${NC} NTP-MCP installed successfully!"
            ;;
            
        *)
            echo -e "${YELLOW}⚠${NC} Unknown status. Attempting installation..."
            claude mcp add --scope user ntp bash "$LAUNCH_SCRIPT" 2>/dev/null || {
                echo -e "${YELLOW}Note: MCP might already be installed. Trying to update...${NC}"
                claude mcp remove --scope user ntp 2>/dev/null || true
                sleep 1
                claude mcp add --scope user ntp bash "$LAUNCH_SCRIPT"
            }
            echo -e "${GREEN}✓${NC} NTP-MCP configuration complete!"
            ;;
    esac
    
    echo ""
    echo "Verifying installation..."
    sleep 2
    if claude mcp list 2>/dev/null | grep -q "ntp.*✓ Connected"; then
        echo -e "${GREEN}✅ SUCCESS! NTP-MCP is connected and working!${NC}"
    else
        echo -e "${YELLOW}⚠${NC} Please restart Claude to complete the setup."
    fi
    
    echo ""
    echo -e "${GREEN}🎉 Configuration Complete!${NC}"
    echo ""
    echo "Summary:"
    echo "  Timezone: $SYSTEM_TZ"
    echo "  NTP Server: $NTP_SERVER"
    echo "  Installation: $SCRIPT_DIR"
    echo ""
    echo "The NTP-MCP will use these settings automatically."
    echo ""
    echo "To change settings, run:"
    echo "  $0 <ntp-server>"
    echo "Example:"
    echo "  $0 time.google.com"
}

# Show manual configuration
show_manual_config() {
    cat << EOF
{
  "mcpServers": {
    "ntp": {
      "command": "bash",
      "args": ["$LAUNCH_SCRIPT"],
      "env": {
        "TZ": "$SYSTEM_TZ",
        "NTP_SERVER": "$NTP_SERVER"
      }
    }
  }
}
EOF
}

# Run main function
main "$@"