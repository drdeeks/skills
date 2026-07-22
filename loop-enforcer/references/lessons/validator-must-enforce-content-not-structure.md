---
title: Validator Must Enforce Content, Not Just Structure
category: validation
failure: Agent could write garbage (2 lines, no class, has placeholder) and pass verification.
root_cause: Initial validator only checked file existence, line count, and placeholder patterns — never what the file was actually supposed to contain.
resolution: Unified validate.py with required patterns, forbidden patterns, min chars, syntax check, and custom checks.
prevention: A chain enforcer is only as good as its validator. If the validator doesn't enforce what the file SHOULD contain, the chain is theater.
date: 2026-07-09
verified: true
---
