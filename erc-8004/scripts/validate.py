#!/usr/bin/env python3
"""Validation script for ERC-8004 skill."""

import json
import os
import sys
from pathlib import Path


def validate_structure(skill_dir: Path) -> dict:
    """Validate skill directory structure."""
    issues = []

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        issues.append("Missing SKILL.md")

    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.exists():
        issues.append("Missing scripts/ directory")
    else:
        scripts = list(scripts_dir.glob("*.py"))
        if len(scripts) < 2:
            issues.append(f"Need at least 2 scripts, found {len(scripts)}")

    refs_dir = skill_dir / "references"
    if not refs_dir.exists():
        issues.append("Missing references/ directory")
    else:
        refs = list(refs_dir.glob("*.md"))
        if len(refs) < 3:
            issues.append(f"Need at least 3 references, found {len(refs)}")

    return {"valid": len(issues) == 0, "issues": issues}


def main():
    skill_dir = Path(__file__).parent.parent
    result = validate_structure(skill_dir)

    if result["valid"]:
        print("Validation passed")
        return 0
    else:
        print("Validation failed:")
        for issue in result["issues"]:
            print(f"  - {issue}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
