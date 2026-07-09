#!/usr/bin/env python3
"""
Task Execution Poller for Crew Agents
Runs on each agent, polls kanban for assigned tasks, executes work, reports completion
"""

import json
import os
import sys
import time
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime, timezone

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

KANBAN_DB = Path.home() / ".hermes" / "kanban.db"
WORKSPACE_ROOT = Path(os.environ.get("WORKSPACE_ROOT", str(Path.home() / "qwen-cloud-2026")))

class TaskPoller:
    def __init__(self, agent_id, agent_workspace, project_name):
        self.agent_id = agent_id
        self.agent_workspace = Path(agent_workspace)
        self.project_name = project_name
        self.project_dir = WORKSPACE_ROOT / project_name
        
    def get_assigned_tasks(self):
        """Get tasks assigned to this agent from kanban"""
        try:
            conn = sqlite3.connect(str(KANBAN_DB))
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, body, status, assignee 
                FROM tasks 
                WHERE assignee = ? AND status IN ('pending', 'in_progress')
                ORDER BY created_at
            """, (self.agent_id,))
            rows = cursor.fetchall()
            conn.close()
            
            tasks = []
            for row in rows:
                tasks.append({
                    "id": row[0],
                    "title": row[1],
                    "body": row[2],
                    "status": row[3],
                    "assignee": row[4]
                })
            return tasks
        except Exception as e:
            print(f"[{now_iso()}] Error getting tasks: {e}")
            return []
    
    def update_task_status(self, task_id, status):
        """Update task status in kanban"""
        try:
            conn = sqlite3.connect(str(KANBAN_DB))
            cursor = conn.cursor()
            now_ts = int(time.time())
            cursor.execute(
                "UPDATE tasks SET status = ?, started_at = CASE WHEN ? = 'in_progress' AND started_at IS NULL THEN ? ELSE started_at END, completed_at = CASE WHEN ? = 'completed' THEN ? ELSE completed_at END WHERE id = ?",
                (status, status, now_ts, status, now_ts, task_id)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[{now_iso()}] Error updating task: {e}")
            return False
    
    def execute_task(self, task):
        """Execute a task by running the appropriate project work"""
        task_id = task["id"]
        title = task["title"]
        
        print(f"[{now_iso()}] Executing: {task_id} - {title}")
        
        # Update status to in_progress
        self.update_task_status(task_id, "in_progress")
        
        try:
            # Determine project and phase from task_id
            # Format: {project}-phase-{NN}
            parts = task_id.split("-phase-")
            if len(parts) != 2:
                print(f"  Invalid task ID format: {task_id}")
                return False
            
            project = parts[0]
            phase_num = int(parts[1])
            
            # Run chain validator first
            print(f"  Checking chain status for {project} phase {phase_num}...")
            result = subprocess.run(
                ["python3", str(Path.home() / ".hermes" / "scripts" / "chain_enforce.py"), "check", project, str(phase_num)],
                cwd=self.project_dir,
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode != 0:
                print(f"  Chain check failed: {result.stderr}")
                return False
            
            chain_data = json.loads(result.stdout)
            if not chain_data.get("can_proceed", False):
                print(f"  Cannot proceed: {chain_data.get('reason', 'unknown')}")
                return False
            
            print(f"  Chain check passed, can proceed")
            
            # For Phase 0 (Foundation), ensure deliverables exist
            if phase_num == 0:
                print(f"  Running Phase 0 deliverables check...")
                # Check if all Phase 0 files exist
                required_files = [
                    "package.json", ".env.example", ".gitignore", 
                    "LICENSE", "README.md", "CHANGELOG.md",
                    "blueprint.md", "checklist.md"
                ]
                missing = []
                for f in required_files:
                    if not (self.project_dir / f).exists():
                        missing.append(f)
                
                if missing:
                    print(f"  Missing Phase 0 files: {missing}")
                    # The agents should create these
                    return False
                else:
                    print(f"  All Phase 0 deliverables present")
            
            # For Phase 1+, run tests to verify implementation
            if phase_num >= 1:
                print(f"  Running tests for {project}...")
                if (self.project_dir / "package.json").exists():
                    result = subprocess.run(
                        ["npm", "test", "--silent"],
                        cwd=self.project_dir,
                        capture_output=True, text=True, timeout=120
                    )
                    if result.returncode != 0:
                        print(f"  Tests failed: {result.stdout[-500:]}")
                        return False
                    print(f"  Tests passed")
                elif (self.project_dir / "Cargo.toml").exists():
                    result = subprocess.run(
                        ["cargo", "test", "--quiet"],
                        cwd=self.project_dir,
                        capture_output=True, text=True, timeout=120
                    )
                    if result.returncode != 0:
                        print(f"  Tests failed: {result.stdout[-500:]}")
                        return False
                    print(f"  Tests passed")
            
            # Complete the chain step
            print(f"  Completing chain step {phase_num}...")
            result = subprocess.run(
                ["python3", str(Path.home() / ".hermes" / "scripts" / "chain_enforce.py"), "complete", project, str(phase_num)],
                cwd=self.project_dir,
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode != 0:
                print(f"  Chain complete failed: {result.stderr}")
                return False
            
            print(f"  Phase {phase_num} completed successfully")
            
            # Update task status to completed
            self.update_task_status(task_id, "completed")
            return True
            
        except subprocess.TimeoutExpired:
            print(f"  Task timed out")
            return False
        except Exception as e:
            print(f"  Task error: {e}")
            return False
    
    def run_once(self):
        """Run one poll cycle"""
        tasks = self.get_assigned_tasks()
        if not tasks:
            return False  # No work
        
        for task in tasks:
            if task["status"] == "pending":
                self.execute_task(task)
            elif task["status"] == "in_progress":
                # Check if already done (another agent completed it)
                pass
        
        return True  # Had work

def main():
    if len(sys.argv) < 4:
        print("Usage: task-poller.py <agent_id> <agent_workspace> <project_name>")
        sys.exit(1)
    
    agent_id = sys.argv[1]
    agent_workspace = sys.argv[2]
    project_name = sys.argv[3]
    
    poller = TaskPoller(agent_id, agent_workspace, project_name)
    
    print(f"[{now_iso()}] Task poller started for {agent_id} on {project_name}")
    print(f"  Workspace: {agent_workspace}")
    
    while True:
        try:
            had_work = poller.run_once()
            if not had_work:
                time.sleep(30)  # No work, sleep longer
            else:
                time.sleep(5)  # Had work, quick check again
        except KeyboardInterrupt:
            print(f"\n[{now_iso()}] Poller stopped")
            break
        except Exception as e:
            print(f"[{now_iso()}] Poller error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()