#!/usr/bin/env python3
"""gitsanitize -- zero-install entry point.

Self-resolving per FOREVER-SYSTEM §2: the rest of the implementation
(gitsanitize_core.py, gitsanitize_cli.py, ...) sits right next to this file
as flat sibling modules, found from `__file__` at run time. No PYTHONPATH,
no `pip install`, no `pipx`, nothing to set up first. Drop this whole
skill directory anywhere and `python3 scripts/gitsanitize.py` (or
`./scripts/gitsanitize.py` once you `chmod +x` it) just works.

Interactive by default: run with no arguments at all and it walks you
through scan -> classify -> plan -> review -> apply -> publish, confirming
before anything destructive. Every raw subcommand (scan, plan, classify,
review, apply, verify, rollback, publish) is still available for
scripted/CI use -- see `--help`.

An optional `install_alias.sh` sits next to this file if you want the bare
`gitsanitize` command on your PATH. It is entirely optional and asks before
touching your shell config; this script works with zero setup either way.
"""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from gitsanitize_cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
