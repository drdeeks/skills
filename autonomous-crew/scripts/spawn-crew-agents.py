#!/usr/bin/env python3
"""
Spawn all crew agents from blueprint.json
"""

import json
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime, timezone

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def spawn_agent(project_dir, crew_name, agent_def, agent_index, identity_skill_path):
    agent_id = agent_def["agent_id"]
    display_name = agent_def["display_name"]
    agent_type = agent_def["agent_type"]
    
    print(f"  Creating agent: {agent_id} ({display_name})")
    
    # Create workspace
    agent_workspace = project_dir / "agents" / agent_id
    agent_workspace.mkdir(parents=True, exist_ok=True)
    
    # Create .agent directory structure
    agent_dir = agent_workspace / ".agent"
    for d in ["habits", "logs", "metrics", "templates", "constitutions", "templates/tool-enforcement"]:
        (agent_dir / d).mkdir(parents=True, exist_ok=True)
    
    # Copy scripts from identity skill
    scripts_path = identity_skill_path / "scripts"
    if scripts_path.exists():
        for script in scripts_path.glob("*.py"):
            shutil.copy2(script, agent_workspace / script.name)
        for script in scripts_path.glob("*.sh"):
            shutil.copy2(script, agent_workspace / script.name)
            os.chmod(agent_workspace / script.name, 0o755)
    
    # Copy templates
    templates_src = identity_skill_path / "references/templates"
    if templates_src.exists():
        for tpl in templates_src.rglob("*"):
            if tpl.is_file():
                rel = tpl.relative_to(templates_src)
                dest = agent_dir / "templates" / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(tpl, dest)
    
    # Copy reference habits
    for habit in identity_skill_path.glob("references/*.yaml"):
        if "habit" in habit.name.lower() or "enforcement" in habit.name.lower():
            shutil.copy2(habit, agent_dir / "habits" / habit.name)
    
    # Create constitution
    constitution = {
        "agent": {
            "id": agent_id,
            "name": display_name,
            "type": agent_type,
            "personality": f"{agent_type}-specialist",
            "purpose": f"Serve as {agent_type} specialist in crew {crew_name}",
            "core_values": [
                "Identity before action",
                "Validation before claim", 
                "Memory before drift",
                "Crew over individual"
            ],
            "hard_constraints": [
                "Never execute without enforcer approval",
                "Never claim completion without reflection",
                "Never hardcode paths - use WORKSPACE_ROOT",
                "Never store secrets in plaintext"
            ],
            "operational_standards": {
                "pre_tool_check": "identity + tool + reflective habits",
                "post_tool_reflection": "mandatory",
                "completion_gate": "reflective-loop habit",
                "heartbeat_interval_seconds": 300
            }
        }
    }
    
    import yaml
    with open(agent_dir / "constitution.yaml", "w") as f:
        yaml.dump(constitution, f, default_flow_style=False, sort_keys=False)
    
    # Create genesis.md
    genesis = f"""# GENESIS

**Agent:** {display_name} ({agent_id})
**Type:** {agent_type}
**Personality:** {agent_type}-specialist
**Crew:** {crew_name}
**Born:** {now_iso()}

## Purpose
Serve as {agent_type} specialist. Build systems that amplify human agency.
Learn continuously. Leave things better than found.

## Promise to Crew
- Constitution loaded at t=0
- Habits internalized, not invoked
- Enforcer watches, I build
- Memory curates, I act
- Next agent deserves better
"""
    with open(agent_dir / "genesis.md", "w") as f:
        f.write(genesis)
    
    # Create tools directory with required tools
    tools_dir = agent_workspace / "tools"
    tools_dir.mkdir(exist_ok=True)
    
    # Generate tool scripts from templates
    for tpl_name in ["enforce.sh.template", "secret.sh.template", "memory-log.sh.template", "memory-promote.sh.template", "TOOLS-GUIDE.md.template"]:
        tpl_path = agent_dir / "templates" / "tool-enforcement" / tpl_name
        if tpl_path.exists():
            dest_name = tpl_name.replace(".template", "")
            shutil.copy2(tpl_path, tools_dir / dest_name)
            os.chmod(tools_dir / dest_name, 0o755)
    
    # Create memory directories
    for d in ["daily", "weekly", "long-term"]:
        (agent_workspace / "memory" / d).mkdir(parents=True, exist_ok=True)
    
    # Create secrets directory
    secrets_dir = agent_workspace / ".secrets"
    secrets_dir.mkdir(exist_ok=True)
    os.chmod(secrets_dir, 0o700)
    
    # Create agent.json for crew manager
    agent_json = {
        "agent_id": agent_id,
        "name": display_name,
        "type": agent_type,
        "personality": f"{agent_type}-specialist",
        "workspace": str(agent_workspace),
        "enforcer_socket": str(Path("/run/agent-enforcer") / f"{agent_id}.sock"),
        "constitution_hash": "",  # Will be set after startup
        "crew_id": crew_name,
        "created_utc": now_iso(),
        "identity_layer": "v1",
        "habits": ["identity-enforcement", "tool-enforcement", "reflective-loop"],
        "builder_code": None
    }
    
    with open(agent_workspace / "agent.json", "w") as f:
        json.dump(agent_json, f, indent=2)
    
    # Create crew registry entry
    crew_registry = project_dir / "agents.json"
    if crew_registry.exists():
        with open(crew_registry) as f:
            registry = json.load(f)
    else:
        registry = {"crew_id": crew_name, "agents": []}
    
    # Remove existing entry if any
    registry["agents"] = [a for a in registry["agents"] if a["agent_id"] != agent_id]
    registry["agents"].append({
        "agent_id": agent_id,
        "name": display_name,
        "type": agent_type,
        "workspace": str(agent_workspace)
    })
    
    with open(crew_registry, "w") as f:
        json.dump(registry, f, indent=2)
    
    return agent_workspace

def start_agent(agent_workspace, agent_id):
    """Start the agent enforcer and runtime"""
    print(f"  Starting agent: {agent_id}")
    
    # Set environment
    env = os.environ.copy()
    env["AGENT_ID"] = agent_id
    env["AGENT_WORKSPACE"] = str(agent_workspace)
    env["WORKSPACE_ROOT"] = str(agent_workspace.parent.parent)  # project root
    
    # Start enforcer daemon
    enforcer_script = agent_workspace / "enforcer_daemon.py"
    if enforcer_script.exists():
        proc = subprocess.Popen(
            ["python3", str(enforcer_script)],
            cwd=agent_workspace,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"    Enforcer started (PID: {proc.pid})")
        return proc
    else:
        print(f"    ERROR: enforcer_daemon.py not found")
        return None

if __name__ == "__main__":
    import subprocess
    
    if len(sys.argv) < 3:
        print("Usage: spawn-crew-agents.py <project_dir> <crew_name>")
        sys.exit(1)
    
    project_dir = Path(sys.argv[1])
    crew_name = sys.argv[2]
    
    crew_dir = project_dir / f".crew-{crew_name}"
    blueprint_path = crew_dir / "blueprint.json"
    
    if not blueprint_path.exists():
        print(f"Blueprint not found: {blueprint_path}")
        sys.exit(1)
    
    with open(blueprint_path) as f:
        blueprint = json.load(f)
    
    identity_skill_path = Path(os.environ.get(
            "AGENT_IDENTITY_SKILL",
            str(Path.home() / ".hermes" / "skills" / "devops" / "agent-identity-architecture")
        ))
    
    print(f"Spawning {len(blueprint['agents'])} agents for {crew_name}...")
    
    agents = []
    for i, agent_def in enumerate(blueprint["agents"]):
        workspace = spawn_agent(project_dir, crew_name, agent_def, i, identity_skill_path)
        agents.append((agent_def["agent_id"], workspace))
    
    print("\nStarting agents...")
    processes = []
    for agent_id, workspace in agents:
        proc = start_agent(workspace, agent_id)
        if proc:
            processes.append(proc)
    
    print(f"\nStarted {len(processes)} agents")
    print("Agents are running in background. Check logs in agent workspaces.")
    
    # Keep running to maintain processes
    try:
        for proc in processes:
            proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        for proc in processes:
            proc.terminate()