# Multi-Agent Workspace Setup - Best Practices

## Directory Structure Standards

- All agents use `agent/` subdirectory for identity files
- Separate `memory/`, `projects/`, `skills/`, `sessions/` directories
- Keep templates in `templates/` directory
- Central registry at `workspaces/agents.json`

## Naming Conventions

- Agent IDs: lowercase-hyphen (e.g., `trading-agent`)
- Display names: Title Case (e.g., `Trading Agent`)
- Services: `[agent-id]-bot.service`

## Security

- Principle of least privilege per agent
- Separate workspaces for isolation
- Different API keys/tokens per agent
- Resource limits via cgroups for resource-intensive agents

## Documentation

- Document each agent's purpose and permissions
- Keep registry updated
- Maintain templates as conventions evolve
