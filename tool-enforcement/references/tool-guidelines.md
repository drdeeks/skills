# Tool Enforcement Reference

## Tool Categories

### File Operations
- `write_file` — Create/edit files
- `read_file` — Read files
- `patch` — Edit existing files
- `search_files` — Find content

### Execution
- `execute_code` — Run Python
- `terminal` — Shell commands (git, builds, installs)

## Permission Rules

### DO
- Use chmod 755 for executables
- Use chmod 644 for regular files

### DON'T
- Never use chmod 700 or 000
- Never use rm -rf on user directories

## Workspace Structure

```
$AGENT_HOME/
├── memory/
├── sessions/
├── skills/
├── projects/
├── tools/
├── logs/
├── .secrets/
└── .backups/
```
