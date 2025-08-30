# NTP-MCP Setup Guide

## Quick Start (Automatic Setup)

Run the setup script to automatically configure your timezone and install the MCP:

```bash
# Using Python (recommended - cross-platform)
python3 setup_timezone.py

# Or using Bash (Linux/WSL only)
./setup_timezone.sh
```

This will:
1. ✅ Detect your system's current timezone
2. ✅ Configure the NTP-MCP to use your timezone
3. ✅ Set a reliable default NTP server (time.cloudflare.com)
4. ✅ Check if NTP-MCP is already installed
5. ✅ Install or update the MCP safely using `claude mcp add`
6. ✅ Verify the connection is working

## What the Setup Script Does

### Smart Installation Management
The script intelligently handles different installation states:
- **Not Installed**: Automatically installs NTP-MCP
- **Already Working**: Asks if you want to update settings
- **Failed Connection**: Automatically reinstalls with correct settings
- **No Claude CLI**: Provides manual configuration instructions

### Automatic Timezone Detection
The script detects your timezone using multiple methods:
- System timezone settings (`timedatectl` on Linux)
- `/etc/timezone` file
- `TZ` environment variable
- `/etc/localtime` symlink

### Safe Configuration Updates
The script safely updates:
1. **Claude MCP Registration** (using `claude mcp add`)
   - Checks for existing installation first
   - Only updates if you confirm (when already installed)
   - Automatically fixes failed installations
   
2. **Launch Script Defaults** (`launch_ntpmcp.sh`)
   - Updates default timezone
   - Updates default NTP server
   - Fixes Windows line endings automatically

## Manual Configuration Options

### Option 1: Use a Different NTP Server

Run the setup script with a server name:

```bash
# Use Google's time server
python3 setup_timezone.py time.google.com

# Use NIST time server
python3 setup_timezone.py time.nist.gov
```

**Approved NTP Servers:**
- `time.cloudflare.com` (default - recommended)
- `time.google.com`
- `pool.ntp.org`
- `time.nist.gov`
- `time.windows.com`
- `time.apple.com`

### Option 2: Manual Installation with Claude CLI

If the setup script doesn't work for you, manually install:

```bash
# Add the MCP globally
claude mcp add --scope user ntp bash /path/to/ntp-mcp/launch_ntpmcp.sh

# Verify it's connected
claude mcp list
```

### Option 3: Edit Claude Configuration Directly

Add this to your Claude config file:

```json
{
  "mcpServers": {
    "ntp": {
      "command": "bash",
      "args": ["/path/to/ntp-mcp/launch_ntpmcp.sh"],
      "env": {
        "TZ": "America/New_York",
        "NTP_SERVER": "time.cloudflare.com"
      }
    }
  }
}
```

### Option 4: Set Environment Variables

Before starting Claude:

```bash
export TZ="America/Los_Angeles"
export NTP_SERVER="time.google.com"
claude
```

## Common Timezones

| Region | Timezone String |
|--------|----------------|
| US Eastern | `America/New_York` |
| US Central | `America/Chicago` |
| US Mountain | `America/Denver` |
| US Pacific | `America/Los_Angeles` |
| UK | `Europe/London` |
| EU Central | `Europe/Berlin` |
| Japan | `Asia/Tokyo` |
| Australia | `Australia/Sydney` |
| UTC | `UTC` |

## Verification

After setup, start Claude and test:

```
You: "What time is it?"
```

The response should show:
- Your local time
- Your configured timezone
- The NTP server used

Example response:
```
Date:2025-08-29
Time:14:30:45
Timezone:EST
NTP Server:time.cloudflare.com
Source:NTP
```

## Troubleshooting

### "Cannot execute: required file not found" Error
If you get this error when running the scripts, they may have Windows line endings:

```bash
# Fix line endings for both scripts
sed -i 's/\r$//' setup_timezone.sh launch_ntpmcp.sh
sed -i 's/\r$//' setup_timezone.py

# Or if you don't have sed, the Python script will auto-fix launch_ntpmcp.sh
python3 setup_timezone.py
```

The setup scripts now automatically fix line endings in launch_ntpmcp.sh.

### Script Can't Find Claude Config
If the setup script can't find your Claude configuration:

1. The script creates a local config at `~/.config/ntp-mcp/config.json`
2. Copy the contents to your Claude configuration manually
3. Or set the `CLAUDE_CONFIG_PATH` environment variable:
   ```bash
   export CLAUDE_CONFIG_PATH="/path/to/your/claude/config.json"
   python3 setup_timezone.py
   ```

### Wrong Timezone Detected
Override with the TZ environment variable:

```bash
export TZ="America/New_York"
python3 setup_timezone.py
```

### NTP Server Blocked
If your preferred NTP server is blocked by security filters, use one from the approved list above.

## Advanced Usage

### Using Different Timezones for Different Sessions

You can override the configured timezone for a specific Claude session:

```bash
# Override just for this session
TZ="Europe/London" claude

# Or permanently change
python3 setup_timezone.py  # Re-run to update
```

### Checking Current Configuration

View your current NTP-MCP configuration:

```bash
# If using Claude config
cat ~/.config/claude/claude_desktop_config.json | grep -A5 "ntp-server"

# Check launch script defaults
grep "export TZ\|export NTP_SERVER" ~/ntp-mcp/launch_ntpmcp.sh
```

## Security Notes

- The NTP-MCP implements geographic security filtering
- Direct IP addresses are not allowed as NTP servers
- Only approved NTP servers in the whitelist can be used
- The setup script only modifies configuration files, never system settings

## Need Help?

1. Run the setup script - it handles 90% of use cases automatically
2. Check the timezone is correct: `timedatectl` (Linux) or `echo $TZ`
3. Verify Claude is using the updated config (restart Claude after changes)
4. Test with "What time is it?" in your conversation

The setup script is idempotent - you can run it multiple times safely.