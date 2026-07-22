# Skill Creator — Enterprise Standards & Responsibility Model

Complete reference for how this skill actually validates, scores, and reasons about
skill quality, plus the full responsibility model this skill enforces across the
ecosystem. Every claim below is checked against the real code in `scripts/` — if a
script this file names doesn't exist, or doesn't do what's described, that's a bug in
this file, not a stale fact to leave standing (see `references/lessons/always-scaffold-through-init.md`
for what happens when that's allowed to persist for years).

## Table of Contents

1. [What Actually Gets Checked](#1-what-actually-gets-checked)
2. [analyze_skill.py's Quality Score](#2-analyze_skillpys-quality-score)
3. [Validation Commands](#3-validation-commands)
4. [Quality Checklist (authorial guidance, not all validator-enforced)](#4-quality-checklist-authorial-guidance-not-all-validator-enforced)
5. [Template Permissions](#5-template-permissions)
6. [Information Quality (authorial guidance)](#6-information-quality-authorial-guidance)
7. [Reusable Script Patterns](#7-reusable-script-patterns)
8. [Frontmatter & Provider Tags](#8-frontmatter--provider-tags)
9. [Real SKILL.md Structure](#9-real-skillmd-structure)
10. [Consolidation Precision Protocol](#10-consolidation-precision-protocol)
11. [Skill Definition Enforcement](#11-skill-definition-enforcement)
12. [Component Responsibility Model](#12-component-responsibility-model)
13. [Contamination Detection](#13-contamination-detection)

---

## 1. What Actually Gets Checked

`validate.py` is binary per-check FAIL/WARN, not a weighted score. There is no "8
pillars" percentage system anywhere in this skill's actual code — if you see that
framing elsewhere, it describes a different, unbuilt design, not this validator. The
real checks, both tiers unless noted:

| Area | What's checked | Enterprise | Basic |
|---|---|---|---|
| Frontmatter | Required keys (`name`, `description`, `version`); allowed keys only (`name`, `description`, `license`, `metadata`, `allowed-tools`, `version`) | same | same |
| Description | 100–1024 chars, no `<`/`>` | same | same |
| Tags | `metadata.tags` count | ≥7 | ≥5 |
| Structure | Exactly the 5 root items; `references/` may only contain files + `templates/` + `lessons/` | same | same |
| Scripts | Count of `.py .sh .bat .exe .ps1 .js .ts .mjs .cjs` files | ≥3 | ≥2 |
| References | Count of `.md .txt .html .pdf` files (`templates/` exempt from extension check) | ≥5 | ≥3 |
| Body length | SKILL.md body ≤500 lines | same | same |
| Placeholders | No `TODO`/`FIXME`/`TBD`/`WIP`/etc. patterns anywhere in the skill | same | same |
| Hardcoded paths | No literal `/home/`, `/Users/`, `/media/`, `/mnt/` paths in scripts (FAIL) or refs (WARN) unless behind an overridable default | same | same |
| Secrets | No hardcoded credential-shaped assignments in scripts | same | same |
| Lessons | Optional in both tiers; if `references/lessons/*.md` exist, each must open with the required YAML frontmatter | same | same |
| Content contamination | No lesson-shaped narrative language in SKILL.md/script docstrings (WARN) | same | same |
| Cross-references | Every script/ref should be mentioned in SKILL.md (WARN if not) | same | same |

There is no permissions check (no 755/644 enforcement) and no provider-harness
frontmatter requirement anywhere in `validate.py` — see sections 5 and 8 below for what
actually exists in those areas.

## 2. analyze_skill.py's Quality Score

`analyze_skill.py` (read-only, separate from `validate.py`) computes an **unweighted
average across 4 dimensions** — frontmatter, content, structure, agnostic — each scored
0–100 by its own heuristics, then simple-averaged for `overall_score`. This is the only
scoring system that actually exists in this skill; it's advisory (never gates
packaging), distinct from `validate.py`'s pass/fail checks.

## 3. Validation Commands

```bash
# Enterprise validation (default)
python3 scripts/validate.py /path/to/skill

# Basic (lighter-count) tier
python3 scripts/validate.py /path/to/skill --basic

# Advisory quality score (separate tool, not a gate)
python3 scripts/analyze_skill.py /path/to/skill

# Batch validate every skill under a root (see references/scan-report.md)
python3 scripts/scan_report.py --root /path/to/skills/

# External source verification (heuristic URL probing, not a real search —
# see SKILL.md's verify_sources.py section)
python3 scripts/verify_sources.py /path/to/skill
```

## 4. Quality Checklist (authorial guidance, not all validator-enforced)

Structural items marked **(V)** are enforced by `validate.py`; the rest are judgment
calls a human or reviewing agent should still apply.

- **(V)** SKILL.md exists with YAML frontmatter (`name` + `description`)
- **(V)** Description 100–1024 characters, contains what + when + triggers
- **(V)** `scripts/` and `references/` meet tier minimums
- **(V)** No stale template names (`example.py`, `api_reference.md`, `example_asset.txt`)
- **(V)** Every script and reference mentioned in SKILL.md (WARN if missed)
- Directory name matches frontmatter `name`
- Content accuracy — every claim in SKILL.md is true of the actual code (not
  mechanically checkable beyond the contamination scan; verify by hand for anything the
  automated checks can't see)
- Use case coverage, example quality, reference completeness

## 5. Template Permissions

The only permissions rule `validate.py` actually enforces: files under
`references/templates/` must be read-only (`chmod 0444` — any write bit set is a FAIL).
`auto_fix.py` repairs this automatically. There is no broader 755/644
directory/file-permission requirement anywhere in this toolchain — don't apply one that
isn't there.

## 6. Information Quality (authorial guidance)

Not validator-enforced; use as a review lens when writing or auditing a skill's content.

| Check | Description |
|---|---|
| **Completeness** | API endpoints, code examples, error states, configuration, and prerequisites are all documented, not just described in passing |
| **Robustness** | Edge cases, idempotency, rollback, timeout/retry, and graceful-degradation behavior are covered where relevant |
| **Accuracy** | Code examples parse, version numbers match current releases, example secrets are clearly marked as examples |

## 7. Reusable Script Patterns

Generic patterns for skill authors to build on — illustrative, not claims about this
skill's own scripts (which follow their own documented behavior in SKILL.md).

### Script Skeleton

```python
#!/usr/bin/env python3
"""
[Skill] — [Purpose]

Usage:
    python3 script.py <command> [options]
    python3 script.py --help
    python3 script.py --dry-run
"""

import json, sys
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path.home() / ".skill-name"
CONFIG_PATH = STATE_DIR / "config.json"

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def append_jsonl(filepath, record):
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "a") as f:
        f.write(json.dumps(record) + "\n")

COMMANDS = {"help": lambda: print(__doc__), "status": do_status}

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd in ("--help", "-h"): cmd = "help"
    if cmd == "--dry-run": print("[DRY RUN]"); return
    COMMANDS.get(cmd, lambda: print(f"Unknown: {cmd}"))()

if __name__ == "__main__":
    main()
```

### Queue Processor Pattern

```python
QUEUE = STATE_DIR / "queue.jsonl"
RETRY = STATE_DIR / "retry_queue.jsonl"
FAILED = STATE_DIR / "permanent_failures.jsonl"
MAX_RETRIES = 3

# pending → processing → completed
#              ↓ failure
#         retry (retries < 3)
#              ↓ retries >= 3
#         permanent_failures
```

### Health Checker Pattern

```python
def check_service(name, check_fn):
    start = time.time()
    try:
        result = check_fn()
        return {"service": name, "status": "healthy", "ms": round((time.time()-start)*1000)}
    except Exception as e:
        return {"service": name, "status": "unhealthy", "error": str(e)}
```

### Command Pattern

Multi-function scripts with subcommands:

```python
COMMANDS = {
    "process": do_process,
    "status": do_status,
    "retry": do_retry,
}

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd in ("--help", "-h"): cmd = "help"
    COMMANDS.get(cmd, lambda: print(f"Unknown: {cmd}"))()
```

### Pipeline Pattern

Stage-isolated queues (pending → processing → completed → retry → failed):

```python
# Stage isolation
QUEUE_FILE = STATE_DIR / "queue.jsonl"
PROCESSING_FILE = STATE_DIR / "processing.jsonl"
COMPLETED_FILE = STATE_DIR / "completed.jsonl"
RETRY_FILE = STATE_DIR / "retry.jsonl"
FAILED_FILE = STATE_DIR / "failed.jsonl"

# No state collision between concurrent runs
```

### Declarative Config Pattern

Cron definitions as data arrays + deploy function:

```python
CRONS = [
    {"name": "scan", "schedule": "0 */4 * * *", "command": "python3 scan.py"},
    {"name": "process", "schedule": "0 */2 * * *", "command": "python3 pipeline.py process"},
    {"name": "report", "schedule": "0 23 * * *", "command": "python3 report.py"},
]

def deploy_crons():
    for cron in CRONS:
        # Deploy each cron definition
        pass
```

## 8. Frontmatter & Provider Tags

The real, currently-enforced frontmatter schema has exactly these top-level keys:
`name`, `description`, `version`, `license` (optional), `metadata` (optional, holds
`tags` + free-form fields like `category`/`complexity`), `allowed-tools` (optional).
There is no required per-provider harness section (`metadata.openclaw`,
`metadata.openai`, `metadata.anthropic`, etc.) — `validate.py` never checks for one.

What actually exists for provider-specific behavior: `skill_enhance.py`'s provider tag
remap (see `references/provider-tag-remapping.md`). Before packaging, it detects the
harness from environment signals (`HERMES_*`/`OPENCLAW_*`/`OPENAI_*` env vars,
`HEMLOCK_MODE`, or an explicit `--provider` flag) and copies the canonical
`metadata.tags` list into that provider's own block (`metadata.<provider>.tags`) —
additive and idempotent; the canonical list is never altered. That's the entire scope of
per-provider metadata in this toolchain.

## 9. Real SKILL.md Structure

```markdown
---
name: skill-name
description: "What this skill does and when to use it — 100 to 1024 characters,
  concrete triggers, no angle brackets."
version: 0.1.0
license: MIT
metadata:
  category: your-category
  complexity: enterprise
  tags:
    - at least 5 (basic) or 7 (enterprise) natural-language trigger phrases
---

# Skill Name

One or two sentences on what this does and why it matters.

## When to use

Concrete scenarios that should trigger this skill.

## Toolchain / workflow

Whatever the skill's own body needs — a scripts table, workflow steps, etc. There is no
fixed required section list beyond what's useful for this specific skill's own domain.

## Key References

Bulleted links into `references/`, each with a one-line "when to load this" note.
```

There's no requirement for "Provider Compatibility," "Free-First Strategy," or
"Enforced Output Statistics" sections — those describe a different, unbuilt template.
Write the sections this specific skill actually needs; keep the body under 500 lines and
push detail into `references/`.

## 10. Consolidation Precision Protocol

### When Merging Skills

1. **Read ALL source files completely** before writing anything
2. **Map content to sections** — identify where each piece belongs
3. **Deduplicate** — same information in multiple sources, keep one copy
4. **Preserve unique features** — never drop skill-specific functionality
5. **Merge common modules** — shared code goes in shared location
6. **Update all references** — internal links point to new structure
7. **Verify completeness** — every source file's content appears somewhere
8. **Test consolidated skill** — run `validate.py` (not a "pro" variant — there is only one validator) on the result

### Consolidation Checklist

- [ ] All source SKILL.md files read completely
- [ ] All reference files copied (no duplicates)
- [ ] All scripts merged (no conflicts)
- [ ] YAML frontmatter merged with combined description
- [ ] Content organized logically (not just appended)
- [ ] Duplicate sections removed
- [ ] Internal cross-references updated
- [ ] No information lost from any source
- [ ] `validate.py` passes on the consolidated skill

### Methodical Precision Rules

| Rule | Description |
|---|---|
| **Exhaustive Read** | Read every file in every source skill before writing |
| **Section Mapping** | Create a mapping of where each section goes |
| **Lossless Merge** | Every piece of information must appear in output |
| **Conflict Resolution** | When sources disagree, document both and pick one |
| **Reference Integrity** | All links must resolve to valid targets |
| **Backward Compatibility** | Existing users can find equivalent content |

## 11. Skill Definition Enforcement

Before anything else, this skill's whole purpose is answering: **is this actually a
skill?** A skill is a reusable, applied capability — executable behavior, structured
knowledge, validation, a lifecycle. It is not:

- A knowledge article, tutorial, or policy document
- A collection of notes or a prompt dump
- A personal history log
- A template with no behavior behind it

If something fails this test, the answer is not to force it into skill shape by padding
content to hit the enterprise minimums — it's to either find a genuinely broader,
real application of the capability, or leave it as a document, not a skill. See
`references/lessons/validator-vs-content-rephrase-not-relax.md`: the fix for a validator
flag is always to change the content's truth, never to weaken the check.

## 12. Component Responsibility Model

| Component | Purpose | Must NOT contain |
|---|---|---|
| `SKILL.md` | The operational contract — what, when, required behavior, execution rules, boundaries | Development history, debug logs, failed attempts, session notes, long tutorials |
| `scripts/` | Executable capability — automation, validators, generators, parsers | Non-executable notes; every script must run, handle errors, avoid hidden assumptions and hardcoded paths |
| `references/` | Supporting intelligence loaded on demand — schemas, specs, domain knowledge | Duplicated SKILL.md content; anything not actually referenced |
| `references/templates/` | Read-only (chmod 0444) instantiation skeletons, copied out and then acted upon | Environment-specific data; anything that becomes an edited-in-place copy |
| `references/lessons/` | Historical intelligence — known failures, root causes, resolutions, prevention patterns, in structured YAML frontmatter | Operational rules that belong in SKILL.md instead; unstructured narrative with no frontmatter |

Lessons answer "what has happened before" — they do not define "what must happen." An
operational rule discovered via a specific incident still belongs in SKILL.md (or a
reference doc) once generalized; the incident narrative itself belongs in
`references/lessons/`.

## 13. Contamination Detection

`validate.py`'s lesson-shaped-content check exists because doc drift is otherwise
invisible to the pipeline: structural checks (counts, extensions, placeholders) can't
tell whether SKILL.md's prose is still *true* of the code. If SKILL.md or a script
docstring reads like a case study — "during testing," "we discovered," "originally,"
"fixed by," "in this session," "pitfall" — that's a signal the content is either
misplaced (move it to `references/lessons/`) or has rotted into an unverified historical
claim dressed as a current instruction (verify it against the actual code and correct
whichever side is wrong). Nothing gets auto-moved; a human or reviewing agent judges
operational-vs-historical, the same way `auto_fix.py` never renames files in batch.
