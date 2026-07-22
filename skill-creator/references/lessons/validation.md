---
title: Session residue (unfenced transcripts, absolute paths) corrupts lesson files
category: validation
failure: Raw shell transcripts were pasted into a lesson file — unfenced commands, stray docstring delimiters, absolute home-directory paths — which corrupted the lesson's readability and tripped the content scanners (placeholder/hardcoded-path checks)
root_cause: Lesson files were written by pasting session output directly instead of distilling it into context/cause/resolution/prevention
resolution: Rewrote the affected lessons to record only the distilled facts, with any necessary commands inside fenced code blocks using placeholder-free, portable paths
prevention: A lesson records context, cause, resolution, and prevention in prose — not a raw transcript; any commands that must be shown go in fenced code blocks with portable (non-absolute, non-username-bearing) paths
date: unknown
verified: true
---

Several other validation rules were established alongside this one and are already
enforced directly rather than restated here (avoid duplicating the same rule in two
places): SKILL.md body length stays under the pipeline's line limit (see SKILL.md
itself); enterprise script/reference/tag minimums are documented in
`references/standards.md`; external sources need resolvable documentation links
(`verify_sources.py`); and work-marker hygiene (never let a live `TODO`/`FIXME`/placeholder
marker appear outside of quoted/fenced discussion of the concept) is enforced by
`validate.py`'s placeholder scan — the fix for a scanner flag is always to rephrase the
content, never to weaken the scanner.
