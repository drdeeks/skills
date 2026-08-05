---
title: Crew Poller Execution Stall — Root Cause and Fix
category: chain-enforcement
date: 2026-07-09
failure: >
  5 kanban-orchestrated crews ran for ~3.8h at 0% CPU with zero deliverable
  files. Kanban showed tasks active/in_progress (looked like real work),
  but nothing was ever produced — the crews were phantom.
root_cause: >
  Two compounding defects. (A) Pollers were launched with a crew-level
  agent_id (e.g. "mnemosyne-crew"), but kanban tasks carry a specific
  per-task assignee (e.g. "mnemosyne-learning-1") — a WHERE assignee = ?
  query against the crew-level id matched zero rows, so the poller looped
  forever finding no work. (B) Even with a matching query, execute_task
  only called verify_deliverables() (checks whether files already exist)
  and marked tasks complete — it never invoked anything that could actually
  write the code. spawn-crew-agents.py only starts an idle enforcer daemon,
  not a code-generating runtime, so nothing in the pipeline ever produced
  a deliverable in the first place.
resolution: >
  Query by project-id prefix instead of exact assignee match (robust to
  whichever id the poller process itself was launched with). Added an
  agent-model-map.json (agent_id -> {role, profile}, provider/path-agnostic)
  and a run_agent_runtime() step that invokes the platform's agent runtime
  (hemlock-agent -p <profile> -z "<task prompt>" --yolo) BEFORE re-checking
  deliverables, so the poller actually does the work instead of only
  auditing for work that already happened by some other means. A runtime
  failure (missing binary, missing model-map entry, nonzero exit, timeout)
  leaves the task in_progress for retry rather than faking completion.
prevention: >
  When a "the crew isn't doing anything" symptom shows 0% CPU and no child
  processes, check for a stalled query (wrong id shape) before assuming the
  execution logic itself is broken. Separately, always audit whether a
  "verify and complete" step has a real "do the work" step upstream of it —
  a poller/dispatcher that only ever checks for pre-existing deliverables
  can look completely healthy (green logs, no errors) while producing
  nothing, because there is no error path for "nobody ever tried."
verified: true
---

# Session 2026-07-09 — Crew Poller Execution Stall (Root Cause + Fix)

## Symptom
5 kanban-orchestrated crews ran for ~3.8h at 0% CPU with ZERO deliverable files.
Kanban showed tasks `active`/`in_progress` (looked like work), but nothing was produced.
The TV Command Center / MCP gateway showed 20 agents "registered" but no real activity.

## Root cause (two compounding defects)

### Defect A — fatal stall (wrong query)
Pollers launched as `task-poller.py <crew> <ws> <project>` → `agent_id = "<project>-crew"`,
but the poller queried `WHERE assignee = ?` with that crew name. Kanban tasks
carry SPECIFIC agent IDs as `assignee` (`mnemosyne-learning-1`), never the
crew name — the query matched zero rows, `execute_task` returned `False`,
poller slept forever.

### Defect B — missing execution step
Even with a matching query, the original `execute_task` only called
`verify_deliverables()` (checks if files ALREADY exist) and marked complete.
It never INVOKED the agent runtime to WRITE the code. `spawn-crew-agents.py`
only starts an enforcer daemon (idle constraint checker) — no component in
the pipeline actually generated code.

## The fix (agent->model map + auto-consume task)
1. `agent-model-map.json` at workspace root: `agent_id -> {role, profile}`,
   provider-agnostic (no model/provider/key/path).
2. Rewrote `task-poller.py`: query by project-id prefix; resolve
   assignee -> role -> profile via the map; invoke
   `hemlock-agent -p <profile> -z "<task prompt>" --yolo` (cwd=project_dir);
   on runtime failure leave the task active for retry (no fake completion);
   on success, `verify_deliverables()` -> `chain_enforce.py complete` -> mark
   completed.

## Verification recipe (minimal test first)
- Prove the execution primitive non-interactively:
  `hemlock-agent -p <profile> -z "Create proof.txt with: AGENT_RUNTIME_OK" --yolo`
- Controlled rollout: kill ONE old poller, launch the fixed one for one
  project, confirm a real `src/...` file appears with a fresh timestamp,
  THEN roll out to all.
- Watch for the fake-completion trap: a task that fails the runtime but
  gets marked `completed` anyway. The fix leaves it `in_progress`.
- Common runtime failure: profile does not exist — the map's `profile`
  MUST match a real runtime profile name (a different namespace than
  agent IDs).

## Outcome (at the time)
After fix: 13+ runtimes actively coding; real deliverable files generated
across all 5 projects. Crews no longer phantom — they build.

## Status as of the 2026-08-05 merge
The same execution-step gap (Defect B) was re-discovered independently in
the v2 lineage's `task-poller.py` during the 2026-08-05 crew-integration
merge (it had the poller-chain-advance fix from
`references/lessons/2026-07-poller-chain-advance-fix.md` but had regressed
back to verify-only, no execution). Re-applied the same fix pattern:
`load_model_map()` + `run_agent_runtime()`, wired in before the
verify/complete step, and fixed the "fake completion" trap in the
completion path (`continue` on unverified deliverables instead of
unconditionally marking the task `completed`).
