#!/usr/bin/env python3
"""
gitsanitize/__init__.py — skill metadata and a thin Python entry point.

The real interface is the CLI (scripts/gitsanitize.py, zero-install,
self-resolving). This module exists so the skill can also be imported
programmatically and so its version/description are declared in one place,
matching every other skill in this repository.

Usage (CLI, the primary interface):
    python3 scripts/gitsanitize.py                 # interactive wizard
    python3 scripts/gitsanitize.py scan --repo .    # any raw subcommand

Usage (Python):
    from gitsanitize import run
    run(["--repo", "/path/to/repo", "scan"])
"""
import sys
from pathlib import Path

NAME = "gitsanitize"
VERSION = "0.2.3"
DESCRIPTION = (
    "Layered, fail-closed git history identity sanitization. Interactive by "
    "default: scan -> classify -> plan -> review -> apply -> publish, "
    "confirming before anything destructive. Merges or removes author "
    "identities without dropping a single commit unless explicitly told to; "
    "verifies binary content byte-for-byte before and after any rewrite."
)

_ENTRY = Path(__file__).resolve().parent / "scripts" / "gitsanitize.py"


def run(argv=None) -> int:
    """Programmatic entry point. Runs the same self-contained CLI script a
    human would, in a subprocess, rather than importing the vendored
    package directly in-process: this wrapper module and the vendored
    package it calls are both named `gitsanitize`, which collides in
    sys.modules the moment both get imported in one interpreter (confirmed
    by hitting it while building this -- `from gitsanitize.cli import main`
    silently resolved against the wrong `gitsanitize` once this file itself
    had already been imported under that name). Subprocess isolation
    sidesteps the collision entirely instead of fighting sys.modules."""
    import subprocess
    proc = subprocess.run([sys.executable, str(_ENTRY), *(argv or [])])
    return proc.returncode


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
