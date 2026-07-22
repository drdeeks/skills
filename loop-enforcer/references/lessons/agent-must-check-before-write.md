---
title: Agent Must Check Before Write
category: chain-enforcement
failure: Chain state said a step was "locked," but the agent wrote to it anyway.
root_cause: Without enforcement on the caller's side, nothing stopped an agent from writing to a file whose step hadn't been unlocked.
resolution: Chain state is the source of truth — the agent must call chain.py check before any file write, and stop if the result is locked.
prevention: The tool enforces; the agent must obey. Both parts are required — a chain engine with no caller discipline is not enforcement.
date: 2026-07-09
verified: true
---
