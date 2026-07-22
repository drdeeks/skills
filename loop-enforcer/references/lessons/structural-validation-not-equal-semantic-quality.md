---
title: Structural Validation Does Not Equal Semantic Quality
category: validation
failure: A skill passed validate.py (structural) but failed manual review per standards.md.
root_cause: The automated validator only checks file counts and extensions, not content quality.
resolution: Also run verify_sources.py, the manual review checklist, and actually test scripts — not validate.py alone.
prevention: An enterprise-grade result from a structural validator is necessary but not sufficient; treat it as one gate among several, not the whole bar.
date: 2026-07-09
verified: true
---
