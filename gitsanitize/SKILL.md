---
name: gitsanitize
description: Interactive-by-default git history identity sanitization. Scans a repo
  for every author identity, walks you through classifying anything unrecognized (bot,
  agent, or a real human byline that needs merging), generates a fail-closed plan,
  and rewrites history only after you confirm -- never dropping a commit unless a
  reviewed rule explicitly says to. Verifies binary content byte-for-byte before and
  after any rewrite, keeps a hash-chained audit log, and backs up before touching
  anything. Zero-install; run the bundled script directly, no pip/pipx/PATH setup
  required. Use when preparing a repo to be shown externally (investors, public release,
  a new collaborator) and commit authorship needs to be correct rather than accidental
  -- consolidating duplicate identities, dropping automated bot noise, or deliberately
  protecting specific identities (an agent's own commits, a co-founder's) from being
  touched.
version: 0.2.5
previous_version: 0.2.4
license: MIT
metadata:
  tags:
  - git
  - history
  - identity
  - sanitization
  - security
  - devops
  - compliance
  openclaw:
    category: devops
    priority: high
  hermes:
    category: devops
    related_skills:
    - guardrail-enforcement
    - loop-enforcer
  providers:
  - openai
  - claude
  - mistral
  - gemini
  - hermes
  - copilot
  - any
---

# gitsanitize

Fixes commit authorship in a git repository's history without touching
anything else: no commit is dropped unless a reviewed rule explicitly says
to, tree content is verified byte-identical before and after, and nothing
gets force-pushed without a confirmed prompt.

## Why this exists

A repo's commit history accumulates identities nobody chose on purpose:
a local machine's default git config (`user@localhost`), a case-typo
variant of the same name, an autonomous agent committing under its own
name, a persona name that happens to use a real email. Before a repo goes
in front of anyone external, that needs to be *correct*, not just
whatever accumulated by accident -- and it needs to be correct without
losing a single commit's content, timestamp, or message.

Manually rewriting git history to fix this is exactly the kind of
operation that goes wrong quietly: a `git filter-branch` or hand-rolled
`rebase -i` that silently corrupts a binary file, drops the wrong commits,
or force-pushes before anyone actually reviewed the plan. gitsanitize
exists so that class of mistake is structurally hard to make.

## Zero-install

```bash
python3 scripts/gitsanitize.py                    # interactive wizard, default
python3 scripts/gitsanitize.py --repo /path scan   # any raw subcommand

python3 scripts/sanitize.py                        # same wizard, short form:
python3 scripts/sanitize.py /path/to/repo           # path first, no --repo,
python3 scripts/sanitize.py /path/to/repo scan      # verifies it's a real
                                                     # git repo before anything
```

That's it. No `pip install`, no `pipx`, no `PYTHONPATH`. `gitsanitize.py`
finds the rest of the implementation from its own location on disk at run
time -- drop this skill directory anywhere, on any machine, and it works.
The implementation is flat sibling modules in `scripts/`, one file per
engine, each independently readable:

| Module | Responsibility |
|---|---|
| `sanitize.py` | Short, path-first front door: `sanitize [path] [subcommand...]`, defaulting to the current directory and verifying it's a real git repo first. Delegates to `gitsanitize_cli.py`, no reimplemented logic. |
| `gitsanitize_cli.py` | Command dispatch, the wizard, argument parsing |
| `gitsanitize_core.py` | git subprocess helpers, errors, hashing |
| `gitsanitize_config.py` | Self-resolving paths, layered policy loading |
| `gitsanitize_identity.py` | Manual rules, bot detection, similarity clustering |
| `gitsanitize_policy.py` | Turns scan + policy into a plan; fail-closed validation |
| `gitsanitize_rewrite.py` | The byte-cursor stream transformer (see [references/binary-safety.md](references/binary-safety.md)) |
| `gitsanitize_scanner.py` | Read-only history scan |
| `gitsanitize_state.py` | Backup, session/rollback, ACID-style checkpoints |
| `gitsanitize_verify.py` | Post-rewrite verification against baseline |
| `gitsanitize_audit.py` | Hash-chained, tamper-evident audit log |
| `gitsanitize_plugins.py` | Optional pre/post-stage hook dispatch |
| `gitsanitize_yamlx.py` | Stdlib-only YAML fallback (used when PyYAML isn't installed) |

If you want the bare `gitsanitize` and `sanitize` words on your shell PATH
for convenience, run `scripts/install_alias.sh` -- it is entirely
optional, asks before it touches your shell config, and tells you exactly
what lines it adds.

## Interactive by default

Run the script with no arguments and it walks the full pipeline for you,
stopping to ask at every point that matters:

```
scan -> classify -> plan -> review -> apply -> publish
```

1. **scan** -- read-only. Lists every author identity and commit-message
   trailer found in history.
2. **classify** -- for every identity that isn't already a known bot
   (matched against a provider database) or covered by an existing rule,
   asks you directly: keep it as-is, merge it into another identity, or
   remove it. Your answer is written as a reusable rule (global by
   default, so the same call applies to every repo you scan afterward,
   not just this one) -- so you are never asked about the same identity
   twice.
3. **plan** -- generates the concrete list of merges/removals from your
   classifications plus the bundled bot/provider database. Fail-closed:
   a removal with no rule behind it blocks the plan from being applied at
   all, on purpose (see [references/safety-model.md](references/safety-model.md)).
4. **review** -- shows you every merge and removal the plan contains and
   asks you to confirm each one individually before it can be applied.
5. **apply** -- backs up the repo first (a full mirror clone), then
   rewrites history. Confirms before doing anything. Verifies afterward
   that commit count, tree content, and binary blobs are unchanged except
   for what the plan explicitly changed.
6. **publish** -- confirms, then force-pushes with `--force-with-lease`
   (aborts if the remote moved since you last saw it) rather than a bare
   `--force`.

Every one of those is also a standalone subcommand
(`gitsanitize.py scan`, `gitsanitize.py apply`, ...) for scripted or CI
use -- see [references/workflow.md](references/workflow.md) for the full
command reference and flags.

## What it will never do

- Drop a commit because of a fuzzy match. Automatic identity clustering
  only ever *merges* look-alike identities (rewrites the author line);
  it never removes one. Removal only ever happens from an explicit rule
  (a provider-database bot match, or something you personally classified).
- Silently rewrite in place with no way back. Every `apply` creates a full
  backup clone first; `gitsanitize.py rollback` restores it.
- Push without an explicit confirmation, or push in a way that could
  silently clobber someone else's concurrent push (`--force-with-lease`,
  never bare `--force`).
- Touch binary content. Every rewrite is verified byte-for-byte against
  the original for every blob in history, not just checked for "did it
  run without error." See
  [references/binary-safety.md](references/binary-safety.md) for exactly
  what broke the first time this was built and how it's tested now.

## References

- [references/workflow.md](references/workflow.md) -- full command
  reference, every subcommand and flag, non-interactive/CI usage.
- [references/identity-resolution.md](references/identity-resolution.md)
  -- how an identity gets matched: provider database, manual rules,
  similarity clustering, and the priority order between them.
- [references/policy-layers.md](references/policy-layers.md) -- how
  classifications persist as reusable, layered policy rules (global vs.
  per-repo scope, how a later rule can override an earlier one on
  purpose, how conflicts fail closed instead of silently picking one).
- [references/safety-model.md](references/safety-model.md) -- the
  fail-closed validation gate, backup/rollback, and the verification
  checks that run after every rewrite.
- [references/binary-safety.md](references/binary-safety.md) -- the
  byte-cursor stream parser, why line-based parsing of a git fast-export
  stream cannot be made safe for binary content, and how this is tested.
- [references/troubleshooting.md](references/troubleshooting.md) --
  real errors you can hit and what they actually mean.