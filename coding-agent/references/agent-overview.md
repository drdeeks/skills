# Coding Agent Overview

Overview of coding agent delegation patterns.

## Agent Types

- **Codex**: OpenAI's coding agent (requires PTY)
- **Claude Code**: Anthropic's CLI (print mode)
- **Pi**: Coding agent (requires PTY)
- **OpenCode**: Interactive coding (requires PTY)

## Mode Selection

| Agent | Mode | PTY Required |
|-------|------|--------------|
| Codex | Interactive | Yes |
| Claude Code | Print (`-p`) | No |
| Pi | Interactive | Yes |
| OpenCode | Interactive | Yes |

## Best Practices

- Use `--max-turns` in print mode to prevent runaway
- Set `--max-budget-usd` for cost caps
- Use `--allowedTools` to restrict capabilities
