# iMessage Skill Overview

## Description

This skill enables sending and receiving iMessages/SMS via the `imsg` CLI on macOS. It provides a simple interface to interact with Messages.app from the command line.

## Features

### Message Sending
- Send text messages to phone numbers or Apple IDs
- Send attachments (images, files, etc.)
- Force iMessage or SMS delivery
- Auto-detect service type

### Message Reading
- List recent chats
- View message history
- Watch for new messages
- Get attachment information

### Chat Management
- Search chats by name or number
- Get chat metadata
- Monitor conversation activity

## Requirements

- **macOS** with Messages.app signed in
- **imsg CLI** installed via Homebrew
- **Full Disk Access** granted for terminal
- **Automation permission** for Messages.app

## Installation

```bash
# Install imsg
brew install steipete/tap/imsg

# Verify installation
imsg --version
```

## Configuration

### Permissions
1. **Full Disk Access**: System Settings → Privacy → Full Disk Access
2. **Automation**: Grant when prompted by Messages.app

### Environment
- No environment variables required
- Uses system Messages.app configuration

## Use Cases

### Personal Automation
- Send reminders to yourself
- Read messages while working in terminal
- Automate repetitive messages

### Integration
- ChatOps workflows
- Notification systems
- Monitoring scripts

### Development
- Testing messaging applications
- Building chatbots
- Automating notifications

## Limitations

- **macOS only** - Not available on other platforms
- **No group management** - Can't add/remove members
- **Rate limiting** - Should avoid bulk messaging
- **Permissions required** - Needs Full Disk Access

## Security Considerations

- **No credential storage** - Uses system Messages.app
- **User confirmation** - Always confirm before sending
- **No bulk messaging** - Prevents spam
- **Privacy** - Messages stay in Messages.app

## Best Practices

1. **Confirm recipients** - Always verify before sending
2. **Check attachments** - Ensure files exist before attaching
3. **Rate limit** - Don't send too many messages quickly
4. **Use appropriate service** - Choose iMessage or SMS as needed
5. **Monitor activity** - Use watch mode for real-time updates

## Examples

### Basic Usage
```bash
# List recent chats
imsg chats --limit 10 --json

# Send a message
imsg send --to "+14155551212" --text "Hello!"

# View history
imsg history --chat-id 1 --limit 20 --json
```

### Advanced Usage
```bash
# Watch for new messages
imsg watch --chat-id 1 --attachments

# Send with attachment
imsg send --to "+14155551212" --text "Check this out" --file /path/to/image.jpg

# Force SMS
imsg send --to "+14155551212" --text "Hi" --service sms
```

## Troubleshooting

### Common Issues
1. **Permission denied** - Grant Full Disk Access
2. **Command not found** - Install via Homebrew
3. **Messages not sending** - Check Messages.app sign-in
4. **Attachments failing** - Verify file paths

### Debug Steps
1. Check imsg version: `imsg --version`
2. Verify permissions in System Settings
3. Test with simple text message
4. Check Messages.app connectivity

## Integration

### With Other Skills
- **Notification systems** - Send alerts via iMessage
- **Monitoring** - Watch for specific messages
- **Automation** - Trigger actions based on messages

### With External Tools
- **jq** - Parse JSON output
- **curl** - Combine with web APIs
- **AppleScript** - Extend Messages.app functionality

## Future Enhancements

- **Group messaging** - Support for group chats
- **Rich media** - Better attachment handling
- **Scheduling** - Timed message delivery
- **Analytics** - Message statistics and insights