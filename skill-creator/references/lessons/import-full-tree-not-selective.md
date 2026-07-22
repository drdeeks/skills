---
title: Import the whole tree, never selectively pick one item and drop the rest
category: consolidation
failure: User asked to copy a 217-skill directory from USB alongside the existing skills; after cross-referencing just skill-creator, the entire imported tree was deleted, losing 216 skills the user wanted kept for later consolidation
root_cause: Treated "delete the old copy" (meant for the one cross-referenced skill) as license to delete the whole import tree it came from
resolution: Corrected by the user; re-established that imported material is preserved until explicitly told the whole tree is done
prevention: When asked to bring over/copy/import/pull in a directory, import the entire tree, not just the piece needed for the immediate task; when told to delete "the old copy" after a cross-reference, delete only the specific item referenced, never the tree it came from
date: unknown
verified: true
---

Even if the immediate purpose is a cross-reference on one item, the user's broader intent
is usually to have all the source material available for follow-up consolidation and
merging.

**How to apply:**
- If unsure whether "delete X" means "delete only X" vs "delete the whole thing X came
  from," ask before removing anything
- For same-named-skill overlaps between imported and existing sets, merge/dedupe (keep
  the more-complete version, surface the differences) — don't blindly overwrite either side
- For similar-but-not-identical variants (e.g. `8004`, `8004scan`, `8004scan-webhooks`),
  keep as separate directories for later manual consolidation; don't force-merge on
  name-similarity alone
