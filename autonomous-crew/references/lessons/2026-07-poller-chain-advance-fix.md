---
title: Poller Chain-Advance Bug Fix (v1.1.15)
category: chain-enforcement
date: 2026-07-09
failure: >
  task-poller.py only called chain_enforce.py complete for Phase 0. For
  Phases 1-6 it marked kanban tasks completed but never advanced the chain
  step, so the dispatcher never unlocked subsequent phases — all 5 projects
  stalled permanently at Phase 1.
root_cause: >
  Chain advancement was gated on the phase number itself (an if phase_num
  == 0 special case) instead of on whether that phase's deliverables were
  actually verified — a hidden assumption that only Phase 0 needed a
  verify-then-complete step, everything else silently fell through.
resolution: >
  Added verify_deliverables(project, project_dir, phase_num, task), applied
  uniformly to every phase (Phase 0: required files from the checklist;
  Phase 1+: test files or a non-empty src tree), and made chain_enforce.py
  complete run unconditionally after verification for every phase, not just
  Phase 0.
prevention: >
  Never gate chain advancement on phase number/index. Deliverable
  verification is the gate — if the artifacts exist, the phase is complete
  regardless of index, and the poller must call complete uniformly for
  every phase.
verified: true
---

# Poller Chain-Advance Bug Fix (v1.1.15)

## The Bug
`task-poller.py` only called `chain_enforce.py complete` for **Phase 0**. For Phases 1–6, it marked kanban tasks `completed` but **never advanced the chain step**, so the dispatcher never unlocked subsequent phases. All 5 projects stalled at Phase 1.

## Root Cause
```python
# BEFORE (broken)
if phase_num == 0:
    verify deliverables -> complete chain step
else:
    mark task completed  # chain step never advanced!
```

## The Fix
```python
# AFTER (v1.1.15)
verify_deliverables()  # for ALL phases
complete_chain_step()  # for ALL phases
```

Added `verify_deliverables(project, project_dir, phase_num, task)` that:
- Phase 0: checks for required files from checklist
- Phase 1+: requires test files OR non-empty src tree
- Calls `chain_enforce.py complete <project> <phase>` on success

## Verification (at the time)
After fix, all 5 projects advanced past their prior stall point (mnemosyne
reached Phase 2, the other four reached Phase 3).

## Status as of the 2026-08-05 merge
This fix is present in the current `scripts/task-poller.py` — see
`verify_deliverables()` and the "Complete the chain step for ALL phases (0
and 1+)" comment. A separate, more fundamental defect (the poller never
actually invoking any code-generating runtime, only verifying pre-existing
deliverables) was found and fixed in the same merge — see
`references/lessons/2026-07-crew-poller-execution-stall.md`.
