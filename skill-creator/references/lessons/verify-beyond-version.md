---
title: Newer version number does not mean better content — cross-verify before overwriting
category: consolidation
failure: A blind bulk overwrite during consolidation replaced a just-merged skill-creator v2.1.0 with a "drdeeks" copy checked in as v0.0.10 — an older, less-complete version that happened to be processed last and win a naive last-write-wins pass; separately, the 816-line validator got replaced with a 96-line "quick" validator
root_cause: The overwrite had no version guard at all (not even the newer-wins rule), and even a naive version guard wouldn't be sufficient on its own — a higher version number doesn't guarantee the content is more accurate, complete, or unbroken
resolution: Recovered from a docker-context backup; established that every "take this version" decision during consolidation must be cross-verified against multiple signals, not just version number
prevention: Cross-verify version number, validator pass status (basic + enterprise), substance check (no stubs/placeholders), cross-reference completeness, self-declared status, and script functionality before choosing a side in any consolidation — never trust version number alone
date: unknown
verified: true
---

**Decision matrix** for src-vs-dst comparison during consolidation:

| Src version | Dst version | Src validates | Dst validates | Winner |
|---|---|---|---|---|
| Newer | Older | pass | pass | src |
| Newer | Older | fail | pass | **dst** (don't downgrade quality just for a version bump) |
| Newer | Older | pass | fail | src |
| Newer | Older | fail | fail | flag to user |
| Same | Same | pass | pass | either (dst by default) |
| Older | Newer | * | * | dst (never overwrite newer with older) |

**How to apply:**
- When importing from a remote / USB / peer directory, run the full validator on BOTH
  sides before choosing
- Report the decision explicitly per skill (e.g. `src=v1.0.1 (validates), dst=v2.0.0
  (fails-substance) → picking src`)
- Never trust a single signal

**Forensic cross-reference:** the "merged skill-creator v2.1.0" this lesson describes
nearly losing is one version-tick behind the `previous_version: 2.1.1` recorded in every
subsequent production copy of this skill (v3.0.8 through the current v3.0.13) — meaning
this incident sits right at the edge of the one gap in the recovered lineage that no
surviving snapshot bridges. The fabricated `package_skills.py` "validate → chmod →
refuse" documentation claim (see the skill's own doc-history findings) most plausibly
originated during manual merge work in this same v2.1.0→2.1.1 window.
