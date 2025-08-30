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

### What You'll Need

1. **Python 3.11 or newer** - The programming language this server runs on
   - Check if you have it: Open a terminal and type `python --version`
   - If you need it: Download from [python.org](https://python.org)

2. **UV Package Manager** - A fast, modern Python package installer (like npm for Node.js)
   - UV is faster and more reliable than pip
   - It handles dependencies and virtual environments automatically
   - Install UV with ONE of these commands:
     - Windows/Mac/Linux with pip: `pip install uv`
     - Mac/Linux with curl: `curl -LsSf https://astral.sh/uv/install.sh | sh`

3. **Git** (optional) - For cloning the repository
   - Or you can download the ZIP file from GitHub

### Step-by-Step Installation

#### Option 1: Using Git (Recommended)

```bash
# 1. Clone (download) the repository
git clone https://github.com/jdez427/ntp-mcp.git

# 2. Enter the project directory
cd ntp-mcp

# 3. Let UV install all dependencies
#    This creates a virtual environment and installs everything needed
uv sync

# 4. Add the MCP to Claude (global installation)
#    This makes it available to all Claude instances
claude mcp add --scope user ntp bash /path/to/ntp-mcp/launch_ntpmcp.sh
```

That's it! Claude will automatically start the NTP server when needed.

#### Option 2: Download ZIP

1. Go to https://github.com/jdez427/ntp-mcp
2. Click the green "Code" button → "Download ZIP"
3. Extract the ZIP file to a folder
4. Open a terminal in that folder
5. Run:
   ```bash
   uv sync
   claude mcp add --scope user ntp bash /path/to/ntp-mcp/launch_ntpmcp.sh
   ```

### What's Happening During Installation?

- **`uv sync`** reads the `pyproject.toml` file and:
  - Creates an isolated Python environment (so it won't affect other Python projects)
  - Downloads and installs all required packages (mcp, ntplib, pytz, etc.)
  - Locks the versions for consistency
  
- **`claude mcp add`** command:
  - Registers the NTP-MCP with Claude globally (--scope user)
  - Points to the launch script that Claude will use
  - Claude automatically starts/stops the server as needed
  - No manual server management required!

### Local Installation

```bash
# Install to local directory
mkdir -p ~/ntp-mcp
cp -r src pyproject.toml launch_ntpmcp.sh ~/ntp-mcp/
cd ~/ntp-mcp
uv sync

# Add to Claude globally
claude mcp add --scope user ntp bash ~/ntp-mcp/launch_ntpmcp.sh
```

### Environment Variables

- `NTP_SERVER`: NTP server to use (default: `pool.ntp.org` for dev, `time.cloudflare.com` for prod)
- `TZ`: Timezone for time display (default: system local or UTC)

## 📦 Installation for Claude Desktop

### Method 1: Command Line (Recommended for Linux/WSL)

```bash
# Global installation for all Claude instances
claude mcp add --scope user ntp bash /path/to/ntp-mcp/launch_ntpmcp.sh

# Verify it's connected
claude mcp list
```

### Method 2: Manual Configuration

If you prefer manual configuration or are on Windows/Mac without the CLI:

#### Finding Your Configuration File

Claude Desktop stores its configuration in different places depending on your operating system:

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

#### Manual Setup
1. **Open the configuration file** in a text editor (Notepad, TextEdit, etc.)
2. **Find or create the `mcpServers` section**
3. **Add the NTP-MCP configuration** (see Configuration Format below)

### Configuration Format

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

## 🧪 Testing the Server (Optional)

If you want to test the server manually before adding it to Claude:

```bash
# Run the server manually (Ctrl+C to stop)
./launch_ntpmcp.sh

# In another terminal, you can test it with:
echo '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "clientInfo": {"name": "test", "version": "1.0"}, "capabilities": {}}, "id": 1}' | uv run python -m ntp_mcp
```

**Note:** Manual testing is optional. Once added to Claude with `claude mcp add`, Claude handles all server management automatically.

## 🔧 Troubleshooting

### Common Issues

**"Command not found" or "uv not found"**
- Make sure UV is installed: `pip install uv`
- On Windows, you might need to use `python -m uv` instead of just `uv`

**"Permission denied" or "cannot execute: required file not found"**
- On Mac/Linux: Run `chmod +x launch_ntpmcp.sh` to make it executable
- If you get "required file not found", the script may have Windows line endings
  - Fix with: `sed -i 's/\r$//' launch_ntpmcp.sh`
- On Windows: Use `python launch_ntpmcp.sh` instead

**Claude doesn't recognize the time command**
- Check your configuration file for syntax errors (missing commas, etc.)
- Make sure the path to ntp-mcp directory is correct
- Restart Claude Desktop completely (quit and reopen)

**"Module not found" errors**
- Run `uv sync` again to ensure all dependencies are installed
- Make sure you're in the ntp-mcp directory when running commands

**Time shows wrong timezone**
- Run the setup wizard: `python setup_timezone.py`
- Or manually set the TZ environment variable in the Claude config

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