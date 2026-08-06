#!/usr/bin/env python3
"""Verification Engine: compares pre/post state to guarantee no surprises.

Runs after apply and before any publish. Any unexpected divergence blocks
completion (fail-closed). Produces a machine-readable report.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from gitsanitize_core import VerificationError, run_git


_REWRITE_SCOPE = ["--branches", "--tags"]
# rewrite.py (via `fast-export --branches --tags`) only ever touches
# refs/heads/* and refs/tags/* -- see StreamTransformer._KEEP_REF_PREFIXES.
# Every metric here must be scoped to that same set, matching --all would
# also pull in refs/remotes/origin/* (untouched, correctly still pointing at
# pre-rewrite history until the next fetch/push) and inflate counts on any
# repo that has ever had a remote -- which is every real repo. That's not a
# corruption signal, it's a scope mismatch between what got rewritten and
# what got measured.


def _post_apply_head(state: Path) -> str | None:
    """The HEAD gitsanitize recorded right after the most recent successful
    `apply` finished (Session.complete()'s "completed" checkpoint), if any."""
    manifest_path = state / "session" / "manifest.yaml"
    if not manifest_path.exists():
        return None
    try:
        import gitsanitize_yamlx as yamlx
        data = yamlx.load(manifest_path)
    except Exception:
        return None
    for entry in reversed(data.get("steps", []) or []):
        if entry.get("step") == "completed" and entry.get("head"):
            return entry["head"]
    return None


def _shortlog(repo: Path):
    """Return {email_lower: (name, count)} and total from git shortlog."""
    proc = run_git(["shortlog", "-sne", *_REWRITE_SCOPE], repo, check=False)
    authors = {}
    total = 0
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            count, rest = line.split("\t", 1)
        except ValueError:
            continue
        count = int(count.strip())
        total += count
        m = rest.rsplit("<", 1)
        if len(m) != 2 or not m[1].endswith(">"):
            continue
        name = m[0].strip()
        email = m[1][:-1].strip().lower()
        authors.setdefault(email, [name, 0])[1] += count
    return authors, total


def _commit_count(repo: Path) -> int:
    proc = run_git(["rev-list", "--count", *_REWRITE_SCOPE], repo, check=False)
    return int(proc.stdout.strip() or 0)


def _fsck(repo: Path) -> list[str]:
    proc = subprocess.run(
        ["git", "fsck", "--full", "--no-dangling"],
        cwd=str(repo), capture_output=True, text=True,
    )
    return [l for l in (proc.stdout + proc.stderr).splitlines() if l.strip()]


def _missing_trailers(repo: Path, patterns: list) -> list[str]:
    found = []
    for pat in patterns:
        proc = subprocess.run(
            ["git", "log", *_REWRITE_SCOPE, "--grep", pat, "-i", "--pretty=format:%H"],
            cwd=str(repo), capture_output=True, text=True,
        )
        found.extend(proc.stdout.splitlines())
    return [h for h in found if h]


def _ref_list(repo: Path) -> dict:
    out = {}
    proc = run_git(["show-ref"], repo, check=False)
    for line in proc.stdout.splitlines():
        parts = line.split(" ", 1)
        if len(parts) == 2:
            out[parts[1]] = parts[0]
    return out


def verify_baseline(repo: Path, plan, state: Path, audit):
    """Capture pre-rewrite metrics into a baseline JSON (used at apply start)."""
    authors, total = _shortlog(repo)
    baseline = {
        "author_count": len(authors),
        "commit_count": _commit_count(repo),
        "refs": _ref_list(repo),
        "author_emails": sorted(authors.keys()),
        "expected_commit_delta": plan.data.get("expectations", {}).get("expected_commit_delta", 0),
    }
    (state / "baseline.json").write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    audit.log("baseline_captured", commit_count=baseline["commit_count"])
    return baseline


def verify(repo: Path, plan, state: Path, audit, strict: bool = True) -> dict:
    base_path = state / "baseline.json"
    if not base_path.exists():
        raise VerificationError("no baseline.json found. Run apply first (captures baseline).")
    baseline = json.loads(base_path.read_text(encoding="utf-8"))

    post_authors, post_total = _shortlog(repo)
    post_commits = _commit_count(repo)
    post_refs = _ref_list(repo)
    fsck_errors = _fsck(repo)
    missing = _missing_trailers(
        repo, [p.get("pattern", "") for p in plan.trailer_removes if p.get("pattern")]
    )

    issues = []

    # commit count: expect baseline - expected_delta (within tolerance).
    #
    # A count LOWER than expected is always a hard failure -- data loss,
    # full stop. A count HIGHER than expected is not automatically a
    # problem: `publish` re-runs this same check against the ORIGINAL
    # apply-time baseline, and ordinary work (new, real commits) between
    # apply and publish is completely normal -- it must not be blocked
    # forever just because verify has no other reference point. The
    # distinction that actually matters: is the HEAD gitsanitize recorded
    # right after apply finished still an ancestor of the current HEAD? If
    # so, everything since then is fast-forward growth on top of the
    # rewrite -- fine. If not (history was altered again in a way that
    # isn't a simple continuation), that's the real red flag and still
    # fails closed.
    expected = baseline["commit_count"] - baseline.get("expected_commit_delta", 0)
    if post_commits < expected:
        issues.append(
            f"commit count mismatch: expected {expected}, got {post_commits}"
        )
    elif post_commits > expected:
        post_apply_head = _post_apply_head(state)
        grew_on_top = False
        if post_apply_head:
            check = subprocess.run(
                ["git", "merge-base", "--is-ancestor", post_apply_head, "HEAD"],
                cwd=str(repo), capture_output=True,
            )
            grew_on_top = check.returncode == 0
        if not grew_on_top:
            issues.append(
                f"commit count mismatch: expected {expected}, got {post_commits} "
                "(could not confirm the extra commits are ordinary growth on top "
                "of the rewrite -- the recorded post-apply HEAD is not an "
                "ancestor of the current one; investigate before publishing)"
            )

    # authors expected to be gone (merged away or removed)
    intentionally_lost = {r["from_email"].lower() for r in plan.removals}
    for m in plan.merges:
        if m["from_email"].lower():
            intentionally_lost.add(m["from_email"].lower())
    for email in baseline.get("author_emails", []):
        if email in intentionally_lost:
            continue
        if email not in post_authors:
            issues.append(f"author '{email}' vanished unexpectedly")

    # branches preserved (by name)
    base_branches = {k for k in baseline.get("refs", {}) if k.startswith("refs/heads/")}
    post_branches = {k for k in post_refs if k.startswith("refs/heads/")}
    missing_branches = base_branches - post_branches
    if missing_branches:
        issues.append(f"branches lost: {sorted(missing_branches)}")

    # fsck
    if fsck_errors:
        issues.append(f"git fsck errors: {fsck_errors[:10]}")

    # leftover trailers
    if missing:
        issues.append(f"banned trailers still present in {len(missing)} commits")

    ok = not issues
    result = {
        "ok": ok,
        "commit_count_before": baseline["commit_count"],
        "commit_count_after": post_commits,
        "author_count_before": baseline["author_count"],
        "author_count_after": len(post_authors),
        "branches_before": len(base_branches),
        "branches_after": len(post_branches),
        "tags_before": len({k for k in baseline.get("refs", {}) if k.startswith("refs/tags/")}),
        "tags_after": len({k for k in post_refs if k.startswith("refs/tags/")}),
        "fsck_errors": len(fsck_errors),
        "banned_trailers_remaining": len(missing),
        "issues": issues,
    }
    state.mkdir(parents=True, exist_ok=True)
    out = state / "verify.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    audit.log("verify_complete", ok=ok, issues=len(issues))

    if strict and not ok:
        raise VerificationError(
            "verification failed:\n  " + "\n  ".join(issues[:10])
        )
    return result


if __name__ == "__main__":  # pragma: no cover
    import argparse as _argparse
    _p = _argparse.ArgumentParser(
        prog="gitsanitize_verify.py",
        description=(
            "gitsanitize library module: verify.py. This is implementation, "
            "not a standalone CLI -- run scripts/gitsanitize.py instead, "
            "which is the real entry point and imports this module itself."
        ),
    )
    _p.parse_args()  # no arguments defined: --help prints usage and exits 0;
                      # any unexpected argument is argparse's own clean
                      # "unrecognized arguments" error (exit 2), not a traceback
