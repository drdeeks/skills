# OpenCode CLI Reference

## Common Flags

| Flag | Use |
|------|-----|
| `run 'prompt'` | One-shot execution and exit |
| `--continue` / `-c` | Continue the last OpenCode session |
| `--session <id>` / `-s` | Continue a specific session |
| `--agent <name>` | Choose OpenCode agent (build or plan) |
| `--model provider/model` | Force specific model |
| `--format json` | Machine-readable output/events |
| `--file <path>` / `-f` | Attach file(s) to the message |
| `--thinking` | Show model thinking blocks |
| `--variant <level>` | Reasoning effort (high, max, minimal) |
| `--title <name>` | Name the session |
| `--attach <url>` | Connect to a running opencode server |

## TUI Keybindings

| Key | Action |
|-----|--------|
| `Enter` | Submit message (press twice if needed) |
| `Tab` | Switch between agents (build/plan) |
| `Ctrl+P` | Open command palette |
| `Ctrl+X L` | Switch session |
| `Ctrl+X M` | Switch model |
| `Ctrl+X N` | New session |
| `Ctrl+X E` | Open editor |
| `Ctrl+C` | Exit OpenCode |

## Commands

### One-Shot Tasks
```bash
opencode run 'Add retry logic to API calls and update tests'
opencode run 'Review this config for security issues' -f config.yaml -f .env.example
opencode run 'Debug why tests fail in CI' --thinking
opencode run 'Refactor auth module' --model openrouter/anthropic/claude-sonnet-4
```

### Interactive Sessions
```bash
# Start background session
opencode

# Resume last session
opencode -c

# Resume specific session
opencode -s ses_abc123
```

### PR Review
```bash
opencode pr 42
```

### Session Management
```bash
opencode session list
opencode stats
opencode stats --days 7 --models anthropic/claude-sonnet-4
```
