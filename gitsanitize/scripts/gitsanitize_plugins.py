#!/usr/bin/env python3
"""Plugin Manager: discovers and invokes executable plugins at lifecycle hooks.

Plugins live in the plugin path (env -> user state -> repo-local). Each plugin
is an executable that reads a JSON context on stdin and writes a JSON result
on stdout. The core defines WHERE plugins hook; plugins decide WHAT they do.
"""
from __future__ import annotations

import json
import subprocess
import hashlib
from pathlib import Path

from gitsanitize_config import find_plugin_path
from gitsanitize_core import GSError

HOOKS = (
    "pre-scan", "post-scan", "pre-plan", "post-plan",
    "on-approval", "pre-rewrite", "post-rewrite", "post-verify", "publish-hook",
)


class Plugin:
    def __init__(self, path: Path, name: str, version: str, hooks: list[str]):
        self.path = path
        self.name = name
        self.version = version
        self.hooks = hooks

    def run(self, hook: str, context: dict) -> dict:
        payload = {"hook": hook, "plugin": self.name, "context": context}
        try:
            proc = subprocess.run(
                [str(self.path)],
                input=json.dumps(payload),
                capture_output=True,
                text=True,
                timeout=60,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise GSError(f"plugin {self.name} failed to run: {exc}") from exc
        try:
            result = json.loads(proc.stdout or "{}")
        except ValueError as exc:
            raise GSError(
                f"plugin {self.name} returned non-JSON output: {proc.stdout[:200]}"
            ) from exc
        return result


def _checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def discover(repo: Path | None) -> list[Plugin]:
    """Load all plugins found in the plugin path."""
    plugins = []
    for d in find_plugin_path(repo):
        for p in sorted(d.iterdir()):
            if p.suffix in (".py", ".sh") or (p.is_file() and not p.suffix):
                if not p.suffix and not _is_executable(p):
                    continue
                name = p.stem
                plugins.append(Plugin(p, name, "0", HOOKS))
    return plugins


def _is_executable(p: Path) -> bool:
    import os
    return os.access(p, os.X_OK)


def dispatch(plugins: list[Plugin], hook: str, context: dict, audit) -> list[dict]:
    results = []
    for pl in plugins:
        if hook not in pl.hooks:
            continue
        res = pl.run(hook, context)
        audit.log("plugin_invoked", plugin=pl.name, hook=hook, checksum=_checksum(pl.path))
        results.append({"plugin": pl.name, "result": res})
    return results


if __name__ == "__main__":  # pragma: no cover
    import argparse as _argparse
    _p = _argparse.ArgumentParser(
        prog="gitsanitize_plugins.py",
        description=(
            "gitsanitize library module: plugins.py. This is implementation, "
            "not a standalone CLI -- run scripts/gitsanitize.py instead, "
            "which is the real entry point and imports this module itself."
        ),
    )
    _p.parse_args()  # no arguments defined: --help prints usage and exits 0;
                      # any unexpected argument is argparse's own clean
                      # "unrecognized arguments" error (exit 2), not a traceback
