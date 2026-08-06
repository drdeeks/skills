#!/usr/bin/env python3
"""Identity Resolution Engine: similarity scoring, clustering, bot
classification. This is the ONLY module that merges/removes authors."""
from __future__ import annotations

import re

PROVIDER_DOMAINS = {
    "gmail.com": {"googlemail.com"},
    "googlemail.com": {"gmail.com"},
    "users.noreply.github.com": {"github.com"},
}


def _norm_email(email: str) -> str:
    return (email or "").strip().lower()


def _norm_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def jaro(a: str, b: str) -> float:
    if a == b:
        return 1.0
    la, lb = len(a), len(b)
    if la == 0 or lb == 0:
        return 0.0
    match_dist = max(la, lb) // 2 - 1
    match_dist = max(match_dist, 0)
    a_match = [False] * la
    b_match = [False] * lb
    matches = 0
    for i in range(la):
        start = max(0, i - match_dist)
        end = min(i + match_dist + 1, lb)
        for j in range(start, end):
            if b_match[j] or a[i] != b[j]:
                continue
            a_match[i] = True
            b_match[j] = True
            matches += 1
            break
    if matches == 0:
        return 0.0
    transpositions = 0
    k = 0
    for i in range(la):
        if not a_match[i]:
            continue
        while not b_match[k]:
            k += 1
        if a[i] != b[k]:
            transpositions += 1
        k += 1
    m = matches
    return (m / la + m / lb + (m - transpositions / 2) / m) / 3.0


def jaro_winkler(a: str, b: str) -> float:
    j = jaro(a, b)
    if j > 0.7:
        prefix = 0
        for ca, cb in zip(a, b):
            if ca != cb:
                break
            prefix += 1
            if prefix == 4:
                break
        return j + prefix * 0.1 * (1 - j)
    return j


def email_similarity(e1: str, e2: str) -> float:
    e1, e2 = _norm_email(e1), _norm_email(e2)
    if not e1 or not e2:
        return 0.0
    if e1 == e2:
        return 1.0
    d1 = e1.split("@")[-1]
    d2 = e2.split("@")[-1]
    lp1 = e1.split("@")[0]
    lp2 = e2.split("@")[0]
    # same local part across provider-alias domains
    if lp1 == lp2 and (d1 in PROVIDER_DOMAINS and d2 in PROVIDER_DOMAINS[d1]
                       or d2 in PROVIDER_DOMAINS and d1 in PROVIDER_DOMAINS[d2]):
        return 0.95
    if d1 == d2 and lp1 != lp2:
        jw = jaro_winkler(lp1, lp2)
        return 0.4 + 0.5 * jw
    # same local part, different domain
    if lp1 == lp2:
        return 0.6
    jw = jaro_winkler(lp1, lp2)
    if jw > 0.85:
        return 0.55 + 0.3 * (jw - 0.85) / 0.15
    return 0.0


def identity_similarity(a: dict, b: dict) -> float:
    """0..1 confidence that two author identities are the same person."""
    name_sim = jaro_winkler(_norm_name(a.get("name", "")), _norm_name(b.get("name", "")))
    email_sim = email_similarity(a.get("email", ""), b.get("email", ""))
    if email_sim >= 1.0:
        return 1.0
    # same name (normalized identical)
    if _norm_name(a.get("name", "")) and _norm_name(a.get("name", "")) == _norm_name(b.get("name", "")):
        return max(email_sim, 0.85)
    if name_sim > 0.8 and email_sim > 0.5:
        return (name_sim + email_sim) / 2
    return max(name_sim, email_sim)


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1


def match_providers(author: dict, providers: list[dict]) -> dict | None:
    """Return the strongest matching provider entry, if any."""
    best = None
    best_score = 0
    haystack = f"{author.get('name','')} {author.get('email','')}"
    for p in providers:
        pat = p.get("id_pattern")
        if not pat:
            continue
        try:
            if re.search(pat, haystack, re.IGNORECASE):
                score = p.get("confidence", 50) or 50
                if score > best_score:
                    best, best_score = p, score
        except re.error:
            continue
    return best


def is_bot(author: dict, providers: list[dict], remove_threshold: int = 95) -> bool:
    prov = match_providers(author, providers)
    if prov and (prov.get("confidence", 0) or 0) >= remove_threshold:
        return True
    low = f"{author.get('name','')} {author.get('email','')}".lower()
    hints = ("[bot]", "bot@", "dependabot", "renovate", "github-actions")
    return any(h in low for h in hints)


def resolve(authors: list[dict], policy, providers: list[dict]) -> list[dict]:
    """Compute merge/remove decisions.

    Manual identity rules are pinned (highest priority) and take precedence
    over clustering for deciding canonical targets. Clustering runs only over
    identities not covered by a manual rule or provider/bot removal.
    """
    threshold_auto = policy.thresholds["auto_merge_threshold"]
    threshold_suggest = policy.thresholds["suggest_threshold"]
    remove_threshold = policy.thresholds["remove_confidence"]

    decisions = []

    def _manual_for(author: dict):
        best = None
        for rule in policy.identity_rules:
            action = rule.get("action", "merge")
            if (rule.get("name") or "").lower() == (author.get("name") or "").lower() and \
               (rule.get("email") or "").lower() == (author.get("email") or "").lower():
                to_name = rule.get("to_name") or author["name"]
                to_email = rule.get("to_email") or author["email"]
                conf = float(rule.get("confidence", 99) or 99)
                best = {
                    "action": action,
                    "to_name": to_name, "to_email": to_email,
                    "confidence": conf,
                    "reason": f"manual rule (layer {rule.get('_layer_id', '?')})",
                }
        return best

    pinned_idx = set()

    # 1. manual rules + bot/provider removals -> pin identities
    #
    # Manual rules are checked, IN FULL, before the bot/provider heuristic
    # gets a vote — that's what "manual rules are pinned (highest priority)"
    # above actually means. A `keep`/`merge` rule for an identity that also
    # happens to match the provider DB (e.g. deciding a bot's commits should
    # be preserved rather than dropped) must win; the bot heuristic only
    # gets to decide for authors nobody has made an explicit call on.
    for idx, author in enumerate(authors):
        manual = _manual_for(author)

        if manual and manual["action"] == "remove":
            pinned_idx.add(idx)
            decisions.append({
                "from_name": author["name"], "from_email": author["email"],
                "to_name": author["name"], "to_email": author["email"],
                "confidence": manual["confidence"],
                "reason": manual["reason"], "action": "remove",
            })
            continue
        if manual and manual["action"] in ("keep", "ignore"):
            # Explicit "leave this identity alone" — pins it out of
            # clustering with no merge/remove decision emitted. Distinct
            # from an author `resolve()` has simply never seen: this one
            # was deliberately reviewed and dismissed, so it must not keep
            # resurfacing as unclassified on every future scan.
            pinned_idx.add(idx)
            continue
        if manual and manual["action"] == "merge":
            pinned_idx.add(idx)
            decisions.append({
                "from_name": author["name"], "from_email": author["email"],
                "to_name": manual["to_name"], "to_email": manual["to_email"],
                "confidence": manual["confidence"],
                "reason": manual["reason"], "action": "merge",
            })
            continue

        # No manual rule at all for this identity — only now does the
        # provider/bot heuristic get to decide.
        prov = match_providers(author, providers)
        if is_bot(author, providers, remove_threshold):
            pinned_idx.add(idx)
            conf = prov.get("confidence", 100) if prov else 100.0
            decisions.append({
                "from_name": author["name"], "from_email": author["email"],
                "to_name": author["name"], "to_email": author["email"],
                "confidence": float(conf),
                "reason": f"bot detected ({prov.get('name', 'heuristics') if prov else 'heuristics'})",
                "action": "remove",
            })

    # 2. clustering over the remaining (unpinned) identities
    remaining = [i for i in range(len(authors)) if i not in pinned_idx]
    if len(remaining) >= 2:
        uf = UnionFind(len(remaining))
        edges = []
        for a in range(len(remaining)):
            for b in range(a + 1, len(remaining)):
                ia, ib = remaining[a], remaining[b]
                score = identity_similarity(authors[ia], authors[ib])
                if score >= threshold_suggest / 100.0:
                    edges.append((score, a, b))
        edges.sort(reverse=True, key=lambda e: e[0])
        for score, a, b in edges:
            if score >= threshold_auto / 100.0:
                uf.union(a, b)
        groups: dict[int, list[int]] = {}
        for a in range(len(remaining)):
            groups.setdefault(uf.find(a), []).append(a)
        for g in groups.values():
            if len(g) < 2:
                continue
            g_sorted = sorted(g, key=lambda x: -authors[remaining[x]]["count"])
            canonical = authors[remaining[g_sorted[0]]]
            for pos in g_sorted[1:]:
                a = authors[remaining[pos]]
                pair_score = identity_similarity(a, canonical) * 100
                if pair_score >= threshold_suggest:
                    decisions.append({
                        "from_name": a["name"], "from_email": a["email"],
                        "to_name": canonical["name"], "to_email": canonical["email"],
                        "confidence": round(pair_score, 1),
                        "reason": "identity clustering",
                        "action": "merge",
                    })

    # dedupe by from-identity; keep highest confidence
    seen = {}
    for d in decisions:
        key = (d["from_name"].lower(), d["from_email"].lower(), d["action"])
        if key not in seen or d["confidence"] > seen[key]["confidence"]:
            seen[key] = d
    out = [
        d for d in seen.values()
        if d["action"] == "remove"
        or (d["from_name"], d["from_email"]) != (d["to_name"], d["to_email"])
    ]
    return out


def find_unclassified(authors: list[dict], policy, providers: list[dict]) -> list[dict]:
    """Authors `resolve()` silently drops: no provider/bot match, no manual
    identity_rule (merge/remove/keep), and no identity-similarity cluster
    partner. These are identities nobody has ever actually made a decision
    about — as opposed to ones an operator reviewed and explicitly chose to
    leave alone (a "keep" rule), which are classified and must not
    resurface. `gitsanitize classify` surfaces exactly this list."""
    remove_threshold = policy.thresholds["remove_confidence"]
    decided_from = {
        (d["from_name"].lower(), d["from_email"].lower())
        for d in resolve(authors, policy, providers)
    }

    def _has_manual_rule(author: dict) -> bool:
        for rule in policy.identity_rules:
            if (rule.get("name") or "").lower() == (author.get("name") or "").lower() and \
               (rule.get("email") or "").lower() == (author.get("email") or "").lower():
                return True
        return False

    out = []
    for a in authors:
        key = (a["name"].lower(), a["email"].lower())
        if key in decided_from:
            continue
        if _has_manual_rule(a) or is_bot(a, providers, remove_threshold):
            continue
        out.append(a)
    return out


if __name__ == "__main__":  # pragma: no cover
    import argparse as _argparse
    _p = _argparse.ArgumentParser(
        prog="gitsanitize_identity.py",
        description=(
            "gitsanitize library module: identity.py. This is implementation, "
            "not a standalone CLI -- run scripts/gitsanitize.py instead, "
            "which is the real entry point and imports this module itself."
        ),
    )
    _p.parse_args()  # no arguments defined: --help prints usage and exits 0;
                      # any unexpected argument is argparse's own clean
                      # "unrecognized arguments" error (exit 2), not a traceback
