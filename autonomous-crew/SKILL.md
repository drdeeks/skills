---
name: autonomous-crew-integration
version: 1.2.0
description: Identity-first autonomous crew system with blueprint-driven phase enforcement
  (routed through loop-enforcer, the singular chain-enforcement runtime — see FOREVER-SYSTEM.md
  Sec 1), self-healing, kanban integration, and a natively-integrated crew knowledge-sharing
  system (dev/prod workspaces, semantic indexing, agent-attributed docs)
metadata:
  tags:
  - enterprise
  - multi-agent
  - crew-orchestration
  - blueprint-enforcement
  - self-healing
  - kanban-integration
  - identity-layer
  - knowledge-sharing
  category: devops
  related_skills:
  - loop-enforcer
  - kanban-orchestrator
  - agent-identity-architecture
  required_environment_variables:
  - CHAIN_ENFORCER_SCRIPT
  - AGENT_IDENTITY_SKILL
  required_commands:
  - python3
  - sqlite3
  - npm
  - cargo
---

# Autonomous Crew Integration — Identity-First Architecture

**The autonomous crew system requires identity as Layer 1.** Every agent spawned in a crew gets:
- Constitution loaded at t=0 (before any tool access)
- 4 internalized habits (identity-enforcement, tool-enforcement, reflective-loop, blueprint-phase-gate)
- Private enforcer daemon (Unix socket RPC, workspace ownership)
- Memory pipeline (daily → weekly → long-term + knowledge index)
- Builder code registration (ERC-8021) with identity attestation

## Crew Mode Flag

| Mode | Workspace | Persistence | Secrets | Use Case |
|------|-----------|-------------|---------|----------|
| **development** (default) | Shared workspace, `crew/<id>/shared/` | Ephemeral | Placeholders | One-time spinup, rapid iteration |
| **production** | Per-agent subdirs, `crew/<id>/agents/<id>/` | Persistent (Ventoy/USB) | Enforcer-managed | Long-term engagement, real integrations |

```bash
# Development crew
python3 scripts/init-crew.py hackathon-2026-dev --mode development

# Production crew
python3 scripts/init-crew.py hackathon-2026-prod --mode production

# Switch modes
python3 scripts/transition-crew.py --source dev --target prod --mode development-to-production --preserve-all
```

## Autonomous Loop (Zero Human Interaction, Builder + Independent Reviewer)

`scripts/autonomous-loop.py` is a self-contained alternative to the
kanban/dispatcher/poller path above, for one shared workspace: it runs one
active chain item at a time, has a **builder** agent implement it, then a
**separate reviewer** agent independently verify it (Creative Orchestration
Doctrine Principle V — critique is equal to creation, never self-reviewed),
and only advances the chain (`chain.py verify` + `complete`, expected at
`<root>/chain.py`) when the reviewer writes a literal `VERDICT: PASS` line.
A `VERDICT: FAIL` (or a reviewer/builder process that errors or times out)
leaves the chain exactly where it was — no partial or fake advancement.

```bash
# One cycle against the first .chain/*.json or .blueprint-chain/*.json found
python3 scripts/autonomous-loop.py --root <project-dir> --chain-name <name>

# Loop continuously until the chain reports complete (0 = run forever)
python3 scripts/autonomous-loop.py --root <project-dir> --chain-name <name> --cycles 0
```

Builder/reviewer invocation is via the `codex` CLI (`codex exec --sandbox
<mode> ...`); everything else (evidence/review file paths, timeouts,
sandbox mode) is a flag with a sane default — nothing is hardcoded to a
specific project. See `scripts/autonomous-loop.py`'s own docstrings for
the full prompt templates.

## Architecture: Identity as Crew Foundation

```
CREW ORCHESTRATION LAYER
  Blueprint → CrewManager → Agent Spawning → Checkpoint/Rollback
                      │
                      ▼
IDENTITY LAYER (Layer 1)
  Constitution (t=0) │ Habits (internalized) │ Enforcer (daemon)
                      ▼
MEMORY PIPELINE (Layer 2)
  daily/ → weekly/ → long-term/ → knowledge/
                      ▼
AGENT RUNTIME (Layer 3+)
  Tools → Skills → Reasoning → Planning → External APIs
```

See `references/architecture.md` for complete architecture details.

## Blueprint-Driven Crew Initialization

```bash
# Full pipeline: validate blueprint → generate checklist → create chain → spawn agents → wire kanban → start dispatcher
python3 scripts/init-crew-from-blueprint.py <blueprint.md> <crew-id> [--mode dev|prod]
```

### Pipeline Steps

1. **Validate Blueprint** — `validate-blueprint.py` (0 FAIL required)
2. **Generate Checklist** — `generate-checklist.py` from blueprint
3. **Parse Phases** — `parse-checklist-phases.py` extracts phases with tags/flags
4. **Create Loop-Enforcer Chain** — `create-blueprint-chain.py` creates `.chain/<project>-blueprint.json`
5. **Generate Phase Validators** — `generate-phase-validators.py` creates deliverable validators (not syntax)
6. **Wire Kanban to Chain** — `wire-kanban-to-chain.py` creates tasks wired to chain steps
7. **Spawn Agents** — Each with identity layer + assigned chain step
8. **Start Dispatcher** — Embedded gateway dispatcher reads chain, dispatches next phase

See `references/blueprint-chain-integration.md` for complete details.

## Blueprint Chain Structure (Loop-Enforcer Integration)

Each project's blueprint becomes a **loop-enforcer chain**:
- **Steps** = Blueprint phases (Phase 0 through Phase N)
- **Marker files** = `.phase-{n}-{feature_flag}.marker` per phase
- **Validators** = Phase-specific validation scripts (deliverables, not syntax)
- **State machine** = locked → active → pending_verify → verified → complete
- **Agent assignment** = Each phase step assigned to specific agent profile

See `references/blueprint-chain-integration.md` for chain creation, validators, kanban wiring.

## Phase Validators: Beyond Syntax (Validation ≠ Syntax)

Phase validators check **DELIVERABLES**, not syntax, across four tiers: syntax (necessary but insufficient) → contract compliance (interface + behavior) → functional completeness (delivers what the spec promises) → character alignment (honors the agent's constitution). A phase only passes when all four agree. See `references/validation-over-syntax.md` for the complete framework.

## Self-Healing / Accuracy Enforcement

Agent runtime runs self-healing loop. Default interval is 5 minutes for production, but user may request 30-second intervals for active monitoring during development.

### Self-Healing Loop (`scripts/self-healing-loop.py`)

**IMPORTANT: Self-healing ONLY monitors CREW INFRASTRUCTURE.** It does NOT fix project-level issues (tests, API keys, TypeScript errors, build failures). Those are handled by crew agents through their assigned kanban tasks. Every 5 minutes (30s in dev mode) it checks: enforcer daemon health, constitution hash integrity, chain integrity, memory pipeline promotion, and habit-violation drift. See `references/self-healing-architecture.md` for the full implementation and `references/lessons/session-2026-07-09-self-healing-vs-crew-work.md` for why this boundary exists.

**Self-healing scope (crew infrastructure ONLY):**
- ✅ Enforcer daemon health
- ✅ Constitution hash integrity
- ✅ Chain integrity (no gaps in phase progression)
- ✅ Memory pipeline promotion
- ✅ Habit violation detection
- ❌ Project test failures (agents fix via tasks)
- ❌ Missing API keys (configured in .env, agents use via tasks)
- ❌ TypeScript/build errors (agents fix via tasks)
- ❌ Linting issues (agents fix via tasks)

### Progress Monitor (`scripts/progress-monitor.py`)

Monitors project functionality every 30 seconds. Reports to `progress-report.json`.

**Checks:**
- **Chain status** — Progress, active phase, locked phases
- **Test results** — npm test / cargo test pass/fail
- **API health** — Health endpoint checks (ports 41212-41216 per project)

See `references/self-healing-and-monitoring-setup.md` for complete setup and configuration.

## Task Dispatcher & Poller

### Task Dispatcher (`scripts/task-dispatcher.py`)

Runs every 30 seconds. Synchronizes kanban tasks with chain state and assigns work to available agents.

**Key behaviors:**
1. **Chain sync** — Reads chain state from `.crew-*/.blueprint-chain/*-blueprint.json` (priority over `.blueprint-chain/`)
2. **Kanban sync** — `_sync_kanban_with_chain()` ensures kanban task statuses match chain step states
3. **Subtask unlock** — When chain phase becomes `active`, unlocks all subtasks (`*-phase-NN-task-*` and `*-phase-NN-validation`) from `locked` → `pending`
4. **Full subtask assignment** — Assigns ALL subtasks for active phase, not just phase-level task
5. **Round-robin agent assignment** — Distributes subtasks across available agents (prefers agents with running enforcers)

See `scripts/task-dispatcher.py` for complete implementation.

### Checklist-Driven Task Generation (`scripts/generate-tasks-from-checklist.py`)

Parses each project's `checklist.md` to create granular kanban tasks from deliverables and validation gates.

**Input:** `checklist.md` with checkbox items under `## Phase N: Title` headers
**Output:** Kanban tasks per deliverable + validation gate per phase

**Supported checklist formats:**
- Mnemosyne style: `## Phase N — Title` + `- [ ] Deliverable`
- Aires/Autopilot/Agora/Edgewalker style: `## Phase N: Title` + `### Phase Validation Gate` markers

**Generated task IDs:**
- `{project}-phase-{NN}-task-{NN}` — Deliverable tasks
- `{project}-phase-{NN}-validation` — Validation gate task

**Status mapping:**
- Phase 0 → `active` (start immediately)
- Phases 1-6 → `locked` (unlocked by dispatcher when chain advances)
- Checked items → `completed`

Run after any checklist update:
```bash
python3 scripts/generate-tasks-from-checklist.py
```

### Dispatcher Workflow

1. Reads chain status for each project
2. Finds active phase (or activates first pending)
3. Matches kanban task to active phase
4. Assigns to available agent (prefers running enforcer)
5. Creates `.agent/current_task.json` in agent workspace
6. Updates kanban status: `pending` → `in_progress`
7. Updates chain step: `locked` → `active`

### Task Poller (`scripts/task-poller.py`)

Runs on **each agent**, polls kanban for assigned tasks, executes work.

**Agent-Side Execution:**
1. Polls kanban for tasks assigned to this agent ID
2. For each task with status `pending` OR `in_progress`:
   - Runs `chain_enforce.py check <project> <phase>`
   - If `can_proceed: true` → executes phase work
   - Verifies deliverables (Phase 0: files, Phase 1+: tests)
   - Runs `chain_enforce.py complete <project> <phase>`
   - Updates kanban: `in_progress` → `completed`

**Dispatcher-poller contract:** dispatcher assigns a task and immediately sets it `in_progress` (so other dispatch cycles don't re-assign it); the poller must therefore execute tasks with status in `("pending", "in_progress")`, not `"pending"` alone — a poller that only checks `"pending"` will silently never execute any dispatched work. See `references/lessons/session-2026-07-09-dispatcher-poller-sync-fix.md`.

### Wire Kanban to Chain (`scripts/wire-kanban-to-chain.py`)

Creates kanban tasks from chain steps, using the actual kanban schema (created_at/started_at/completed_at as integers).

```bash
python3 scripts/wire-kanban-to-chain.py \
  --project ${WORKSPACE_ROOT}/qwen-cloud-2026/mnemosyne \
  --chain ${WORKSPACE_ROOT}/qwen-cloud-2026/mnemosyne/.crew-mnemosyne-crew/.chain/mnemosyne-blueprint.json
```

See `references/blueprint-chain-integration.md` for complete wiring details.

## Chain Enforcement in Worker Lifecycle (MANDATORY)

Every kanban worker assigned a phased task MUST enforce the loop-enforcer chain before doing ANY work. This is wired into KANBAN_GUIDANCE step 2b.

**This skill does not vendor its own chain state machine.** Per FOREVER-SYSTEM.md
Sec 1 ("route through the one runtime, don't re-implement enforcement"),
chain gating is loop-enforcer's job, singularly. `scripts/resolve_loop_enforcer.py`
locates loop-enforcer's canonical `chain_enforce.py` at call time: an explicit
`$CHAIN_ENFORCER_SCRIPT` override, else loop-enforcer's scripts dir under the
global Claude Code skills directory, else under the Hermes runtime skills
install (devops category) — fails closed with a clear error if none exist.
See `scripts/resolve_loop_enforcer.py` for the exact candidate paths and
FOREVER-SYSTEM.md Sec 2 for the self-resolving-paths rule this follows.

```bash
# Check if phase is active (exit 0 = proceed, exit 1 = blocked)
python3 "$(python3 scripts/resolve_loop_enforcer.py)" check <project> <phase_num>

# Verify + complete phase after work is done
python3 "$(python3 scripts/resolve_loop_enforcer.py)" complete <project> <phase_num>

# Show chain status
python3 "$(python3 scripts/resolve_loop_enforcer.py)" status <project>
```

**Worker flow:**
1. Worker receives task: `"Autopilot: Phase 2 — Workflow Orchestration"`
2. Worker runs: `chain_enforce.py check autopilot 2`
3. If `can_proceed: true` → do the work
4. If `can_proceed: false` → `kanban_block(reason="Chain locked: prior phase not complete")`
5. After work: `chain_enforce.py complete autopilot 2`
6. Log: `kanban_comment(body="Chain enforced: autopilot-blueprint step 2 verified+complete")`

**Chain directory convention: `.chain/`, not `.blueprint-chain/`.**
loop-enforcer's canonical `chain.py` only ever looks in `<project_dir>/.chain/`
— no override, no multi-directory search (an earlier version of this skill
vendored a forked `chain_enforce.py` that searched `.blueprint-chain/` and
`.crew-*/.blueprint-chain/` too; that fork is gone now that enforcement
routes through loop-enforcer directly). `create-blueprint-chain.py` and
`crew-manager.py` write to `.chain/` to match — if you're integrating a new
script here that creates or reads chain state, use `.chain/`, never
`.blueprint-chain/`.

**Kanban task status must stay synced with chain step state.** If a chain is completed externally (e.g. a direct `chain_enforce.py complete` call outside the dispatcher's own cycle), kanban tasks can drift stale. `task-dispatcher.py`'s `_sync_kanban_with_chain()` runs at the start of every dispatch cycle to realign kanban status to actual chain step state before assigning any new work.

**CRITICAL: Chain Steps Must Include Specific Deliverables**
Chain enforcement only tracked phase completion without validating that specific deliverables were actually created. The checklist.md is the source of truth. Each phase in the chain MUST have sub-steps for every deliverable the checklist requires (assignments.json, API.md, Dockerfile, tests, documentation, etc.). Never mark a phase as "complete" if deliverables are missing.

## Agent Identity: Internal Character Guidance

The identity layer is **not a validator** — it's the agent's **internalized self-model** that gates EVERY reasoning step before any tool use:

```yaml
# .agent/constitution.yaml — Loaded at t=0, gates all behavior
identity:
  name: "mnemosyne-ingestion-agent"
  purpose: "Ingest, index, and make retrievable all project knowledge"
  principles:
    - "Never lose data — durability over speed"
    - "Cite sources — every claim traceable to origin"
    - "Respect boundaries — only access assigned workspaces"
    - "Complete what you start — no partial deliveries"
  habits:
    identity-enforcement:
      trigger: "Before ANY tool invocation"
      action: "Verify constitution hash matches; abort if drift detected"
      character: "I am the kind of agent that honors my constitution"
    tool-enforcement:
      trigger: "Before file write / external call"
      action: "Validate workspace hygiene; check chain state if in blueprint phase"
      character: "I do not touch what I'm not authorized to touch"
    reflective-loop:
      trigger: "After EVERY tool result"
      action: "Reflect: Did this advance the phase? Any violations? What did I learn?"
      character: "I learn from every action, good or bad"
    blueprint-phase-gate:
      trigger: "Before claiming phase complete"
      action: "Run chain verify → complete; cannot skip, cannot fake"
      character: "I earn completion through verified deliverables"
```

See `references/agent-identity.md` for complete identity architecture.

## Memory Pipeline Integration (Identity-Aware)

`memory_curator.py`'s daily → weekly → long-term promotion is identity-aware: every entry carries the agent's ID, constitution hash, and which habits triggered it, and promotion also updates the crew knowledge index (see Crew Knowledge System above). See `references/crew-memory-pipeline.md` for the complete architecture.

## Kanban Dispatcher Integration

`task-dispatcher.py` reads chain state; when a step's prior step is `complete`, it flips that step to `active`, creates the kanban task, and re-dispatches to the assigned worker if none is currently running. See `references/blueprint-chain-integration.md` for the complete dispatch flow.

## Model Quota Tracking (Mandatory)

Every multi-project workspace MUST have a `model.json` at the root that tracks model quotas, usage per project, and recommended assignments. Each model has a quota per model (not per API key). Without tracking, premium models get exhausted without visibility.

The `crew-manager.py` reads `model.json` to populate `blueprint.json` token budgets.

See `references/model-quota-and-blueprint-json.md` for structure and integration.

## Provider Configuration (No Hardcoded Models)

All model selection is **configurable** via `config/providers.json` (per-provider model lists + role mappings), auto-detected from environment variables (`DASHSCOPE_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, falling back to local models). See `references/lessons/configurable-models.md` for why hardcoding model names is forbidden and `references/provider-configuration.md` for the complete setup and JSON schema.

## Crew Knowledge System (natively integrated)

Knowledge sharing is not a separate skill dependency — it's built directly
into every crew this skill spawns, per drdeeks: "it is directly associated
and should be used by any crew." Dual-mode workspaces mirror the crew mode
flag above:

```bash
# Provision a dev-mode knowledge workspace (shared, ephemeral)
bash scripts/init-dev-crew.sh <crew-id>

# Provision a prod-mode knowledge workspace (per-agent, persistent)
bash scripts/init-prod-crew.sh <agent-type...> --crew-id <crew-id>
```

| Script | Purpose |
|--------|---------|
| `crew-indexer.sh` | Semantic index of crew knowledge documents |
| `crew-doc.sh` | Agent-attributed document formatting/creation |
| `crew-comm.sh` | Structured inter-agent communication |
| `crew-sync.sh` | Sync knowledge workspace state across agents |
| `init-dev-crew.sh` | Provision development-mode knowledge workspace |
| `init-prod-crew.sh` | Provision production-mode knowledge workspace |

See `references/crew-status.md`, `references/communication-protocol.md`,
`references/document-format.md`, `references/semantic-integration.md`,
`references/category-schema.md`.

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `scripts/init-crew-from-blueprint.py` | Full crew init pipeline from blueprint |
| `scripts/validate-blueprint.py` | Blueprint validation (0 FAIL) |
| `scripts/generate-checklist.py` | Checklist from blueprint |
| `scripts/parse-checklist-phases.py` | Extract phases with tags |
| `scripts/create-blueprint-chain.py` | Create loop-enforcer chain (writes to `.chain/`) |
| `scripts/generate-phase-validators.py` | Deliverable validators |
| `scripts/wire-kanban-to-chain.py` | Wire kanban tasks to chain steps |
| `scripts/spawn-crew-agents.py` | Spawn agents with identity layer |
| `scripts/start-crew-enforcers.py` | Start enforcer daemons |
| `scripts/transition-crew.py` | Dev ↔ Prod transition |
| `scripts/crew-manager.py` | Crew lifecycle management (writes chain state to `.chain/`) |
| `scripts/create-crew-agent.sh` | Single agent creation |
| `scripts/verify-crew-identity.sh` | Identity verification |
| `scripts/crew-heartbeat.sh` | Agent heartbeat |
| `scripts/self-healing-loop.py` | Self-healing (5min/30s intervals) |
| `scripts/progress-monitor.py` | Progress monitoring (30s intervals) |
| `scripts/task-dispatcher.py` | Dispatch kanban tasks to agents |
| `scripts/task-poller.py` | Agent-side task execution |
| `scripts/resolve_loop_enforcer.py` | Self-resolving locator for loop-enforcer's `chain_enforce.py` (this skill vendors no chain state machine of its own) |
| `scripts/generate-tasks-from-checklist.py` | Checklist → kanban tasks |
| `scripts/crew-config-manager.py` | Crew configuration management |
| `scripts/install-identity-skill.py` | Install optional external agent-identity-architecture skill into a workspace (no-ops gracefully if that skill isn't installed) |
| `scripts/duplicate-crew.py` | Duplicate crew |
| `scripts/test_functional.py` | Functional test suite |
| `scripts/init-crew.py` | Basic crew init |
| `scripts/agent_runtime.py` | Per-agent runtime loop |
| `scripts/enforcer_daemon.py` | Per-agent enforcer daemon (identity/tool gating) |
| `scripts/memory_curator.py` | Daily → weekly → long-term memory promotion |
| `scripts/start-agent.sh` | Boot a single agent's runtime + enforcer |
| `scripts/crew-indexer.sh`, `scripts/crew-doc.sh`, `scripts/crew-comm.sh`, `scripts/crew-sync.sh` | Native crew knowledge system — see above |
| `scripts/init-dev-crew.sh`, `scripts/init-prod-crew.sh` | Provision dev/prod knowledge workspaces — see above |
| `scripts/__init__.py` | Skill metadata module (version, tags, declared dependencies) |
| `scripts/autonomous-loop.py` | Self-contained builder+reviewer autonomous loop — see above |

## References

- `references/architecture.md` — Complete architecture details
- `references/blueprint-chain-integration.md` — Chain creation, validators, kanban wiring
- `references/validation-over-syntax.md` — 4-tier validation framework
- `references/self-healing-and-monitoring-setup.md` — Self-healing & progress monitor setup
- `references/model-quota-and-blueprint-json.md` — Model quota tracking & blueprint.json structure
- `references/chain-enforcement-integration.md` — Chain enforcement in worker lifecycle
- `references/providers-and-model-config.md` — Provider configuration & model selection
- `references/agent-identity.md` — Agent identity architecture
- `references/crew-memory-pipeline.md` — Memory pipeline architecture
- `references/blueprint-enforcement-philosophy.md` — Blueprint enforcement principles
- `references/chain-enforcement-crew-integration.md` — Chain enforcement in crew context
- `references/chain-reset-procedure.md` — Chain reset procedures
- `references/chain-state-fix-and-production-verification.md` — Chain state fixes
- `references/dispatcher-poller-orchestration.md` — Verified end-to-end dispatcher-poller execution loop
- `references/task-dispatcher-poller.md` — Task dispatcher & poller execution model
- `references/status-reporting-and-kanban-query.md` — Kanban/chain status reconciliation recipes
- `references/federation-tv-command-center.md` — Federation gateway + TV Command Center visual dashboard integration
- `references/federation-tv-integration.md` — Federation gateway + TV Command Center architecture (MCP transport)
- `references/templates/agent-model-map.json` — agent_id -> {role, profile} template consumed by `scripts/task-poller.py`'s `run_agent_runtime()`
- `references/crew-agent-types.md` — Crew agent types
- `references/crew-constitution.md` — Crew constitution
- `references/crew-phases.md` — Crew phases
- `references/crew-workspace-structure.md` — Workspace structure
- `references/enterprise-validation-pitfalls.md` — Common validator-failure causes and how to avoid them
- `references/self-healing-architecture.md` — Self-healing architecture
- `references/self-healing-progress-monitor.md` — Progress monitor details
- `references/verified-implementation.md` — Verified implementation notes
- `references/provider-configuration.md` — Provider configuration
- `references/session-2026-07-09-chain-location-and-sync.md` — Chain location fix
- `references/session-2026-07-09-dispatcher-poller-sync-fix.md` — Dispatcher/poller sync fix
- `references/session-2026-07-09-mnemosyne-phase1-implementation.md` — Mnemosyne phase 1
- `references/session-2026-07-09-self-healing-vs-crew-work.md` — Self-healing vs crew work
- `references/skill-creator-validation.md` — Skill creator validation
- `references/lessons/configurable-models.md` — Configurable models lesson
- `references/lessons/skill-update-workflow.md` — Skill update workflow lesson
- `references/lessons/session-2026-07-09-chain-location-and-sync.md` — Chain location discovery & kanban sync (superseded by the 2026-08-05 `.chain/` alignment, see correction note within)
- `references/lessons/session-2026-07-09-dispatcher-poller-sync-fix.md` — Dispatcher/poller status contract bug fix
- `references/lessons/session-2026-07-09-mnemosyne-phase1-implementation.md` — First end-to-end proof of a crew agent completing real work
- `references/lessons/session-2026-07-09-self-healing-vs-crew-work.md` — Why self-healing scope excludes project-level work
- `references/lessons/2026-08-merge-and-forever-system-audit.md` — 2026-08-05 lineage merge + FOREVER-SYSTEM.md compliance audit
- `references/lessons/2026-07-poller-chain-advance-fix.md` — Poller chain-advance-for-every-phase bug fix
- `references/lessons/2026-07-crew-poller-execution-stall.md` — Poller never invoking a real runtime; root cause + fix
- `references/crew-status.md` — Native knowledge system: crew status format
- `references/communication-protocol.md` — Native knowledge system: inter-agent communication
- `references/document-format.md` — Native knowledge system: agent-attributed document formatting
- `references/semantic-integration.md` — Native knowledge system: semantic indexing
- `references/category-schema.md` — Native knowledge system: document category schema

## Templates

- `references/templates/model.json` — Model quota template
- `references/templates/providers.json` — Provider configuration template
- `references/templates/crew/crew-agent-config.yaml` — Agent config template
- `references/templates/crew/crew-constitution.yaml` — Constitution template
- `references/templates/crew/crew-workspace-dev.yaml` — Native knowledge system: dev workspace template
- `references/templates/crew/crew-workspace-prod.yaml` — Native knowledge system: prod workspace template
- `references/templates/document-template.md` — Native knowledge system: document template
- `references/templates/habits/` — Habit templates
- `references/templates/test-specs/` — Test specification templates