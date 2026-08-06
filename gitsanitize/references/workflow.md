# Workflow: commands and flags

All commands take a common set of top-level flags before the subcommand:

| Flag | Meaning |
|---|---|
| `--repo PATH` | Repository to operate on (default: `.`) |
| `--layer FILE` | Extra policy layer file, repeatable |
| `--state-dir DIR` | Override the auto-resolved state directory |
| `--config FILE` | Explicit config file |
| `--deep` | Deep scan of blob content (scan/plan/classify) |

## `gitsanitize.py` (no subcommand)

Runs the full interactive wizard: `scan -> classify -> plan -> review ->
apply -> publish`, in that order, against the same repo. This is the
default specifically so that "just run it" does the safe, guided thing
rather than printing a usage error. Every step it runs is the exact same
implementation the standalone subcommand uses — the wizard does not
duplicate any logic, it only sequences the existing commands.

```
--yes                          assume yes at every confirmation, including publish
--batch                        non-interactive CI mode (fails closed on anything
                                that would need a real answer, rather than guessing)
--scope {global,repo}          where classify persists new rules (default: global)
--dangerously-skip-safety-checks
--no-verify
```

## `scan`

Read-only. Lists every author identity, commit count per identity, and
every commit-message trailer found in history, plus a repo classification
(PERSONAL / ORGANIZATION / OPEN_SOURCE, used to pick default thresholds).
Writes `scan_report.json` into the state directory.

## `classify`

Interactively surfaces every identity `scan` found that is not already
covered by the bundled provider/bot database or an existing manual rule.
For each one, asks: keep as-is / merge into another identity / remove as
bot-or-agent / skip for now / quit. Recorded decisions are written as a
policy layer — see [policy-layers.md](policy-layers.md) for where and how.

```
--rescan            force a fresh scan first
--scope {global,repo}   global (default): the decision applies to every
                        repo scanned afterward. repo: only this one.
--yes                non-interactive: marks every unclassified identity
                     "keep as-is" (the only safe default with no human
                     answering) and records nothing destructive
--batch              non-interactive: lists unclassified identities and
                     exits, records nothing
```

## `plan`

Generates `cleanup-plan.yaml` from the scan output plus the loaded policy
(provider database + every layered rule). This is where identity
similarity clustering happens for anything with no manual rule — see
[identity-resolution.md](identity-resolution.md) for the exact priority
order between manual rules, bot detection, and clustering.

```
--rescan    re-run scan first instead of using the last scan_report.json
```

## `review`

Prints every merge and removal the plan contains and asks you to confirm
each one individually. Declining a specific item removes it from the plan
before it's written back; it does not cancel the whole run.

## `apply` — the only genuinely irreversible step

1. Confirms.
2. Validates the plan fail-closed (every removal must be justified by a
   provider match or a manual rule — see [safety-model.md](safety-model.md)).
3. Creates a full mirror-clone backup.
4. Snapshots refs and a baseline (commit count, author list, tree state).
5. Rewrites history in place, in the working tree itself.
6. Verifies the result against the baseline: commit count, author list,
   branches, tags, `git fsck`, and any trailers that were supposed to be
   stripped.

```
--yes / --batch / --dangerously-skip-safety-checks
--no-verify         skip the post-rewrite verification (not recommended)
```

## `verify`

Re-runs the same post-rewrite checks `apply` runs, standalone, against an
existing baseline. Useful to re-confirm state without redoing the rewrite.

## `rollback`

Restores the repo from the most recent backup clone. Confirms first.

## `publish`

Re-verifies (unless `--no-verify`), confirms, then pushes with
`--force-with-lease` — two separate invocations under the hood, one for
branches (`--all`) and one for tags (`--tags`), since git rejects combining
those two flags in a single push. Aborts if the remote has moved since you
last fetched it, rather than blindly overwriting.

## Non-interactive / CI usage

Every subcommand respects `--yes`/`--batch` consistently: `--yes` answers
every prompt with the safe default (never a destructive default —
`classify --yes` keeps everything rather than removing anything);
`--batch` refuses to act at all rather than guess, and exits nonzero with
a clear reason. There is no flag that makes `apply` or `publish` skip
their own confirmation entirely without also explicitly saying `--yes`.
