---
name: enterprise-blueprint-validation
description: "Validate enterprise blueprints, generate phase-gated checklists, and orchestrate tiered implementation testing (unit/integration/e2e/playwright) for multi-phase agent framework projects. Provider-agnostic and free-first: $0 Python stdlib toolchain, path-agnostic scripts, no external services."
license: MIT
metadata:
  tags:
    - blueprint
    - validation
    - testing
    - enterprise
    - checklist
    - phase-gating
    - devops
  openclaw:
    tags:
      - validation
      - testing
      - enterprise
      - blueprint
    category: devops
    priority: high
  hermes:
    tags:
      - validation
      - testing
      - development
    category: development
    related_skills:
      - enterprise-blueprint
      - guardrail-enforcement
  providers:
    - openai
    - claude
    - mistral
    - gemini
    - hermes
    - copilot
    - any
version: 0.0.2
---

# Enterprise Blueprint Validation & Testing

## Purpose
Validate enterprise blueprints, generate phase-gated checklists, and orchestrate implementation testing for multi-phase agent framework projects.

## When to Use
- Validating INTEGRATION_BLUEPRINT.md or similar enterprise blueprints
- Generating implementation checklists from validated blueprints
- Running phase-gated testing (unit, integration, e2e, playwright)
- Wiring blueprint phases to implementation scripts

## Core Workflow

### 1. Validate Blueprint
```bash
python3 scripts/validate_blueprint.py INTEGRATION_BLUEPRINT.md --json
```
**Pass criteria:** 0 FAIL, warnings only for minor doc gaps.  
**Output:** JSON with summary {passed, failed, warned}.

### 2. Generate Checklist
```bash
python3 scripts/generate_checklist.py INTEGRATION_BLUEPRINT.md
```
Produces `checklist.md` with phase-gated tasks, feature flags, module mapping.

### 3. Phase-Gated Implementation
Each phase has:
- **Rollback tag** `[PHASE-N-v1]`
- **Feature flag** `FEAT_*`
- **Validation gate** - must pass before next phase
- **Rollback procedure** documented

### 4. Testing
```bash
# Unit tests (25+ function validations)
hemlock test-unit

# Integration (6 scenarios)
hemlock test-integration

# E2E (8 workflows)
hemlock test-e2e

# Playwright (18 browser scenarios)
hemlock test-playwright

# All
hemlock test-all
```

## Blueprint Structure Requirements
- PART I–VII present with rollback tags
- Module Registry with MOD-NNN, feature flags
- Screen specs with SCR-NNN, module refs
- Data Architecture: SQL schemas + API contracts + migration naming
- Change Control: 9-field CL entries, contributor rules
- Quality Standards: error hierarchy, testing targets, performance budgets

## Safety Framework Integration
All implementation scripts must source `safety-test-framework.sh`:
- Confirmation prompts for destructive actions
- Dry-run mode (`--dry-run` / `-n`) with toggle in menus
- Error recovery: retry, modify, skip, rollback, diagnostics
- Automatic rollback stack on failure

## Common Pitfalls
1. **Missing PART sections** → validator catches this
2. **Unwired CLI entries** → verify entrypoint.sh has all commands
3. **Syntax errors in scripts** → run `bash -n` on all .sh files
4. **Blueprint warnings ignored** → fix before implementation
5. **Phase validation skipped** → each phase must pass gate

## Scripts

| Script | Purpose |
|---|---|
| `scripts/validate_blueprint.py` | Validate a blueprint against enterprise rules; FAIL/WARN/PASS scoring with `--json` |
| `scripts/generate_checklist.py` | Generate a phase-gated enforcement checklist from a validated blueprint |
| `scripts/test-runner.py` | Phase-gated test orchestrator (unit/integration/e2e/playwright); runner-agnostic, `--dry-run`, `--json` |

## References
- [references/blueprint-structure.md](references/blueprint-structure.md) — required sections checklist
- [references/validation-rules.md](references/validation-rules.md) — validation logic and pass/fail criteria
- [references/testing-framework.md](references/testing-framework.md) — test tiers, runner resolution, safety integration
- [references/phase-gating.md](references/phase-gating.md) — rollback tags, feature flags, validation gates
- [references/cli-wiring.md](references/cli-wiring.md) — mapping blueprint phases to CLI commands
- [references/phase-template.md](references/phase-template.md) — phase definition template with worked example