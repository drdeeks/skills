# Curated Skills Repository

**The canonical, version-tracked, self-enforcing source of truth for every curated skill maintained in this repository.**

This repository is not a loose folder of scripts. It is a governed skill library: every skill has passed an enforced validation and packaging workflow, is tracked by version, recorded in a verifiable manifest, and maintained through a consistent lifecycle.

Every skill is designed to be portable, self-describing, isolated, and reproducible across environments.

---

## Table of Contents

- [What this repository is](#what-this-repository-is)
- [Design philosophy](#design-philosophy)
- [Skill anatomy](#skill-anatomy)
- [The three-tool system](#the-three-tool-system)
- [Packaging](#packaging)
- [Validation](#validation)
- [Versioning and manifest](#versioning-and-manifest)
- [Git workflow](#git-workflow)
- [Skill catalog](#skill-catalog)
- [Tags and metadata](#tags-and-metadata)
- [Adding or updating a skill](#adding-or-updating-a-skill)
- [License](#license)

---

# What this repository is

This repository is the canonical source for curated, validated, and finalized skills.

It provides:

- A version-controlled registry of reusable skills.
- A consistent structure for every skill.
- Automated validation and packaging.
- Reproducible skill distribution.
- Integrity checks between source files, packages, and metadata.

Every finalized skill is maintained as an independent directory containing documentation, executable tools, references, and a distributable package.

---

# Design philosophy

Every skill follows the same principles:

| Principle | Description |
|---|---|
| **Portable** | Skills avoid machine-specific assumptions and work across environments. |
| **Path-agnostic** | No hardcoded user paths or environment-specific locations. |
| **Free-first** | Local execution is prioritized. External services are optional. |
| **Provider-neutral** | Skills describe compatibility without depending on one vendor. |
| **Isolated** | Skills avoid unexpected changes outside their own workspace. |
| **Diagnostic** | Tools provide structured output for automation and inspection. |
| **Self-verifying** | Metadata, packages, and source files remain consistent. |

---

# Skill anatomy

Every skill follows this structure:

```text
<skill-name>/
├── SKILL.md
├── __init__.py
├── scripts/
├── references/
└── <skill-name>.skill
```

## SKILL.md

The `SKILL.md` file defines the skill contract:

```yaml
---
name: <skill-name>
description: "What the skill does and when it should be used."
license: MIT
metadata:
  tags:
    - example
  providers:
    - any
version: 1.0.0
---
```

A skill must define:

- Identity
- Purpose
- Metadata
- Version
- Compatibility information

---

# The three-tool system

The lifecycle of a skill is managed through three independent tools.

| Tool | Purpose |
|---|---|
| skill-creator | Creates, validates, upgrades, and packages skills. |
| skill-installer | Installs finalized skill packages. |
| guardrail-enforcement | Maintains repository integrity and workflow enforcement. |

---

# skill-creator

The creation pipeline handles:

1. Skill updates.
2. Metadata validation.
3. Structure validation.
4. Automated fixes.
5. Script testing.
6. Packaging.
7. Extraction verification.

A skill is not considered complete until it passes validation.

---

# skill-installer

The installer handles finalized packages.

Responsibilities:

- Verify package integrity.
- Install skills without modifying source packages.
- Preserve reproducibility.
- Maintain consistent deployment.

---

# guardrail-enforcement

The enforcement layer maintains repository integrity.

Capabilities:

- Version tracking.
- Validation gates.
- Manifest verification.
- Change auditing.
- Workflow enforcement.
- Consistency checks.

---

# Packaging

Skills are distributed as:

```text
<skill-name>.skill
```

The packaging process:

1. Validates the skill.
2. Updates version information.
3. Creates the package.
4. Records metadata.
5. Verifies extracted contents.

The package must exactly match the source tree.

---

# Validation

Validation ensures every skill is:

## Structurally valid

Checks:

- Required files exist.
- Directory layout is correct.
- Scripts and references are organized properly.

## Metadata valid

Checks:

- Name.
- Description.
- License.
- Tags.
- Version.

## Portable

Checks:

- No hardcoded system paths.
- No hidden assumptions.
- No unnecessary dependencies.

## Operational

Checks:

- Scripts execute correctly.
- Documentation exists.
- References are usable.

---

# Versioning and manifest

Every skill uses semantic versioning:

```text
MAJOR.MINOR.PATCH
```

The repository manifest tracks:

- Current version.
- Previous versions.
- Package metadata.
- File information.
- Version history.

Every change remains traceable.

---

# Git workflow

The standard workflow:

```text
Create/update skill
        ↓
Validate
        ↓
Package
        ↓
Verify
        ↓
Update manifest
        ↓
Commit
        ↓
Push
```

Rollback is possible through normal Git history:

```bash
git checkout <previous-version>
```

---

# Skill catalog

Every skill entry contains:

- Name.
- Version.
- Purpose.
- Documentation.
- Scripts.
- References.
- Package archive.

Skills are maintained through the same validation lifecycle.

---

# Tags and metadata

Skills use metadata for discovery:

```yaml
metadata:
  tags:
    - category
    - capability
    - domain
  providers:
    - any
```

Metadata enables:

- Searching.
- Filtering.
- Compatibility checks.
- Automated discovery.

---

# Adding or updating a skill

Example:

```bash
python3 skill-creator/scripts/skill_enhance.py update \
  --path ./my-skill

python3 guardrail-enforcement/scripts/verify_manifest.py \
  --repo .

git add .
git commit -m "Update skill"
git push
```

---

# License

MIT.

Each skill declares its own license through its `SKILL.md` metadata.
