#!/usr/bin/env python3
"""
Start all enforcer daemons for a crew in the background
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

def start_enforcer(agent_workspace, agent_id):
    """Start enforcer daemon for an agent"""
    enforcer_script = agent_workspace / "enforcer_daemon.py"
    if not enforcer_script.exists():
        print(f"  ✗ {agent_id}: enforcer_daemon.py not found")
        return False
    
    runtime_dir = Path(os.environ.get("XDG_RUNTIME_DIR", "/run/user/" + str(os.getuid())))
    env = os.environ.copy()
    env["AGENT_ID"] = agent_id
    env["AGENT_WORKSPACE"] = str(agent_workspace)
    env["WORKSPACE_ROOT"] = str(agent_workspace.parent.parent)
    env["ENFORCER_SOCKET_DIR"] = str(runtime_dir / "agent-enforcer")
    env["ENFORCER_LOG_DIR"] = str(Path.home() / "var" / "log" / "agent-enforcer")
    
    # Start with nohup to detach from parent
    log_file = agent_workspace / ".agent" / "logs" / "enforcer.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(log_file, "a") as f:
        proc = subprocess.Popen(
            ["python3", str(enforcer_script), agent_id],
            cwd=agent_workspace,
            env=env,
            stdout=f,
            stderr=subprocess.STDOUT,
            start_new_session=True  # Detach from parent
        )
    
    # Save PID
    pid_file = agent_workspace / ".agent" / "enforcer.pid"
    with open(pid_file, "w") as f:
        f.write(str(proc.pid))
    
    print(f"  ✓ {agent_id}: enforcer started (PID: {proc.pid})")
    return True

def main():
    if len(sys.argv) < 3:
        print("Usage: start-crew-enforcers.py <project_dir> <crew_name>")
        sys.exit(1)
    
    project_dir = Path(sys.argv[1])
    crew_name = sys.argv[2]
    
    agents_dir = project_dir / "agents"
    if not agents_dir.exists():
        print(f"Agents directory not found: {agents_dir}")
        sys.exit(1)
    
    print(f"Starting enforcers for {crew_name}...")
    
    for agent_dir in agents_dir.iterdir():
        if agent_dir.is_dir():
            agent_id = agent_dir.name
            start_enforcer(agent_dir, agent_id)
            time.sleep(0.5)  # Stagger startup
    
    print("All enforcers started!")
    
    # Show status
    print("\nStatus:")
    for agent_dir in agents_dir.iterdir():
        if agent_dir.is_dir():
            pid_file = agent_dir / ".agent" / "enforcer.pid"
            if pid_file.exists():
                with open(pid_file) as f:
                    pid = f.read().strip()
                # Check if process is alive
                try:
                    os.kill(int(pid), 0)
                    print(f"  ✓ {agent_dir.name}: PID {pid} (running)")
                except:
                    print(f"  ✗ {agent_dir.name}: PID {pid} (dead)")
            else:
                print(f"  ? {agent_dir.name}: no PID file")

if __name__ == "__main__":
    main()