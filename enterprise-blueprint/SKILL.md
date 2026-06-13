---
name: enterprise-blueprint
description: "Generate enterprise-grade technical system blueprints paired with synchronized phase-by-phase enforcement checklists. Enforces modular structure, rollback tags, append-only change logs, and agent role assignment across all implementation phases. Provider-agnostic: OpenAI, Claude, Mistral, Gemini, Hermes, or any LLM with tool use. Free-first: $0 Python stdlib toolchain."
license: MIT
metadata:
  openclaw:
    tags:
      - blueprint
      - architecture
      - enterprise
      - planning
    category: devops
    priority: high
  hermes:
    tags:
      - creation
      - development
      - planning
    category: development
    related_skills:
      - portable-linux-usb
      - backup-protocol
  providers:
    - openai
    - claude
    - mistral
    - gemini
    - hermes
    - copilot
    - any
version: 0.0.4
---

# Enterprise Blueprint

Unified system for generating, validating, and maintaining enterprise-grade technical blueprints alongside synchronized enforcement checklists, with agent role assignment and progress measurement built in. The blueprint is the law. The checklist is the enforcement.

## Provider Compatibility

| Provider | Compatibility | Notes |
|---|---|---|
| Claude (Anthropic) | Full | Tool use, MCP servers, artifact generation |
| OpenAI / ChatGPT | Full | Function calling, Actions, assistants |
| Mistral / Vibe | Full | Tool calling, script execution |
| Gemini (Google) | Full | Extensions, Vertex AI |
| Hermes (Nous) | Full | Tool-use fine-tuned |
| GitHub Copilot | Partial | Code generation; use external runner for scripts |
| Any LLM + tools | Full | All scripts are plain Python, provider-independent |

## Free-First Strategy

| Tier | Cost | Stack | Escalation Criteria |
|---|---|---|---|
| **Tier 0** | $0/mo | Python 3.8+ stdlib only | Default — covers all individual use |
| **Tier 1** | $0-5/mo | + CI/CD automated validation | When validating 10+ blueprints automatically |
| **Tier 2** | $5-20/mo | + Hosted blueprint registry | When distributing across a team or org |

Free alternatives: every script uses Python stdlib exclusively — zero pip installs, zero paid services. The $0 toolchain covers the full lifecycle from init through assignment metrics. Escalate only when team collaboration or automated pipelines justify additional cost.

## Core Concepts

A blueprint project produces two coexisting documents in the same output directory:

- **blueprint.md** — The authoritative master specification (single source of truth)
- **checklist.md** — The enforcement companion, phase-synchronized to the blueprint

Supporting metadata files:

- **project.json** — Phase registry, configuration, and version tracking
- **assignments.json** — Agent role assignments keyed by phase and module ID

Both documents share version numbers and rollback tag anchors. When `blueprint.md` is amended, `checklist.md` must be updated in the same commit. The checklist may never lead the blueprint — it enforces what the blueprint defines.

## Workflow: Initialize a New Blueprint

### Step 1 — Scaffold the Project

```bash
# Default phases
python3 scripts/init_blueprint.py "Project Name" --path ./output/project-name

# Custom phases
python3 scripts/init_blueprint.py "Project Name" --path ./output \
  --phases "Pre-Build,Foundation,Auth,Core,Integration,Launch"

# Preview without writing files
python3 scripts/init_blueprint.py "Project Name" --path ./output --dry-run
```

`blueprint.md` and `checklist.md` are created with all required enterprise sections, rollback tags, change log stub, and module registry populated.

### Step 2 — Populate Blueprint Top-Down

Replace all markers following this sequence:
Part I (vision, architecture) → Part II (module registry) → Part III (specifications) → Part IV (data architecture) → Part V (change control) → Part VI (phase checklists) → Part VII (quality standards).

### Step 3 — Validate

```bash
python3 scripts/validate_blueprint.py ./output/project-name/blueprint.md
python3 scripts/validate_blueprint.py ./output/project-name/blueprint.md --verbose
python3 scripts/validate_blueprint.py ./output/project-name/blueprint.md --json
```

### Step 4 — Sync Checklist

After populating the blueprint, sync the checklist to pull in all phases and sections:

```bash
python3 scripts/generate_checklist.py ./output/project-name/blueprint.md --sync
```

## Workflow: Validate a Blueprint

```bash
# Standard scored report
python3 scripts/validate_blueprint.py ./project/blueprint.md

# Full verbose — all checks including passes
python3 scripts/validate_blueprint.py ./project/blueprint.md --verbose

# Machine-readable JSON for CI pipelines
python3 scripts/validate_blueprint.py ./project/blueprint.md --json
```

The validator checks all enterprise rules: required parts, rollback tags on every section, change log presence and format, module registry completeness, feature flag coverage, performance budgets, and testing requirements. See [references/enterprise-rules.md](references/enterprise-rules.md) for the full rule set and fix guidance.

## Workflow: Generate or Sync the Checklist

```bash
# Generate checklist from existing blueprint
python3 scripts/generate_checklist.py ./project/blueprint.md

# Sync after blueprint amendments (adds new phases, preserves checked items)
python3 scripts/generate_checklist.py ./project/blueprint.md --sync

# Write to a specific path
python3 scripts/generate_checklist.py ./project/blueprint.md \
  --output ./project/checklist.md
```

Parsed from the blueprint: phase markers, module registry entries, rollback tags, and screen/feature spec headers. Each checklist phase gets: prerequisites, granular implementation steps with example commands, a validation gate, and an agent sign-off block. See [references/checklist-patterns.md](references/checklist-patterns.md) for pattern detail.

## Workflow: Assign and Track Agents

```bash
# Assign an agent to a phase
python3 scripts/assign_agents.py ./project --assign "AgentName:PHASE-1"

# Assign an agent to a specific module
python3 scripts/assign_agents.py ./project --assign "AgentName:MOD-003"

# List all current assignments
python3 scripts/assign_agents.py ./project --list

# Full assignment and completion status report
python3 scripts/assign_agents.py ./project --report

# Performance metrics and bottleneck detection
python3 scripts/assign_agents.py ./project --metrics
```

See [references/agent-roles.md](references/agent-roles.md) for role taxonomy, delegation patterns, load-balancing rules, and measurement framework.

## Scripts

| Script | Purpose |
|---|---|
| `scripts/init_blueprint.py` | Scaffold a new blueprint + checklist pair with full enterprise structure |
| `scripts/validate_blueprint.py` | Validate a blueprint against enterprise rules; FAIL/WARN/PASS scoring |
| `scripts/generate_checklist.py` | Generate or sync a granular enforcement checklist from a blueprint |
| `scripts/assign_agents.py` | Manage agent role assignments and report completion metrics |

## Enforced Output Statistics

Every script produces structured JSON on completion:

```json
{
  "operation": "init_blueprint | validate | generate_checklist | assign_agents",
  "timestamp": "ISO8601",
  "status": "success | failed | dry_run",
  "project": "project-name",
  "details": {},
  "cost": {"tier": 0, "amount_usd": 0.0, "service": "local"}
}
```

All scripts support `--json` for machine-readable output suitable for CI pipelines.

## Error Handling

| Error | Response |
|---|---|
| Blueprint file not found | Report path; suggest `init_blueprint.py` |
| Missing required section (e.g., no PART IV) | Name the section; cite enterprise-rules.md |
| Missing rollback tag on section | Report header; provide correct tag format |
| Checklist out of sync with blueprint | List diverged phases; run `generate_checklist.py --sync` |
| `assignments.json` corrupt or missing | Rebuild from `project.json`; log the incident |
| Phase marked complete with failing tests | Block sign-off; require test fix before flag set |
| Python < 3.8 | Report minimum version; suggest upgrade |

See [references/enterprise-rules.md](references/enterprise-rules.md) for the full error catalog and recovery procedures. See [references/phase-templates.md](references/phase-templates.md) for phase-specific recovery patterns.

## Safety Practices

- Never overwrite critical files — use override protocol
- Blueprint files are critical — always backup before modification
- Use `--dry-run` flag to preview changes before applying
- See [safety-practices.md](references/safety-practices.md) for details
- See [critical-file-protection.md](references/critical-file-protection.md) for override protocol

## Enhancement Hooks

| Skill | Enhancement | When to Add |
|---|---|---|
| `skill-creator` | Package and validate this skill itself | When distributing enterprise-blueprint |
| `html-report` | Visual validation dashboard | When auditing 10+ blueprints |
| `xlsx` | Export assignments and metrics to spreadsheet | When managing large multi-agent teams |
| `docx` | Generate a Word document from blueprint | When delivering to external stakeholders |
| `frontend-design` | Interactive checklist web UI | When teams need browser-based tracking |

## Key References

- **Blueprint compliance standard and required sections**: [references/blueprint-standard.md](references/blueprint-standard.md) — Read when building, auditing, or amending a blueprint
- **Checklist generation patterns and item anatomy**: [references/checklist-patterns.md](references/checklist-patterns.md) — Read when writing, generating, or syncing checklist items
- **Agent role taxonomy, delegation, and measurement**: [references/agent-roles.md](references/agent-roles.md) — Read when assigning agents or analyzing bottlenecks
- **Phase-type templates for common implementation phases**: [references/phase-templates.md](references/phase-templates.md) — Read when populating a specific phase type for the first time
- **Enterprise enforcement rules and full error catalog**: [references/enterprise-rules.md](references/enterprise-rules.md) — Read when validating, troubleshooting, or enforcing compliance
