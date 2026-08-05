---
title: Task Dispatcher/Poller Sync Bug Fix
category: chain-enforcement
date: 2026-07-09
failure: >
  All 36 Phase 1 tasks across 5 projects showed in_progress in kanban but
  no agent was executing any work — tasks appeared permanently stuck.
root_cause: >
  task-dispatcher.py set task status to in_progress immediately on
  assignment, but task-poller.py's run_once() only executed tasks with
  status pending, so dispatcher-assigned tasks were invisible to pollers.
resolution: >
  Changed task-poller.py to execute tasks with status in ("pending",
  "in_progress") instead of only "pending".
prevention: >
  Any status written by a producer (dispatcher) must be in the exact set a
  consumer (poller) checks for — verify this explicitly when either side's
  status-writing or status-checking logic changes, don't assume they still
  agree.
verified: true
---

# Session 2026-07-09: Task Dispatcher/Poller Sync Bug Fix

## Critical Bug Identified
**Symptom:** All 36 Phase 1 tasks across 5 projects showed `in_progress` in kanban but agents were not executing any work. Tasks appeared "stuck."

**Root Cause:** 
- `task-dispatcher.py` assigns tasks and **immediately sets status to `in_progress`** (lines 298, 314)
- `task-poller.py` `run_once()` **only executes tasks with status `pending`** (line 191)
- Tasks assigned by dispatcher were **invisible to pollers** — they were skipped entirely

## Fix Applied
**File:** `scripts/task-poller.py` line 191

```python
# BEFORE (broken):
if task["status"] == "pending":
    self.execute_task(task)

# AFTER (fixed):
if task["status"] in ("pending", "in_progress"):
    self.execute_task(task)
```

## Why This Happened
The dispatcher's design intent: mark `in_progress` immediately so other dispatch cycles don't re-assign. The poller's design intent: only pick up `pending` to avoid duplicate execution. These two intents conflicted because there was no "claimed but not started" state.

## Verification
After fix and poller restart:
- Tasks with `in_progress` status are now picked up and executed
- Chain enforcement (`chain_enforce.py check`) runs before work
- Phase 1 deliverables (embedding-engine.js, memory-store.js, tests) created and validated
- npm test passes → chain complete → kanban updated to `completed`

## Related Pitfall: Chain Directory Mismatch (superseded 2026-08-05)
`chain_enforce.py` originally only looked in `.chain/` but `create-blueprint-chain.py` creates `.blueprint-chain/`. At the time, patched a locally-vendored `chain_enforce.py` to search both (plus `.crew-*/.blueprint-chain/` for crew-manager projects). That local fork is gone as of the 2026-08-05 merge — chain enforcement now routes through loop-enforcer's canonical `chain_enforce.py` (`.chain/` only), and `create-blueprint-chain.py`/`crew-manager.py` were changed to write `.chain/` to match, rather than re-forking the lookup again. See `references/lessons/2026-08-merge-and-forever-system-audit.md`.

## Prevention for Future
1. **State machine alignment:** Any status written by dispatcher must be readable by poller
2. **Add explicit "assigned" state** between `pending` and `in_progress` for clarity
3. **Integration test:** Dispatch → poller pick → execute → complete cycle in CI
4. **Document status flow** in skill SKILL.md (added above)

## Status Flow (Current)
```
locked → (dispatcher activates phase) → pending → (dispatcher assigns) → in_progress 
    → (poller executes, chain verify passes) → completed
```

## Files Modified
- `scripts/task-poller.py` — Line 191: execute both pending and in_progress
- `scripts/task-dispatcher.py` — Added `--help`/`-h` and `--dry-run` args (enterprise compliance)
- `scripts/generate-tasks-from-checklist.py` — Added `--help`/`-h` and `--dry-run` args
- `scripts/progress-monitor.py` — Added `--help`/`-h` support