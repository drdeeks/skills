---
description: 'Set up and organize a multi-agent workspace with standardized structure,
  registry, templates, and management tools. Use when: creating new agents, organizing
  existing agents, establishing agent conventions, or setting up agent management
  infrastructure. NOT for: single-agent setups, modifying agent behavior/SOUL.md content,
  or managing running agent services (use systemd/telegram-admin-portal for that).'
metadata:
  hermes:
    related_skills:
    - telegram-admin-portal
    - soul-generator
    - autonomous-ai-agents
    tags:
    - agents
    - workspace
    - organization
    - multi-agent
    - templates
name: multi-agent-workspace-setup
version: 0.0.4
---

# Multi-Agent Workspace Setup

Set up a standardized, scalable multi-agent workspace with registry, templates, and management tools.

## When to Use

✅ **USE this skill when:**
- Creating a new agent workspace from scratch
- Organizing existing agents into a consistent structure
- Setting up agent management infrastructure
- Documenting agent conventions and processes
- Creating templates for future agents

❌ **DON'T use this skill when:**
- Modifying individual agent SOUL.md or behavior
- Managing running agent services (use systemd)
- Deploying Telegram bots (use telegram-admin-portal)
- Fine-tuning models or training

## Quick Start

```bash
# 1. Create agent registry
cat > ~/hermes-agent/workspaces/agents.json << 'EOF'
{
  "version": "1.0",
  "last_updated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "agents": []
}
EOF

# 2. Create template directory
mkdir -p ~/hermes-agent/workspaces/templates/new-agent/agent

# 3. Copy template files (see references/template-files.md)
# 4. Create management script (see references/agent-manager.py)
```

## Directory Structure

```
workspaces/
├── agents.json                    # Central agent registry
├── templates/
│   └── new-agent/                 # Template for new agents
│       ├── agent/
│       │   ├── SOUL.md           # Identity template
│       │   ├── USER.md           # User profile template
│       │   ├── AGENTS.md         # Session protocol template
│       │   ├── HEARTBEAT.md      # Background tasks template
│       │   ├── MEMORY.md         # Long-term memory (empty)
│       │   ├── TOOLS.md          # Tool notes template
│       │   ├── config.json       # Configuration template
│       │   └── identity.json     # Metadata template
│       └── README.md             # Template usage guide
├── [agent-id]/                   # Individual agent workspaces
│   ├── agent/
│   ├── memory/
│   ├── projects/
│   ├── skills/
│   └── sessions/
└── docs/
    └── adding-new-agents.md      # Agent creation guide
```

## Step-by-Step Setup

### 1. Create Agent Registry

Location: `~/hermes-agent/workspaces/agents.json`

```json
{
  "version": "1.0",
  "last_updated": "2026-04-10T15:30:00Z",
  "agents": [
    {
      "id": "agent-id",
      "name": "Agent Name",
      "description": "What this agent does",
      "workspace": "~/hermes-agent/workspaces/agent-id",
      "model": {
        "provider": "codestral|ollama|openai|anthropic",
        "name": "model-name",
        "type": "cloud|local"
      },
      "service": "agent-id-bot.service",
      "allowed_users": ["user1"],
      "permissions": {
        "shell_access": true|false,
        "file_operations": "full|read_only|none",
        "network_access": true|false,
        "external_actions": "ask_first|never|always",
        "destructive_commands": "confirm|never"
      },
      "skills": ["all"] or ["skill1", "skill2"],
      "created": "2026-04-10",
      "status": "active"
    }
  ]
}
```

### 2. Create Standardized Template

See `references/template-files.md` for complete template files.

Key files:
- `agent/SOUL.md` - Agent identity with placeholders
- `agent/identity.json` - Machine-readable metadata
- `agent/config.json` - Runtime configuration
- `agent/AGENTS.md` - Session protocol

### 3. Create Management Script

See `references/agent-manager.py` for a complete CLI tool.

Commands:
```bash
python3 agent-manager.py list                    # Show all agents
python3 agent-manager.py show <agent-id>         # Agent details
python3 agent-manager.py create <id> <name> <desc> [model-provider] [model-name]
```

### 4. Document the Process

Create `~/hermes-agent/docs/adding-new-agents.md` with:
- Prerequisites
- Workspace creation steps
- Configuration guide
- Service setup
- Testing checklist

## Agent Creation Workflow

### Using Template
```bash
# 1. Copy template
cp -r ~/hermes-agent/workspaces/templates/new-agent ~/hermes-agent/workspaces/[agent-id]

# 2. Customize files
cd ~/hermes-agent/workspaces/[agent-id]
# Edit agent/SOUL.md, identity.json, config.json, AGENTS.md, USER.md

# 3. Create supporting directories
mkdir -p memory projects skills sessions backups

# 4. Add to registry
# Edit ~/hermes-agent/workspaces/agents.json

# 5. Set up Telegram bot (if needed)
# Create /opt/telegram-webhook/[agent-id]-bot.py
# Create /etc/systemd/system/[agent-id]-bot.service
# sudo systemctl enable --now [agent-id]-bot.service
```

## Best Practices

### Structure
- All agents use `agent/` subdirectory for identity files
- Separate `memory/`, `projects/`, `skills/`, `sessions/` directories
- Keep templates in `templates/` directory

### Naming
- Agent IDs: lowercase-hyphen (e.g., `trading-agent`)
- Display names: Title Case (e.g., `Trading Agent`)
- Services: `[agent-id]-bot.service`

### Security
- Principle of least privilege per agent
- Separate workspaces for isolation
- Different API keys/tokens per agent
- Resource limits via cgroups (for resource-intensive agents)

### Documentation
- Document each agent's purpose and permissions
- Keep registry updated
- Maintain templates as conventions evolve

## Common Agent Types

### Infrastructure Agent (like Titan)
- Full shell access
- All skills enabled
- Cloud model (Codestral, Claude, GPT-4)
- For: DevOps, automation, system administration

### Child-Safe Agent (like Avery)
- No shell access
- Restricted skills (child-safe subset)
- Local model (Qwen, Llama)
- For: Kids, educational, safe interactions

### Trading Agent
- Limited shell access (trading commands only)
- Trading-specific skills
- Cloud model with low latency
- For: Market analysis, trading automation

### Research Agent
- Read-only file access
- Research skills (arxiv, web search)
- Cloud model with large context
- For: Academic research, paper analysis

## Troubleshooting

### Agent Not Starting
1. Check service: `systemctl status [agent-id]-bot.service`
2. Check logs: `journalctl -u [agent-id]-bot.service -f`
3. Verify bot token in environment
4. Check workspace permissions

### Registry Issues
1. Validate JSON: `python3 -m json.tool agents.json`
2. Check workspace paths exist
3. Verify service names match

### Template Problems
1. Ensure all placeholders replaced
2. Check file permissions
3. Validate JSON files

## Pitfalls

### Common Mistakes
- **Inconsistent structure**: Some agents with `agent/` subdirectory, some without
- **Missing registry**: Agents exist but not tracked centrally
- **Hardcoded paths**: Service files with absolute paths that break on reorganization
- **No documentation**: Adding agents without updating docs

### Solutions
- Always use template system
- Keep registry updated
- Use relative paths where possible
- Document as you go

## References

- `references/template-files.md` - Complete template file contents
- `references/agent-manager.py` - Management script
- `~/hermes-agent/docs/adding-new-agents.md` - Detailed guide
- Existing agents: `titan/`, `avery/` - Real-world examples

## Verification

After setup, verify:
1. `agents.json` exists and is valid JSON
2. Template directory has all required files
3. Management script runs: `python3 agent-manager.py list`
4. Documentation exists and is accurate
5. Existing agents are registered in registry

---

*This skill creates the infrastructure for managing multiple agents. Use it when setting up new agent workspaces or organizing existing ones.*