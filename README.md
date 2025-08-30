# NTP MCP Server 🕒

A Model Context Protocol (MCP) server that provides accurate time information from Network Time Protocol (NTP) servers with timezone support, security filtering, and structured output formatting.

## 🚀 Quick Start - Session Initialization

**Start every AI conversation with:**
```
"What time is it?"
"Sync time"
```

This simple command syncs your AI assistant with accurate network time, ensuring correct timestamps throughout your session.

[![UV](https://img.shields.io/badge/UV-Package%20Manager-blue?logo=python)](https://github.com/astral-sh/uv)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green?logo=anthropic)](https://modelcontextprotocol.io/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)](https://python.org/)
[![Security](https://img.shields.io/badge/Security-Enhanced-red?logo=shield)](https://github.com/)

## ✨ Features

- 🌍 **Multiple NTP Server Support**: Connect to approved NTP servers worldwide
- 🔒 **Security Filtering**: Blocks unauthorized sources and untrusted domains
- 📋 **Whitelist Approach**: Only approved servers allowed for enhanced security
- 🕰️ **Timezone Conversion**: Automatic timezone conversion with pytz
- 📋 **Structured Output Format**: Clean, parseable time format
- 🔄 **Fallback Mechanism**: Falls back to local time if NTP is unavailable
- ⚡ **Ultra-Fast Startup**: UV package manager for instant dependency resolution
- ⚡ **Retry Logic**: Automatic retry with exponential backoff
- 🔧 **Configurable**: Environment variable configuration
- 📋 **MCP Compatible**: Works with Claude Desktop and other MCP clients
- 🧪 **Security Testing**: Comprehensive security validation

## 🔒 Security Features

This version includes enhanced security filtering:

- **Geographic filtering** for untrusted domains
- **Blocks direct IP addresses** for security
- **Whitelist of approved servers** including:
  - Global pools: pool.ntp.org, time.google.com, time.cloudflare.com
  - Regional pools: US, Europe, Asia, etc.
  - Major providers: NIST, Windows, Apple, Ubuntu

Use the `list_approved_servers` tool to see all approved servers.

## 🕐 Time Output Format

The NTP server outputs time in a **structured, easy-to-parse format**:

```
Date:YYYY-MM-DD
Time:HH:mm:ss
Timezone:timezone_name
NTP Server:server_name
```

### Example Outputs

**Successful NTP Response:**
```
Date:2025-08-29
Time:14:30:25
Timezone:UTC
NTP Server:time.cloudflare.com
```

**Blocked Server Response:**
```
Security Error: Server 'ntp.ru' blocked: matches pattern '\.ru$'

Please use one of the approved servers. Use 'list_approved_servers' tool to see the list.
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- UV package manager (`pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Development Installation

```bash
# Clone the repository
git clone https://github.com/jdez427/ntp-mcp.git
cd ntp-mcp

# Initialize UV environment
uv sync

# Run the server
./launch_ntpmcp.sh
```

### Local Installation

```bash
# Install to local directory
mkdir -p ~/ntp-mcp
cp -r src pyproject.toml launch_ntpmcp.sh ~/ntp-mcp/
cd ~/ntp-mcp
uv sync

# Run the server
./launch_ntpmcp.sh
```

### Environment Variables

- `NTP_SERVER`: NTP server to use (default: `pool.ntp.org` for dev, `time.cloudflare.com` for prod)
- `TZ`: Timezone for time display (default: system local or UTC)

## 📦 Installation for Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "ntp-server": {
      "command": "uv",
      "args": ["run", "python", "-m", "ntp_mcp"],
      "cwd": "/path/to/ntp-mcp",
      "env": {
        "NTP_SERVER": "time.cloudflare.com",
        "TZ": "UTC"
      }
    }
  }
}
```

## 🔧 Available Tools

### `get_current_time`
Get the current time from an approved NTP server.

**Example:**
```javascript
{
  "tool": "get_current_time",
  "arguments": {}
}
```

### `list_approved_servers`
List all approved NTP servers that can be used.

**Example:**
```javascript
{
  "tool": "list_approved_servers",
  "arguments": {}
}
```


## 🐧 Systemd Service (Optional)

For automatic startup on Linux:

```bash
# Copy service file
sudo cp /path/to/ntp-mcp/ntp-mcp.service /etc/systemd/system/

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ntp-mcp
sudo systemctl start ntp-mcp

# Check status
sudo systemctl status ntp-mcp
```

## 📝 Configuration

### Claude Desktop (Windows)
```json
{
  "mcpServers": {
    "ntp-server": {
      "command": "wsl",
      "args": ["-e", "bash", "-c", "cd /path/to/ntp-mcp && uv run python -m ntp_mcp"],
      "env": {
        "NTP_SERVER": "time.cloudflare.com",
        "TZ": "America/New_York"
      }
    }
  }
}
```

### Claude Desktop (Linux/Mac)
```json
{
  "mcpServers": {
    "ntp-server": {
      "command": "/path/to/ntp-mcp/.venv/bin/python",
      "args": ["-m", "ntp_mcp"],
      "env": {
        "NTP_SERVER": "time.cloudflare.com",
        "TZ": "UTC"
      }
    }
  }
}
```

## 📊 Performance

- **Startup time**: <1 second (UV optimization)
- **Memory usage**: <50MB
- **Response time**: <100ms (local region servers)


## 🛡️ Security Notes

- Geographic security filtering is enforced
- Direct IP addresses are not allowed
- Only whitelisted servers can be used
- Security patterns are regularly updated

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please ensure:
- Security filtering is maintained
- All tests pass
- UV package management is used
- Security best practices are followed

## 📞 Support

For issues or questions, please open an issue on GitHub.

## 🙏 Acknowledgments

This project was initially inspired by [n3r0-b1n4ry/ntp-mcp-server](https://github.com/n3r0-b1n4ry/ntp-mcp-server), but has been completely redesigned and rewritten with enhanced security, performance optimizations, and production robustness.