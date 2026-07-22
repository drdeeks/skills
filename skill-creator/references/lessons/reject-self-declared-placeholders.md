---
title: Reject skills that self-declare as placeholders, even from a trusted remote
category: consolidation
failure: Pulled a "skills" skill from a remote whose SKILL.md opened with "**Status:** PLACEHOLDER - This skill needs to be completed," and filed it under in-progress/ reasoning "we'll deal with it later"
root_cause: Assumed the no-stubs policy only applied to authored content, not to imports, and that a lower tier (in-progress/) was an acceptable place to park an admitted placeholder
resolution: User corrected immediately — placeholders never enter the working set, regardless of tier; the skill was excluded
prevention: Any import (remote, USB, local directory, tarball) must grep SKILL.md for self-declared placeholder markers before writing the destination file, and skip + report the skip if any match, at every tier including in-progress/
date: unknown
verified: true
---

The specific patterns to reject (case-insensitive):
- `PLACEHOLDER` appearing as a status label (e.g. `**Status:** PLACEHOLDER`)
- "This skill needs to be completed"
- "Placeholder for" at the start of a `description:` field
- "## Placeholder Notice" or similar section headers

**What this does NOT apply to:**
- References to the concept of placeholders in prose (e.g. "the validator detects
  placeholder patterns") — that's describing behavior, not declaring the skill itself
  incomplete.
- Skills whose content has placeholder-tier scripts but a substantive SKILL.md — those
  get flagged by the validator's per-file substance check, not by this import filter.
