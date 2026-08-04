---
name: enterprise-blueprint
description: Parse, validate, and generate execution checklists from a blueprint —
  scaled to any scope, from a single trivial task through a full multi-phase
  enterprise project. Tier-aware validation (MICRO/TASK/PROJECT), phase-gated
  workflow planning, and CI/CD integration. Use when planning any assigned task
  end-to-end, creating project blueprints, validating blueprint structure,
  generating execution checklists, or planning multi-phase workflows. Triggers
  on 'blueprint', 'enterprise blueprint', 'project blueprint', 'blueprint validation',
  'checklist generation', 'phase planning', 'task plan'.
version: 1.0.14
previous_version: 1.0.13
license: MIT
metadata:
  category: project-planning
  complexity: enterprise
  tags:
  - enterprise
  - blueprint
  - project planning
  - validation
  - checklist generation
  - workflow planning
  - phase gating
  - CI/CD integration
  - execution planning
---

# Enterprise Blueprint

Standalone blueprint workflow engine. Parses blueprint structure, validates
against a tier-scaled rule set (62 checks at PROJECT tier, fewer/looser at
TASK and MICRO — see `references/blueprint-standard.md`), generates
execution checklists, and plans multi-phase workflows. Zero external
dependencies — Python 3.8+ stdlib only.

A blueprint is written **once**, for whatever scope the assigned task
actually has:

| Scope | For | `--scope` flag |
|---|---|---|
| `micro` | A trivial single- or few-step task | `--scope micro` |
| `task` | A multi-step assignment or single feature | `--scope task` |
| `project` | A full, complete, multi-phase project (default) | `--scope project` (or omit) |

The seven-part structure (Part I–VII) and the blueprint → checklist →
chain-enforcement pipeline are the same at every tier; scope only changes
how much of Parts II–IV must be substantively populated versus legitimately
marked `N/A — Rationale: ...` (never silently skipped — see
`references/blueprint-standard.md` §5).

## When to Use

- Planning any assigned task end-to-end — from a one-off task through a full project
- Creating or reviewing blueprints at any scope tier
- Validating blueprint structure against its declared tier
- Generating phase-by-phase execution checklists
- Planning resource allocation and dependency chains
- CI/CD integration for automated validation gates

## Core Capabilities

### Blueprint Structure Parsing
- **7 Required Parts**: Part I-VII at every scope tier
- **Phase Extraction**: Detects and tracks development phases (1 at MICRO, 3+ at PROJECT)
- **Task Breakdown**: Granular checklist items with validation gates
- **Deliverable Types**: `file`/`glob`/`approval`/`external-check`/`review` — `external-check` fails closed with no validator wired, `review` fails closed if the reviewer is the same agent as the phase's assignee — neither silently auto-passes (see `references/blueprint-standard.md` §6)
- **Rollback Management**: Phase and section rollback tag tracking

### Tier-Aware Validation
- **62 checks at PROJECT tier** (48 structural/content + 2 per phase for the Review Gate, §9), scaled down at TASK/MICRO — a data-driven rule table (`validate_blueprint.py`'s `RULES`), not a fixed one-size-fits-all bar
- **N/A + Rationale enforcement**: Parts II-IV may only be skipped with a stated reason, never silently
- **Immutability check**: a blueprint's content hash is stamped at generation time; a later undocumented edit (no new CL-#### entry) surfaces as a WARN instead of going unnoticed
- **Part Compliance**: All 7 parts always required; depth scales by declared tier

### Agent Delegation & Review Gate (Creative Orchestration Doctrine)
- **Real assignment enforcement**: `assign_agents.py --model-map <agent-or-crew-map.yaml>` bulk-assigns agents to phases from a real model-map file (previously write-only — nothing consumed it); a phase's validation gate now **fails if no real agent is assigned** to it, not just if deliverables are missing (`check_agent_assignment`)
- **Review Gate (Principle V — "every creative layer has a corresponding reviewer")**: every phase requires a `**Reviewer Agent:**` field and a `Type: review` critique artifact (`Reviewed-By:`/`Date:`/`Critique:`). The phase gate **fails closed if the reviewer is the same agent as the assignee** — proven live: no-review, self-review, and independent-review all produce the expected fail/fail/pass sequence. See `references/agent-roles.md` §9.
- **Zero external dependencies, for real**: `scripts/simple_yaml.py` is a stdlib-only YAML subset (dump/load) — replaces a prior undeclared `import yaml` (PyYAML) that violated this skill's own dependency contract and silently blocked any model-map data from ever being read back in.

### Checklist Generation
- **Phase-by-Phase Breakdown**: Detailed task breakdown per development phase
- **Validation Gates**: Phase completion verification points
- **Progress Tracking**: Real-time completion metrics and dashboard
- **Dependency Mapping**: Sequential phase and task dependencies

### Workflow Planning
- **Timeline Generation**: Phase-based execution schedules
- **Resource Allocation**: Hour estimates and validation requirements
- **Critical Path**: Dependency analysis for bottleneck identification
- **Status Reporting**: Completion tracking and progress dashboards

## Usage

The primary tool is `generate_checklist.py` — a unified lifecycle tool and the single manager for blueprint lifecycle, enforcement, and looping. `enforce_blueprint.py` is a thin compat wrapper that delegates to it for legacy CLI callers. The old standalone `enterprise_blueprint_checker.py` (a competing, independent checklist/validation implementation) has been removed — use `generate_checklist.py` directly.

### Generate checklist from blueprint (default subcommand)
```bash
python3 scripts/generate_checklist.py ./project/blueprint.md
# Output: ./project/checklist.md + ./project/checklist-data.json
```

### Init enforcement chain
```bash
# Loop-locked only (default, no validators)
python3 scripts/generate_checklist.py ./project --init

# With blueprint-driven validators
python3 scripts/generate_checklist.py ./project --init --with-validators
```

### Chain operations
```bash
python3 scripts/generate_checklist.py ./project --status       # chain state
python3 scripts/generate_checklist.py ./project --phase 0 --step 0 --verify
python3 scripts/generate_checklist.py ./project --phase 0 --step 0 --complete
python3 scripts/generate_checklist.py ./project --phase 0 --step 0 --check
python3 scripts/generate_checklist.py ./project --menu          # interactive
python3 scripts/generate_checklist.py ./project --generate-validators
```

### Initialize New Blueprint
```bash
# Full project (default — unchanged prior behavior)
python3 scripts/init_blueprint.py "My Project" --path ./output/project-name

# Trivial single/few-step task
python3 scripts/init_blueprint.py "Check Weather" --path ./output/weather --scope micro

# Multi-step assignment / single feature
python3 scripts/init_blueprint.py "CSV Export Feature" --path ./output/csv-export --scope task
```

### Validate a Blueprint
```bash
# Tier read from the blueprint's own "## Scope:" header
python3 scripts/validate_blueprint.py ./output/project-name/blueprint.md

# Or force a tier explicitly (mismatch vs. the declared header is a FAIL)
python3 scripts/validate_blueprint.py ./output/weather/blueprint.md --tier micro
```

## Output Formats

| Format | Use Case |
|--------|----------|
| Markdown | Human-readable checklists and reports |
| JSON | Machine-readable for CI/CD pipelines |
| Validation Reports | Detailed compliance scores and fix guidance |

## Error Handling

- Detailed error messages with fix guidance
- Graceful degradation for missing or corrupt files
- Automatic rollback and recovery workflows
- Enterprise compliance strict validation

## Key References

- `references/enterprise-rules.md` — tier-scaled validation rule catalog (62 checks at PROJECT tier)
- `references/phase-templates.md` — Phase-specific templates
- `references/blueprint-structure.md` — Blueprint structure standards
- `references/checklist-patterns.md` — Checklist generation patterns
- `references/hackathon-blueprint-lessons.md` — Best-practices reference for hackathon-scoped blueprints
- `references/skill-enhancement-pipeline.md` — ACK character enforcement pipeline (11 gates) via skill-creator/skill_enhance.py
- `references/loop-enforcer-integration.md` — Loop-enforcer chain enforcement integration (gaps, env vars, worker API)
- `references/agent-detection-rules.md` — Agent/crew detection rules (singular source of truth)
- `references/model-tiering-strategy.md` — Token-optimized model tiering with flash/final pattern
- `references/templates/agent-model-map-template.yaml` — Agent model map template
- `references/templates/crew-model-map-template.yaml` — Crew model map template
- `references/verification-results-v1.0.6.md` — Complete test transcripts for self-healing, tamper resistance, opt-out, agent watch
- `references/validator-registry.md` — Project-Type → Phase Validator Registry (this session)

## Self-Enhancement Pipeline (ACK Character Enforcement)

The enterprise-blueprint skill can self-validate through the **skill-creator's ACK character enforcement pipeline** (`skill-creator/scripts/skill_enhance.py`). This applies the Agent Character Kit's enforcement methodology to the skill itself:

```bash
python3 .hermes/skills/skill-creator/scripts/skill_enhance.py update \
  --path .hermes/skills/devops/enterprise-blueprint \
  --tier enterprise --noninteractive
```

### 11-Gate Chain Enforcement

| Gate | Purpose | Hard/Soft |
|------|---------|-----------|
| 1. Scaffold | Skill structure exists | Soft (skipped on update) |
|| 2. Frontmatter | 7+ tags, description ≥100 chars, no placeholder markers | Hard |
| 3. Scripts | ≥3 substantive scripts (no __pycache__) | Hard |
| 4. References | ≥5 substantive reference docs | Hard |
| 5. Validate | Enterprise validation (58+ rules) | Hard |
| 6. Auto-fix | Safe structural fixes only | Hard |
| 7. Re-validate | 0 FAIL required (warnings OK) | **Hard (gate)** |
| 8. Test scripts | Syntax + shebang + --help exits 0 | Hard |
| 9. Verify sources | Provider tags remapped, no dead URLs | Soft |
| 10. Package | Version bump, .skill archive emitted | Hard |
| 11. Extract-verify | Archive layout intact, hashes match | Hard |

Operational rules and gotchas from hardening this skill (path
handling, chain-name sanitization, argparse quirks, validator contracts) are
documented in `references/lessons/skill-hardening-session-pitfalls.md` and
`references/lessons/chain-enforcement-lessons.md` — read those before adding
new scripts or modifying chain/path logic.

## Verification Results (v1.0.6 Session — Live End-to-End Tests)

### Agent Watch (Chain State) Created ✅
- File-based state machine at `.chain/blueprint-<agent>.json` with 6 steps, timestamps, attempts, transitions
- Marker files in `.blueprint-chain/` for each step (0-byte presence files)
- No external daemon needed — survives process crashes, container restarts, USB moves

### Self-Healing Verified ✅
| Test | Action | Result |
|------|--------|--------|
| State file deleted | `rm .chain/blueprint-*.json` → re-run `apply_blueprint.py` | Chain recreated fresh from checklist |
| State file corrupted | `echo '{"bad":true}' > .chain/blueprint-*.json` → `chain_worker.py status` | Fail-closed: `KeyError: 'steps'` — no silent recovery, explicit error |
| Re-apply after corruption | Re-run `apply_blueprint.py` on corrupted agent | Clean chain created, no residue from bad state |

### Tamper Resistance Verified ✅
| Attack | Attempt | Result |
|--------|---------|--------|
| Fake completion | Edit `.chain/blueprint-*.json` to set all steps `"state": "complete"` | `chain_worker.py status` shows tampered state but `check` returns `"locked"` for future steps — index gate blocks |
| Skip phase | Call `complete` on step 2 without step 1 | `verify` rejects: `"Step is 'locked', must be 'active' to verify"` |
| Marker file mismatch | Delete `.blueprint-chain/phase-00-*` but keep `.chain` state | Next `status` shows mismatch — chain validation catches drift |

### Opt-Out Flag Working ✅
```bash
apply_blueprint.py --target /path/agent --blueprint bp.md --no-loop-enforcement
# → Generates checklist.md ONLY, no .blueprint-chain/, no .chain/ state file
```

### Enterprise Validation Gates Passed (11/11) ✅
```
v1.0.4 → v1.0.5 → v1.0.6 (this session)
- All scripts pass syntax + --help + shebang
- 14 substantive scripts, 28 reference docs
- 0 FAIL, 11 WARNINGS (optional refs not linked in SKILL.md)
- Archive extracted & verified: hashes match, layout intact
```

## Checklist Generator — Single Source of Truth (Consolidated)

The checklist generator was rewritten to be the **single source of truth** for all enforcement. Blueprint is parsed ONCE by `generate_checklist.py`, which outputs two files:

| File | Purpose |
|------|---------|
| `checklist.md` | Human-readable task list with phase/step breakdown |
| `checklist-data.json` | Structured data for enforcement (phases, tasks, deliverables, validation gates, rollback, feature flags) |

### Flow (Consolidated)

**One tool, all verbs.** `enforce_blueprint.py` was folded into `generate_checklist.py` — the old file was replaced by a thin compat wrapper that delegates all legacy calls to the unified tool.

```
blueprint.md ──→ generate_checklist.py generate ──→ checklist.md
                                                     └──→ checklist-data.json ←── generate_checklist.py init
                                                                                    generate_checklist.py verify
                                                                                    generate_checklist.py complete
                                                                                    generate_checklist.py status
```

| Subcommand | Function |
|------------|----------|
| `generate` (default) | Parse blueprint, write `checklist.md` + `checklist-data.json` |
| `init` | Build enforcement chain from existing `checklist-data.json` |
| `verify` | Verify a phase step |
| `complete` | Complete a phase step |
| `status` | Show chain state |
| `check` | Check step status |
| `menu` | Interactive chain menu |
| `generate-validators` | Generate phase validators from blueprint data |

### Enforcement Modes

`--mode` flag on `generate` subcommand:

| Mode | Behavior | Use Case |
|------|----------|----------|
| `plain` | Just the checklist, no locking | Reference/planning only |
| `loop` | Checklist + loop locking (default) | Single agent with phase gating |
| `agent` | Checklist + loop + agent enforcement | Multi-agent with per-agent gates |
| `crew` | Checklist + loop + crew enforcement | Full crew orchestration |

### Opt-In Validators

Validators are **disabled by default** — only loop locking. Enable with `--with-validators`:

```bash
# Default: loop-locked ONLY (no validators)
python3 scripts/generate_checklist.py . --init

# Opt-in: generates per-phase validators from blueprint Part VI tables
python3 scripts/generate_checklist.py . --init --with-validators

# During generate (pre-populates enforcement config)
python3 scripts/generate_checklist.py blueprint.md --with-validators
```

### Usage Examples

```bash
# Generate checklist + data
python3 scripts/generate_checklist.py blueprint.md

# Init chain (loop-locked)
python3 scripts/generate_checklist.py /project --init

# Init chain with validators
python3 scripts/generate_checklist.py /project --init --with-validators

# Chain status
python3 scripts/generate_checklist.py /project --status

# Phase operations
python3 scripts/generate_checklist.py /project --phase 0 --step 0 --verify
python3 scripts/generate_checklist.py /project --phase 0 --step 0 --complete
python3 scripts/generate_checklist.py /project --phase 0 --step 0 --check

# Generate validators separately
python3 scripts/generate_checklist.py /project --generate-validators
```

### Blueprint Structure That Works (Part VI Tables)

The authoritative source of deliverables per phase is the **Part VI implementation checklist table** — this is what `init_blueprint.py` actually scaffolds (single `#`, em-dash title):

```markdown
# PART VI — MASTER IMPLEMENTATION CHECKLIST
### PHASE-0: Foundation
| Prerequisite | Feature Flag | Deliverables | Validation Gate | Rollback |
|--------------|--------------|--------------|-----------------|----------|
| Ventoy USB | FEAT_USB_BOOT | iso/maestro.iso | Boot test | RB-001 |
```

Each row = one task in the checklist; each deliverable in the
`Deliverables` cell may carry a `Type: file|glob|approval|external-check`
tag (default `file`) — see `references/blueprint-standard.md` §6. The data
flows into `checklist-data.json` for enforcement.

Table columns are matched **by header name**, not fixed position — a
reordered or renamed table (e.g. `Gate` instead of `Validation Gate`) still
parses correctly, as does either `# PART VI` or `## PART VI` heading depth.
(An earlier version of this parser matched only `## PART VI` against the
Part I boundary while the real heading is `# PART VI`, and used fixed
column positions — both silently produced zero tasks for any table not in
that exact shape; both are fixed.)

**Parsing priority**: Part VI table → fallback to checkbox tasks in phase sections. There is no other fallback path.

### Blueprint-Driven Validator Generator (This Session — Primary Pattern)

**Key Principle**: The blueprint IS the source of truth. Validators are GENERATED from Part VI implementation checklist tables, not from project-type assumptions.

### Architecture
```
Blueprint Part VI Tables (deliverables per phase)
        ↓
scripts/blueprint_validator_gen.py (parses tables, generates validators)
        ↓
.project/.blueprint-chain/validators/validate_phase{N}_blueprint.py
        ↓\ngenerate_checklist.py --with-validators maps gates → generated validators
        ↓
Enforcer (loop-enforcer) runs validator on verify() — AGENTS NEVER RUN VALIDATORS
```

### Opt-In Validator Pattern (Default = Loop-Locking Only)
```bash
# Default: checklist + phase locking ONLY (no validators)
python3 generate_checklist.py /project --init

# Opt-in: generates validators from blueprint Part VI tables
python3 generate_checklist.py /project --init --with-validators
```

**Why**: Validators are enforcer-only tools. Agents must not validate their own work (Creative Orchestration Doctrine Principle V: Critique Is Equal to Creation).

### Validator Generation Process (`blueprint_validator_gen.py`)
1. Parses **Part VI implementation checklist tables** in blueprint.md
2. Each table row = one deliverable with: prerequisite, feature flag, deliverable(s), validation gate, rollback
3. Generates `validate_phase{N}_blueprint.py` per phase in `.blueprint-chain/validators/`
4. Each validator checks EXACTLY what the blueprint declares (ISO files, scripts, configs, binaries, etc.)
5. **No project-type registry** — validation is blueprint-driven only. The old `registry.py` was deleted.

### New Phase-Specific Validators Created

| Phase | Project Type | Validator | Key Deliverables Checked |
|-------|-------------|-----------|-------------------------|
| 0 | All | `validate_phase0_foundation.py` | `.gitignore` patterns, dir structure, README, LICENSE, pyproject.toml, git init, linting |
| 1 | agent-crew | `validate_phase1_core_services.py` | API spec, DB config, service entry point, /health endpoint, config mgmt, logging, lock files, unit tests |
| 1 | web-app/dapp/backend | `validate_phase1_backend_api.py` | Same as above, tailored for web backends |
| 2 | web-app/dapp | `validate_phase2_frontend_web.py` | **Next.js/Vite/Svelte/Astro/Nuxt/Remix/Gatsby config**, pages/routes, components, TypeScript config, lint/format, build output, accessibility, SEO meta, responsive breakpoints, tests |
| 2 | mobile-flutter | `validate_phase2_mobile_flutter.py` | **pubspec.yaml**, platform dirs (android/ios/macos/windows/linux/web), build configs (gradle/Podfile), code signing, Fastlane/Codemagic, flutter analyze/test |
| 2 | agent-crew | `validate_phase2_runtime_agents.py` | Agent defs (SOUL.md/agent.json), Dockerfile/process mgmt, crew config, comms (Redis/gRPC), observability, lifecycle scripts |
| 3 | web3-dapp | `validate_phase3_smart_contracts.py` | **Foundry/Hardhat/Brownie/Ape config**, contracts in contracts/src/, tests, deploy scripts, ABIs (out/artifacts/), gas reports, Slither/Mythril, Etherscan verification |
| 3 | general | `validate_phase3_persistence_hardening.py` | Backup/restore scripts, firewall (nftables/iptables), hardening, volumes, secrets (SOPS/age), SSL, audit |
| 4 | web-app/dapp | `validate_phase4_integration_web.py` | E2E tests (Cypress/Playwright), CI/CD (GitHub Actions), deploy config (k8s/helm/terraform/Docker/vercel/netlify), smoke tests, perf tests (k6/locust), security scans (CodeQL/Semgrep/Trivy), docs, changelog, observability, feature flags |
| 4 | agent-crew | `validate_phase4_integration_validation.py` | Same as above + agent-specific integration tests |

### Reference Added
- `references/validator-registry.md` — Project-Type → Phase Validator Registry (this session)

## New References Added This Session

- `references/verification-results-v1.0.6.md` — Complete test transcripts for self-healing, tamper resistance, opt-out, agent watch
- `scripts/test_runner.py` — Phase-gated test orchestrator (syntax + help + execution probe)
- `scripts/test-runner.py` — Alias for compatibility
- `scripts/validate_phase0_foundation.py` — Phase 0 validator (git, .gitignore, README, LICENSE, pyproject.toml, dir structure, linting)
- `scripts/validate_phase1_core_services.py` — Phase 1 validator (API spec, DB config, service entry point, /health endpoint, config mgmt, logging, lock files, unit tests)
- `scripts/validate_phase2_runtime_agents.py` — Phase 2 validator (agent defs, Dockerfile/process mgmt, crew config, comms, observability, lifecycle scripts)
- `scripts/validate_phase3_persistence_hardening.py` — Phase 3 validator (backup/restore scripts, firewall, hardening, volumes, secrets, SSL, audit)
- `scripts/validate_phase4_integration_validation.py` — Phase 4 validator (integration/e2e tests, CI/CD, deploy config, smoke tests, contract tests, perf tests, security scanning, docs, changelog)
- `scripts/blueprint_validator_gen.py` — Blueprint-driven validator generator (parses Part VI tables, generates per-project validators)

## Enforcer Validation Architecture (This Session — Critical Fix)

**Problem**: The original `auto-verify-complete` allowed the **agent to validate itself** — creator reviewing own work. Violates Creative Orchestration Doctrine Principle V: *Critique Is Equal to Creation*.

**Solution**: Split verify/complete; enforcer owns validators. **Agents NEVER run validators** — only the enforcer can.

| Component | Role |
|-----------|------|
| `generate_checklist.py` | **Single unified tool**: generates checklist data AND manages chain state. Subcommands: generate, init, verify, complete, status, check, menu, generate-validators. After generation, reads only from `checklist-data.json` — never re-parses blueprint. Clears old chain state on re-init. |
| `chain.py` (loop-enforcer) | On `verify`, reads validator from state, executes it DIRECTLY (not via `python3`), marks `verified`/`active` |
| `chain_worker.py` | Agent interface: `check` → `verify` (enforcer runs validator) → `complete` — **no auto-verify-complete** |
| Phase validators | Independent scripts checking **real deliverables** (files, configs, patterns), not placeholder commands |

**Blueprint-Driven Validator Generator** (`scripts/blueprint_validator_gen.py`):
- Parses **Part VI implementation checklist tables** in blueprint.md for deliverables per phase
- Generates `validate_phase{N}_blueprint.py` scripts in `.blueprint-chain/validators/`
- Each validator checks EXACTLY what the blueprint declares (ISO files, scripts, configs, binaries, etc.)
- Falls back to project-type registry only if Part VI tables not found

**Validator Contract**:
```python
def check_<phase>(project_root: Path) -> tuple[bool, list[str]]:
    # Returns (passed, messages)
    # messages: ["ERROR: ...", "WARN: ..."]
    # Errors block phase completion; warnings only surface
```

**Phase Gate Flow** (enforcer-controlled):
```
1. Agent completes work → calls `chain_worker.py verify <step>`
2. Enforcer reads validators.json → sets validator on step
3. Enforcer runs validator DIRECTLY (subprocess.run([validator, path])) — exit code = pass/fail
4. If pass: step.state = "verified", next step.state = "active"
5. Agent calls `complete` → step.state = "complete"
6. Phase N+1 remains locked until Phase N validator passes
```

**Doctrine Compliance** (Creative Orchestration):
- **Identity immutable** — Phase gates reference blueprint tags/flags
- **Singular responsibility** — Each validator owns one phase's checks
- **Every decision → artifact** — Validators check for actual files/configs
- **Iterative critique** — Failed validation = phase stays active, agent fixes, re-verify
- **Critique = creation** — Phase gates are mandatory enforcer review
- **Regenerate only failure** — Failed phase re-verified; others stay complete
- **Hierarchical** — Phase N+1 locked until Phase N validated + completed

Validator implementation rules (never use `python3 validator.py` directly,
step-path-to-project-root navigation, exit-code contract, filename
sanitization, phase-gate indexing) are documented in
`references/lessons/skill-hardening-session-pitfalls.md`.

## File Index (validator-complete)

- `references/checklist-consolidation.md` — Checklist tool consolidation: enforce_blueprint.py merged into generate_checklist.py
- `references/agent-roles.md` — Agent Roles Reference
- `references/blueprint-standard.md` — Blueprint Standard Reference (v2)
- `references/cli-wiring.md` — CLI Wiring Reference
- `references/critical-file-protection.md` — Critical File Protection
- `references/enforcer-validation-architecture.md` — Enforcer Validation Architecture (this session)
- `references/lessons/chain-enforcement-lessons.md` — Chain-enforcement integration history and rationale
- `references/lessons/skill-hardening-session-pitfalls.md` — Skill-hardening operational gotchas (paths, chain names, argparse, validator contract)
- `references/phase-gating.md` — Phase Gating Reference
- `references/safety-practices.md` — Safety Practices
- `references/testing-framework.md` — Testing Framework Reference
- `references/validation-rules.md` — Validation Rules Reference
- `references/agent-detection-rules.md` — Agent/Crew Detection Rules
- `references/model-tiering-strategy.md` — Model Tiering Strategy
- `references/templates/agent-model-map-template.yaml` — Agent Model Map Template
- `references/templates/crew-model-map-template.yaml` — Crew Model Map Template
- `references/validator-registry.md` — Project-Type → Phase Validator Registry (this session)
- `references/verification-results-v1.0.6.md` — Live End-to-End Verification Results (self-healing, tamper resistance, opt-out, agent watch)
- `references/skill-validation-pitfalls.md` — General troubleshooting FAQ for skill_enhance.py validation failures
- `references/checklist-enforcement-failure.md` — Incident report: 2026-07-09 checklist enforcement failure
- `references/mv-maestro-usb-integration-lessons.md` — MV Maestro USB integration blueprint lessons (2026-07-13)
- `references/comprehensive-enforcement-requirements.md` — Generic enforcement requirements checklist (v2.0), applies to most enterprise projects
- `references/loop-enforcement-root-cause-analysis.md` — Root cause analysis of a loop-enforcement failure
- `references/session-2026-07-09-standalone-blueprint-checker.md` — Standalone blueprint checker session notes (2026-07-09)
- `references/erpv2-blueprint-lessons.md` — ERPv2 cross-chain escrow wallet blueprint generation lessons (2026-07-13)
- `references/mv-maestro-status.md` — MV Maestro blueprint validation status snapshot
- `references/checklist-generator-priority-chain.md` — generate_checklist.py's 3-try phase-extraction priority chain
- `references/checklist-generator-phase-format.md` — Phase & module-ref format requirements for the checklist generator
- `scripts/assign_agents.py` — enterprise-blueprint — Assign agent roles and track implementation metrics
- `scripts/blueprint_validator.py` — Validator for blueprint chain steps.
- `scripts/generate_checklist.py` — **Single unified tool**: generate, init, verify, complete, status, check, menu, generate-validators. Reads only from checklist-data.json after generation. `enforce_blueprint.py` is now a thin compat wrapper around this tool.
- `scripts/enforce_blueprint.py` — Thin compat wrapper translating legacy CLI calls to `generate_checklist.py`
- `scripts/skill_paths.py` — Self-contained loop-enforcer chain.py resolution (vendored copy, env-var overridable)
- `scripts/validator_registry.py` — Project-Type → Phase Validator Registry lookup/reporting tool
- `scripts/chain.py` — Vendored loop-enforcer chain engine (byte-identical copy; standalone operation)
- `scripts/test-runner.py` — Phase-Gated Test Orchestrator
- `scripts/test_runner.py` — Alias for compatibility
- `scripts/validate_blueprint.py` — Blueprint Validation Script
- `scripts/discover_agents.py` — Detect agent/crew/project identity (singular source of truth)
- `scripts/apply_blueprint.py` — Main entry: --target/--crew/--agents with --no-loop-enforcement opt-out
- `scripts/chain_worker.py` — Real plugin interface for agent→loop-enforcer
- `scripts/interactive_setup.py` — Walkthrough creating agent-model-map.yaml / crew-model-map.yaml
- `scripts/validate_phase0_foundation.py` — Phase 0 validator (git, .gitignore, README, LICENSE, pyproject.toml, dir structure, linting)
- `scripts/validate_phase1_core_services.py` — Phase 1 validator (agent-crew: API spec, DB config, service entry point, /health endpoint, config mgmt, logging, lock files, unit tests)
- `scripts/validate_phase1_backend_api.py` — Phase 1 validator (web-app/dapp/backend: API spec, DB config, service entry, health, config, logging, lock files, unit tests)
- `scripts/validate_phase2_runtime_agents.py` — Phase 2 validator (agent-crew: agent defs, Dockerfile/process mgmt, crew config, comms, observability, lifecycle scripts)
- `scripts/validate_phase2_frontend_web.py` — Phase 2 validator (web-app/dapp: Next.js/Vite/Nuxt/SvelteKit/Astro, pages, components, TypeScript, lint, build, a11y, SEO, tests)
- `scripts/validate_phase2_mobile_flutter.py` — Phase 2 validator (mobile-flutter: pubspec, platform dirs, Android/iOS/desktop/web config, main.dart, analysis_options, tests, code signing, Fastlane, CI/CD, flavors, l10n)
- `scripts/validate_phase3_persistence_hardening.py` — Phase 3 validator (agent-crew/backend: backup/restore scripts, firewall, hardening, volumes, secrets, SSL, audit)
- `scripts/validate_phase3_smart_contracts.py` — Phase 3 validator (web3-dapp/contracts: Foundry/Hardhat/Brownie/Ape, contracts, tests, deploy, ABIs, gas, static analysis, verification, networks, deps, CI/CD, SPDX, NatSpec, sizes)
- `scripts/validate_phase4_integration.py` — Phase 4 validator (general: e2e tests, CI/CD, deploy configs, smoke/perf tests, security scans, docs, changelog)
- `scripts/validate_phase4_integration_validation.py` — Phase 4 validator (agent-crew: e2e tests, CI/CD, deploy config, smoke tests, perf tests, security scans, docs, changelog, observability, feature flags)
- `scripts/validate_phase4_integration_web.py` — Phase 4 validator (web-app/dapp: same as above + web-specific deploy configs)