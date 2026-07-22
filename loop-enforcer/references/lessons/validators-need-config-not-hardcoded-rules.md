---
title: Validators Need Config, Not Hardcoded Rules
category: validation
failure: Unmaintainable validation logic that couldn't combine checks and wasted tokens re-implementing similar logic per script.
root_cause: The first version had three separate validator scripts, each hardcoding a different set of checks.
resolution: Collapsed to a single validate.py with composable flags and a JSON spec file for complex cases.
prevention: Configurable beats hardcoded — one script with options beats multiple single-purpose scripts.
date: 2026-07-09
verified: true
---
