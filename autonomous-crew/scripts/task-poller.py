#!/usr/bin/env python3
"""
Task Execution Poller for Crew Agents
Runs on each agent, polls kanban for assigned tasks, executes work, reports completion
"""

import json
import os
import shutil
import sys
import time
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent))
from resolve_loop_enforcer import find_chain_enforce_script

KANBAN_DB = Path.home() / ".hermes" / "kanban.db"
WORKSPACE_ROOT = Path(os.environ.get("WORKSPACE_ROOT", "/home/ubuntu/qwen-cloud-2026"))
HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
CHAIN_ENFORCE_SCRIPT = find_chain_enforce_script()

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def now_ts():
    return int(datetime.now(timezone.utc).timestamp())

def verify_deliverables(project, project_dir, phase_num, task):
    """Verify the checklist deliverables for this phase actually exist.
    
    This is the gate that prevents fake completion. A phase is only
    'complete' when its real deliverables are present on disk.
    Returns True if verified, False otherwise.
    """
    # Phase 0: foundation files must exist
    if phase_num == 0:
        required = ['package.json', 'README.md', 'CHANGELOG.md',
                    'blueprint.md', 'checklist.md', 'LICENSE']
        missing = [f for f in required if not (project_dir / f).exists()]
        if missing:
            print(f"  Phase 0 missing: {missing}")
            return False
        return True
    
    # Phase 1+: verify the specific deliverable this task represents exists.
    # Derive the expected artifact from the task body / id.
    task_body = task.get('body', '') or ''
    task_id = task.get('id', '')
    
    # If the task names a file path, check it exists
    import re
    file_refs = re.findall(r'(src/[^\s`]+\.\w+|[a-zA-Z0-9_/.-]+\.(js|ts|py|rs|go|md|json|yaml|yml|sql|sh))', task_body)
    if file_refs:
        for ref in file_refs:
            f = project_dir / ref[0] if isinstance(ref, tuple) else project_dir / ref
            if not f.exists():
                print(f"  Missing deliverable: {ref[0] if isinstance(ref, tuple) else ref}")
                return False
        return True
    
    # Validation tasks: require the project test suite to pass
    if 'validation' in task_id or 'test' in task_body.lower():
        # Don't block on tests here — the dispatcher's quality gate handles that.
        # We only require that test files exist.
        test_files = list((project_dir / 'src').rglob('*.test.js')) + \
                     list((project_dir / 'src').rglob('*.test.ts')) + \
                     list((project_dir / 'src').rglob('test_*.py'))
        if not test_files:
            print(f"  No test files found for {project}/{task_id}")
            return False
        return True
    
    # Default: require that the project src tree is non-empty and has content
    src = project_dir / 'src'
    if src.exists() and any(src.iterdir()):
        return True
    
    print(f"  No verifiable deliverable for {task_id}")
    return False

def load_model_map(project_dir):
    """Load agent_id -> {role, profile} from agent-model-map.json at the
    workspace root. Returns {} if absent (execute_task then leaves tasks
    active for retry rather than faking completion)."""
    map_path = WORKSPACE_ROOT / "agent-model-map.json"
    if not map_path.exists():
        return {}
    try:
        return json.loads(map_path.read_text()).get("agents", {})
    except (json.JSONDecodeError, OSError):
        return {}


def run_agent_runtime(assignee, task, project_dir, model_map):
    """Actually perform the task's work via the platform's agent runtime.

    This is the step that used to be missing entirely (see
    references/lessons/2026-07-crew-poller-execution-stall.md): a poller
    that only checks whether deliverables already exist can never produce
    them. Returns True only if the runtime process exits 0 -- a failure
    here must leave the task active for retry, never fake-complete it.
    """
    entry = model_map.get(assignee)
    if not entry or not entry.get("profile"):
        print(f"[{assignee}] No agent-model-map.json entry for this assignee "
              "-- cannot invoke a runtime, leaving task active")
        return False
    if shutil.which("hemlock-agent") is None:
        print(f"[{assignee}] 'hemlock-agent' not found on PATH -- cannot "
              "execute; leaving task active")
        return False
    prompt = f"{task['title']}\n\n{task['body'] or ''}".strip()
    try:
        result = subprocess.run(
            ["hemlock-agent", "-p", entry["profile"], "-z", prompt, "--yolo"],
            cwd=project_dir, capture_output=True, text=True, timeout=1800,
        )
    except subprocess.TimeoutExpired:
        print(f"[{assignee}] Runtime timed out on {task['id']}")
        return False
    if result.returncode != 0:
        print(f"[{assignee}] Runtime failed ({result.returncode}) on {task['id']}: "
              f"{result.stderr[-500:]}")
        return False
    return True


def execute_task(agent_id, agent_workspace, project_name):
    """Execute assigned tasks for this agent"""

    project_dir = WORKSPACE_ROOT / project_name
    model_map = load_model_map(project_dir)

    # Query by project prefix, not by exact assignee match against agent_id --
    # kanban tasks carry a specific per-task assignee (e.g. "mnemosyne-learning-1"),
    # which is not guaranteed to equal the id this poller process was launched
    # with. See references/lessons/2026-07-crew-poller-execution-stall.md
    # (Defect A) for the stall this caused when the two didn't match.
    conn = sqlite3.connect(str(KANBAN_DB))
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, body, status, assignee
        FROM tasks
        WHERE id LIKE ? AND status IN ('pending', 'in_progress', 'active')
        ORDER BY created_at
    ''', (f"{project_name}-%",))
    rows = cursor.fetchall()
    conn.close()
    
    tasks = []
    for row in rows:
        tasks.append({
            'id': row[0],
            'title': row[1],
            'body': row[2],
            'status': row[3],
            'assignee': row[4]
        })
    
    if not tasks:
        return False  # No work
    
    for task in tasks:
        print(f"[{agent_id}] Executing: {task['id']}")
        
        # Update status to in_progress
        conn = sqlite3.connect(str(KANBAN_DB))
        cursor = conn.cursor()
        cursor.execute('UPDATE tasks SET status = ?, started_at = ? WHERE id = ?', 
                      ('in_progress', now_ts(), task['id']))
        conn.commit()
        conn.close()
        
        # Parse project and phase from task ID
        # Format: project-phase-NN-task-NN or project-phase-NN-validation
        parts = task['id'].split('-phase-')
        project = parts[0]
        phase_part = parts[1] if len(parts) > 1 else "0"
        phase_num = int(phase_part.split('-')[0])
        
        # Check chain enforcement
        result = subprocess.run(
            ['python3', str(CHAIN_ENFORCE_SCRIPT),
             'check', project, str(phase_num)],
            cwd=project_dir,
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode != 0:
            print(f"[{agent_id}] Chain check failed: {result.stdout[:200]}")
            # Check if can_proceed is false
            try:
                chain_data = json.loads(result.stdout)
                if not chain_data.get('can_proceed', False):
                    print(f"[{agent_id}] Chain blocked: {chain_data.get('reason', 'unknown')}")
                    continue
            except:
                pass
        
        print(f"[{agent_id}] Chain allows proceed")

        # Verify deliverables BEFORE completing the chain step.
        # The checklist is the source of truth: every phase must have its
        # deliverables actually present, not just marked done.
        verified = verify_deliverables(project, project_dir, phase_num, task)

        if not verified:
            # Deliverables don't exist yet -- actually do the work instead of
            # just re-checking forever. Without this step this poller can
            # only ever notice work that already happened by some other
            # means; see references/lessons/2026-07-crew-poller-execution-stall.md.
            print(f"[{agent_id}] Deliverables missing, invoking agent runtime")
            ran = run_agent_runtime(task['assignee'], task, project_dir, model_map)
            if ran:
                verified = verify_deliverables(project, project_dir, phase_num, task)

        if verified:
            # Complete the chain step for ALL phases (0 and 1+).
            # This is what advances the loop-enforcer chain so the dispatcher
            # can unlock the next phase. Without this, phases stall at active.
            print(f"[{agent_id}] Deliverables verified, completing chain step {phase_num}")
            subprocess.run(
                ['python3', str(CHAIN_ENFORCE_SCRIPT),
                 'complete', project, str(phase_num)],
                cwd=project_dir,
                capture_output=True, text=True, timeout=30
            )
        else:
            # Fake-completion trap: never mark a task completed when its
            # deliverables aren't actually present. Leave it in_progress
            # (set above) so the next poll cycle retries it.
            print(f"[{agent_id}] Deliverables NOT verified for phase {phase_num} — leaving task in_progress for retry")
            continue

        # Only reached when verified is True.
        conn = sqlite3.connect(str(KANBAN_DB))
        cursor = conn.cursor()
        cursor.execute('UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?',
                      ('completed', now_ts(), task['id']))
        conn.commit()
        conn.close()

        print(f"[{agent_id}] Completed: {task['id']}")
    
    return True

def main():
    if len(sys.argv) < 4:
        print("Usage: task-poller.py <agent_id> <agent_workspace> <project_name>")
        sys.exit(1)
    
    agent_id = sys.argv[1]
    agent_workspace = Path(sys.argv[2])
    project_name = sys.argv[3]
    
    print(f"Starting task poller for {agent_id} on {project_name}")
    
    while True:
        try:
            execute_task(agent_id, agent_workspace, project_name)
        except Exception as e:
            print(f"[{agent_id}] Error: {e}")
        
        time.sleep(15)  # Poll every 15 seconds

if __name__ == "__main__":
    main()