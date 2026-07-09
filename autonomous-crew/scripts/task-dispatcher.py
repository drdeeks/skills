#!/usr/bin/env python3
"""
Crew Task Dispatcher - Assigns kanban tasks to available agents
Runs continuously, polling for active chain phases and available agents
"""

import json
import os
import sys
import time
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime, timezone

WORKSPACE_ROOT = Path(os.environ.get("WORKSPACE_ROOT", str(Path.home() / "qwen-cloud-2026")))
KANBAN_DB = Path.home() / ".hermes" / "kanban.db"

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

class TaskDispatcher:
    def __init__(self):
        self.projects = ["mnemosyne", "aires", "autopilot", "agora", "edgewalker"]
        self.agent_workspaces = {}
        self.last_poll = 0
        
    def get_chain_status(self, project):
        """Get chain status for a project - searches .crew-*/.blueprint-chain/ first"""
        try:
            # Search in order of priority (same as chain_enforce.py)
            search_dirs = []
            project_dir = WORKSPACE_ROOT / project
            
            # Check .crew-* directories first
            for item in project_dir.iterdir():
                if item.is_dir() and item.name.startswith(".crew-"):
                    search_dirs.append(item / ".blueprint-chain")
            
            # Then check .blueprint-chain and .chain
            search_dirs.append(project_dir / ".blueprint-chain")
            search_dirs.append(project_dir / ".chain")
            
            chain_file = None
            for search_dir in search_dirs:
                if search_dir.exists():
                    candidates = list(search_dir.glob("*-blueprint.json"))
                    if candidates:
                        chain_file = candidates[0]
                        break
            
            if not chain_file:
                return None
            
            with open(chain_file) as f:
                chain = json.load(f)
            
            steps = chain.get("steps", [])
            active_steps = [s for s in steps if s.get("state") == "active"]
            completed_steps = [s for s in steps if s.get("state") == "complete"]
            
            return {
                "steps": steps,
                "active": active_steps,
                "completed": completed_steps,
                "progress": f"{len(completed_steps)}/{len(steps)}"
            }
        except Exception as e:
            print(f"Error getting chain status for {project}: {e}")
            return None
    
    def get_kanban_tasks(self, project):
        """Get kanban tasks for a project"""
        try:
            conn = sqlite3.connect(str(KANBAN_DB))
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, status, body, assignee FROM tasks WHERE id LIKE ?",
                (f"{project}-phase-%",)
            )
            rows = cursor.fetchall()
            conn.close()
            
            tasks = []
            for row in rows:
                tasks.append({
                    "id": row[0],
                    "title": row[1],
                    "status": row[2],
                    "body": row[3],
                    "assignee": row[4]
                })
            return tasks
        except Exception as e:
            print(f"Error getting kanban tasks for {project}: {e}")
            return []
    
    def get_available_agents(self, project):
        """Get agents available for a project"""
        agents_dir = WORKSPACE_ROOT / project / "agents"
        if not agents_dir.exists():
            return []
        
        agents = []
        for agent_dir in agents_dir.iterdir():
            if agent_dir.is_dir():
                agent_id = agent_dir.name
                # Check if enforcer is running
                pid_file = agent_dir / ".agent" / "enforcer.pid"
                enforcer_running = False
                if pid_file.exists():
                    try:
                        pid = int(pid_file.read_text().strip())
                        os.kill(pid, 0)
                        enforcer_running = True
                    except:
                        pass
                
                agents.append({
                    "id": agent_id,
                    "workspace": agent_dir,
                    "enforcer_running": enforcer_running
                })
        return agents
    
    def assign_task_to_agent(self, project, task, agent):
        """Assign a task to an agent by creating a work file"""
        work_file = agent["workspace"] / ".agent" / "current_task.json"
        work_file.parent.mkdir(parents=True, exist_ok=True)
        
        task_data = {
            "task_id": task["id"],
            "title": task["title"],
            "body": task["body"],
            "assigned_at": now_iso(),
            "project": project,
            "agent_id": agent["id"]
        }
        
        with open(work_file, "w") as f:
            json.dump(task_data, f, indent=2)
        
        print(f"  Assigned {task['id']} to {agent['id']}")
        return True
    
    def update_kanban_status(self, task_id, status, assignee=None):
        """Update kanban task status"""
        try:
            conn = sqlite3.connect(str(KANBAN_DB))
            cursor = conn.cursor()
            if assignee:
                cursor.execute(
                    "UPDATE tasks SET status = ?, assignee = ? WHERE id = ?",
                    (status, assignee, task_id)
                )
            else:
                cursor.execute(
                    "UPDATE tasks SET status = ? WHERE id = ?",
                    (status, task_id)
                )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error updating kanban: {e}")
    
    def update_chain_step(self, project, step_index, state):
        """Update chain step state AND corresponding kanban task"""
        chain_dir = WORKSPACE_ROOT / project / ".blueprint-chain"
        chain_files = list(chain_dir.glob("*-blueprint.json"))
        if not chain_files:
            return
        
        chain_file = chain_files[0]
        with open(chain_file) as f:
            chain = json.load(f)
        
        steps = chain.get("steps", [])
        if step_index < len(steps):
            steps[step_index]["state"] = state
            if state == "active":
                steps[step_index]["activated_at"] = now_iso()
            elif state == "complete":
                steps[step_index]["completed_at"] = now_iso()
        
        with open(chain_file, "w") as f:
            json.dump(chain, f, indent=2)
        
        # Also update the corresponding kanban task status
        phase_task_id = f"{project}-phase-{step_index:02d}"
        kanban_status = "active" if state == "active" else "completed" if state == "complete" else "locked"
        try:
            conn = sqlite3.connect(str(KANBAN_DB))
            cursor = conn.cursor()
            cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (kanban_status, phase_task_id))
            conn.commit()
            conn.close()
            print(f"  {project}: Updated kanban task {phase_task_id} to {kanban_status}")
        except Exception as e:
            print(f"Error updating kanban: {e}")
    
    def _sync_kanban_with_chain(self, project, chain_status, tasks):
        """Sync kanban task statuses with chain step states"""
        steps = chain_status["steps"]
        for step in steps:
            step_index = step.get("index", 0)
            step_state = step.get("state", "locked")
            phase_task_id = f"{project}-phase-{step_index:02d}"
            
            # Find the kanban task
            task = next((t for t in tasks if t["id"] == phase_task_id), None)
            if not task:
                continue
            
            # Determine expected kanban status
            expected_status = "active" if step_state == "active" else "completed" if step_state == "complete" else "locked"
            
            if task["status"] != expected_status:
                print(f"  {project}: Syncing {phase_task_id} from {task['status']} to {expected_status}")
                try:
                    conn = sqlite3.connect(str(KANBAN_DB))
                    cursor = conn.cursor()
                    cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (expected_status, phase_task_id))
                    conn.commit()
                    conn.close()
                except Exception as e:
                    print(f"Error syncing kanban: {e}")
            
            # ALSO sync subtasks for this phase
            # When phase becomes active, unlock all its subtasks
            if step_state == "active":
                # Unlock subtasks for this phase
                subtask_prefix = f"{project}-phase-{step_index:02d}-task-"
                validation_id = f"{project}-phase-{step_index:02d}-validation"
                
                for t in tasks:
                    if t["id"].startswith(subtask_prefix) or t["id"] == validation_id:
                        if t["status"] == "locked":
                            print(f"  {project}: Unlocking subtask {t['id']}")
                            try:
                                conn = sqlite3.connect(str(KANBAN_DB))
                                cursor = conn.cursor()
                                cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", ("pending", t["id"]))
                                conn.commit()
                                conn.close()
                            except Exception as e:
                                print(f"Error unlocking subtask: {e}")
    
    def run_once(self):
        """Run one dispatch cycle"""
        print(f"\n[{now_iso()}] Dispatcher cycle")
        
        for project in self.projects:
            chain_status = self.get_chain_status(project)
            if not chain_status:
                continue
            
            tasks = self.get_kanban_tasks(project)
            agents = self.get_available_agents(project)
            
            if not agents:
                continue
            
            # SYNC: Ensure kanban task statuses match chain step states
            self._sync_kanban_with_chain(project, chain_status, tasks)
            
            # Find active phase
            active_steps = chain_status["active"]
            if not active_steps:
                # Check if there are pending tasks that should be activated
                pending_tasks = [t for t in tasks if t["status"] == "pending"]
                if pending_tasks:
                    # Activate first pending phase
                    first_pending = pending_tasks[0]
                    phase_num = int(first_pending["id"].split("-")[-1])
                    self.update_chain_step(project, phase_num, "active")
                    print(f"  {project}: Activated phase {phase_num}")
                    continue
            
            # Get tasks matching active phase
            for step in active_steps:
                step_index = step.get("index", 0)
                phase_task_id = f"{project}-phase-{step_index:02d}"
                
                # Find the kanban phase task
                phase_task = next((t for t in tasks if t["id"] == phase_task_id), None)
                if not phase_task:
                    continue
                
                # Assign phase task if unassigned
                if phase_task["status"] in ("pending", "active") and (phase_task.get("assignee") is None or phase_task.get("assignee") == ""):
                    available_agents = [a for a in agents if a["enforcer_running"]]
                    if not available_agents:
                        available_agents = agents
                    
                    if available_agents:
                        agent = available_agents[0]  # Simple round-robin
                        self.assign_task_to_agent(project, phase_task, agent)
                        self.update_kanban_status(phase_task["id"], "in_progress", agent["id"])
                        print(f"  {project}: Assigned phase {step_index} to {agent['id']}")
                
                # ALSO assign all subtasks for this active phase
                subtask_prefix = f"{project}-phase-{step_index:02d}-task-"
                subtasks = [t for t in tasks if t["id"].startswith(subtask_prefix) and t["status"] in ("pending", "active")]
                
                for i, subtask in enumerate(subtasks):
                    if subtask.get("assignee") is None or subtask.get("assignee") == "":
                        available_agents = [a for a in agents if a["enforcer_running"]]
                        if not available_agents:
                            available_agents = agents
                        
                        # Round-robin assignment across agents
                        agent = available_agents[i % len(available_agents)]
                        self.assign_task_to_agent(project, subtask, agent)
                        self.update_kanban_status(subtask["id"], "in_progress", agent["id"])
                        print(f"  {project}: Assigned subtask {subtask['id']} to {agent['id']}")
                
                # Assign validation task too
                validation_id = f"{project}-phase-{step_index:02d}-validation"
                validation_task = next((t for t in tasks if t["id"] == validation_id), None)
                if validation_task and (validation_task.get("assignee") is None or validation_task.get("assignee") == ""):
                    available_agents = [a for a in agents if a["enforcer_running"]]
                    if not available_agents:
                        available_agents = agents
                    if available_agents:
                        agent = available_agents[0]
                        self.assign_task_to_agent(project, validation_task, agent)
                        self.update_kanban_status(validation_task["id"], "in_progress", agent["id"])
                        print(f"  {project}: Assigned validation to {agent['id']}")
                    # Check if agent completed it (work file removed or marked done)
                    # For now, we'll check if chain validator passes
                    pass

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Task Dispatcher for Autonomous Crews", add_help=False)
    parser.add_argument("--help", "-h", action="help", help="Show this help message and exit")
    parser.add_argument("--dry-run", action="store_true", help="Run once and exit")
    args = parser.parse_args()
    
    dispatcher = TaskDispatcher()
    
    print(f"Starting Task Dispatcher for {len(dispatcher.projects)} projects")
    print(f"Workspace: {WORKSPACE_ROOT}")
    print(f"Kanban DB: {KANBAN_DB}")
    print("=" * 60)
    
    # Initial wire kanban to chain for all projects
    for project in dispatcher.projects:
        print(f"Wiring {project}...")
        result = subprocess.run([
            "python3", 
            str(Path(__file__).parent / "wire-kanban-to-chain.py"),
            "--project", str(WORKSPACE_ROOT / project),
            "--chain", str(WORKSPACE_ROOT / project / ".blueprint-chain" / f"{project}-crew-blueprint.json")
        ], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ {project} wired")
        else:
            print(f"  ✗ {project}: {result.stderr}")
    
    print("=" * 60)
    
    if args.dry_run:
        dispatcher.run_once()
        print("\n[DRY RUN] Exiting after single cycle")
        return
    
    # Main dispatch loop
    while True:
        try:
            dispatcher.run_once()
            time.sleep(30)  # Poll every 30 seconds
        except KeyboardInterrupt:
            print("\nDispatcher stopped")
            break
        except Exception as e:
            print(f"Dispatcher error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()