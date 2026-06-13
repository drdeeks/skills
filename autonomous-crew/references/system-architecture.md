# Autonomous Crew Reference

Multi-agent system architecture and deployment reference.

## System Architecture

4 Telegram bots with 192+ commands:
- Hermes: Communication agent
- Titan: Infrastructure agent
- Avery: Child-safe agent
- Agent Allman: ERC-8004 agent creator

## Deployment

Use systemd services for each bot:
```bash
sudo systemctl start telegram-bot.service
```

## Workspace Structure

Standardized directory layout for all agents with:
- `.secrets/` for credentials (mode 700)
- `memory/` for session memory
- `tools/` for utilities
