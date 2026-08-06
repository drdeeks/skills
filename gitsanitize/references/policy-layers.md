# Policy layers: how a classification persists and where

A classification isn't a one-off answer that only applies to the repo you
happened to be scanning. It's written as a layer — a small YAML file with
an `identity_rules` list — following the same layered-not-rewritten model
FOREVER-SYSTEM §3 describes for everything else in this ecosystem: each
layer has an ID, a timestamp, and (when it needs to override an earlier
one) a `supersedes` pointer. Nothing is ever edited in place.

## Where layers live

```
~/.gitsanitize/layers/*.yaml        global — loaded for every repo, always
<state-dir>/layers/*.yaml           per-repo scope, only if you asked for it
--layer FILE                        explicit, one-off, highest precedence
```

`classify --scope global` (the default) writes to the first location, so a
decision made once — "titan-agent stays," "Hemlock Curator merges into
DrDeeks" — applies automatically to every repo scanned afterward, not just
the one it was recorded against. `--scope repo` writes to the second
location instead, scoped to just that repo's own state directory.

Global layers are loaded independently of a repo's own state-dir
resolution — this is deliberate, not an accident of the state-dir default.
Per-repo working state (the scan report, the generated plan, the audit
log) is namespaced per repo specifically so two different repos never
contaminate each other's plans; identity rules are the opposite case on
purpose, since the whole point is that they generalize.

## Conflicts fail closed, they don't silently pick one

If two layers map the exact same (name, email) to two different targets,
loading raises a `SafetyError` — unless the newer layer's rule is marked
`override: true`, or the newer layer's `supersedes` list names the older
layer's ID. This is the same principle as everywhere else in this
codebase: an ambiguous state blocks rather than guesses.

## Rule shape

```yaml
layer_id: classify-1785957200
source: "gitsanitize classify (interactive)"
timestamp: 1785957200
supersedes: []
identity_rules:
- name: "Hemlock Curator"
  email: "mr.anon.juice@gmail.com"
  to_name: "DrDeeks"
  to_email: "drdeeks@outlook.com"
  action: "merge"        # merge | remove | keep
  confidence: 99
  override: true          # only needed when replacing an earlier layer's answer
```

## Changing your mind about a past decision

`classify` won't re-ask about an identity that already has a rule —
that's the entire point, it's supposed to stop asking once you've
answered. To correct a rule you already recorded, write a new layer with
the same `name`/`email` and `override: true`. There is currently no
`classify --reclassify` shortcut for this; hand-writing (or generating)
the override layer is the supported path today.
