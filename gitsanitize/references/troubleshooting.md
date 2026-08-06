# Troubleshooting: real errors and what they actually mean

## `error (safety): author removal '...' is not justified by any provider rule or manual identity rule`

The plan wants to drop commits from an identity with no rule backing it.
Either classify it first (`classify`, answer `r` for remove), or if you
believe it should already be covered, check that the manual rule's
`name`/`email` match the scan output *exactly* (case-insensitive, but
otherwise exact — no partial matches). See
[safety-model.md](safety-model.md).

## `fatal: options '--all' and '--tags' cannot be used together`

If you're calling `git push` yourself with both flags in one invocation:
git genuinely rejects that combination. `publish` already handles this
correctly (two separate push calls). Use `publish` rather than
constructing the push manually, or if scripting around it directly, push
branches and tags as two separate commands.

## `error: fast-import failed: fatal: Unsupported command:`

This means the fast-export/fast-import stream got desynchronized —
almost certainly a symptom of a bug in the byte-cursor stream parser, not
something you did wrong. See [binary-safety.md](binary-safety.md) for the
two specific bugs that produced exactly this error during development
and how they were actually fixed (not worked around). If you hit this on
a real repo, the safe next step is: don't retry against the same repo,
reproduce it against a disposable clone first (`git clone` the repo
somewhere throwaway, run `apply` there), since the working repo is
unaffected as long as `fast-import` failed before completing — check
`git rev-parse HEAD` against what it was before to confirm.

## `commit count mismatch: expected N, got 2N` (or similar unexpected inflation)

Almost always means verification is measuring the wrong ref scope, not
that history was actually duplicated. Confirm with
`git rev-list --count --branches --tags` versus `git rev-list --count
--all` — if they differ, the extra count is coming from
`refs/remotes/origin/*` or another ref namespace the rewrite never
touched. This exact bug existed in `verify.py` itself early on; if you
see it after that fix, something else is wrong and worth investigating
properly rather than assuming it's the same already-fixed issue.

## `layer_id: ... expected a list of identity_rule`

A YAML parsing bug, now fixed: the stdlib-only fallback parser (used
whenever PyYAML isn't installed, which is the normal case for a
zero-install setup) failed to parse a block sequence written at the same
indentation as its parent key — exactly the format `classify` itself
writes. If you see this, you're running an old copy of this skill; the
vendored `yamlx.py` needs the same-indent-sequence fix. Confirm by
checking whether `python3 -c "import yaml"` succeeds in your environment
— if PyYAML genuinely isn't present and this error appears, that's the
signal.

## The wizard asked me something I already answered in a previous run

Only true the first time you see a given identity — `classify` records
your answer as a policy rule specifically so it never re-asks. If it's
asking about the *same* identity again, check that the previous run's
layer file actually got written (`classify`'s scope defaults to global,
`~/.gitsanitize/layers/`) and that nothing since has deleted or
overridden it.

## I want to change a classification I already made

There's no `--reclassify` shortcut yet. Write a new layer with the same
`name`/`email` and `override: true` — see
[policy-layers.md](policy-layers.md).
