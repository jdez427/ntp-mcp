# Natural Language Commands for NTP-MCP

## 🚀 SESSION START COMMAND (Use This First!)

When starting a new conversation, use ONE of these commands to force time synchronization:

```
"What time is it?"
```

That's it! This simple question will:
- ✅ Force the AI to sync with the NTP server
- ✅ Establish the correct timezone for your session
- ✅ Ensure all timestamps in the conversation are accurate
- ✅ Cache the time for 30 seconds (subsequent requests use cache)

**Alternative session start commands that do the same thing:**
- "Get time"
- "Sync the time"
- "Sync time"
- "Synchronize time"
- "Get the current time"
- "Check the time"

But honestly, **"What time is it?"** is the most natural.

---

## Primary Purpose: Initial Time Synchronization

The NTP-MCP server's main purpose is to ensure AI assistants are synchronized with accurate time immediately when a conversation begins. This prevents timezone confusion and ensures all timestamps, scheduling, and time-based decisions are correct from the start.

## Why Start With "What time is it?"

AI assistants may start with incorrect time assumptions, especially when:
- Running in containers with UTC time
- Deployed across different time zones
- Restored from snapshots or checkpoints
- Subject to clock drift in virtual environments

By asking "What time is it?" at the start, you ensure:
- Accurate scheduling and reminders
- Correct relative time calculations ("in 2 hours", "yesterday")
- Proper timestamp formatting for logs and records
- Timezone-aware responses for global teams

## Other Time Commands

### Direct Time Requests
*These all trigger the get_current_time tool:*
- "What time is it?" (RECOMMENDED for session start)
- "Get the current time"
- "Show me the current time"
- "Fetch the time from NTP"
- "What's the time right now?"
- "Tell me the current time"

### Timezone-Related Commands
*Note: The MCP uses the TZ environment variable set at startup. These commands will show time in the configured timezone, not change it dynamically.*
- "What time is it?" (shows in configured timezone)
- "Get the current time" (uses TZ environment setting)
- "Show me the time and timezone" (displays configured TZ)

### Getting Time (All Equivalent)
*The MCP doesn't have separate "verify" vs "get" - all these commands return the current time:*
- "Check the time"
- "Verify the current time"
- "Get time from NTP server"
- "What time does the NTP server say?"
- "Synchronize and show time"

### Time-Related Questions
- "What time is it?"
- "What's the current time and date?"
- "Can you tell me what time it is right now?"
- "Show me the current date and time"
- "What day is it today?"

### Context-Setting Requests
- "Good morning! What time is it?" (Polite session start)
- "Let's start - what's the current time?" (Professional session start)
- "Hello! Can you tell me the time?" (Friendly session start)
- "Before we begin, what time is it?" (Explicit sync request)


## Configuration Commands

While these aren't typically used at session start, users might also ask:

### Server Information
- "List the approved time servers"
- "Show me available NTP servers"
- "What servers are approved?"
- "Which time servers can I use?"

*Note: The MCP has exactly 25 approved servers including pool.ntp.org, time.google.com, time.cloudflare.com, and regional pools. Untrusted servers are blocked.*

## Technical Capabilities

### What the MCP Actually Does

**Tool 1: get_current_time**
- Returns current date, time, timezone from NTP server
- Uses NTP_SERVER environment variable (default: pool.ntp.org)
- Uses TZ environment variable (default: system timezone)
- Caches responses for 30 seconds
- Falls back to local system time if NTP fails
- No input parameters accepted from prompts

**Tool 2: list_approved_servers**
- Returns list of 25 approved NTP servers
- Includes pool.ntp.org, time.google.com, time.cloudflare.com, etc.
- No input parameters accepted from prompts

### Important Limitations
- ❌ Cannot dynamically change timezone (set via TZ env var at startup)
- ❌ Cannot use custom NTP servers (uses NTP_SERVER env var at startup)
- ❌ Cannot accept IP addresses as servers
- ❌ Cannot perform time calculations or comparisons
- ❌ Cannot show multiple timezones simultaneously
- ❌ Cannot modify system time

## Actual MCP Response Examples

### Successful NTP Response
When you ask "What time is it?" or similar, the MCP returns:
```
Date:2025-08-29
Time:09:30:45
Timezone:EST
NTP Server:pool.ntp.org
Source:NTP
```

### Cached Response
If you ask again within 30 seconds, you'll get:
```
Date:2025-08-29
Time:09:30:45
Timezone:EST
NTP Server:pool.ntp.org
Source:NTP
(cached)
```

### Fallback Response
If the NTP server is unreachable:
```
Date:2025-08-29
Time:09:30:45
Timezone:EST
Source:LOCAL SYSTEM (NTP unavailable: Network error: Connection timed out)
```

## MCP Tools Available

The NTP-MCP provides exactly two tools:

1. **get_current_time** - Returns the current time from an NTP server
   - No input parameters accepted in prompts
   - Server configured via NTP_SERVER environment variable at startup (default: 'pool.ntp.org')
   - Timezone configured via TZ environment variable at startup (default: system timezone)
   - Returns: Date, Time, Timezone, NTP Server, Source

2. **list_approved_servers** - Lists all 25 approved NTP servers
   - No input parameters accepted in prompts
   - Returns the complete whitelist including pool.ntp.org, time.google.com, time.cloudflare.com, and regional pools
   - Untrusted servers are automatically blocked

## Security Note

The NTP-MCP server includes security filtering to prevent connections to potentially compromised time servers. If a user requests a specific server that's blocked, the AI will explain the security policy and suggest approved alternatives.