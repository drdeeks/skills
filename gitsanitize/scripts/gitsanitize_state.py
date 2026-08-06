#!/usr/bin/env python3
"""Session/transaction state: manifests, backups, checkpoints, refs.

Implements the ACID lifecycle: BEGIN -> backup -> snapshot -> rewrite ->
verify -> COMMIT. Every step writes a checkpoint. If a run dies without a
COMPLETED marker, subsequent commands refuse to proceed (fail-closed) until
`--resume` or `rollback` is invoked.
"""
from __future__ import annotations

import json
import os
import shutil
import time
from pathlib import Path

from gitsanitize_core import SafetyError, fresh_clone, is_bare_git_repo, run_git, sha256
from gitsanitize_config import resolve_state_dir
import gitsanitize_yamlx as yamlx

SESSION_ID_KEY = "session/session_id"


def new_session_id(repo: Path) -> str:
    ts = time.strftime("%Y%m%dT%H%M%S")
    head = run_git(["rev-parse", "--short", "HEAD"], repo, check=False).stdout.strip()[:8]
    return f"{ts}-{head or 'init'}"


class Session:
    def __init__(self, repo: Path, state: Path, sid: str | None = None,
                 completed: bool = False):
        self.repo = repo
        self.state = state
        self.sid = sid
        self._backed_up = False
        self._completed = completed
        self._steps: list[dict] = []
        self._env = None

    @classmethod
    def begin(cls, repo: Path) -> "Session":
        state = resolve_state_dir(repo)
        state.mkdir(parents=True, exist_ok=True)
        sid = new_session_id(repo)
        sess = cls(repo, state, sid)
        sess._steps = [{
            "step": "begin",
            "session_id": sid,
            "timestamp": time.time(),
            "git_version": _git_version(),
            "user": os.environ.get("USER", os.environ.get("USERNAME", "unknown")),
        }]
        sess._flush()
        (state / "session").mkdir(parents=True, exist_ok=True)
        (state / "session" / "session_id").write_text(sid, encoding="utf-8")
        return sess

    @classmethod
    def resume_or_new(cls, repo: Path) -> "Session":
        """Return the in-progress session if one exists, else start a new one."""
        state = resolve_state_dir(repo)
        sid_file = state / "session" / "session_id"
        if sid_file.exists():
            sid = sid_file.read_text(encoding="utf-8").strip()
            sess = cls(repo, state, sid)
            data = sess._load_manifest()
            if data is None:
                raise SafetyError("session manifest is unreadable/tampered; run rollback")
            sess._steps = data.get("steps", [])
            sess._backed_up = bool(data.get("backed_up"))
            if data.get("completed"):
                sess._completed = True
                return cls.begin(repo)  # completed session -> start fresh
            return sess
        return cls.begin(repo)

    # -- manifest ----------------------------------------------------------

    def _manifest_path(self) -> Path:
        return self.state / "session" / "manifest.yaml"

    def _load_manifest(self) -> dict | None:
        p = self._manifest_path()
        if not p.exists():
            return None
        try:
            return yamlx.load(p)
        except (ValueError, OSError) as exc:
            raise SafetyError(f"cannot read session manifest: {exc}") from exc

    def _flush(self) -> None:
        p = self._manifest_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(yamlx.dump({
            "session_id": self.sid,
            "backed_up": self._backed_up,
            "completed": self._completed,
            "steps": self._steps,
        }), encoding="utf-8")
        os.replace(tmp, p)  # atomic write

    def checkpoint(self, step: str, **fields) -> None:
        entry = {"step": step, "timestamp": time.time(), **fields}
        self._steps.append(entry)
        logp = self.state / "session" / "steps.jsonl"
        logp.parent.mkdir(parents=True, exist_ok=True)
        prev = "0" * 64
        if logp.exists():
            last = logp.read_text(encoding="utf-8").strip().splitlines()
            if last:
                prev = hashlib_sha256(last[-1].encode())
        entry["prev"] = prev
        with open(logp, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, sort_keys=True) + "\n")
        self._flush()

    # -- actions -----------------------------------------------------------

    def backup_clone(self) -> Path:
        backup_dir = self.state / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        dest = backup_dir / (self.sid or "backup")
        if dest.exists():
            shutil.rmtree(dest)
        dest.mkdir(parents=True)
        fresh_clone(self.repo, dest)
        self._backed_up = True
        self.checkpoint("backup_created", path=str(dest), sha256=sha256(sha256_dir(dest).encode()))
        return dest

    def snapshot_refs(self) -> dict:
        show = run_git(["show-ref"], self.repo, check=False).stdout
        refs = {}
        for line in show.splitlines():
            parts = line.split(" ", 1)
            if len(parts) == 2:
                refs[parts[1]] = parts[0]
        head = run_git(["symbolic-ref", "--short", "HEAD"], self.repo, check=False).stdout.strip()
        payload = {"refs": refs, "head": head}
        out = self.state / "session" / "original_refs.json"
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.checkpoint("refs_snapshot", sha256=sha256(out.read_bytes()))
        return payload

    def mark_verified(self) -> None:
        self.checkpoint("verified")

    def commit(self, plan_path: str, result: dict) -> None:
        self.checkpoint(
            "commit",
            plan=plan_path,
            commits_kept=result.get("commits_kept"),
            commits_dropped=result.get("commits_dropped"),
        )

    def complete(self, final_head: str) -> None:
        self._completed = True
        self.checkpoint("completed", head=final_head)

    @property
    def is_complete(self) -> bool:
        return self._completed

    @property
    def backed_up(self) -> bool:
        return self._backed_up


def _git_version() -> str:
    return run_git(["version"], Path.cwd(), check=False).stdout.strip()


def hashlib_sha256(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest()


def sha256_dir(path: Path) -> str:
    """Cheap fingerprint of a tree of git objects (walk .git objects + refs)."""
    import hashlib
    digest = hashlib.sha256()
    git = path / ".git"
    if git.is_dir():
        for root, _dirs, files in os.walk(git):
            for f in sorted(files):
                fp = os.path.join(root, f)
                rel = os.path.relpath(fp, git).encode()
                digest.update(rel)
                with open(fp, "rb") as fh:
                    digest.update(fh.read(65536))
    return digest.hexdigest()


def rollback(repo: Path, state_path: Path | None = None, audit=None) -> None:
    """Restore original history from the backup clone."""
    state = state_path or resolve_state_dir(repo)
    backups = state / "backups"
    candidates = sorted(backups.glob("*")) if backups.is_dir() else []
    if not candidates:
        raise SafetyError("no backup found; cannot rollback")
    backup = candidates[-1]
    if not is_bare_git_repo(backup):
        raise SafetyError(f"backup at {backup} is not a valid git repository")

    backup_refs = {}
    for line in run_git(["--git-dir", str(backup), "for-each-ref",
                         "--format=%(refname) %(objectname)"],
                        repo, check=False).stdout.splitlines():
        parts = line.split(" ", 1)
        if len(parts) == 2:
            backup_refs[parts[0]] = parts[1]

    branches = [r for r in backup_refs if r.startswith("refs/heads/")]
    if not branches:
        raise SafetyError("backup has no branches")
    if audit:
        audit.log("rollback_start", backup=str(backup))

    # import backup objects into the repo via a temp ref namespace
    run_git(["fetch", str(backup), "+refs/heads/*:refs/_gitsanitize_restore/*", "+refs/tags/*:refs/_gitsanitize_restore/tags/*"],
            repo)
    restore_refs = {}
    for line in run_git(["for-each-ref", "--format=%(refname) %(objectname)",
                         "refs/_gitsanitize_restore/"], repo).stdout.splitlines():
        parts = line.split(" ", 1)
        if len(parts) == 2:
            restore_refs[parts[0]] = parts[1]

    # reset every local ref to the backup state (fail-closed: replace, don't guess)
    local_refs = [r for r in run_git(
        ["for-each-ref", "--format=%(refname)"], repo).stdout.splitlines() if r.strip()]
    for ref in local_refs:
        if ref.startswith("refs/_gitsanitize_restore/"):
            continue
        if ref.startswith(("refs/heads/", "refs/tags/")):
            restore = "refs/_gitsanitize_restore/" + ref[len("refs/heads/"):]
            if ref.startswith("refs/tags/"):
                restore = "refs/_gitsanitize_restore/tags/" + ref[len("refs/tags/"):]
            sha = restore_refs.get(restore)
            if sha:
                run_git(["update-ref", ref, sha], repo)
            else:
                run_git(["update-ref", "-d", ref], repo)  # prune refs absent in backup

    default_branch = None
    for name in ("main", "master"):
        if backup_refs.get(f"refs/heads/{name}"):
            default_branch = name
            break
    if not default_branch:
        default_branch = next(iter(branches)).split("refs/heads/")[1]
    run_git(["checkout", "-f", default_branch], repo)

    # clean up the temp namespace
    for ref in list(restore_refs):
        run_git(["update-ref", "-d", ref], repo)
    run_git(["reflog", "expire", "--expire=now", "--all"], repo)
    run_git(["gc", "--prune=now", "--quiet"], repo)
    if audit:
        audit.log("rollback_complete", backup=str(backup))


if __name__ == "__main__":  # pragma: no cover
    import argparse as _argparse
    _p = _argparse.ArgumentParser(
        prog="gitsanitize_state.py",
        description=(
            "gitsanitize library module: state.py. This is implementation, "
            "not a standalone CLI -- run scripts/gitsanitize.py instead, "
            "which is the real entry point and imports this module itself."
        ),
    )
    _p.parse_args()  # no arguments defined: --help prints usage and exits 0;
                      # any unexpected argument is argparse's own clean
                      # "unrecognized arguments" error (exit 2), not a traceback
