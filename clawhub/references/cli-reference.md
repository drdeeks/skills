# ClawHub CLI Reference

Quick reference for ClawHub CLI commands.

## Installation

```bash
npm i -g clawhub
```

## Commands

| Command | Purpose |
|---------|---------|
| `clawhub search "query"` | Search for skills |
| `clawhub install <name>` | Install a skill |
| `clawhub update <name>` | Update a skill |
| `clawhub update --all` | Update all skills |
| `clawhub list` | List installed skills |
| `clawhub publish <path>` | Publish a skill |

## Configuration

Default registry: https://clawhub.com
Override: `CLAWHUB_REGISTRY` env var or `--registry` flag
