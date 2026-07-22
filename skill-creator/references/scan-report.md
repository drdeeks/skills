# scan_report.py — multi-root scan, batch validate, diff, report

Tree-wide layer on top of the single-skill `validate.py`/`auto_fix.py`. Absorbs what a
separate "skill-scan-validate-resolver" skill used to do as an external dependency:
walk one or more root directories for skill dirs, validate every one found with the
SAME validator every other script in this toolchain uses, optionally diff skill names
across sources, optionally auto-fix failures, and emit a consolidated report.

## When to use it

- Auditing an entire skills directory at once (not just one skill)
- Comparing which skills exist in one source tree but not another (e.g. a USB import
  vs. the live skills directory) before deciding what to merge
- Batch-repairing structural issues across many skills in one pass

For single-skill work, use `skill_enhance.py` — this script is for operating across
many skills at once, not for authoring or editing any individual one.

## Usage

```bash
# Scan and validate every skill under one root
python3 scripts/scan_report.py --root /path/to/skills

# Scan multiple roots at once (a skill found under more than one root is
# reported once)
python3 scripts/scan_report.py --root /path/a --root /path/b

# Report skill names present in the source root(s) but missing from a target
python3 scripts/scan_report.py --root /source/skills --diff-target /target/skills

# Auto-fix structural failures, then re-validate (dry-run first to preview)
python3 scripts/scan_report.py --root /path/to/skills --fix --dry-run
python3 scripts/scan_report.py --root /path/to/skills --fix

# Basic (production) tier instead of enterprise; machine-readable output
python3 scripts/scan_report.py --root /path/to/skills --basic --json
```

## What it reuses (never forks)

- `skill_root.py`'s `find_skills()` for tree discovery (skips cache/VCS dirs, never
  descends into a found skill looking for nested ones)
- `validate.py`'s `validate_skill()` for every per-skill verdict — the single source of
  truth every script in this toolchain shares
- `auto_fix.py`'s `auto_fix_skill()` when `--fix` is passed

## Output shape

JSON output follows the `operation`/`timestamp`/`status`/`details` convention used by
`package_skills.py`. `details.results` is a list of per-skill verdicts (`skill`, `path`,
`root`, `valid`, `status`, `fails`, `warnings`, `issues`, `fixes_applied`).
`details.diff` (only present with `--diff-target`) has `missing_from_target` and
`extra_in_target`.
