#!/usr/bin/env python3
"""
scan_report.py — multi-root skill scan, batch validate, diff, and report.

Absorbs what a separate "skill-scan-validate-resolver" skill used to do as an
external dependency: walk one or more root directories for skill dirs, run
the SAME validator every other script in this toolchain uses (never a forked
copy), optionally diff skill names across sources, optionally auto-fix
failing skills, and emit a consolidated report.

skill-creator's own validate.py/auto_fix.py operate on one skill at a time.
This script is the tree-wide layer on top of them — reusing skill_root.py's
scan logic and validate.py's validate_skill() as the single source of truth,
per the project rule that downstream tooling delegates, never forks.

Usage:
  python3 scan_report.py --root /path/to/skills [--root /another/root ...]
  python3 scan_report.py --root /source/skills --diff-target /target/skills
  python3 scan_report.py --root /path/to/skills --fix
  python3 scan_report.py --root /path/to/skills --basic --json
"""
import argparse
import json
import os
import sys
sys.dont_write_bytecode = True  # never litter skills with __pycache__ (validator FAIL)
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skill_root import find_skills
from validate import validate_skill
from auto_fix import auto_fix_skill


def scan_and_validate(roots, basic_mode=False, fix=False, dry_run=False):
    """Walk every root, validate every skill found, optionally auto-fix
    failures and re-validate. Returns a list of per-skill result dicts."""
    results = []
    seen = set()
    for root in roots:
        for skill_dir in find_skills(root):
            resolved = str(skill_dir.resolve())
            if resolved in seen:
                continue  # same skill reachable from two roots — report once
            seen.add(resolved)

            outcome = validate_skill(str(skill_dir), basic_mode)
            fixes_applied = []
            if fix and not outcome["valid"]:
                fixes_applied = auto_fix_skill(str(skill_dir), dry_run=dry_run)
                if not dry_run:
                    outcome = validate_skill(str(skill_dir), basic_mode)

            results.append({
                "skill": skill_dir.name,
                "path": resolved,
                "root": str(Path(root).resolve()),
                "valid": outcome["valid"],
                "status": outcome["status"],
                "fails": outcome["fails"],
                "warnings": outcome["warnings"],
                "issues": [
                    {"name": c.name, "severity": c.severity, "detail": c.detail}
                    for c in outcome["checks"] if not c.passed
                ],
                "fixes_applied": fixes_applied,
            })
    return sorted(results, key=lambda r: r["skill"])


def diff_sources(source_roots, target_root):
    """Report skill names present under source_roots but missing under
    target_root (mirrors the absorbed skill's --sources/--target diff)."""
    source_names = set()
    for root in source_roots:
        source_names |= {s.name for s in find_skills(root)}
    target_names = {s.name for s in find_skills(target_root)}
    return {
        "target": str(Path(target_root).resolve()),
        "missing_from_target": sorted(source_names - target_names),
        "extra_in_target": sorted(target_names - source_names),
    }


def build_report(roots, basic_mode, fix, dry_run, diff_target):
    results = scan_and_validate(roots, basic_mode=basic_mode, fix=fix, dry_run=dry_run)
    passed = sum(1 for r in results if r["valid"])
    details = {
        "roots": [str(Path(r).resolve()) for r in roots],
        "mode": "basic" if basic_mode else "enterprise",
        "skills_scanned": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "results": results,
    }
    if diff_target:
        details["diff"] = diff_sources(roots, diff_target)

    return {
        "operation": "scan_report",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "success" if details["failed"] == 0 else "partial",
        "details": details,
    }


def main():
    ap = argparse.ArgumentParser(
        description="Multi-root skill scan, batch validate, diff, and report")
    ap.add_argument("--root", action="append", required=True, metavar="DIR",
                     help="Root directory to scan for skills (repeatable)")
    ap.add_argument("--diff-target", metavar="DIR",
                     help="Report skill names present in --root sources but "
                          "missing from this target directory")
    ap.add_argument("--basic", action="store_true",
                     help="Basic (production) validation instead of enterprise")
    ap.add_argument("--fix", action="store_true",
                     help="Run auto_fix.py on every failing skill, then re-validate")
    ap.add_argument("--dry-run", action="store_true",
                     help="With --fix, report what would change without writing")
    ap.add_argument("--json", action="store_true", help="JSON output")
    args = ap.parse_args()

    report = build_report(args.root, args.basic, args.fix, args.dry_run,
                           args.diff_target)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        d = report["details"]
        print(f"\n{'='*62}")
        print(f"  Scan Report ({d['mode'].upper()})")
        print(f"{'='*62}\n")
        for r in d["results"]:
            mark = "✓" if r["valid"] else "✗"
            print(f"  {mark} {r['skill']} — {r['status']} "
                  f"({r['fails']} fail, {r['warnings']} warn)  [{r['root']}]")
            for issue in r["issues"]:
                print(f"      {issue['severity']}: {issue['name']}")
            for f in r["fixes_applied"]:
                print(f"      fix: {f}")
        print(f"\n{'─'*62}")
        print(f"  Scanned : {d['skills_scanned']}")
        print(f"  Passed  : {d['passed']}")
        print(f"  Failed  : {d['failed']}")
        if "diff" in d:
            print(f"  Missing from target ({d['diff']['target']}): "
                  f"{', '.join(d['diff']['missing_from_target']) or '(none)'}")
        print(f"{'─'*62}\n")

    sys.exit(0 if report["details"]["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
