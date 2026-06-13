# iMessage Integration Guide

## Overview

This guide covers integrating the imsg CLI into automated workflows and scripts.

## Script Integration

### Basic Script Example
```bash
#!/bin/bash
# Simple iMessage integration script

RECIPIENT="+14155551212"
MESSAGE="Hello from automation!"

# Send message
imsg send --to "$RECIPIENT" --text "$MESSAGE"

# Check exit code
if [ $? -eq 0 ]; then
    echo "Message sent successfully"
else
    echo "Failed to send message"
    exit 1
fi
```

### Python Integration
```python
import subprocess
import json

def send_imessage(recipient, message, service="auto"):
    """Send iMessage using imsg CLI."""
    cmd = [
        "imsg", "send",
        "--to", recipient,
        "--text", message,
        "--service", service
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        return {"status": "success", "message": "Message sent"}
    else:
        return {"status": "error", "message": result.stderr}

def get_recent_chats(limit=10):
    """Get recent chats."""
    cmd = ["imsg", "chats", "--limit", str(limit), "--json"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        return []
```

## CI/CD Integration

### GitHub Actions
```yaml
- name: Send iMessage Notification
  run: |
    imsg send --to "${{ secrets.PHONE_NUMBER }}" \
      --text "Build ${{ github.run_id }} completed"
```

### GitLab CI
```yaml
notify:
  script:
    - imsg send --to "$PHONE_NUMBER" --text "Deployment complete"
```

## Automation Patterns

### Scheduled Messages
```bash
# Send daily reminder
cron="0 9 * * *"
command="imsg send --to '+14155551212' --text 'Daily reminder: Check emails'"

# Add to crontab
echo "$cron $command" | crontab -
```

### Event-Driven Messages
```bash
#!/bin/bash
# Watch for specific messages and respond

imsg watch --chat-id 1 --json | while read -r line; do
    # Parse message
    message=$(echo "$line" | jq -r '.message')
    
    # Check for specific content
    if [[ "$message" == *"urgent"* ]]; then
        imsg send --to "+14155551212" --text "Urgent message received!"
    fi
done
```

### Batch Processing
```bash
#!/bin/bash
# Send messages to multiple recipients

RECIPIENTS=("+14155551212" "+14155551213" "+14155551214")
MESSAGE="Team meeting at 3 PM"

for recipient in "${RECIPIENTS[@]}"; do
    imsg send --to "$recipient" --text "$MESSAGE"
    sleep 1  # Rate limiting
done
```

## Error Handling

### Retry Logic
```bash
retry_send() {
    local recipient="$1"
    local message="$2"
    local max_attempts=3
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if imsg send --to "$recipient" --text "$message" 2>/dev/null; then
            echo "Message sent successfully"
            return 0
        fi
        
        attempt=$((attempt + 1))
        sleep 2
    done
    
    echo "Failed to send message after $max_attempts attempts"
    return 1
}
```

### Validation
```bash
validate_recipient() {
    local recipient="$1"
    
    # Check phone number format
    if [[ "$recipient" =~ ^\+[0-9]{10,15}$ ]]; then
        return 0
    fi
    
    # Check Apple ID format
    if [[ "$recipient" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
        return 0
    fi
    
    echo "Invalid recipient format: $recipient"
    return 1
}
```

## Security Considerations

### Credential Management
- **No credentials stored** - Uses system Messages.app
- **User confirmation** - Always confirm before sending
- **Rate limiting** - Prevent accidental spam
- **Audit logging** - Log sent messages for review

### Privacy
- **Local processing** - No external services
- **System integration** - Uses Messages.app directly
- **User control** - Manual permission grants

## Best Practices

1. **Confirm before sending** - Always verify recipients and content
2. **Use JSON output** - For reliable parsing
3. **Implement error handling** - Handle failures gracefully
4. **Rate limit** - Avoid sending too many messages quickly
5. **Log activity** - Track sent messages for debugging
6. **Test thoroughly** - Verify integration works correctly
7. **Handle permissions** - Ensure system permissions are granted