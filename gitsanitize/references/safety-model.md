# Safety model

## Fail-closed plan validation

Before `apply` ever runs, `validate_plan_fail_closed()` checks two things
and refuses to proceed if either fails:

1. Every trailer removal in the plan must be backed by a `trailer_rule` in
   the loaded policy. No guessing that a message-body pattern is safe to
   strip.
2. Every author removal must be justified — by a provider/bot database
   match, **or** by a manual `remove` rule (from `classify` or a
   hand-written layer). An unjustified removal blocks the entire apply
   with a `SafetyError`, not a warning.

This second check was actually broken for a while during this tool's own
development: the code only ever checked the provider database, despite its
own docstring and error message both promising manual rules counted too —
meaning a `classify`-recorded removal could never actually pass. Fixed by
checking `policy.identity_rules` for a matching `remove` rule as an
equally valid justification. Mentioned here because it's exactly the kind
of gap this safety layer exists to prevent elsewhere, and it's worth
knowing the check is real and tested, not just present.

## Backup before anything irreversible

`apply` creates a full mirror-clone backup (`git clone --mirror`) before
touching the working repo, every time, unconditionally. `rollback`
restores from the most recent one. The backup is never deleted
automatically — keep it until you're confident you don't need it.

## Verification after every rewrite

Comparing before/after, and blocking (in strict mode, the default) if any
of these don't match expectations:

- **Commit count** — must never be *lower* than baseline minus whatever
  the plan's removals account for; that's data loss, always a hard
  failure. Higher is not automatically a problem: `publish` re-runs this
  same check later, and ordinary work continuing between `apply` and
  `publish` is normal and must not be blocked forever. The real question
  for a higher count is whether the HEAD recorded right after `apply`
  finished is still an ancestor of the current HEAD (`git merge-base
  --is-ancestor`) — if so, everything since is fast-forward growth on top
  of the rewrite and that's fine, no matter how much of it there is. If
  not, that's history having been altered again in a way that isn't a
  simple continuation, and it still fails closed.
- **Author list** — everyone from before is still present after, except
  identities the plan intentionally merged away or removed.
- **Branches and tags** — none silently lost.
- **`git fsck --full`** — zero errors.
- **Banned trailers** — none of the patterns the plan was supposed to
  strip are still findable.

All of these are scoped to `refs/heads/*` and `refs/tags/*` — the same
scope `git fast-export --branches --tags` actually rewrites. An earlier
version of this check used `--all`, which also counts
`refs/remotes/origin/*`. Since a local rewrite correctly never touches
remote-tracking refs (they're supposed to stay stale until you fetch or
push again), that inflated the "after" count on literally any repo that
has ever had a remote — which is every real repo — and looked exactly
like commit duplication even though nothing was wrong. Fixed to measure
the same scope that gets rewritten, not everything reachable.

## Publish: `--force-with-lease`, never bare `--force`

`--force-with-lease` refuses to push if the remote has moved since you
last fetched it — it protects against silently overwriting a concurrent
push you didn't know about. Bare `--force` has no such check.

## Tamper-evident, not tamper-proof

The audit log (`audit.log`) is hash-chained: each entry includes a hash of
the previous one, so a modified or deleted entry breaks the chain
detectably. That's a real, verified property — but it's *detection*, not
*prevention*. Anyone with filesystem access could still truncate the log
file entirely, chain and all. Say "tamper-evident," never "tamper-proof,"
per FOREVER-SYSTEM §4.

## What "irreversible" actually means here

`apply` rewrites the working repo's history in place. That's not
undoable by itself — but the backup clone means the *operation* is
reversible via `rollback`, right up until you run `publish`. After
`publish`, the rewritten history is what's on the remote; anyone else's
existing clone or fork still has the old history and will need to reset
to the new one, not merge or pull normally.
