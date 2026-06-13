# Workspace Structure Reference

## Required Directories

Every agent workspace must have:

| Directory | Purpose | Permissions |
|-----------|---------|-------------|
| `memory/` | Daily memory logs (YYYY-MM-DD.md) | 755 |
| `skills/` | Skill definitions (read-only reference) | 755 |
| `projects/` | Working project directories | 755 |
| `tools/` | Operational scripts | 755 |
| `logs/` | Agent log files | 755 |
| `.secrets/` | Encrypted secret storage | 755 |
| `.archive/` | Long-term archive storage | 755 |
| `.override/` | Critical file overrides | 755 |

## Required Files

| File | Purpose |
|------|---------|
| `SOUL.md` | Agent's core identity and principles |
| `USER.md` | Owner preferences |
| `agent.json` | Machine-readable agent manifest |
| `config.yaml` | Runtime configuration |
| `MEMORY.md` | Long-term curated memory |
| `HEARTBEAT.md` | Scheduled task definitions |

## Required Tools

| Tool | Purpose |
|------|---------|
| `enforce.sh` | Workspace structure enforcement |
| `secret.sh` | Encrypted secret management |
| `memory-log.sh` | Memory logging |
| `memory-promote.sh` | Memory promotion |
| `jsonfmt.py` | JSON formatting and validation |
| `TOOLS-GUIDE.md` | Tool usage documentation |
| `inject-context.sh` | Session context injection |
| `safe-write.sh` | Safe file writing with override protocol |

## Forbidden Patterns

- Never use `chmod 700` or `chmod 000` (except `.secret-key`)
- Never use `rm -rf` on user directories
- Never overwrite critical files — use override protocol
