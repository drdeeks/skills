# Claude Code Hooks Reference

Automation hooks for Claude Code sessions.

## Hook Types

| Hook | When | Common Use |
|------|------|------------|
| PreToolUse | Before tool execution | Security gates |
| PostToolUse | After tool finishes | Auto-format |
| Stop | Response complete | Logging |
| UserPromptSubmit | Before processing | Validation |
| SessionStart | Session begins | Load context |

## Hook Variables

- `CLAUDE_PROJECT_DIR` - Current project path
- `CLAUDE_FILE_PATHS` - Files being modified
- `CLAUDE_TOOL_INPUT` - Tool parameters as JSON

## Security Hooks

Block dangerous commands:
```json
{
  "PreToolUse": [{
    "matcher": "Bash",
    "hooks": [{"type": "command", "command": "exit 2"}]
  }]
}
```
