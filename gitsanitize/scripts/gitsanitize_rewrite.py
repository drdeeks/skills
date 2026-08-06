#!/usr/bin/env python3
"""Rewrite Executor: orchestrates the history rewrite.

Backend: a dependency-free `git fast-export` -> transform -> `git fast-import`
pipeline. It applies:

  * mailmap (identity merges) by rewriting author/committer lines
  * trailer removal by editing commit message data blocks
  * commit dropping for removed authors (with branch/tag remapping)

Everything runs inside the working tree directly (a prior backup clone is the
safety net, see state.py's Session.backup_clone).

The whole pipeline operates on BYTES, not str, and walks the stream with an
explicit byte cursor rather than pre-splitting it into "lines". Both of
those are load-bearing, not style choices:

  * A fast-export `data <N>` block (a blob, a commit message, a tag message)
    is exactly N raw bytes, which for a blob can be arbitrary binary content
    -- not guaranteed valid UTF-8, and not guaranteed to respect anything
    that looks like a line boundary. Decoding the stream as text crashes the
    instant a repo has real binary content in it (zip archives, images...).
  * Pre-splitting into "lines" and then scanning for a blank line as a data
    block's stop condition (the original implementation's approach for
    blobs) works by luck on small/text content and is wrong by construction
    for binary content: a blob's own bytes can easily contain a byte
    sequence that looks like a blank line, which truncates the blob early
    and desynchronizes the rest of the stream for fast-import. The fix is
    to never scan for a data block's end -- always consume exactly N bytes
    from a running cursor, the same way git itself writes them.

No external tool is used or required.
"""
from __future__ import annotations

import re
import subprocess
from shutil import which
from pathlib import Path

from gitsanitize_core import GSError, run_git

_TRAILER_HINT = re.compile(rb"^[A-Za-z][A-Za-z0-9-]{1,63}:")


def build_mailmap(plan) -> str:
    """Human-readable .mailmap text (not part of the binary-unsafe stream
    path -- this is plain text output for anyone who wants a mailmap file)."""
    out = []
    for old_name, old_email, new_name, new_email in plan.effective_mailmap():
        if old_email == new_email and old_name == new_name:
            continue
        out.append(f"{new_name} <{new_email}> <{old_name}> <{old_email}>")
    return "\n".join(out)


def filter_repo_available() -> bool:
    return which("git-filter-repo") is not None


class StreamTransformer:
    """Transforms a fast-export stream, byte for byte, via an explicit cursor."""

    def __init__(self, plan):
        self.merges = {
            (m["from_name"].encode("utf-8"), m["from_email"].encode("utf-8")):
                (m["to_name"].encode("utf-8"), m["to_email"].encode("utf-8"))
            for m in plan.merges if m["action"] == "merge"
        }
        self.removed_emails = {r["from_email"].lower().encode("utf-8") for r in plan.removals}
        self.trailer_patterns = [
            re.compile(p.get("pattern", "").encode("utf-8")) for p in plan.trailer_removes
        ]
        self._parents: dict[int, list[int]] = {}
        self._surviving: dict[int, int] = {}  # mark -> surviving mark or None
        self._orig_author: dict[int, tuple] = {}
        self._ref_tips: dict[bytes, int] = {}  # ref -> original tip mark
        self._buf = b""
        self._pos = 0
        self._n = 0

    # -- byte-cursor primitives ----------------------------------------------
    # These never scan into a data block's content; a data block is always
    # consumed by the exact byte count git itself wrote, full stop.

    def _peek_line(self) -> bytes:
        nl = self._buf.find(b"\n", self._pos)
        if nl == -1:
            return self._buf[self._pos:]
        return self._buf[self._pos:nl + 1]

    def _take_line(self) -> bytes:
        nl = self._buf.find(b"\n", self._pos)
        if nl == -1:
            line = self._buf[self._pos:]
            self._pos = self._n
        else:
            line = self._buf[self._pos:nl + 1]
            self._pos = nl + 1
        return line

    def _at_end(self) -> bool:
        return self._pos >= self._n

    def _take_data_block(self) -> tuple[bytes, bytes]:
        """Expects the cursor to be at a `data <N>` header line. Consumes
        that header plus exactly N following bytes. Returns (header, body)."""
        header = self._take_line()
        n = int(header.strip().split()[1])
        body = self._buf[self._pos:self._pos + n]
        self._pos += n
        return header, body

    # -- identity mapping --------------------------------------------------

    _PERSON_RE = re.compile(
        rb"^[a-z]+ (?P<name>[^<]*) <(?P<email>[^>]*)> "
        rb"(?P<ts>-?\d+) (?P<tz>[+-]\d{4})$",
        re.I,
    )

    @staticmethod
    def _parse_person(line: bytes):
        m = StreamTransformer._PERSON_RE.match(line)
        if not m:
            return None
        return (
            m.group("name").strip(),
            m.group("email"),
            m.group("ts"),
            m.group("tz"),
        )

    def _map_person(self, person) -> tuple:
        name, email, ts, tz = person
        new = self.merges.get((name, email))
        if new:
            name, email = new
        return (name, email, ts, tz)

    def _emit_person(self, prefix: bytes, line: bytes) -> bytes:
        person = self._parse_person(line)
        if person is None:
            return line
        name, email, ts, tz = self._map_person(person)
        return prefix + b" " + name + b" <" + email + b"> " + ts + b" " + tz + b"\n"

    # -- message trailer stripping -----------------------------------------

    def _strip_trailers(self, body: bytes) -> bytes:
        if not self.trailer_patterns:
            return body
        changed = False
        out = []
        for raw in body.splitlines(keepends=True):
            line = raw.rstrip(b"\n")
            if _TRAILER_HINT.match(line.strip()) and any(
                p.search(line) for p in self.trailer_patterns
            ):
                changed = True
                continue
            out.append(raw)
        return b"".join(out) if changed else body

    # -- stream transform --------------------------------------------------

    def transform_stream(self, stream: bytes) -> bytes:
        self._buf = stream
        self._pos = 0
        self._n = len(stream)
        out: list[bytes] = []
        while not self._at_end():
            stripped = self._peek_line().strip()
            if stripped.startswith(b"commit "):
                self._handle_commit(out)
            elif stripped.startswith(b"blob"):
                self._handle_blob(out)
            elif stripped.startswith(b"tag "):
                self._handle_tag(out)
            elif stripped.startswith(b"reset "):
                out.append(self._take_line())
                if not self._at_end() and self._peek_line().strip().startswith(b"from :"):
                    out.append(self._take_line())
            else:
                out.append(self._take_line())
        return b"".join(out)

    def _handle_blob(self, out: list[bytes]) -> None:
        """`blob` -> `mark :N` -> `data <SIZE>` -> exactly SIZE raw bytes.
        Content is opaque and copied through untouched; only the byte count
        governs where it ends, never a scan for a blank line."""
        out.append(self._take_line())  # "blob"
        while not self._at_end():
            s = self._peek_line().strip()
            if s.startswith(b"mark :"):
                out.append(self._take_line())
                continue
            if s.startswith(b"data "):
                header, body = self._take_data_block()
                out.append(header)
                out.append(body)  # byte-exact: no padding, the header's N is the contract
                return
            # Neither mark nor data yet seen -- not expected mid-blob, stop
            # rather than risk misreading something that belongs elsewhere.
            return

    def _handle_commit(self, out: list[bytes]) -> None:
        commit_line = self._take_line()
        refname = commit_line.strip().split(b" ", 1)[1].strip()
        header = [commit_line]
        mark = None
        author = None
        committer = None
        msg_header = None
        msg_body = None
        while not self._at_end():
            s = self._peek_line().strip()
            if s.startswith(b"mark :"):
                line = self._take_line()
                mark = int(s[6:])
                header.append(line)
            elif s.startswith(b"author "):
                line = self._take_line()
                person = self._parse_person(s)
                if person is not None:
                    author = person
                header.append(line)
            elif s.startswith(b"committer "):
                line = self._take_line()
                person = self._parse_person(s)
                if person is not None:
                    committer = person
                header.append(line)
            elif s.startswith(b"data "):
                msg_header, msg_body = self._take_data_block()
                break
            else:
                header.append(self._take_line())

        # decide drop
        drop = False
        if author and author[1] and author[1].lower() in self.removed_emails:
            drop = True
        if committer and committer[1] and committer[1].lower() in self.removed_emails:
            drop = True

        if drop:
            if mark is not None:
                self._surviving[mark] = None
                self._ref_tips[refname] = mark  # remember tip even though dropped
            # skip file-change lines, but record parent links for remapping
            while not self._at_end():
                s = self._peek_line().strip()
                if s.startswith((b"from ", b"merge ")):
                    self._record_parent(mark, s)
                    self._take_line()
                elif s.startswith((b"M ", b"D ", b"C ", b"R ", b"deleteall", b"m ")):
                    self._take_line()
                else:
                    break
            if not self._at_end() and self._peek_line().strip() == b"":
                self._take_line()
            return

        # survived: emit transformed header (remap from/merge if present)
        for line in header:
            s = line.strip()
            if s.startswith(b"author "):
                out.append(self._emit_person(b"author", s))
            elif s.startswith(b"committer "):
                out.append(self._emit_person(b"committer", s))
            elif s.startswith((b"from ", b"merge ")):
                self._record_parent(mark, s)
                out.append(self._remap_parent_line(s))
            else:
                out.append(line)

        # emit transformed message. Byte-exact: the header's N must equal
        # exactly what follows, so no padding newline gets added here either.
        if msg_body is not None:
            new_body = self._strip_trailers(msg_body)
            out.append(b"data " + str(len(new_body)).encode() + b"\n")
            out.append(new_body)

        # remaining file-change lines (from/merge commonly live here)
        while not self._at_end():
            s = self._peek_line().strip()
            if s.startswith((b"from ", b"merge ")):
                self._record_parent(mark, s)
                out.append(self._remap_parent_line(self._take_line()))
            elif s.startswith((b"M ", b"D ", b"C ", b"R ", b"deleteall", b"m ")):
                out.append(self._take_line())
            else:
                break
        if not self._at_end() and self._peek_line().strip() == b"":
            out.append(self._take_line())

        if mark is not None:
            self._surviving[mark] = mark
            self._orig_author[mark] = author
            self._ref_tips[refname] = mark

    def _record_parent(self, mark, s: bytes) -> None:
        if mark is None:
            return
        self._parents.setdefault(mark, [])
        try:
            parent = int(s.split(b" ")[1].lstrip(b":"))
            self._parents[mark].append(parent)
        except (IndexError, ValueError):
            pass

    def _remap_parent_line(self, s: bytes) -> bytes:
        s = s.strip()
        kw, _, rest = s.partition(b" ")
        try:
            parent = int(rest.lstrip(b":"))
        except ValueError:
            return s + b"\n"
        survivor = self._nearest_survivor(parent)
        if survivor is None:
            return b""  # drop the parent edge -> becomes a root commit
        return kw + b" :" + str(survivor).encode() + b"\n"

    def _handle_tag(self, out: list[bytes]) -> None:
        out.append(self._take_line())  # "tag <name>"
        while not self._at_end():
            s = self._peek_line().strip()
            if s == b"":
                out.append(self._take_line())
                return
            if s.startswith(b"from "):
                line = self._take_line()
                try:
                    target = int(line.strip().split(b" ")[1].lstrip(b":"))
                    survivor = self._nearest_survivor(target)
                except (IndexError, ValueError):
                    survivor = None
                if survivor is not None:
                    out.append(b"from :" + str(survivor).encode() + b"\n")
                continue
            if s.startswith(b"data "):
                header, body = self._take_data_block()
                out.append(header)
                out.append(body)  # byte-exact, same contract as everywhere else
                continue
            out.append(self._take_line())

    # -- ref remapping -----------------------------------------------------

    def _nearest_survivor(self, mark: int) -> int | None:
        if self._surviving.get(mark) is not None:
            return self._surviving[mark]
        seen = set()

        def dfs(m):
            if m is None or m in seen:
                return None
            seen.add(m)
            if self._surviving.get(m) == m:
                return m
            for p in self._parents.get(m, []):
                res = dfs(p)
                if res is not None:
                    return res
            return None

        return dfs(mark)

    _KEEP_REF_PREFIXES = (b"refs/heads/", b"refs/tags/")

    def trailing_resets(self) -> bytes:
        """Emit explicit `reset <ref> from :<survivor>` commands AFTER all commits.

        Fast-import assigns a ref to the *last* commit emitted for that ref.
        When a ref's tip commit is dropped (author removed), that assignment is
        lost, so we state it explicitly, pointing each ref at its deepest
        surviving ancestor (mirroring git-filter-repo behaviour).
        """
        lines = []
        for ref, tip in self._ref_tips.items():
            if not ref.startswith(self._KEEP_REF_PREFIXES):
                continue
            survivor = self._nearest_survivor(tip)
            if survivor is None:
                continue  # whole lineage dropped; leave to the importer
            lines.append(b"reset " + ref + b"\n")
            lines.append(b"from :" + str(survivor).encode() + b"\n")
        return b"".join(lines)


def run_rewrite(workdir: Path, plan, audit, expire_gc: bool = True) -> dict:
    proc = run_git(["fast-export", "--use-done-feature", "--branches", "--tags"],
                   workdir, binary=True)
    transformer = StreamTransformer(plan)
    transformed = transformer.transform_stream(proc.stdout)

    # drop any trailing 'done' we may have copied, then append explicit refs
    body = transformed.rsplit(b"done\n", 1)[0]
    final_stream = body + transformer.trailing_resets() + b"done\n"

    imp = subprocess.run(
        ["git", "fast-import", "--quiet", "--force"],
        cwd=str(workdir),
        input=final_stream,
        capture_output=True,
    )
    if imp.returncode != 0:
        raise GSError(
            f"fast-import failed:\n"
            f"{imp.stdout.decode('utf-8', errors='replace')}\n"
            f"{imp.stderr.decode('utf-8', errors='replace')}"
        )

    branches = [b.strip() for b in run_git(
        ["branch", "--format=%(refname:short)"], workdir).stdout.splitlines() if b.strip()]
    default = next((b for b in branches if b in ("main", "master")), branches[0] if branches else None)
    if default:
        run_git(["checkout", "-f", default], workdir)

    if expire_gc:
        run_git(["reflog", "expire", "--expire=now", "--all"], workdir)
        run_git(["gc", "--prune=now", "--quiet"], workdir)

    dropped = sum(1 for v in transformer._surviving.values() if v is None)
    kept = sum(1 for v in transformer._surviving.values() if v is not None)
    audit.log(
        "rewrite_complete",
        backend="fast-export/fast-import (byte-cursor, binary-safe)",
        commits_kept=kept,
        commits_dropped=dropped,
    )
    return {"commits_kept": kept, "commits_dropped": dropped}


if __name__ == "__main__":  # pragma: no cover
    import argparse as _argparse
    _p = _argparse.ArgumentParser(
        prog="gitsanitize_rewrite.py",
        description=(
            "gitsanitize library module: rewrite.py. This is implementation, "
            "not a standalone CLI -- run scripts/gitsanitize.py instead, "
            "which is the real entry point and imports this module itself."
        ),
    )
    _p.parse_args()  # no arguments defined: --help prints usage and exits 0;
                      # any unexpected argument is argparse's own clean
                      # "unrecognized arguments" error (exit 2), not a traceback
