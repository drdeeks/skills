#!/usr/bin/env python3
"""
skill_enhance.py — public entry point for creating OR updating a skill.

Runs the full create/update pipeline as a straight orchestration of the
sibling scripts. Every script it calls is directly invokable by a human or
downstream tool; skill_enhance.py just sequences them into the standard
create/update flow.

Two modes:
  Interactive (default): step-by-step TUI. Blocks until each gate passes,
    shows a live checklist of what's still missing.
  Agent (--noninteractive): every gate reads from CLI flags or a manifest.

Tiers:
  --tier enterprise (default): 7 tags, 3+ scripts, 5+ refs, 100-1024 char desc
  --tier basic:                5 tags, 2+ scripts, 3+ refs, 100-1024 char desc

Pipeline (both create and update follow the same gates):

  1. SCAFFOLD       — if creating: call skill-creator/__init__.py scaffold()
                       to produce the canonical 5-item root layout
  2. FRONTMATTER    — poll SKILL.md until: no REPLACE_ME_* markers, tags
                       count >= tier-min, description 100-1024 chars
  3. SCRIPTS        — poll scripts/ until >= tier-min count, each substantive
  4. REFERENCES     — poll references/ until >= tier-min count, each substantive
  5. VALIDATE       — run validate.py (basic OR enterprise per --tier)
  6. AUTO-FIX       — run auto_fix.py to move stray files into correct dirs
  7. RE-VALIDATE    — run validate.py again to confirm auto-fix cleaned up
  8. TEST SCRIPTS   — run test_script.py: syntax + shebang + dry-run
  9. VERIFY SOURCES — run verify_sources.py (read-only external check)
 10. PACKAGE        — run package_skills.py: bumps patch version, emits .skill
 11. EXTRACT-VERIFY — extract fresh .skill to /tmp, verify version bumped

Usage:
  # Interactive create
  python3 skill_enhance.py create --name my-skill --tier enterprise

  # Interactive update
  python3 skill_enhance.py update --path /path/to/my-skill

  # Agent-mode create (no prompts)
  python3 skill_enhance.py create --name my-skill --tier enterprise \\
      --noninteractive --manifest ./manifest.json

  # Agent-mode update (assumes edits already made to path)
  python3 skill_enhance.py update --path ./my-skill --noninteractive
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
sys.dont_write_bytecode = True  # keep __pycache__ out of skill trees
import tempfile
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent.resolve()
SKILL_CREATOR_ROOT = SCRIPT_DIR.parent
VALIDATE = SCRIPT_DIR / "validate.py"
AUTO_FIX = SCRIPT_DIR / "auto_fix.py"
PACKAGE = SCRIPT_DIR / "package_skills.py"
TEST_SCRIPT = SCRIPT_DIR / "test_script.py"
VERIFY_SOURCES = SCRIPT_DIR / "verify_sources.py"

# Tier gate minimums (mirrors validate.py — kept in sync)
TIER_MINS = {
    "enterprise": {"tags": 7, "scripts": 3, "references": 5},
    "basic":      {"tags": 5, "scripts": 2, "references": 3},
}


# ─── ANSI helpers (stdlib only, no rich/curses dependency) ────────────────

def _tty(): return sys.stdout.isatty()

class C:
    G = "\033[32m" if _tty() else ""
    R = "\033[31m" if _tty() else ""
    Y = "\033[33m" if _tty() else ""
    B = "\033[1m"  if _tty() else ""
    D = "\033[2m"  if _tty() else ""
    X = "\033[0m"  if _tty() else ""


def step(n, total, msg): print(f"{C.B}[{n}/{total}]{C.X} {msg}")
def ok(msg):   print(f"  {C.G}✓{C.X} {msg}")
def fail(msg): print(f"  {C.R}✗{C.X} {msg}", file=sys.stderr)
def info(msg): print(f"  {C.D}·{C.X} {msg}")
def warn(msg): print(f"  {C.Y}⚠{C.X} {msg}")


# ─── Frontmatter / substance helpers ──────────────────────────────────────

def read_frontmatter(skill_md: Path) -> dict:
    """Simple frontmatter reader that doesn't require yaml."""
    try:
        text = skill_md.read_text(encoding="utf-8")
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return {}
    end = 1
    while end < len(lines) and lines[end].strip() != "---":
        end += 1
    fm_text = "\n".join(lines[1:end])
    try:
        import yaml
        d = yaml.safe_load(fm_text) or {}
        return d if isinstance(d, dict) else {}
    except Exception:
        # Naive line-by-line
        out = {}
        for line in fm_text.split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                out[k.strip()] = v.strip()
        return out


def has_replace_me_markers(skill_md: Path) -> bool:
    try:
        return "REPLACE_ME" in skill_md.read_text(encoding="utf-8")
    except OSError:
        return True


def count_substantive_files(dir_path: Path, min_bytes: int = 200) -> int:
    """Count files with >= min_bytes of non-whitespace content, ignoring
    empty files and dotfiles. Recursive."""
    if not dir_path.is_dir():
        return 0
    count = 0
    for p in dir_path.rglob("*"):
        if not p.is_file():
            continue
        if p.name.startswith("."):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        stripped = "".join(text.split())
        if len(stripped) >= min_bytes:
            count += 1
    return count


# ─── Gate polling (blocking, with visual checklist) ───────────────────────

def gate_frontmatter(skill_dir: Path, mins: dict, interactive: bool) -> bool:
    """Blocking poll until SKILL.md is filled in."""
    skill_md = skill_dir / "SKILL.md"
    while True:
        problems = []
        if not skill_md.exists():
            problems.append("SKILL.md does not exist yet")
        else:
            fm = read_frontmatter(skill_md)
            if has_replace_me_markers(skill_md):
                problems.append("SKILL.md still contains REPLACE_ME_* markers")
            desc = str(fm.get("description", "")).strip()
            if len(desc) < 100:
                problems.append(f"description too short ({len(desc)} chars; need >= 100)")
            elif len(desc) > 1024:
                problems.append(f"description too long ({len(desc)} chars; need <= 1024)")
            meta = fm.get("metadata", {}) or {}
            tags = meta.get("tags", []) if isinstance(meta, dict) else []
            if not isinstance(tags, list): tags = []
            if len(tags) < mins["tags"]:
                problems.append(f"tags: have {len(tags)}, need >= {mins['tags']}")
        if not problems:
            ok(f"SKILL.md filled in ({mins['tags']}+ tags, description ok, no REPLACE_ME left)")
            return True
        if not interactive:
            for p in problems: fail(p)
            return False
        # Interactive: repaint status
        os.write(1, b"\x1b[2K\r")  # clear line
        info(f"waiting on SKILL.md — {len(problems)} thing(s) missing:")
        for p in problems:
            info(f"    · {p}")
        info("(edit the file; this gate rescans every 2s)")
        time.sleep(2)
        # Move cursor back up to overwrite
        os.write(1, ("\x1b[" + str(len(problems) + 2) + "A").encode())
        os.write(1, b"\x1b[J")


def gate_scripts(skill_dir: Path, mins: dict, interactive: bool) -> bool:
    scripts = skill_dir / "scripts"
    while True:
        count = count_substantive_files(scripts, min_bytes=100)
        if count >= mins["scripts"]:
            ok(f"scripts/ has {count} substantive script(s) (need >= {mins['scripts']})")
            return True
        if not interactive:
            fail(f"scripts/ has {count}, need >= {mins['scripts']}")
            return False
        info(f"waiting on scripts/ — have {count}, need >= {mins['scripts']}")
        time.sleep(2)
        os.write(1, b"\x1b[1A\x1b[K")


def gate_references(skill_dir: Path, mins: dict, interactive: bool) -> bool:
    refs = skill_dir / "references"
    while True:
        count = count_substantive_files(refs, min_bytes=200)
        if count >= mins["references"]:
            ok(f"references/ has {count} substantive doc(s) (need >= {mins['references']})")
            return True
        if not interactive:
            fail(f"references/ has {count}, need >= {mins['references']}")
            return False
        info(f"waiting on references/ — have {count}, need >= {mins['references']}")
        time.sleep(2)
        os.write(1, b"\x1b[1A\x1b[K")


# ─── Child invocations ────────────────────────────────────────────────────

def run(script: Path, args: list, cwd: Path = None) -> int:
    r = subprocess.run([sys.executable, str(script), *args],
                       cwd=str(cwd) if cwd else None)
    return r.returncode


# ─── Scaffold via skill-creator's __init__.py ─────────────────────────────

def scaffold_skill(name: str, parent_dir: Path) -> Path:
    """Call skill-creator/__init__.py's scaffold(). Returns dest path."""
    creator_init = SKILL_CREATOR_ROOT / "__init__.py"
    sys.path.insert(0, str(SKILL_CREATOR_ROOT))
    import importlib.util
    spec = importlib.util.spec_from_file_location("_sc", str(creator_init))
    sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)
    result = sc.scaffold(name, parent_dir, force=True, tier="enterprise")
    return Path(result["path"])


# ─── Extract-verify ──────────────────────────────────────────────────────

def extract_and_verify(skill_dir: Path, expected_min_version: str) -> bool:
    """Extract <skill_dir>/<name>.skill to a temp dir, verify version bumped,
    root layout intact, and every archived file hash-identical to its source
    on disk (no mutations). Remove the extract on success."""
    import hashlib

    name = skill_dir.name
    archive = skill_dir / f"{name}.skill"
    if not archive.is_file():
        fail(f"no .skill archive found at {archive}")
        return False
    workdir = Path(tempfile.mkdtemp(prefix=f"verify-{name}-"))
    try:
        with zipfile.ZipFile(archive) as z:
            z.extractall(workdir)
        # Find the extracted SKILL.md
        candidates = list(workdir.rglob("SKILL.md"))
        if not candidates:
            fail("no SKILL.md inside extracted archive")
            return False
        fm = read_frontmatter(candidates[0])
        got_version = str(fm.get("version", "")).strip()
        if not got_version:
            fail("extracted SKILL.md has no version")
            return False
        # Verify version >= expected_min_version
        def _tup(v):
            return tuple(int(x) for x in v.split(".") if x.isdigit())
        if _tup(got_version) < _tup(expected_min_version):
            fail(f"extracted version {got_version} < expected {expected_min_version}")
            return False
        # Verify canonical root files exist
        skill_root = candidates[0].parent
        for required in ("SKILL.md", "__init__.py", "scripts", "references"):
            if not (skill_root / required).exists():
                fail(f"extracted archive missing {required}")
                return False
        # Hash-compare every archived file against its on-disk source —
        # proves the pack introduced no mutations.
        def _sha(p: Path) -> str:
            h = hashlib.sha256()
            h.update(p.read_bytes())
            return h.hexdigest()
        mismatched = []
        for extracted in skill_root.rglob("*"):
            if not extracted.is_file():
                continue
            rel = extracted.relative_to(skill_root)
            source = skill_dir / rel
            if not source.is_file():
                mismatched.append(f"{rel} (missing on disk)")
            elif _sha(extracted) != _sha(source):
                mismatched.append(str(rel))
        if mismatched:
            fail(f"archive/source hash mismatch: {', '.join(mismatched[:5])}"
                 + (f" … +{len(mismatched)-5} more" if len(mismatched) > 5 else ""))
            return False
        ok(f"extracted archive verified — version={got_version}, root layout "
           "intact, all file hashes match source (no mutations)")
        return True
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


# ─── Main pipeline ───────────────────────────────────────────────────────

def run_pipeline(cmd: str, args) -> int:
    tier = args.tier
    mins = TIER_MINS[tier]
    interactive = not args.noninteractive

    # Decide the skill dir
    if cmd == "create":
        # Scaffold under the target parent dir
        default_parent = Path.home() / "Downloads" / "curated_skills"
        parent = Path(args.path or default_parent).resolve()
        parent.mkdir(parents=True, exist_ok=True)
        step(1, 11, f"Scaffold {args.name} at {parent}")
        skill_dir = scaffold_skill(args.name, parent)
        ok(f"scaffolded {skill_dir}")
    else:  # update
        skill_dir = Path(args.path).resolve()
        if not (skill_dir / "SKILL.md").exists():
            fail(f"{skill_dir} has no SKILL.md — is this a skill dir?")
            return 1
        step(1, 11, f"Update {skill_dir.name}")
        ok(f"targeting {skill_dir}")

    step(2, 11, f"Gate: SKILL.md frontmatter ({tier})")
    if not gate_frontmatter(skill_dir, mins, interactive):
        return 2

    step(3, 11, f"Gate: scripts/ ({mins['scripts']}+ substantive)")
    if not gate_scripts(skill_dir, mins, interactive):
        return 3

    step(4, 11, f"Gate: references/ ({mins['references']}+ substantive)")
    if not gate_references(skill_dir, mins, interactive):
        return 4

    step(5, 11, "Run validate.py (initial status — informational)")
    v_args = [str(skill_dir)] + (["--basic"] if tier == "basic" else [])
    initial_rc = run(VALIDATE, v_args)
    if initial_rc != 0:
        info("initial validation has fails — auto_fix runs next, then the "
             "re-validation is the hard gate")

    step(6, 11, "Run auto_fix.py (safe moves only, never deletes)")
    rc = run(AUTO_FIX, [str(skill_dir)])
    if rc != 0:
        fail(f"auto_fix.py exited {rc}")
        return 6

    step(7, 11, "Re-validate after auto-fix (HARD GATE)")
    rc = run(VALIDATE, v_args)
    if rc != 0:
        fail(f"skill fails {tier} tier after auto-fix — rename/complete the "
             "flagged items and rerun (auto-fix cannot pick names or write "
             "content for you)")
        return 7

    step(8, 11, "Run test_script.py (syntax + shebang + --help; BLOCKING)")
    if TEST_SCRIPT.exists():
        rc = run(TEST_SCRIPT, [str(skill_dir)])
        if rc != 0:
            fail(f"test_script.py exited {rc} — every script must pass "
                 "before packaging (core loop rule)")
            return 8

    step(9, 11, "Run verify_sources.py (external source check)")
    if VERIFY_SOURCES.exists():
        rc = run(VERIFY_SOURCES, [str(skill_dir)])
        if rc != 0:
            warn(f"verify_sources.py exited {rc} — continuing (non-blocking)")

    step(10, 11, "Package skill (package_skills.py)")
    # Read pre-package version
    fm_before = read_frontmatter(skill_dir / "SKILL.md")
    version_before = str(fm_before.get("version", "0.0.0"))
    rc = run(PACKAGE, [
        "--skills-root", str(skill_dir.parent),
        "--skill", skill_dir.name,
    ])
    if rc != 0:
        fail(f"package_skills.py exited {rc}")
        return 10
    fm_after = read_frontmatter(skill_dir / "SKILL.md")
    version_after = str(fm_after.get("version", "0.0.0"))
    ok(f"packaged: version {version_before} → {version_after}")

    step(11, 11, "Extract-verify the fresh .skill archive")
    if not extract_and_verify(skill_dir, version_after):
        return 11

    ok(f"{skill_dir.name} {tier}-tier pipeline complete")
    return 0


def main():
    ap = argparse.ArgumentParser(
        description="Public entry point for creating or updating a skill.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_create = sub.add_parser("create", help="Scaffold + author a new skill")
    ap_create.add_argument("--name", required=True, help="Skill name (hyphen-case)")
    ap_create.add_argument("--path", help="Parent dir (default: ~/Downloads/curated_skills)")
    ap_create.add_argument("--tier", choices=["enterprise", "basic"], default="enterprise")
    ap_create.add_argument("--noninteractive", action="store_true",
                           help="Agent mode — no prompts; every gate reads flags/manifest")

    ap_update = sub.add_parser("update", help="Update an existing skill through the pipeline")
    ap_update.add_argument("--path", required=True, help="Path to the existing skill dir")
    ap_update.add_argument("--tier", choices=["enterprise", "basic"], default="enterprise")
    ap_update.add_argument("--noninteractive", action="store_true")

    args = ap.parse_args()
    sys.exit(run_pipeline(args.cmd, args))


if __name__ == "__main__":
    main()
