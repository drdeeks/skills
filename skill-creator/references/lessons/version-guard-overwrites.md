---
title: Never overwrite a skill with a lower-version copy; commit every skill change
category: consolidation
failure: A bulk overwrite blindly replaced a just-merged skill-creator v2.1.0 with an older v0.0.10 copy from another source — the 816-line validator got replaced with a 96-line "quick" validator. Recovered from a docker-context backup, but only by luck; hours of merge work could have been lost permanently
root_cause: The overwrite ran as a raw copy loop with no version comparison at all
resolution: Recovered the v2.1.0 merge from backup; established a version-guard gate before any overwrite
prevention: Before overwriting any versioned artifact, compare SKILL.md frontmatter version and only overwrite if source > destination (skip or ask otherwise, logging the skip); commit every skill change, however small, so history stays granular and recoverable without relying on luck
date: unknown
verified: true
---

**How to apply:**
1. Overwrite gate: before copying source over target, parse both `SKILL.md` frontmatter
   versions as semver. If `src_ver < target_ver`, skip (or ask the user); log the skip.
2. Any batch merge that touches skills should go through this version-guard, not a raw
   copy loop.
3. Git checkpoint per skill change: after any successful edit to a skill (edit, upgrade,
   package, consolidate), commit that skill's directory with a message naming the
   version and the one-line reason. Keeps history granular and makes recovery reliable
   instead of luck-dependent.
4. When bulk-restoring from a backup, still apply the version-guard — don't assume the
   backup is newer than what's live.

**Failure signature to detect:** if about to run an unconditional overwrite loop (copy
source over target with no check), stop and add the version check first.

See also [verify-beyond-version](verify-beyond-version.md) — the same incident's
follow-up lesson: a version-guard alone isn't sufficient, since a higher version number
doesn't guarantee the content is actually better.
