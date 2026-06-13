#!/usr/bin/env python3
"""
Hermes Agent Manager
Simple CLI for managing agents in the multi-agent system.
"""

import json
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Configuration
WORKSPACES_DIR = Path.home() / "hermes-agent" / "workspaces"
AGENTS_JSON = WORKSPACES_DIR / "agents.json"
TEMPLATE_DIR = WORKSPACES_DIR / "templates" / "new-agent"

def load_agents():
    """Load agents from agents.json."""
    if not AGENTS_JSON.exists():
        return {"agents": []}
    try:
        with open(AGENTS_JSON) as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading agents.json: {e}")
        return {"agents": []}

def save_agents(data):
    """Save agents to agents.json."""
    try:
        with open(AGENTS_JSON, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving agents.json: {e}")
        return False

def list_agents():
    """List all registered agents."""
    data = load_agents()
    agents = data.get("agents", [])
    
    if not agents:
        print("No agents registered.")
        return
    
    print(f"\nRegistered Agents ({len(agents)}):")
    print("-" * 80)
    for agent in agents:
        status = "✓" if agent.get("status") == "active" else "✗"
        print(f"{status} {agent['id']:15} | {agent['name']:20} | {agent['description'][:40]}")
        print(f"   Model: {agent.get('model', {}).get('name', 'unknown'):20} | Service: {agent.get('service', 'none')}")
        print(f"   Workspace: {agent.get('workspace', 'unknown')}")
        print()

def create_agent(agent_id, name, description, model_provider="codestral", model_name="codestral-latest"):
    """Create a new agent from template."""
    # Check if agent already exists
    data = load_agents()
    for agent in data.get("agents", []):
        if agent["id"] == agent_id:
            print(f"Error: Agent '{agent_id}' already exists.")
            return False
    
    # Check if workspace already exists
    agent_dir = WORKSPACES_DIR / agent_id
    if agent_dir.exists():
        print(f"Error: Workspace '{agent_dir}' already exists.")
        return False
    
    # Copy template
    if not TEMPLATE_DIR.exists():
        print(f"Error: Template directory '{TEMPLATE_DIR}' not found.")
        return False
    
    try:
        shutil.copytree(TEMPLATE_DIR, agent_dir)
        print(f"Created workspace: {agent_dir}")
    except Exception as e:
        print(f"Error copying template: {e}")
        return False
    
    # Update identity.json
    identity_file = agent_dir / "agent" / "identity.json"
    if identity_file.exists():
        try:
            with open(identity_file) as f:
                identity = json.load(f)
            
            identity["id"] = agent_id
            identity["name"] = name
            identity["description"] = description
            identity["created"] = datetime.now().isoformat()
            identity["model"]["provider"] = model_provider
            identity["model"]["name"] = model_name
            
            with open(identity_file, 'w') as f:
                json.dump(identity, f, indent=2)
            print(f"Updated: {identity_file}")
        except Exception as e:
            print(f"Warning: Could not update identity.json: {e}")
    
    # Add to registry
    new_agent = {
        "id": agent_id,
        "name": name,
        "description": description,
        "workspace": str(agent_dir),
        "model": {
            "provider": model_provider,
            "name": model_name,
            "type": "cloud" if model_provider != "ollama" else "local"
        },
        "service": f"{agent_id}-bot.service",
        "allowed_users": [],
        "permissions": {
            "shell_access": False,
            "file_operations": "read_only",
            "network_access": False,
            "external_actions": "never",
            "destructive_commands": "never"
        },
        "skills": ["child-safe-subset"] if "child" in description.lower() else ["all"],
        "created": datetime.now().strftime("%Y-%m-%d"),
        "status": "active"
    }
    
    data["agents"].append(new_agent)
    if save_agents(data):
        print(f"Added agent to registry: {AGENTS_JSON}")
        print(f"\nAgent '{name}' created successfully!")
        print(f"Next steps:")
        print(f"1. Edit {agent_dir}/agent/SOUL.md")
        print(f"2. Edit {agent_dir}/agent/identity.json")
        print(f"3. Edit {agent_dir}/agent/config.json")
        print(f"4. Create user profile: {agent_dir}/agent/USER.md")
        print(f"5. Set up Telegram bot (if needed)")
        return True
    else:
        print("Error: Could not save to agents.json")
        return False

def show_agent(agent_id):
    """Show details of a specific agent."""
    data = load_agents()
    for agent in data.get("agents", []):
        if agent["id"] == agent_id:
            print(f"\nAgent: {agent['name']} ({agent['id']})")
            print("-" * 50)
            print(f"Description: {agent['description']}")
            print(f"Status: {agent.get('status', 'unknown')}")
            print(f"Created: {agent.get('created', 'unknown')}")
            print(f"\nModel:")
            model = agent.get('model', {})
            print(f"  Provider: {model.get('provider', 'unknown')}")
            print(f"  Name: {model.get('name', 'unknown')}")
            print(f"  Type: {model.get('type', 'unknown')}")
            print(f"\nPlatform:")
            print(f"  Service: {agent.get('service', 'none')}")
            print(f"  Workspace: {agent.get('workspace', 'unknown')}")
            print(f"\nPermissions:")
            perms = agent.get('permissions', {})
            for key, value in perms.items():
                print(f"  {key}: {value}")
            print(f"\nAllowed Users: {', '.join(agent.get('allowed_users', []))}")
            print(f"Skills: {', '.join(agent.get('skills', []))}")
            return True
    
    print(f"Agent '{agent_id}' not found.")
    return False

def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("Hermes Agent Manager")
        print("Usage:")
        print("  agent-manager.py list                - List all agents")
        print("  agent-manager.py show <agent-id>     - Show agent details")
        print("  agent-manager.py create <id> <name> <description> [model-provider] [model-name]")
        print("  agent-manager.py help                - Show this help")
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        list_agents()
    elif command == "show" and len(sys.argv) > 2:
        show_agent(sys.argv[2])
    elif command == "create" and len(sys.argv) > 4:
        agent_id = sys.argv[2]
        name = sys.argv[3]
        description = sys.argv[4]
        model_provider = sys.argv[5] if len(sys.argv) > 5 else "codestral"
        model_name = sys.argv[6] if len(sys.argv) > 6 else "codestral-latest"
        create_agent(agent_id, name, description, model_provider, model_name)
    elif command == "help":
        print("Hermes Agent Manager")
        print("Usage:")
        print("  agent-manager.py list                - List all agents")
        print("  agent-manager.py show <agent-id>     - Show agent details")
        print("  agent-manager.py create <id> <name> <description> [model-provider] [model-name]")
        print("  agent-manager.py help                - Show this help")
    else:
        print(f"Unknown command: {command}")
        print("Use 'agent-manager.py help' for usage information.")

if __name__ == "__main__":
    main()
```

## Installation

```bash
# Save to scripts directory
cp agent-manager.py ~/hermes-agent/scripts/
chmod +x ~/hermes-agent/scripts/agent-manager.py

# Create symlink for easy access (optional)
ln -s ~/hermes-agent/scripts/agent-manager.py /usr/local/bin/hermes-agents
```

## Usage Examples

```bash
# List all agents
python3 ~/hermes-agent/scripts/agent-manager.py list

# Show agent details
python3 ~/hermes-agent/scripts/agent-manager.py show titan

# Create new agent
python3 ~/hermes-agent/scripts/agent-manager.py create trading-agent "Trading Agent" "Autonomous trading and market analysis" "codestral" "codestral-latest"

# Create child-safe agent
python3 ~/hermes-agent/scripts/agent-manager.py create kids-agent "Kids Agent" "Child-safe companion agent" "ollama" "qwen2.5:1.5b"
```

## Customization

Edit the script to add:
- Additional agent types
- Custom validation
- Integration with other tools
- Automated service setup
- Backup/restore functionality
