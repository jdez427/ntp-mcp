#!/bin/bash
# Team-compliant launch script for NTP-MCP

set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Ensure we're in the project directory
cd "$(dirname "$0")" || exit 1

echo -e "${GREEN}🚀 Launching NTP-MCP Server v1.0.0${NC}"
echo "📍 Working directory: $(pwd)"

# Check UV
if ! command -v uv &> /dev/null; then
    echo -e "${RED}❌ ERROR: UV is not installed${NC}"
    exit 1
fi

# Ensure environment is set up
if [ ! -d ".venv" ]; then
    echo "📦 Setting up UV environment..."
    uv sync
fi

# Environment variables
export NTP_SERVER="${NTP_SERVER:-time.cloudflare.com}"
export TZ="${TZ:-UTC}"
export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}$(pwd)/src"

echo "🔧 Configuration:"
echo "  - NTP Server: $NTP_SERVER"
echo "  - Timezone: $TZ"
echo "  - Security: Geographic filtering enabled"

# Launch
echo -e "${GREEN}🏃 Starting NTP-MCP server...${NC}"
exec uv run python -m ntp_mcp