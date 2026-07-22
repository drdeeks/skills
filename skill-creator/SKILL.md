---
name: skill-creator
description: Author, edit, audit, validate, package, and upgrade AgentSkills. Provides
  the philosophical guidance for lean skill authoring (concise-is-key, appropriate
  degrees of freedom, progressive disclosure) alongside the operational toolchain
  (validator, packager, upgrader, auto-fixer). Use when creating a new skill from
  scratch, tidying/reviewing/auditing an existing skill, restructuring a skill directory,
  packaging a .skill archive, or upgrading a basic-tier skill to enterprise. Triggers
  on phrases like 'create a skill', 'author a skill', 'tidy up a skill', 'audit the
  skill', 'package this skill', 'upgrade skill to enterprise'. Validator runs enterprise-strict
  by default; pass --basic for the lighter-count tier. Every script is directly invokable.
version: 3.0.14
license: MIT
metadata:
  category: skill-authoring
  complexity: enterprise
  previous_version: 2.1.1
  fork_origin: _curated/skill-creator@2.1.1
  fork_note: Every script directly invokable; skill_enhance.py sequences the standard
    pipeline.
  tags:
  - skill authoring
  - skill validation
  - skill packaging
  - agent skills
  - progressive disclosure
  - concise skill design
  - enterprise standards
---

# Skill Creator — Authoring Guidance + Unified Toolchain

The **sole source of truth** for how skills are authored, validated, packaged, and upgraded in this project. Every other skill in the `skill-*` family (e.g. `skill-installer`) delegates to the scripts in this skill rather than shipping its own copies.

Two things live here on purpose:

1. **Authoring philosophy** — the *why* behind lean skills. Read this before writing any SKILL.md.
2. **Operational toolchain** — the validator/packager/upgrader/auto-fixer scripts that enforce the philosophy.

---

## Is this actually a skill?

Before creating anything, answer this. A skill is a reusable, executable capability —
not a knowledge dump, tutorial, policy document, or prompt collection.

- **No `scripts/`, or nothing in it that's actually executed?** It's not a skill. Text
  that only ever gets read isn't a capability — it's information, and belongs in a doc,
  not a skill package.
- **Fits on one page with no real toolchain behind it?** It's knowledge, not a skill.
  Knowledge doesn't need `__init__.py`, `scripts/`, or a validator — a skill does.
- **Can't clear the enterprise minimums (3+ scripts, 5+ references, 7+ tags) with real,
  substantive content?** The fix is never to relax the validator or pad content to hit a
  number — find a genuinely broader application of the capability, or don't build it as
  a skill. See `references/lessons/validator-vs-content-rephrase-not-relax.md`.

The full responsibility model (component boundaries, contamination detection, what this
skill exists to prevent) is in `references/standards.md` — this section is the
short-form gate; that file is the long-form reference.

---

## Core Principles (read this first)

### 1. Concise is Key

The context window is a public good. Every skill shares it with the system prompt, conversation history, other skills' metadata, and the actual user request.

**Default assumption: the agent is already very smart.** Only add context the agent doesn't already have. Challenge each piece of information:

- Does the agent really need this explanation?
- Does this paragraph justify its token cost?

Prefer concise examples over verbose explanations. A 5-line example usually beats a 30-line paragraph.

### 2. Set Appropriate Degrees of Freedom

Match specificity to the task's fragility:

| Freedom | When to use | Form |
|---|---|---|
| **High** | Multiple valid approaches; context-dependent | Text instructions, heuristics |
| **Medium** | Preferred pattern exists; some variation OK | Pseudocode, parameterized scripts |
| **Low** | Fragile / consistency-critical / must-follow sequence | Specific scripts, few parameters |

Think of the agent as exploring a path: a narrow bridge with cliffs needs guardrails (low freedom); an open field allows many routes (high freedom).

### 3. Progressive Disclosure — Three-Level Loading

Skills manage context through a three-level system:

| Level | Loaded | Budget |
|---|---|---|
| **Metadata** (name + description) | Always | ~100 words |
| **SKILL.md body** | When triggered | ≤ 500 lines |
| **Bundled resources** (scripts/refs/assets) | On demand | Unlimited (scripts execute without loading) |

Keep the SKILL.md body ≤ 500 lines. When it grows past that, split into `references/`. Reference the split files from SKILL.md and tell the reader clearly *when* to load them.

**Split patterns:**

- **High-level guide with references** — SKILL.md sketches the workflow; `references/FORMS.md`, `references/REFERENCE.md` cover deep dives.
- **Domain-specific** — `references/finance.md`, `references/sales.md`, `references/product.md` per topic; agent loads only the relevant one.
- **Conditional details** — basic content in SKILL.md, links to `references/REDLINING.md` etc. for advanced features.

Keep references one level deep from SKILL.md. For files > 100 lines, put a TOC at the top so the agent can preview scope.

---

## Anatomy of a Skill (EXACTLY 5 root items)

```
skill-name/
├── __init__.py         (REQUIRED — scaffolder for whatever this skill curates)
├── SKILL.md            (REQUIRED — frontmatter + body)
├── scripts/            (REQUIRED — executable code, Python/Bash/etc.)
├── references/         (REQUIRED — docs the agent loads as needed)
│   └── lessons/        (optional nested — real case studies from usage;
│                        presence does NOT change tier classification)
└── <skill_name>.skill  (regenerated by packager on every pack — never
                         author-edited; packager IGNORES it on input and
                         REPLACES it on output)
```

**Nothing else at the root.** No `assets/`, no `README.md`, no `CHANGELOG.md`, no `notes.md`. Any output-file assets belong inside `scripts/` or `references/` under a purpose-scoped filename, not in a top-level `assets/` dir.

### `__init__.py` — the skill's own scaffolder

Every skill's `__init__.py` contains executable scaffolding + integration logic for the skill's own domain. Not just metadata. skill-creator's `__init__.py` scaffolds new skills (that's this file); autowatch's `__init__.py` scaffolds new watched-dir configs; a payments skill's `__init__.py` scaffolds new payment integrations. The scaffolder template is generated by `skill-creator/__init__.py scaffold()` and the author fills in the body with their skill's domain logic.

### SKILL.md

- **Frontmatter** (YAML): `name`, `description`, `version`, optional `license` + `metadata` (including `tags` — minimum 5 for basic, 7 for enterprise so the skill is auto-triggerable).
- **Body** (Markdown): instructions + guidance. Loaded only after the skill triggers.

The description is the primary triggering mechanism. Include **what** the skill does + **when** to use it. "When to use" belongs here, not in the body — the body doesn't exist until the skill triggers.

### Scripts

Executable code for deterministic-reliability or repeatedly-rewritten tasks.

- **Include when:** same code keeps getting rewritten, or determinism matters.
- **Benefits:** token-efficient, deterministic, executable without loading into context.

### References

Docs the agent should reference while working (schemas, API specs, domain knowledge, policies).

- **Keep SKILL.md lean** — move detailed material here.
- **Avoid duplication** — info lives in EITHER SKILL.md OR refs, not both.
- `references/lessons/` (optional nested) — real case studies + learnings from actual usage. Empty lessons dir does NOT block enterprise; but if the dir exists, its contents must be real content, not stubs.

### `<skill_name>.skill` — the packaged archive

Regenerated on every `package_skills.py` run. The packager:

- **IGNORES** any pre-existing `.skill` file on input (never re-packs a stale archive)
- **REPLACES** the archive in place with the freshly-packed one
- **CHECKS** every other file for correct placement and moves stray files to the right dir (never renames in batch — see the auto-fix contract below)

---

## What NOT to Include in a Skill

Extraneous documentation clutters the skill and wastes tokens. Skills should NOT contain:

- `README.md` — SKILL.md is the entry point
- `INSTALLATION_GUIDE.md` — install steps belong in the skill-installer skill, not per-skill
- `QUICK_REFERENCE.md` — that's what SKILL.md IS
- `CHANGELOG.md` — handled by the packager's version bump
- `TODO.md`, `notes.md`, `AGENTS.md`, `WORKSPACE.md`
- Cache dirs (`__pycache__`, `.pytest_cache`, `node_modules`), VCS metadata, OS metadata

A skill contains only what an agent needs to do the job — no auxiliary context about the process that created it, no user-facing marketing, no setup docs.

---

## Skill Creation Process

Six steps. Follow in order; skip only with a clear reason.

1. **Understand** the skill through concrete examples. Ask the user what triggers it, what usage looks like. Don't overwhelm — one or two questions at a time.
2. **Plan** reusable contents. For each example, identify what scripts/refs/assets would help.
3. **Initialize** via `python3 __init__.py --scaffold <name> --path <parent>`. Auto-generates the structural skeleton (enterprise tier only — see `references/lessons/always-scaffold-through-init.md`).
4. **Edit** SKILL.md and add resources. Test any scripts by actually running them.
5. **Package** via `scripts/package_skills.py`. Validates + version-bumps + emits `.skill` archive.
6. **Iterate** based on real usage.

### Skill naming

- Lowercase, digits, hyphens only. Under 64 chars.
- Verb-led when possible (`gh-address-comments`, `linear-address-issue`).
- Folder name matches skill name exactly.

### Frontmatter minimums

| Field | Rule |
|---|---|
| `name` | Hyphen-case, ≤ 64 chars |
| `description` | 100–1024 chars; include what + when; no `<`/`>` |
| `version` | Semantic (X.Y.Z); packager auto-bumps patch |
| `metadata.tags` | ≥ 5 (basic), ≥ 7 (enterprise) — used for auto-triggering |
| `license` | Optional but recommended |
| `allowed-tools` | Optional; the only other top-level key the validator accepts |

Only these keys are allowed at the top level. Extras trigger a FAIL.

---

## Toolchain

Every script is directly invokable — but for actually creating or changing a skill, `skill_enhance.py` is the only sanctioned path, however small the change. Running `validate.py`/`auto_fix.py`/`package_skills.py` directly is for debugging and inspection only; it skips the enforced gate sequence and is never a substitute for the full pipeline. `skill_enhance.py` sequences the full 11-step pipeline by calling each script as an ordinary subprocess.

Most scripts that support `--json` emit `operation`/`timestamp`/... structured output, but the exact shape varies by script's purpose (e.g. `analyze_skill.py` and `detect_redundancy.py` use their own result schemas, and `normalize_tags.py` has no `--json` mode at all) — check a given script's own `--help`/docstring for its actual output shape rather than assuming a universal one.

### `scripts/skill_enhance.py` — Pipeline Orchestrator WITH CHAIN ENFORCEMENT

```bash
# Enterprise (default) — strict counts: 3+ scripts, 5+ refs, 7+ tags
python3 scripts/skill_enhance.py create --name my-skill --tier enterprise

# Basic — lighter counts: 2+ scripts, 3+ refs, 5+ tags
python3 scripts/skill_enhance.py create --name my-skill --tier basic

# Update existing skill through enforced pipeline
python3 scripts/skill_enhance.py update --path ./my-skill
```

**CHAIN ENFORCEMENT (BUILT-IN):** Every pipeline gate (scaffold → frontmatter → scripts → refs → validate → auto_fix → re_validate → test → verify_sources → package → extract_verify) is a LOCKED chain step managed by the skill's OWN `scripts/chain.py` — self-reliant, no other skill required. Set `LOOP_ENFORCER_ROOT` to explicitly delegate to the universal loop-enforcer skill instead. Temp chain workdir auto-created/deleted. Cannot proceed until current step verified + completed. Skill root stays CLEAN — no `.chain` or `.chain-steps` dirs left behind.

**PROVIDER TAG REMAP (in-pipeline):** Before the package gate, enhance detects the harness (`HERMES_*` / `OPENCLAW_*` / `OPENAI_*` env, `HEMLOCK_MODE`; `--provider` overrides) and copies canonical `metadata.tags` into that provider's block (`metadata.<provider>.tags`) — additive, idempotent, canonical untouched. See `references/provider-tag-remapping.md`.

### `scripts/chain.py` — Built-in Chain Enforcer

Vendored copy of the universal chain concept (loop-enforcer). Locked sequential steps, verify-before-complete, JSON output. Used automatically by `skill_enhance.py`; directly invokable.

### `scripts/normalize_tags.py` — Repo-side Standard-Tag Normalizer

Strips install-time provider tag blocks from SKILL.md(s) so the REPO ships standard tags only. Runs automatically from the post-commit gate hook (transmitted by skill-installer on every install); `--check` mode reports without writing.

### `scripts/validate.py` — Structural + Content Validator

```bash
python3 scripts/validate.py /path/to/skill/          # enterprise (default)
python3 scripts/validate.py /path/to/skill/ --basic   # lighter tier
```

Purely read-only — never mutates. Structural fixes live in `auto_fix.py`.

**Checks (both tiers):**

- Root layout: `SKILL.md`, `__init__.py`, `scripts/`, `references/`, `<name>.skill` — nothing else at root
- Frontmatter format + allowed keys + tag minimum (5 basic / 7 enterprise)
- Description 100–1024 chars, no angle brackets
- `scripts/` extensions: `.py .sh .bat .exe .ps1 .js .ts .mjs .cjs` (min 2 basic / 3 enterprise)
- `references/` extensions: `.md .txt .html .pdf` (min 3 basic / 5 enterprise), plus `templates/` (any type) and optional `lessons/`
- No hardcoded absolute paths outside code fences
- No placeholder patterns anywhere in the skill (SKILL.md, references/, scripts/ comments)
- No lesson-shaped narrative language (e.g. `we discovered`, `fixed by`) in SKILL.md or script docstrings — WARN, points at `references/lessons/`
- Every `references/lessons/*.md` opens with required YAML frontmatter (`title`, `category`, `failure`, `root_cause`, `resolution`, `prevention`, `date`, `verified`)
- Body ≤ 500 lines
- Every script + ref cross-referenced from SKILL.md (WARN if not)

### `scripts/auto_fix.py` — Structural Auto-Fixer

```bash
python3 scripts/auto_fix.py /path/to/skill/
```

Applies the safe-move contract:

- **DELETE** — cached/VCS/build dirs (`__pycache__` etc.), empty directories left behind by a move, and foreign/stale `.skill` archives anywhere in the tree (never the skill's own `<name>.skill` — that one is replaced in place by the next `package` step, so a deleted foreign archive doesn't leave the skill without one)
- **MOVE** — `lessons/` → `references/lessons/`, `templates/` → `references/templates/` (chmod 0444), root-level `.md/.txt/.html/.pdf` → `references/`, root-level scripts by extension → `scripts/`
- **NEVER** deletes a file with real, needed content — only cache artifacts and foreign `.skill` archives are ever deleted; mis-named files (`README.md`, `TODO.md`, `notes.md`, etc.) with substantive content get MOVED to the right dir, never renamed in batch — the validator still FAILs with a rename hint so a human picks the name.

### `scripts/package_skills.py` — Packager

```bash
python3 scripts/package_skills.py --skills-root /path/to/parent --skill skill-name
```

This script does exactly two things: reads the current `SKILL.md` version, bumps the
patch number and writes it back (recording `previous_version` in
`.skill-manifest.json`); then zips the tree into `<skill_name>.skill`, excluding
cache/VCS dirs, compiled artifacts, and nested `.skill` files. **It does not validate,
does not chmod anything, and does not refuse to package an invalid skill** — calling it
directly can package a broken skill. The validate → auto_fix → re-validate → package →
extract-verify sequence that makes packaging safe lives one level up, in
`skill_enhance.py` — that's the only sanctioned path (see Toolchain intro above).

### `scripts/upgrade_to_enterprise.py` — Basic → Enterprise

```bash
python3 scripts/upgrade_to_enterprise.py /path/to/skill/
```

Analyzes existing content, prompts for missing tags, migrates structure. Does NOT generate stub files — if the skill lacks substantive content to meet enterprise minimums, it FAILs and reports what real content the author needs to add.

### `scripts/test_script.py` — Script Functionality

Syntax check + shebang check + docstring check + manual execution.

### `scripts/verify_sources.py` — External Source Verification

Extracts URLs from refs + SKILL.md; if an external tool is referenced with no docs URL, probes a handful of guessed URL patterns (`github.com/<slug>`, `npmjs.com/package/<slug>`, `pypi.org/project/<slug>`, `docs.<slug>.com`) with a HEAD request — this is a heuristic guess-and-probe, not a real web search, and a reachable guessed URL is reported as an unverified *candidate*, not confirmed official documentation. FAILS if nothing is found.

### `scripts/analyze_skill.py` — Analysis (read-only)

Structure compliance, content quality, redundancy, cross-reference completeness.

### `scripts/consolidate_skills.py` — Merge

Merges two or more skill directories, resolving conflicts. Interactive.

### `scripts/detect_redundancy.py` — Redundancy Scan

Finds overlapping functionality, duplicate content, similar scripts across a skills tree.

### `scripts/skill_root.py` — Skill-Root Discovery

Shared discovery used by the whole toolchain: resolves any path up to its true skill root (nearest ancestor with a root SKILL.md), scans a tree for skill roots without descending into found skills, and reports nested SKILL.md violations. Read-only.

### `scripts/scan_report.py` — Multi-Root Scan, Batch Validate, Diff, Report

```bash
python3 scripts/scan_report.py --root /path/to/skills
python3 scripts/scan_report.py --root /source/skills --diff-target /target/skills
python3 scripts/scan_report.py --root /path/to/skills --fix --json
```

Tree-wide layer on top of `skill_root.py` (discovery) and `validate.py` (the same
validator every other script uses — never a forked copy): validates every skill under
one or more roots, optionally diffs skill names between a source and target tree,
optionally runs `auto_fix.py` on failures, and emits a consolidated report. This is what
used to require a separate downstream skill for multi-directory audits — that capability
now lives here. See `references/scan-report.md`.

### `scripts/skill_enhance.py` — Pipeline Orchestrator

```bash
python3 scripts/skill_enhance.py create --name my-skill --tier enterprise
python3 scripts/skill_enhance.py update --path ./existing-skill --tier enterprise
```

Sequences the full 11-step pipeline: scaffold → gate SKILL.md → gate scripts/ → gate references/ → validate → auto_fix → re-validate → test → verify sources → package → extract-verify. This is the only sanctioned path for creating or updating a skill — however small the change. Individual steps remain directly invokable (each is a real, independent script) for debugging and inspection, but running them piecemeal instead of through `skill_enhance.py` skips the enforced gate sequence and is never a substitute for it.

---

## Compatibility + Cost

Works with any LLM/agent runtime that can execute Python stdlib scripts. See the `skill-installer` skill for platform-specific install steps.

Cost: Python stdlib only — no pip installs, no paid services required.

---

## Downstream Callers

This skill's `validate.py` is the single source of truth. Downstream skills consume it one of two ways — never by forking:

- **Live delegation** — locate this skill and subprocess-call `scripts/validate.py`. Freshest rules, preferred when both skills are installed.
- **Bundled byte-identical copy** — a downstream skill may ship an exact copy of `validate.py` (+ `skill_root.py`) inside its own `scripts/` so it works standalone, without forcing users to install two skills. `skill-installer` does this.

Current downstream callers:

- `skill-installer` — live delegation when this skill is present, bundled copy otherwise (`--basic` gate before installing)

Multi-directory scan/validate/audit (previously a separate downstream skill) is now
native to this skill — see `scripts/scan_report.py` above. There is no separate "pro"
validator anywhere; `validate.py` is the only one.

When updating this skill, downstream copies get overwritten from here (byte-identical, hash-verifiable). Do not fork; do not edit a copy in place.

---

## Key References

- `references/skill-anatomy.md` — full structural reference
- `references/packaging.md` — packaging conventions + version discipline
- `references/standards.md` — enterprise validation rules + the full skill-responsibility model
- `references/source-verification.md` — external source rules
- `references/error-handling.md` — error report formats
- `references/output-patterns.md` — JSON output schema
- `references/consolidation-patterns.md` — merge patterns
- `references/agnostic-rules.md` — platform-agnostic requirements
- `references/free-first-strategy.md` — when a skill *does* consume paid services, prefer free before paid
- `references/workflows.md` — end-to-end create + update pipelines
- `references/scan-report.md` — multi-root scan/validate/diff/report usage

### Lessons (`references/lessons/`)

Real doctrines carried forward from prior sessions. Each file opens with structured YAML
frontmatter (`title`, `category`, `failure`, `root_cause`, `resolution`, `prevention`,
`date`, `verified`) — see any file for the schema.

- `references/lessons/validator-vs-content-rephrase-not-relax.md` — reword content, don't weaken the validator
- `references/lessons/validation.md` — session residue (raw transcripts, absolute paths) corrupts lesson files; distill, don't paste
- `references/lessons/skill-5-root-items.md` — 5 root items, no exceptions; `assets/` banned everywhere
- `references/lessons/look-before-writing.md` — read a file before diffing it
- `references/lessons/reject-self-declared-placeholders.md` — files that declare themselves PLACEHOLDER don't pass
- `references/lessons/verify-beyond-version.md` — newer version ≠ better; cross-verify with substance + validator + structure
- `references/lessons/version-guard-overwrites.md` — never overwrite a newer copy with an older one
- `references/lessons/always-scaffold-through-init.md` — always init via `__init__.py --scaffold`, never hand-craft — and the earliest on-record instance of the exact phantom-script doc-drift class this skill's validator now catches
- `references/lessons/import-full-tree-not-selective.md` — "copy over" means whole tree, not cherry-pick
- `references/lessons/chain-enforcement-integration.md` — how the 11-gate pipeline was first chain-locked (historical: superseded by built-in `scripts/chain.py`)
- `references/lessons/federation-gateway-skills.md` — coordination-gateway skill scaffolding lessons (server stability, health endpoints)

---

## Enhancement Hooks

| Skill | When to add |
|---|---|
| `html-report` | Auditing 10+ skills at once |
| `xlsx` | Tracking skill quality over time |
| `docx` | Delivering audits to stakeholders |
