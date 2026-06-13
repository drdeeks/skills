# imsg CLI Commands Reference

## Basic Commands

### chats
List recent chats from Messages.app.

```bash
# List last 10 chats
imsg chats --limit 10 --json

# List with metadata
imsg chats --limit 20 --json | jq '.[] | {displayName, service, lastMessage}'
```

**Options:**
- `--limit N` - Number of chats to return (default: 10)
- `--json` - Output as JSON
- `--raw` - Output raw data

### history
View message history for a specific chat.

```bash
# View last 20 messages
imsg history --chat-id 1 --limit 20 --json

# With attachments
imsg history --chat-id 1 --limit 20 --attachments --json

# Specific date range
imsg history --chat-id 1 --from 2024-01-01 --to 2024-01-31 --json
```

**Options:**
- `--chat-id ID` - Chat identifier (required)
- `--limit N` - Number of messages (default: 20)
- `--attachments` - Include attachment info
- `--from DATE` - Start date (YYYY-MM-DD)
- `--to DATE` - End date (YYYY-MM-DD)
- `--json` - Output as JSON

### send
Send a message to a recipient.

```bash
# Text only
imsg send --to "+14155551212" --text "Hello!"

# With attachment
imsg send --to "+14155551212" --text "Check this out" --file /path/to/image.jpg

# Force iMessage
imsg send --to "+14155551212" --text "Hi" --service imessage

# Force SMS
imsg send --to "+14155551212" --text "Hi" --service sms
```

**Options:**
- `--to RECIPIENT` - Phone number or Apple ID (required)
- `--text MESSAGE` - Message text (required)
- `--file PATH` - Attach file
- `--service SERVICE` - Force service (imessage, sms, auto)

### watch
Watch for new messages in a chat.

```bash
# Watch chat
imsg watch --chat-id 1 --attachments

# Watch with timeout
imsg watch --chat-id 1 --timeout 60

# Watch specific sender
imsg watch --chat-id 1 --sender "+14155551212"
```

**Options:**
- `--chat-id ID` - Chat identifier (required)
- `--attachments` - Include attachments
- `--timeout SECONDS` - Watch duration
- `--sender SENDER` - Filter by sender

## Advanced Commands

### search
Search messages across all chats.

```bash
# Search for text
imsg search "meeting tomorrow" --json

# Search with date filter
imsg search "invoice" --from 2024-01-01 --json

# Search specific chat
imsg search "deadline" --chat-id 1 --json
```

**Options:**
- `--query TEXT` - Search text (required)
- `--chat-id ID` - Limit to specific chat
- `--from DATE` - Start date
- `--to DATE` - End date
- `--json` - Output as JSON

### contacts
List contacts from Messages.app.

```bash
# List all contacts
imsg contacts --json

# Search contacts
imsg contacts --search "John" --json

# Get contact details
imsg contacts --id 1 --json
```

**Options:**
- `--search TEXT` - Search contacts
- `--id ID` - Get specific contact
- `--json` - Output as JSON

### attachments
List attachments from messages.

```bash
# List recent attachments
imsg attachments --limit 20 --json

# List from specific chat
imsg attachments --chat-id 1 --json

# Download attachment
imsg attachments --id 1 --download /path/to/save
```

**Options:**
- `--chat-id ID` - Limit to chat
- `--limit N` - Number of attachments
- `--download PATH` - Download attachment
- `--json` - Output as JSON

## Configuration Commands

### config
View or modify imsg configuration.

```bash
# Show config
imsg config

# Set default service
imsg config set default-service imessage

# Set notification settings
imsg config set notifications true
```

**Options:**
- `show` - Show current config
- `set KEY VALUE` - Set config value
- `get KEY` - Get config value
- `reset` - Reset to defaults

### status
Check imsg status and permissions.

```bash
# Check status
imsg status

# Check permissions
imsg status --permissions

# Check Messages.app
imsg status --messages-app
```

**Options:**
- `--permissions` - Check system permissions
- `--messages-app` - Check Messages.app status
- `--verbose` - Detailed output

## Utility Commands

### version
Show imsg version.

```bash
imsg version
```

### help
Show help for commands.

```bash
# General help
imsg help

# Help for specific command
imsg help send
imsg help history
```

## Output Formats

### JSON Output
Most commands support `--json` for structured output.

```json
{
  "chatId": 1,
  "displayName": "Mom",
  "service": "iMessage",
  "lastMessage": "I'll be late",
  "lastMessageDate": "2024-01-15T10:30:00Z"
}
```

### Raw Output
Use `--raw` for unformatted output.

### Table Output
Default output is human-readable tables.

## Best Practices

1. **Use JSON output** - For parsing and scripting
2. **Limit results** - Use `--limit` to avoid large outputs
3. **Filter appropriately** - Use search and date filters
4. **Confirm before sending** - Always verify recipients
5. **Handle errors** - Check exit codes and error messages