#!/usr/bin/env python3
"""
Script functionality testing — syntax, shebang, docstring, help-surface, and
dry-run capability checks for every script in a skill's scripts/ directory.

Safety contract:
  - NEVER executes a script bare (a mutating script run with no args could
    change real state). Execution is limited to `--help`, in an isolated
    temporary working directory, with a timeout.
  - Checks syntax per language: py_compile for .py, `bash -n` for .sh.
  - Reports (as a warning, not a failure) scripts that expose no --dry-run
    flag, per the project rule that every mutating script should support one.

Usage:
    python3 test_script.py <skill_dir_or_scripts_dir> [--json] [--dry-run]
"""
import argparse
import json
import re
import subprocess
import sys
sys.dont_write_bytecode = True  # never litter skills with __pycache__ (validator FAIL)
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

RUN_TIMEOUT = 30
TESTABLE_EXTS = {".py", ".sh", ".bat", ".ps1", ".js", ".mjs", ".cjs", ".ts"}


def check_syntax(script_path: Path) -> Tuple[bool, List[str]]:
    """Language-appropriate syntax check."""
    issues = []
    ext = script_path.suffix.lower()
    if ext == ".py":
        # builtin compile() checks syntax WITHOUT writing a __pycache__
        # bytecode file into the skill tree (py_compile does, and the
        # validator rightly flags that as a junk dir)
        try:
            source = script_path.read_text(encoding="utf-8", errors="replace")
            compile(source, str(script_path), "exec")
        except SyntaxError as e:
            issues.append(f"Syntax error: line {e.lineno}: {e.msg}")
        except Exception as e:
            issues.append(f"Syntax check failed: {e}")
    elif ext == ".sh":
        try:
            r = subprocess.run(["bash", "-n", str(script_path)],
                               capture_output=True, text=True, timeout=RUN_TIMEOUT)
            if r.returncode != 0:
                issues.append(f"Syntax error: {r.stderr.strip()[:200]}")
        except FileNotFoundError:
            pass  # no bash on this platform — skip, don't fail
        except subprocess.TimeoutExpired:
            issues.append("bash -n timed out")
    # Other extensions: no reliable local syntax checker — structural checks only
    return len(issues) == 0, issues


def check_shebang(script_path: Path) -> Tuple[bool, List[str]]:
    issues = []
    if script_path.suffix.lower() in {".bat", ".ps1", ".exe"}:
        return True, []  # Windows formats don't use shebangs
    try:
        first_line = script_path.read_text(
            encoding="utf-8", errors="replace").splitlines()[0].strip()
    except (OSError, IndexError):
        return False, ["Empty file or unreadable"]
    if not first_line.startswith("#!"):
        issues.append("Missing shebang")
    elif not any(k in first_line for k in ("python", "bash", "sh", "node", "env")):
        issues.append(f"Unrecognized shebang: {first_line}")
    return len(issues) == 0, issues


def check_docstring(script_path: Path) -> Tuple[bool, List[str]]:
    """Python: module docstring. Shell: leading comment block."""
    issues = []
    ext = script_path.suffix.lower()
    try:
        text = script_path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return False, [f"Unreadable: {e}"]
    if ext == ".py":
        try:
            import ast
            doc = ast.get_docstring(ast.parse(text))
            if not doc:
                issues.append("Missing module-level docstring")
            elif len(doc.strip()) < 20:
                issues.append("Docstring too short (< 20 chars)")
        except SyntaxError:
            pass  # syntax check reports this
    elif ext == ".sh":
        lines = text.splitlines()[1:6]
        if not any(l.strip().startswith("#") and len(l.strip()) > 3 for l in lines):
            issues.append("No header comment describing the script's purpose")
    return len(issues) == 0, issues


def check_dry_run_support(script_path: Path) -> bool:
    """Does the script expose a --dry-run flag (project convention)?"""
    try:
        text = script_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return bool(re.search(r"--dry[-_]run|DRY_RUN", text))


def check_version_flag(script_path: Path) -> bool:
    """Does the script expose a --version flag? Not yet a hard project
    convention (unlike --dry-run) — reported as a warning, not a failure."""
    try:
        text = script_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return bool(re.search(r"--version", text))


def run_invalid_input(script_path: Path) -> Tuple[bool, List[str]]:
    """Invoke the script with one deliberately-bad positional argument (a
    nonexistent path) and require a CLEAN failure: nonzero exit, no raw
    Python traceback. This is generic across every script's CLI shape —
    either the script's own path validation rejects it cleanly, or argparse
    itself rejects an unexpected/invalid argument cleanly; both satisfy the
    same invariant (bad input never crashes with a traceback). Never runs
    bare — same isolated-temp-cwd, timeout, non-mutating contract as --help."""
    script_path = script_path.resolve()
    ext = script_path.suffix.lower()
    if ext == ".py":
        cmd = [sys.executable, str(script_path),
               "/nonexistent/skill-creator-test-fixture-path-does-not-exist"]
    elif ext == ".sh":
        cmd = ["bash", str(script_path),
               "/nonexistent/skill-creator-test-fixture-path-does-not-exist"]
    else:
        return True, []
    issues = []
    with tempfile.TemporaryDirectory(prefix="skilltest-invalid-") as tmp:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True,
                               timeout=RUN_TIMEOUT, cwd=tmp)
            output = (r.stdout + r.stderr).strip()
            if r.returncode == 0:
                issues.append(
                    "exited 0 on a nonexistent path — should fail clearly"
                )
            if "Traceback (most recent call last)" in output:
                issues.append(
                    f"raw Python traceback leaked on bad input: {output[-200:]}"
                )
        except subprocess.TimeoutExpired:
            issues.append(f"invalid-input run timed out after {RUN_TIMEOUT}s")
        except FileNotFoundError as e:
            issues.append(f"Interpreter unavailable: {e}")
        except Exception as e:
            issues.append(f"Execution failed: {e}")
    return len(issues) == 0, issues


def run_help(script_path: Path) -> Tuple[bool, List[str], str]:
    """Invoke `<script> --help` in an isolated temp cwd. Never runs bare."""
    script_path = script_path.resolve()  # cwd is a temp dir — path must be absolute
    ext = script_path.suffix.lower()
    if ext == ".py":
        cmd = [sys.executable, str(script_path), "--help"]
    elif ext == ".sh":
        cmd = ["bash", str(script_path), "--help"]
    else:
        return True, [], ""  # no safe generic runner — skip execution
    issues = []
    output = ""
    with tempfile.TemporaryDirectory(prefix="skilltest-") as tmp:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True,
                               timeout=RUN_TIMEOUT, cwd=tmp)
            output = (r.stdout + r.stderr).strip()
            # Accept rc 0, or a nonzero rc that still printed usage text
            # (argparse exits 2 for unknown flag but proves the script loads)
            if r.returncode != 0 and not re.search(r"usage|help|options",
                                                   output, re.I):
                issues.append(
                    f"--help exited {r.returncode} with no usage text: "
                    f"{output[:200]}"
                )
        except subprocess.TimeoutExpired:
            issues.append(f"--help timed out after {RUN_TIMEOUT}s")
        except FileNotFoundError as e:
            issues.append(f"Interpreter unavailable: {e}")
        except Exception as e:
            issues.append(f"Execution failed: {e}")
    return len(issues) == 0, issues, output


def test_script(script_path: Path) -> Dict:
    all_issues, warnings = [], []

    ok, issues = check_syntax(script_path)
    if not ok:
        all_issues.extend(f"Syntax: {i}" for i in issues)

    ok, issues = check_shebang(script_path)
    if not ok:
        all_issues.extend(f"Shebang: {i}" for i in issues)

    ok, issues = check_docstring(script_path)
    if not ok:
        all_issues.extend(f"Docstring: {i}" for i in issues)

    ok, issues, output = run_help(script_path)
    if not ok:
        all_issues.extend(f"Runtime: {i}" for i in issues)

    ok, issues = run_invalid_input(script_path)
    if not ok:
        all_issues.extend(f"Invalid-input: {i}" for i in issues)

    if not check_dry_run_support(script_path):
        warnings.append("No --dry-run flag detected (project convention "
                        "for mutating scripts)")

    if not check_version_flag(script_path):
        warnings.append("No --version flag detected")

    return {
        "script": script_path.name,
        "passed": len(all_issues) == 0,
        "issues": all_issues,
        "warnings": warnings,
        "help_output": output[:300],
    }


def test_fixture_pipeline(skill_dir: Path) -> Dict:
    """Build a synthetic skill using THIS skill's own scaffolder, then run
    validate.py / auto_fix.py / package_skills.py against it and assert
    concrete, specific outcomes — not just 'the process exited 0'.

    Scoped to skill-creator's own domain: its scripts operate on skill
    directories, so a scaffolded skill directory is the natural fixture.
    Skips cleanly (not a failure) if `skill_dir` isn't skill-creator itself
    (no scaffold() capability, or missing one of the three scripts tested).
    """
    init_py = skill_dir / "__init__.py"
    scripts_dir = skill_dir / "scripts"
    required = ("validate.py", "auto_fix.py", "package_skills.py")
    if not init_py.is_file() or not all((scripts_dir / r).is_file() for r in required):
        return {"fixture_pipeline": False, "skipped": True,
                "reason": "target is not skill-creator's own toolchain shape "
                          "(missing __init__.py scaffold() or one of "
                          + ", ".join(required) + ")"}

    import importlib.util
    spec = importlib.util.spec_from_file_location("_sc_fixture", str(init_py))
    sc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sc)
    if not hasattr(sc, "scaffold"):
        return {"fixture_pipeline": False, "skipped": True,
                "reason": "__init__.py has no scaffold() function"}

    sys.path.insert(0, str(scripts_dir))
    import validate as _validate
    import auto_fix as _auto_fix
    import package_skills as _package_skills

    checks = []
    with tempfile.TemporaryDirectory(prefix="skill-creator-fixture-") as tmp:
        tmp_path = Path(tmp)

        result = sc.scaffold("fixture-outcome-check", tmp_path, tier="enterprise")
        fixture = Path(result["path"])

        # 1. A freshly scaffolded skill (REPLACE_ME markers, empty scripts/
        #    references) must FAIL enterprise validation — proves validate.py
        #    actually catches an incomplete skill instead of rubber-stamping it.
        outcome = _validate.validate_skill(str(fixture))
        checks.append({
            "assertion": "freshly scaffolded skill fails enterprise validation",
            "passed": (not outcome["valid"]) and outcome["fails"] > 0,
            "detail": f"valid={outcome['valid']} fails={outcome['fails']}",
        })

        # 2. Plant a stray root .md file with real content; auto_fix must
        #    actually move it into references/ — proves auto_fix does what
        #    it claims, not just that the process exits 0.
        stray = fixture / "stray-note.md"
        stray.write_text("Real content for the fixture test, not a stub.\n" * 3,
                         encoding="utf-8")
        _auto_fix.auto_fix_skill(str(fixture))
        moved = (fixture / "references" / "stray-note.md").is_file()
        checks.append({
            "assertion": "auto_fix moves a stray root .md file into references/",
            "passed": moved and not stray.is_file(),
            "detail": f"moved={moved} original_gone={not stray.is_file()}",
        })

        # 3. Packaging must produce a real archive with a bumped version —
        #    proves package_skills.py does what it claims. It deliberately
        #    does NOT validate first (that's skill_enhance.py's job) — this
        #    fixture only asserts what package_skills.py itself is responsible for.
        packager = _package_skills.SkillPackager(tmp_path)
        pkg_result = packager.package_skill(fixture.name)
        archive = fixture / f"{fixture.name}.skill"
        checks.append({
            "assertion": "package_skills produces a .skill archive with a bumped version",
            "passed": (pkg_result.get("status") == "success" and archive.is_file()
                       and pkg_result.get("version_bumped") is True),
            "detail": f"status={pkg_result.get('status')} "
                      f"version={pkg_result.get('version')}",
        })

    passed = sum(1 for c in checks if c["passed"])
    return {
        "fixture_pipeline": True,
        "skipped": False,
        "assertions": checks,
        "passed": passed,
        "total": len(checks),
    }


def main():
    ap = argparse.ArgumentParser(
        description="Test every script in a skill (syntax/shebang/docstring/"
                    "--help/invalid-input; never executes bare)")
    ap.add_argument("target", help="Skill dir or scripts/ dir")
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("--dry-run", action="store_true",
                    help="List what would be tested without running anything")
    args = ap.parse_args()

    target = Path(args.target)
    if not target.exists():
        print(f"Error: {target} does not exist", file=sys.stderr)
        sys.exit(1)
    scripts_dir = target / "scripts" if (target / "scripts").is_dir() else target

    scripts = sorted(
        s for s in scripts_dir.rglob("*")
        if s.is_file() and s.suffix.lower() in TESTABLE_EXTS
        and "__pycache__" not in s.parts
    )
    if not scripts:
        print(f"No scripts found in {scripts_dir}")
        sys.exit(0)

    if args.dry_run:
        print(f"[dry-run] would test {len(scripts)} script(s):")
        for s in scripts:
            print(f"  • {s.relative_to(scripts_dir)}")
        sys.exit(0)

    results = [test_script(s) for s in scripts]
    passed = sum(1 for r in results if r["passed"])

    skill_root = target if (target / "__init__.py").is_file() else (
        target.parent if (target.parent / "__init__.py").is_file() else None)
    fixture = test_fixture_pipeline(skill_root) if skill_root else {
        "fixture_pipeline": False, "skipped": True,
        "reason": "could not determine skill root from target",
    }
    fixture_ok = fixture.get("skipped") or fixture.get("passed") == fixture.get("total")

    if args.json:
        print(json.dumps({
            "operation": "test_scripts",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scripts_tested": len(scripts),
            "passed": passed,
            "failed": len(scripts) - passed,
            "results": results,
            "fixture_pipeline": fixture,
        }, indent=2))
    else:
        for r in results:
            print(f"  {'✓' if r['passed'] else '✗'} {r['script']}")
            for issue in r["issues"]:
                print(f"    - {issue}")
            for w in r["warnings"]:
                print(f"    ⚠ {w}")
        print(f"\nResults: {passed}/{len(results)} scripts passed")

        print("\nFixture pipeline (temp-item outcome testing):")
        if fixture.get("skipped"):
            print(f"  ⊘ skipped — {fixture['reason']}")
        else:
            for a in fixture["assertions"]:
                mark = "✓" if a["passed"] else "✗"
                print(f"  {mark} {a['assertion']} ({a['detail']})")
            print(f"  {fixture['passed']}/{fixture['total']} fixture assertions passed")

    sys.exit(0 if passed == len(results) and fixture_ok else 1)


if __name__ == "__main__":
    main()
