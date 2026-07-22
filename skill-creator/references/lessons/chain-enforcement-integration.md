---
title: Chain enforcement for the 11-gate enterprise pipeline
category: chain-enforcement
failure: The skill_enhance.py pipeline needed to enforce 11 sequential gates (scaffold → frontmatter → scripts → refs → validate → auto_fix → re_validate → test → verify_sources → package → extract_verify) with no skipping or reordering, and had no mechanism to do so
root_cause: No dependency-tracking layer existed yet for multi-step, must-not-skip pipelines
resolution: Integrated a chain-enforcement layer (originally the separate loop-enforcer skill's chain.py) — a temp workdir outside the skill root holds one marker file per gate, each gate must verify+complete before the next unlocks, and the workdir is always cleaned up in a finally block
prevention: Any future multi-step, must-not-skip pipeline (CI/CD, build systems, deploy scripts) should use this same verify-then-complete chain pattern rather than ad-hoc dependency tracking
date: unknown
verified: true
---

Key properties of the pattern: the skill root stays clean (no `.chain/` or
`.chain-steps/` directories left behind — all chain state lives in a temp dir under
`/tmp/chain-skill-<name>-<random>/`), each pipeline phase is its own locked step, and
external agents can check `chain.py check` before touching files.

**Superseded:** this lesson originally described delegating to a separate `loop-enforcer`
skill's `chain.py`. That external dependency was later replaced by a vendored,
self-reliant copy at `scripts/chain.py` inside skill-creator itself — no other skill
required by default (an external `loop-enforcer` can still be used via the
`LOOP_ENFORCER_ROOT` env override). The pattern described here is still correct; the
delivery mechanism changed.
