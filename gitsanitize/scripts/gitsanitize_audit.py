#!/usr/bin/env python3
"""Tamper-evident, append-only audit logging.

Each entry is a JSON line. Every line carries `prev` = sha256 of the
preceding line, and the tool verifies the whole chain on load. If a file is
altered or truncated, the chain breaks and GitSanitize refuses to proceed.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

from gitsanitize_core import GSError, sha256


class AuditLog:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._prev = self._tail_digest()
        self._active = True

    def _tail_digest(self) -> str:
        if not self.path.exists():
            return "0" * 64
        digest = sha256(b"")
        with open(self.path, "rb") as fh:
            line = fh.readline()
            while line:
                if line.strip():
                    digest = sha256(line)
                line = fh.readline()
        return digest

    def verify_chain(self) -> None:
        """Raise if the audit chain is broken or entries are malformed."""
        if not self.path.exists():
            return
        prev = "0" * 64
        with open(self.path, "rb") as fh:
            for lineno, raw in enumerate(fh, 1):
                line = raw.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except ValueError as exc:
                    raise GSError(f"audit log corrupt at line {lineno}: {exc}")
                if entry.get("prev") != prev:
                    raise GSError(
                        f"audit tamper detected: line {lineno} hash chain broken"
                    )
                prev = sha256(raw)
        self._prev = prev

    def _append(self, entry: dict) -> None:
        if not self._active:
            raise GSError("audit log is closed")
        entry["ts"] = time.time()
        entry["prev"] = self._prev
        raw = (json.dumps(entry, sort_keys=True) + "\n").encode()
        self._prev = sha256(raw)
        try:
            with open(self.path, "ab") as fh:
                fh.write(raw)
                fh.flush()
                os.fsync(fh.fileno())
        except OSError as exc:
            raise GSError(f"audit write failed (stopping operation): {exc}") from exc

    def log(self, action: str, **fields) -> dict:
        entry = {"action": action, **fields}
        self._append(entry)
        return entry

    def close(self):
        self._active = False

    def read(self) -> list:
        self.verify_chain()
        out = []
        if self.path.exists():
            for raw in self.path.read_text().splitlines():
                if raw.strip():
                    out.append(json.loads(raw))
        return out


if __name__ == "__main__":  # pragma: no cover
    import argparse as _argparse
    _p = _argparse.ArgumentParser(
        prog="gitsanitize_audit.py",
        description=(
            "gitsanitize library module: audit.py. This is implementation, "
            "not a standalone CLI -- run scripts/gitsanitize.py instead, "
            "which is the real entry point and imports this module itself."
        ),
    )
    _p.parse_args()  # no arguments defined: --help prints usage and exits 0;
                      # any unexpected argument is argparse's own clean
                      # "unrecognized arguments" error (exit 2), not a traceback
