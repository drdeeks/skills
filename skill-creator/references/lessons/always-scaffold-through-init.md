---
title: Always scaffold new skills through skill-creator's own init tooling
category: scaffolding
failure: A new skill (autowatch) was hand-crafted directly — SKILL.md, scripts/, and references/ written by hand — instead of going through skill-creator's scaffolder
root_cause: Skipped skill-creator's init/scaffold step entirely, which also skipped standardized __init__.py generation and the packager's version registry
resolution: Adopted the rule that every new skill starts from skill-creator's own scaffold output, then gets content filled in — never authored from an empty file
prevention: Before writing any file for a new skill, run the scaffolder first and build on the generated skeleton; always finish with package_skills.py so version tracking stays consistent
date: unknown
verified: true
---

Any new skill must be created through `skill-creator`'s tooling, not by hand-crafting
`SKILL.md` + `scripts/` + `references/` files directly. Bypassing it means the new skill
exists outside the process and will drift.

**How to apply:**
- Before writing any file for a new skill, first run the scaffolder and get the skeleton
- Fill in the scaffold content, don't create fresh from empty
- Always end with `package_skills.py` so version tracking + manifest stay consistent
- When writing skills for other tools (Hemlock agents, USB management, etc.), those
  tools should still invoke skill-creator internally rather than reimplementing scaffolding

**Historical note:** at the time this lesson was written, the correct flow used a script
named `init_skill.py` (later `scaffold_skill.py` in other lineage branches), and this
lesson itself flagged that the script wasn't actually present in `scripts/` — "the
missing script is itself a bug in skill-creator that needs fixing." It was never fixed;
instead the scaffolder moved to `__init__.py`'s `scaffold()` function (invoked as
`python3 __init__.py --scaffold <name> --path <destination>`), and SKILL.md's own prose
kept citing the old phantom script name for multiple versions afterward. This lesson is
the earliest on-record instance of that exact failure mode.
