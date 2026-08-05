#!/usr/bin/env python3
"""
USB structure validator for a deployed portable-usb-manager payload
(the tree deploy-usb-system.sh unpacks: menu.sh + usb/{lib,cli,config,...}).

Checks, read-only by default:
  - Required entry points exist (menu.sh, usb/cli/usbctl)
  - Required lib/ modules exist
  - No file that should be executable (per-project convention: .sh scripts,
    usbctl) is missing its execute bit
  - No path uses the never-0700 permission the project's own lessons forbid
  - state.json (if present, per references/state-management.md) parses as
    valid JSON and has a "devices" object

--fix repairs common drift: missing execute bits, 0700 directories, and
creates missing (but expected-empty-ok) directories. It never touches
file contents.
"""

import argparse
import json
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_FILES = [
    "menu.sh",
    "usb/cli/usbctl",
    "usb/config/initialize.sh",
]
REQUIRED_LIB_MODULES = [
    "core.sh", "platform.sh", "usb.sh", "config.sh", "menu.sh", "validation.sh",
]
EXECUTABLE_SUFFIXES = {".sh"}
EXECUTABLE_BASENAMES = {"usbctl", "menu.sh"}


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def check_structure(target: Path, issues: list):
    for rel in REQUIRED_FILES:
        p = target / rel
        if not p.is_file():
            issues.append(f"missing required file: {rel}")

    lib_dir = target / "usb" / "lib"
    if not lib_dir.is_dir():
        issues.append("missing required directory: usb/lib")
    else:
        for mod in REQUIRED_LIB_MODULES:
            if not (lib_dir / mod).is_file():
                issues.append(f"missing lib module: usb/lib/{mod}")


def check_permissions(target: Path, issues: list, fixes: list, do_fix: bool):
    if not target.is_dir():
        return
    for p in target.rglob("*"):
        try:
            mode = stat.S_IMODE(p.stat().st_mode)
        except OSError:
            continue
        if p.is_dir() and mode == 0o700:
            issues.append(f"directory uses forbidden 0700 permission: {p}")
            if do_fix:
                p.chmod(0o755)
                fixes.append(f"chmod 0755 {p}")
        if p.is_file() and (p.suffix in EXECUTABLE_SUFFIXES or p.name in EXECUTABLE_BASENAMES):
            if not (mode & stat.S_IXUSR):
                issues.append(f"expected executable, missing +x: {p}")
                if do_fix:
                    p.chmod(mode | 0o755)
                    fixes.append(f"chmod +x {p}")


def check_state_json(target: Path, issues: list):
    for candidate in (
        Path.home() / ".local" / "share" / "portable-linux-usb" / "state.json",
        target / "state.json",
    ):
        if not candidate.is_file():
            continue
        try:
            data = json.loads(candidate.read_text())
        except (json.JSONDecodeError, OSError) as exc:
            issues.append(f"state.json at {candidate} is not valid JSON: {exc}")
            continue
        if "devices" not in data or not isinstance(data["devices"], dict):
            issues.append(f"state.json at {candidate} missing a 'devices' object")


def validate(target: Path, do_fix: bool) -> dict:
    issues: list = []
    fixes: list = []

    if not target.is_dir():
        return {
            "operation": "validate",
            "timestamp": now_iso(),
            "status": "error",
            "target": str(target),
            "details": {"valid": False, "issues": [f"no such directory: {target}"]},
            "cost": {"tier": 0, "amount_usd": 0.0, "service": "local"},
        }

    check_structure(target, issues)
    check_permissions(target, issues, fixes, do_fix)
    check_state_json(target, issues)

    return {
        "operation": "validate",
        "timestamp": now_iso(),
        "status": "success" if not issues else "failed",
        "target": str(target),
        "details": {"valid": not issues, "issues": issues, "fixes_applied": fixes},
        "cost": {"tier": 0, "amount_usd": 0.0, "service": "local"},
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate (and optionally repair) a deployed USB structure.",
    )
    parser.add_argument("target", help="Path to a deployed USB system root (see deploy-usb-system.sh)")
    parser.add_argument("--fix", action="store_true", help="Repair common drift (perms, missing +x)")
    parser.add_argument("--json", action="store_true", help="JSON output only")
    args = parser.parse_args()

    result = validate(Path(args.target).expanduser().resolve(), args.fix)

    print(json.dumps(result, indent=2))
    if result["details"].get("issues") and not args.json:
        print(f"\n{len(result['details']['issues'])} issue(s) found.", file=sys.stderr)

    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
