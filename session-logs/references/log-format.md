# Session Log Format

## JSON Structure
```json
{
  "session_id": "uuid",
  "timestamp": "ISO8601",
  "agent_id": "string",
  "events": [
    {
      "type": "tool_call | tool_result | message | error",
      "timestamp": "ISO8601",
      "data": {}
    }
  ]
}
```

## Event Types
- `tool_call`: Agent invoked a tool
- `tool_result`: Tool returned a result
- `message`: Agent sent a message
- `error`: An error occurred

## Storage
Logs stored in `${HOME}/.opencode/sessions/{session_id}.jsonl`
