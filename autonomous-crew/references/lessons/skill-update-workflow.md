---
title: Skill Update Workflow — Use skill_enhance.py, Never Raw Patch
category: workflow
date: 2026-07-09
failure: >
  Skills were updated via a raw text-patch operation that only edits files
  and never runs validation, so structurally broken or non-enterprise-tier
  skills were silently left in that state after an "update."
root_cause: >
  No enforced workflow tied skill edits to re-validation; editing and
  validating were two independent, easily-skipped steps.
resolution: >
  Standardized on skill_enhance.py update --tier enterprise --noninteractive
  as the only sanctioned update path — it runs the full 11-gate pipeline
  (frontmatter, scripts, references, validation, auto-fix, re-validation,
  script testing, packaging) after every edit.
prevention: >
  Treat "if the user mentions skill_manage or raw patching" as a stop
  signal to switch to skill_enhance.py immediately, and never consider a
  skill edit done until the full pipeline has been re-run.
verified: true
---

# Skill Update Workflow — CRITICAL

## NEVER use skill_manage(action='patch') to update skills

This is the #1 mistake that causes frustration. `skill_manage(action='patch')` only edits text — it does NOT run validation.

## Correct Workflow

```bash
# 1. Edit skill files (write_file, patch, etc.)
# 2. Run skill_enhance.py update
python3 <skill-creator-path>/scripts/skill_enhance.py update \
  --path <skill-path> \
  --tier enterprise \
  --noninteractive

# 3. Verify all 11 gates pass
```

## What skill_enhance.py Enforces

- Frontmatter validation (7+ tags, description)
- Script validation (3+ substantive, syntax, shebang, --help)
- Reference validation (5+ substantive, cross-references)
- Enterprise rules (58+ checks)
- Version bump
- Packaging

## User Correction Signal

If the user says anything about "use enhance script" or "stop using skill_manage", STOP and switch to skill_enhance.py immediately.
