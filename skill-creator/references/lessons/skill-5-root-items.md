---
title: Every skill has exactly 5 root items — assets/ is banned everywhere
category: validation
failure: skill-creator's own SKILL.md "anatomy" diagram included assets/ as a valid root item (copied from an outdated 1.0.0 template); an "assets" skill was separately imported from a remote as a top-level skill; three existing skills had rogue assets/ subdirs left over from the old scaffolding template
root_cause: An outdated scaffolding template treated assets/ as a legitimate category alongside scripts/ and references/, and that assumption propagated into the doc, an import, and several skills
resolution: Established assets/ as banned everywhere in a skill tree (root, nested under references/, nested under scripts/) — self-contained resources get embedded in the specific script/reference that consumes them, with a purpose-scoped filename
prevention: The scaffolder must never create assets/; the validator must FAIL any skill with an assets/ directory found anywhere in the tree, and must FAIL if references/ contains any subdirectory other than templates/ or lessons/
date: unknown
verified: true
---

The canonical root layout of every skill is exactly 5 items: `__init__.py`, `SKILL.md`,
`scripts/`, `references/` (may contain nested `templates/` and/or `lessons/` — their
presence does not change tier), and `<skill_name>.skill`. Nothing else at the root — no
`README.md`, `CHANGELOG.md`, `TODO.md`, `notes.md`, `INSTALLATION_GUIDE.md`, or OS
metadata.

**Current behavior note:** this lesson originally asserted the auto-fixer "MUST delete
`assets/` dirs" unconditionally. The actual, current `auto_fix.py` is more conservative
than that: it deletes an `assets/` directory only if it's already empty; a non-empty
`assets/` is left in place and reported for a human to redistribute into `scripts/` or
`references/` (the validator still FAILs it either way). Any file at the root that isn't
one of the 5 items gets moved to `scripts/` or `references/` by extension — never
renamed in batch.
