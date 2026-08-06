#!/usr/bin/env python3
"""Core primitives: errors, git subprocess helpers, hashing, schema validation.

Everything here is dependency-free (Python stdlib only) and OS-agnostic.
This module is intentionally thin; domain logic lives in the engines.
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
from pathlib import Path

GITSANITIZE_ENV = "GITSANITIZE_CONFIG"
STATE_DIR_DEFAULT = ".gitsanitize"


class GSError(Exception):
    """Generic, user-facing error. Exit code 2 by default."""

    exit_code = 2


class SafetyError(GSError):
    """A fail-closed precondition was not met. Blocks further action."""

    exit_code = 3


class VerificationError(GSError):
    exit_code = 4


class PlanError(GSError):
    exit_code = 2


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def run_git(args, cwd: Path, check: bool = True, capture: bool = True, binary: bool = False):
    """Run a git subcommand in the given working directory.

    `binary=True` returns raw bytes in .stdout/.stderr instead of decoding as
    text. Required for any command whose output can embed raw blob content
    (fast-export streams) — decoding that as UTF-8 text raises
    UnicodeDecodeError the moment a repo has real binary files in it (zip
    archives, images, ...). Every other call site is unaffected: this is
    opt-in per call, default behavior (text=True) is unchanged."""
    cmd = ["git"] + [str(a) for a in args]
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=capture,
        text=not binary,
    )
    if check and proc.returncode != 0:
        out = proc.stdout.decode("utf-8", errors="replace") if binary and proc.stdout else (proc.stdout or "")
        err = proc.stderr.decode("utf-8", errors="replace") if binary and proc.stderr else (proc.stderr or "")
        raise GSError(
            f"git {' '.join(args)} failed in {cwd}:\n{out}\n{err}"
        )
    return proc


def is_git_repo(path: Path) -> bool:
    if not (path / ".git").exists():
        return False
    cfgdir = path / ".git"
    if cfgdir.is_file():  # worktree/submodule pointer
        return False
    proc = run_git(["rev-parse", "--is-inside-work-tree"], path, check=False)
    return proc.returncode == 0 and proc.stdout.strip() == "true"


def is_bare_git_repo(path: Path) -> bool:
    """True when `path` is a bare git repository directory (e.g. a mirror)."""
    proc = run_git(["--git-dir", str(path), "rev-parse", "--is-bare-repository"],
                   Path.cwd(), check=False)
    return proc.returncode == 0 and proc.stdout.strip() == "true"


def fresh_clone(source: Path, dest: Path) -> None:
    """Create an immutable bare mirror clone for backup/rollback."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    run_git(["clone", "--mirror", str(source), str(dest)], dest.parent)


VALIDATE_RE = re.compile(r"^(?!-)[A-Za-z0-9._-]+$")


def _typename(x):
    if isinstance(x, bool):
        return "bool"
    if isinstance(x, (int, float)):
        return "number"
    if isinstance(x, str):
        return "str"
    if isinstance(x, list):
        return "list"
    if isinstance(x, dict):
        return "dict"
    return type(x).__name__


def validate_schema(data, schema, path="<root>"):
    """Strict schema validator: reject unknown keys and wrong types."""
    if isinstance(schema, list):
        if not isinstance(schema[0], dict) or "@label" not in schema[0]:
            raise GSError(f"bad schema at {path}")
        label = schema[0]["@label"]
        item_schema = schema[0].get("@schema", {})
        if not isinstance(data, list):
            raise GSError(f"{path}: expected a list of {label}")
        for i, item in enumerate(data):
            validate_schema(item, item_schema, f"{path}[{i}]")
        return
    if schema == "*":
        return
    if not isinstance(schema, dict):
        raise GSError(f"bad schema at {path}")
    if not isinstance(data, dict):
        raise GSError(f"{path}: expected dict, got {_typename(data)}")
    for key, val in data.items():
        if key.startswith("_"):
            continue  # internal fields injected by the loader
        if key not in schema:
            raise GSError(f"{path}: unknown key '{key}'")
        exp = schema[key]
        if isinstance(exp, bool):
            # True => key required (any type); False => optional (any type)
            continue
        if exp == "*":
            continue
        if isinstance(exp, str):  # primitive type name
            if _typename(val) != exp:
                raise GSError(f"{path}.{key}: expected {exp}, got {_typename(val)}")
        elif isinstance(exp, dict) or isinstance(exp, list):
            validate_schema(val, exp, f"{path}.{key}")
        else:
            raise GSError(f"{path}.{key}: bad schema entry")
    for key, exp in schema.items():
        if isinstance(exp, bool) and exp and key not in data:
            raise GSError(f"{path}: required key '{key}' missing")


def which(binary: str):
    return shutil.which(binary)


def env_or(var: str, default):
    return os.environ.get(var, default)


if __name__ == "__main__":  # pragma: no cover
    import argparse as _argparse
    _p = _argparse.ArgumentParser(
        prog="gitsanitize_core.py",
        description=(
            "gitsanitize library module: core.py. This is implementation, "
            "not a standalone CLI -- run scripts/gitsanitize.py instead, "
            "which is the real entry point and imports this module itself."
        ),
    )
    _p.parse_args()  # no arguments defined: --help prints usage and exits 0;
                      # any unexpected argument is argparse's own clean
                      # "unrecognized arguments" error (exit 2), not a traceback
