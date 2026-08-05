---
title: Chain Location Discovery & Kanban-Chain Sync Patterns
category: chain-enforcement
date: 2026-07-09
failure: >
  task-dispatcher.py read chain state from a different location than
  chain_enforce.py checked, and kanban task status could drift out of sync
  with chain step state when the chain was advanced externally.
root_cause: >
  Multiple valid-looking chain directory conventions existed
  (.crew-*/.blueprint-chain/, project-root .blueprint-chain/, .chain/) with
  no single agreed priority order, and nothing re-synced kanban after an
  out-of-band chain_enforce.py call.
resolution: >
  At the time, standardized a shared 3-tier search-priority order across
  both task-dispatcher.py and chain_enforce.py, and added
  _sync_kanban_with_chain() to the dispatcher's cycle. See the 2026-08-05
  correction note at the bottom of this file for how this was later
  superseded.
prevention: >
  Any two components reading/writing the same state must agree on exactly
  one location, not a search order across several — a shared priority list
  is a workaround for not having a single source of truth, not a fix for it.
verified: true
---

# Chain Location Discovery & Kanban-Chain Sync Patterns

**Session:** 2026-07-09
**Context:** Multiple chain file locations discovered; dispatcher and chain_enforce.py must agree on priority.

## Chain File Search Priority (matching chain_enforce.py)

Both `task-dispatcher.py` and `chain_enforce.py` use the same priority order:

```python
# In get_chain_status() and update_chain_step()
search_dirs = []

# 1. .crew-* directories FIRST (highest priority)
for item in project_dir.iterdir():
    if item.is_dir() and item.name.startswith(".crew-"):
        search_dirs.append(item / ".blueprint-chain")

# 2. Project root .blueprint-chain
search_dirs.append(project_dir / ".blueprint-chain")

# 3. Project root .chain
search_dirs.append(project_dir / ".chain")

# Use first found
chain_file = None
for search_dir in search_dirs:
    if search_dir.exists():
        candidates = list(search_dir.glob("*-blueprint.json"))
        if candidates:
            chain_file = candidates[0]
            break
```

**Why this order matters:**
- `crew-manager.py` creates chains in `.crew-<name>/.blueprint-chain/`
- Legacy chains may be in project root `.blueprint-chain/`
- Both dispatcher and chain_enforce.py must use SAME priority to stay in sync

## Kanban-Chain Sync Mechanism (`_sync_kanban_with_chain`)

Prevents drift between kanban task statuses and chain step states.

```python
def _sync_kanban_with_chain(self, project, chain_status, tasks):
    for step in chain_status["steps"]:
        step_index = step.get("index", 0)
        step_state = step.get("state", "locked")
        phase_task_id = f"{project}-phase-{step_index:02d}"
        
        # 1. Sync phase task status
        expected_status = "active" if step_state == "active" else "completed" if step_state == "complete" else "locked"
        task = next((t for t in tasks if t["id"] == phase_task_id), None)
        if task and task["status"] != expected_status:
            update_kanban(phase_task_id, expected_status)
        
        # 2. Unlock subtasks when phase becomes active
        if step_state == "active":
            subtask_prefix = f"{project}-phase-{step_index:02d}-task-"
            validation_id = f"{project}-phase-{step_index:02d}-validation"
            
            for t in tasks:
                if t["id"].startswith(subtask_prefix) or t["id"] == validation_id:
                    if t["status"] == "locked":
                        update_kanban(t["id"], "pending")
```

**Without this sync:** External tools (crew-manager, manual chain_enforce.py calls) advance chain but kanban stays stale → dispatcher assigns nothing.

## Subtask Assignment Pattern (Full Phase Parallelism)

When phase is active, dispatcher assigns ALL subtasks, not just phase task:

```python
# Find all subtasks for active phase
subtask_prefix = f"{project}-phase-{step_index:02d}-task-"
subtasks = [t for t in tasks if t["id"].startswith(subtask_prefix) and t["status"] in ("pending", "active")]

# Round-robin across available agents
for i, subtask in enumerate(subtasks):
    agent = available_agents[i % len(available_agents)]
    assign_task(subtask, agent)

# Also assign validation task
validation_id = f"{project}-phase-{step_index:02d}-validation"
# ... assign validation
```

This ensures full parallel work on all deliverables in a phase.

## Session Learnings

1. **Chain location mismatch** caused dispatcher to read old `.blueprint-chain/` while crew-manager wrote to `.crew-*/.blueprint-chain/` → fixed by shared priority logic in both files

2. **Kanban drift** happened when chain completed externally → fixed by `_sync_kanban_with_chain()` running every dispatcher cycle (30s)

3. **Subtask assignment was missing** → dispatcher only assigned phase-level task → fixed to assign all subtasks + validation

4. **Checklist formats vary** across projects:
   - Mnemosyne: `## Phase N — Title` + `- [ ] Deliverable`
   - Aires/Autopilot/Agora/Edgewalker: `## Phase N: Title` + `### Phase Validation Gate` markers
   → `generate-tasks-from-checklist.py` handles both formats

5. **Validation gates** are separate kanban tasks (`*-phase-NN-validation`) assigned to one agent per phase

## Correction (2026-08-05)

The multi-directory search-priority approach documented above was itself the
symptom of not having a singular source of truth (FOREVER-SYSTEM.md Sec 1).
As of the 2026-08-05 merge, this skill vendors no chain state machine at
all — `scripts/resolve_loop_enforcer.py` self-resolves to loop-enforcer's
canonical `chain_enforce.py`, which only ever reads `.chain/`. This skill's
own chain-writing scripts (`create-blueprint-chain.py`, `crew-manager.py`)
were changed to write to `.chain/` instead of `.blueprint-chain/`, so there
is now exactly one location, not a priority list across several. See
`references/lessons/2026-08-merge-and-forever-system-audit.md`.