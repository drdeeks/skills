---
title: Chain State Must Be Atomic
category: chain-enforcement
failure: A half-written state file left the chain in an inconsistent state after a crash.
root_cause: Early versions wrote the state file directly (in place), so a crash mid-write corrupted it.
resolution: Write to a .tmp file, then os.replace() for an atomic rename.
prevention: State persistence is a critical section — treat it like one; the state file must always be either fully old or fully new, never half-written.
date: 2026-07-09
verified: true
---
