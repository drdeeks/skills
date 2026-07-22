---
title: Comparative questions require reading both files, never theory from analogy
category: consolidation
failure: Asked "what's different between your init_skill and the init at root?", answered with a generic Python-package-marker vs. scaffolder-script analogy instead of the actual diff — and separately produced a 140-line init_skill.py that duplicated logic that should have lived in the existing 26-line __init__.py scaffolder pattern already used across 125 other skills
root_cause: Answered from theory/convention instead of opening and reading the actual files first
resolution: Read both files, found the existing __init__.py scaffolder template, and built on it instead of duplicating
prevention: Any comparative question, overwrite, merge, or import must start by reading the actual files involved (Read, diff, wc -l, head) — the response leads with observed facts (line counts, function names, byte differences), theory second or not at all
date: unknown
verified: true
---

If asked "what's the difference between X and Y" — or any comparative question about
files/scripts/skills — read both files and produce the actual diff or side-by-side
before answering. Never fall back to a theoretical explanation ("X is typically a foo
while Y is typically a bar") without opening the files first.

**Pattern to catch this in real time:** if about to write "typically," "conceptually,"
"in \[language\] conventions," or "usually" in a comparison answer — stop, open the
files, and start over with observed facts.
