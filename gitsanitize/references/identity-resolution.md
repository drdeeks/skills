# Identity resolution: how a decision actually gets made

For every author identity found by `scan`, exactly one of these paths
decides what happens to it. The order below is the real priority order in
`identity.py`'s `resolve()` — manual rules are checked in full, for every
possible action, before the bot/provider heuristic ever gets a vote.

## 1. Manual rule (highest priority, checked first, in full)

A rule from `policy.identity_rules` — populated from layered policy files,
most often written by `classify` — matched by exact (name, email). Three
possible actions:

- `remove` — pinned, this identity's commits are dropped entirely.
- `keep` (or `ignore`) — pinned, no merge or removal decision is emitted
  at all. This is deliberate: an identity you explicitly reviewed and
  chose to leave alone must not keep resurfacing as "unclassified" on
  every future `classify` run, and it must not accidentally get swept
  into a bot-removal or a clustering merge either.
- `merge` — pinned, rewritten to the rule's `to_name`/`to_email`.

**Only if no manual rule matches at all** does the bot/provider heuristic
get consulted for that identity. A `keep` or `merge` rule for something
that also happens to match the bot database wins — you can explicitly
decide "yes, this looks like a bot pattern, but I want it kept" and that
decision holds.

## 2. Provider/bot detection

Checked only for identities with no manual rule. Two mechanisms:

- A regex match against the bundled provider database
  (`data/providers.json` — Dependabot, Renovate, GitHub Actions, Copilot,
  Codecov, and others), each with a confidence score.
- A cheap heuristic fallback: `[bot]`, `bot@`, `dependabot`, `renovate`,
  `github-actions` appearing in the name or email.

A match here removes the identity's commits entirely (same as a manual
`remove` rule) — but only if the plan's fail-closed validation later finds
this justification real (see [safety-model.md](safety-model.md); a manual
rule and a provider match are the only two things that count).

## 3. Identity-similarity clustering

Only runs over whatever's left after steps 1 and 2 have pinned everything
they're going to pin. Pairwise similarity (Jaro-Winkler on names,
domain-aware comparison on emails — `gmail.com`/`googlemail.com` and
`users.noreply.github.com`/`github.com` are treated as equivalent-provider
pairs) feeds a union-find clustering pass. Two thresholds from policy
control it: `suggest_threshold` (minimum to even be considered a match)
and `auto_merge_threshold` (minimum to actually union two identities).

**Clustering only ever merges.** It has no removal action. The most
active identity in a cluster (by commit count) becomes the canonical
target; everything else in the cluster gets rewritten to it.

## What "unclassified" actually means

An identity is unclassified — the thing `classify` surfaces — when none of
the three mechanisms above produced a decision for it: no manual rule, no
bot match, and no clustering partner within threshold. This is exactly
the set of authors `resolve()` would otherwise silently drop from its
output with zero explanation. `classify` exists because that silent gap
is the actual problem: an identity nobody has ever looked at should never
be indistinguishable from one that was reviewed and deliberately left
alone (which is why `keep` is a real, first-class action and not just
"don't answer").
