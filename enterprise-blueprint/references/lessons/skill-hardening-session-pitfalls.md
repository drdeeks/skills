---
title: Enterprise-Blueprint Skill Hardening — Session Pitfalls (v1.0.4-v1.0.6)
category: skill-hardening
date: 2026-07-06
failure: >
  Across the v1.0.4-v1.0.6 hardening sessions, enterprise-blueprint repeatedly
  failed enterprise validation and functional testing for a recurring set of
  reasons: hardcoded paths, missing --help handlers, chain-name filesystem
  overflow on long project names, argparse flag-abbreviation collisions,
  subprocess positional-vs-keyword argument mixups, and re-init refusing to
  overwrite existing chain state.
root_cause: >
  Path resolution, CLI argument handling, and chain-state lifecycle were each
  implemented ad hoc per script rather than following one shared, tested
  convention across the whole skill.
resolution: >
  Standardized fixes applied per class of bug: hardcoded paths replaced with
  ${USB_MOUNT}/$HOME placeholders; every script given a --help handler at the
  top of main(); chain names sanitized (strip non-alphanumeric, spaces->dashes,
  hard-cap 80 chars) via one shared _chain_name(data) function used by every
  subcommand; explicit full flag names used in subprocess calls to avoid
  argparse's allow_abbrev auto-matching the wrong longer flag; --root always
  passed as a keyword, never positional; generate_checklist.py's create_chain()
  globs and deletes stale .chain/<name>.json + .log before calling
  chain.py create, so re-init never hits "Chain already exists".
prevention: >
  Every release runs the full skill_enhance.py enterprise pipeline (11 gates,
  0 FAIL) before being considered done. New scripts must: check --help first
  in main(), resolve all paths via env var -> Path.home() default -> sibling
  fallback (never a bare literal), pass subprocess flags by full name never
  abbreviated, and re-init logic must always clear prior chain state rather
  than assuming a fresh start.
verified: true
---

# Enterprise Blueprint — Skill Hardening Session Pitfalls

Consolidated from the v1.0.4 through v1.0.6 hardening sessions.

## Pitfalls Encountered (v1.0.4 + cumulative)

- **Hardcoded paths**: Session-specific paths (`${USB_MOUNT}` or `$HOME`) in reference docs trigger validator warnings — use placeholders
- **Missing reference links**: Every file in `references/` MUST be linked in SKILL.md references section
- **Duplicate sections**: Duplicate headers (e.g., "## Pitfalls" appearing twice) trigger warnings
- **Cached bytecode**: `scripts/__pycache__/` triggers structural violations — clean before validation
- **Missing --help handlers**: Scripts without `--help` that exits 0 fail test_script gate
- **Placeholder text in SKILL.md body**: Example text mentioning banned patterns (e.g., "Placeholder checkboxes", "T0DO markers") triggers validator FAIL — remove or rephrase
- **Template permissions**: Templates in `references/templates/` must be chmod 0444 (auto-fixed by pipeline but slows it down)
- **Check all references before deleting/renaming a script**: `grep -rn "old_script_name"` across all scripts, `__init__.py`, SKILL.md, and references before removing or renaming. A deleted script that `__init__.py` or `apply_blueprint.py` references will break the skill entrypoint. Restoring a compat wrapper is a fix, not a prevention.
- **Chain name filesystem safety**: Chain names derived from `data.project_name` become filenames under `.chain/`. If the blueprint's `Project:` line is very long (100+ chars) or contains special characters (em-dashes, Unicode), the resulting filename can exceed the filesystem's NAME_MAX (typically 255 bytes) or PATH_MAX, producing `Errno 36: File name too long`. Always sanitize: strip non-alphanumeric chars, spaces→dashes, hard-cap at 80 chars. Use a shared `_chain_name(data)` function called by ALL subcommands that construct the chain name (init, status, phase, menu) so they stay consistent.
- **Argparse abbreviation trap (Python-specific)**: Python's `argparse` auto-abbreviates long flags by default (`allow_abbrev=True`). If you pass `--output /path/to/file` but the actual flag is `--output-dir`, argparse silently matches `--output` as an abbreviation for `--output-dir` and treats the intended file path as a directory path. This creates paths like `file/checklist.md` instead of `checklist.md`. Avoid ambiguous flag prefixes that match multiple longer flags. When calling a script from another script (`__init__.py` calling `generate_checklist.py`), explicitly pass the full flag name, not an abbreviated one.
- **Subprocess arg order**: When calling a script that accepts `--root` as a keyword argument, pass it as `--root /path`, not as a positional argument `/path`. Positional arguments are often consumed by positional-only parsers (e.g., test-runner.py uses the first positional for the test tier, not the project root). Always check the target script's `--help` before composing a subprocess call.
- **Consistent chain name across all subcommands**: If `create_chain()` uses a sanitized chain name but `status`/`phase`/`menu` subcommands construct the chain name from raw `data.project_name`, they'll look for a different file than what was created. Extract chain name building into a shared function and use it everywhere.
- **Re-init must clear old chain state**: `chain.py create` refuses to overwrite (`"error": "Chain already exists"`). The fix is to glob `.chain/<chain-name>.json` and `.log` before calling create. This is baked into `generate_checklist.py`'s `create_chain()` — always re-init via `generate_checklist.py --init` rather than calling `chain.py create` directly.

## Pitfall: `chain.py create` Doesn't Overwrite — Must Clear Old State

`chain.py create` (in loop-enforcer) refuses to overwrite. If you re-init, it returns `{"error": "Chain already exists"}`. The fix is baked into `generate_checklist.py`'s `create_chain()` — it globs `.chain/<chain-name>.json` and `.log` and deletes them before calling `chain.py create`. Always call `generate_checklist.py . --init` rather than calling `chain.py create` directly for this reason.

## Validator Implementation Pitfalls

1. **Never use `python3 validator.py`** — breaks shebang scripts. Run validator directly: `subprocess.run([validator_path, step_path])`
2. **Validators receive step file path** — must navigate to project root: `project_root = Path(step_path).parent.parent`
3. **All validators must be executable** — `chmod +x scripts/*.py` (and shell scripts)
4. **Exit codes = pass/fail** — 0 = pass, non-zero = fail. Stdout/stderr captured for output.
5. **No agent self-validation** — removed `auto-verify-complete` from `chain_worker.py` entirely
6. **Sanitize filenames** — em-dashes, colons break matching. Use `.replace('—', '').replace(':', '')` consistently
7. **Phase gate step index = num_steps + 1** — phase steps 1..N, gate at N+1. Lookup logic must match.
8. **Blueprint-driven validators are primary** — `blueprint_validator_gen.py` generates validators from Part VI tables; project-type registry is fallback only
9. **Validator generated per project** — each project gets its own validators in `.blueprint-chain/validators/` matching its blueprint's exact deliverables
10. **Part VI tables are the source of truth** — if blueprint has implementation tables, they drive validation; no project-type assumptions

## Session Summary (v1.0.6 Enterprise Validation)

See `references/lessons/chain-enforcement-lessons.md` for the chain-enforcement-integration-specific lessons (18 lessons). Key cross-cutting takeaways from this hardening pass:

1. **Agent/crew detection must be singular source of truth** (FOREVER SYSTEM §1) — `discover_agents.py` is THE canonical detector; all components delegate to it
2. **Path agnosticism requires env vars everywhere** — `LOOP_ENFORCER_ROOT`, `AGENT_WORKSPACE`, `ENFORCER_SOCKET`, ACK convention paths; no hardcoded paths anywhere
3. **Model tiering with flash/final pattern optimizes token cost** — iteration (flash) vs final (plus/max) per phase/task; `interactive_setup.py` generates versioned maps
4. **All chain enforcement routes through loop-enforcer** — no duplicate implementations; `__init__.py` delegates to `generate_checklist.py`; worker API is thin plugin
5. **Opt-out flag required** — `--no-loop-enforcement` generates checklist only, skips chain init
6. **Template configs essential** — versioned YAML templates prevent hand-written config drift
7. **Interactive setup prevents misconfiguration** — walks user through detection → template → per-phase models → task overrides → write + verify
8. **Dogfood validation via skill_enhance.py is non-negotiable** — 11 gates must pass (0 FAIL, warnings OK) on every release
