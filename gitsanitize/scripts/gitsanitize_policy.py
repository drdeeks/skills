#!/usr/bin/env python3
"""Policy Engine: turns scan output + layered policy + identity decisions
into an actionable, reviewable cleanup plan, and validates plans
fail-closed before any rewrite is allowed."""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

from gitsanitize_core import GSError, SafetyError, sha256
from gitsanitize_identity import resolve as resolve_identities

PLAN_VERSION = 1


class Plan:
    def __init__(self, data: dict, path: Path | None = None):
        self.data = data
        self.path = path

    @property
    def merges(self) -> list[dict]:
        return self.data.get("identities", {}).get("merges", [])

    @property
    def removals(self) -> list[dict]:
        return self.data.get("identities", {}).get("removals", [])

    @property
    def trailer_removes(self) -> list[dict]:
        return self.data.get("trailers", {}).get("remove", [])

    def effective_mailmap(self) -> list[tuple]:
        """Return [(old_name, old_email, new_name, new_email)] from merges."""
        out = []
        for m in self.merges:
            if m.get("action") != "merge":
                continue
            if m["from_email"] == m["to_email"] and m["from_name"] == m["to_name"]:
                continue
            out.append((m["from_name"], m["from_email"], m["to_name"], m["to_email"]))
        return out

    def dropped_author_emails(self) -> list[str]:
        return [r["from_email"] for r in self.removals]


def _build_trailer_decisions(scan, policy) -> dict:
    remove, keep = [], []
    known = {r["label"].lower(): r for r in policy.trailer_rules}
    for t in scan.trailers:
        rule = known.get(t["label"].lower())
        if rule is None:
            keep.append({"label": t["label"], "pattern": r"^" + re.escape(t["label"]) + r":", "managed": False})
            continue
        if rule.get("action") == "remove":
            remove.append({
                "label": t["label"],
                "pattern": rule.get("pattern", r"^" + re.escape(t["label"]) + r":"),
                "layer": rule.get("_layer_id"),
            })
        else:
            keep.append({"label": t["label"], "pattern": rule.get("pattern", ""), "managed": True})
    return {"remove": remove, "keep": keep}


def generate_plan(scan, policy, providers: list[dict], plan_path: Path) -> Plan:
    classification = scan.classify(policy.repo_classification)
    decisions = resolve_identities(scan.authors, policy, providers)

    merges = [d for d in decisions if d["action"] == "merge"]
    removals = [d for d in decisions if d["action"] == "remove"]
    for r in removals:
        r.pop("_auto", None)
    for m in merges:
        m.pop("_auto", None)

    trailers = _build_trailer_decisions(scan, policy)

    plan = {
        "version": PLAN_VERSION,
        "created_at": time.time(),
        "classification": classification,
        "policy_layers": policy.layer_ids,
        "identities": {"merges": merges, "removals": removals},
        "trailers": trailers,
        "expectations": {
            "total_commits": scan.total_commits,
            "author_count": scan.author_count(),
            "expected_commit_delta": _expected_delta(scan, removals),
        },
    }
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    return Plan(plan, plan_path)


def _expected_delta(scan, removals) -> int:
    """Best-effort: commits that become un-authored once all authors removed.
    We approximate with the sum of removed-author commit counts, capped."""
    emails = {r["from_email"].lower() for r in removals}
    delta = 0
    for a in scan.authors:
        if a["email"].lower() in emails:
            delta += a["count"]
    return delta


def load_plan(path: Path) -> Plan:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise GSError(f"cannot read plan {path}: {exc}")
    if not isinstance(data, dict) or data.get("version") != PLAN_VERSION:
        raise GSError(f"plan {path} is missing or has wrong version")
    return Plan(data, path)


def validate_plan_fail_closed(plan: Plan, policy, providers: list[dict], audit) -> None:
    """Fail-closed checks before applying:
    - every trailer removal must be backed by a policy rule (no guessing)
    - removals must be justified by providers or manual rules
    """
    known = {r["label"].lower() for r in policy.trailer_rules}
    for t in plan.trailer_removes:
        label = t.get("label", "").lower()
        if label not in known:
            raise SafetyError(
                f"trailer removal '{label}' has no policy rule. "
                "Add a trailer_rule layer before applying."
            )
    for a in plan.removals:
        low = a["from_email"].lower()
        low_name = a["from_name"].lower()
        justified_by_provider = any(
            p.get("id_pattern") and re.search(p["id_pattern"], f'{a["from_name"]} {low}', re.IGNORECASE)
            for p in providers
        )
        # A manual `remove` rule (e.g. from `gitsanitize classify`) is an
        # equally valid justification — the docstring and error message below
        # both already promised this; only the provider check was ever wired
        # in, which meant no manually classified removal could ever pass.
        justified_by_rule = any(
            (r.get("action") == "remove")
            and (r.get("name") or "").lower() == low_name
            and (r.get("email") or "").lower() == low
            for r in policy.identity_rules
        )
        justified = justified_by_provider or justified_by_rule
        if not justified:
            raise SafetyError(
                f"author removal '{a['from_name']} <{a['from_email']}>' is not justified by "
                "any provider rule or manual identity rule. Refusing to drop authors blindly."
            )
    audit.log(
        "plan_validated",
        plan=sha256(json.dumps(plan.data, sort_keys=True).encode()),
        layers=policy.layer_ids,
    )


if __name__ == "__main__":  # pragma: no cover
    import argparse as _argparse
    _p = _argparse.ArgumentParser(
        prog="gitsanitize_policy.py",
        description=(
            "gitsanitize library module: policy.py. This is implementation, "
            "not a standalone CLI -- run scripts/gitsanitize.py instead, "
            "which is the real entry point and imports this module itself."
        ),
    )
    _p.parse_args()  # no arguments defined: --help prints usage and exits 0;
                      # any unexpected argument is argparse's own clean
                      # "unrecognized arguments" error (exit 2), not a traceback
