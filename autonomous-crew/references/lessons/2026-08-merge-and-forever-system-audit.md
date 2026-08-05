---
title: Merging the two autonomous-crew-integration lineages under FOREVER-SYSTEM.md
category: architecture
date: 2026-08-05
failure: >
  Two divergent lineages of this skill existed with the same name: a "bare"
  copy (v1.1.19) that re-embedded identity/self-healing/chain-enforcement
  scripts directly, and a "v2/v1.5" copy (v1.1.14, byte-identical to each
  other) that split knowledge management into a separate crew-knowledge-system
  skill and documented self-healing/chain-enforcement scripts in its SKILL.md
  that were never actually shipped in its own scripts/ directory — every
  script in v2 that called enforcer_daemon.py, agent_runtime.py,
  memory_curator.py, start-agent.sh, or chain_enforce.py would have failed at
  runtime with a missing-file error.
root_cause: >
  The bare and v2 lineages diverged from a common ancestor without either
  side re-syncing: bare kept re-implementing chain_enforce.py as a local
  fork (with a hardcoded Hermes-install-relative path, no env override) instead of
  routing through loop-enforcer's canonical chain_enforce.py, and its own
  create-blueprint-chain.py / crew-manager.py wrote chain state to a
  .blueprint-chain/ directory that loop-enforcer's chain.py never looks in
  (it only reads .chain/) — so even a correctly-routed chain_enforce.py call
  would have found nothing.
resolution: >
  Took v2 as the skeleton (its modular architecture and richer reference
  docs), pulled in bare's 10 scripts that v2's own SKILL.md and callers
  referenced but never shipped, and fully absorbed crew-knowledge-system's
  scripts/references directly into this skill (per drdeeks: crew knowledge
  sharing "is directly associated and should be used by any crew," not an
  optional companion). Deleted the vendored chain_enforce.py entirely and
  added scripts/resolve_loop_enforcer.py — a self-resolving locator (env
  override, then the global Claude Code skills directory, then the Hermes
  runtime skills install, then fail closed) that finds loop-enforcer's real
  chain_enforce.py instead of vendoring a second copy of its state machine
  (FOREVER-SYSTEM.md Sec 1:
  singular source of truth, route through the one runtime). Renamed every
  .blueprint-chain/ reference across 6 scripts to .chain/ so this skill's own
  chain-creation code (create-blueprint-chain.py, crew-manager.py) writes to
  the one location loop-enforcer's chain.py actually reads — the producer
  was changed to match the canonical consumer, not the other way around.
  Also fixed a dead/broken AGENT_IDENTITY_SKILL override in
  create-crew-agent.sh (bash ${VAR:-default} syntax embedded verbatim inside
  a Python heredoc, where it just assigned a literal unexpanded string that
  could never resolve to a real path) and a missing `import os` in
  install-identity-skill.py.
prevention: >
  Before merging or forking any skill that documents scripts it doesn't
  ship, grep the SKILL.md and every caller for references to files that
  should exist in scripts/ and confirm they're actually present — a skill
  that only "looks complete" from its SKILL.md prose is not verified
  complete. Any script that reaches into another skill's directory for a
  file must resolve via env override -> known home-relative candidates ->
  fail-closed error, never a single hardcoded path — and if the functionality
  that file provides is common/enforcement-shaped (chain gating, character
  enforcement), check FOREVER-SYSTEM.md Sec 1 first: it may belong to a
  single canonical runtime this skill should call into, not vendor.
verified: true
---
