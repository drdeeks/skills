---
title: When a validator flags content, rephrase the content — never relax the validator
category: validation
failure: A validator flagged a work-marker word (e.g. `TODO`) used as a meta-concept within a skill about task tracking; the temptation was to weaken the validator's rule or carve out an allowlist exemption for that one skill
root_cause: Treating a validator flag as a signal to soften the rule instead of a signal to reword the content
resolution: Reworded the flagged content (wrapped the term in inline code formatting, or renamed the concept — "task marker," "open-task token") so it conveys the same meaning without tripping the pattern; the validator's rule was left untouched
prevention: Never edit a validator's regex/patterns/allowlist to make one specific skill pass — rephrase the content instead; this applies to validate.py and any similar lint/policy tooling, without exception
date: unknown
verified: true
---

Validators encode a deliberate policy. Once exemptions get added for "this skill is
about X, so it's allowed to trip the rule," the rule erodes one carve-out at a time until
it no longer means anything.

**How to apply:**
- Validator flags a work marker in prose → wrap in inline code formatting or rename the
  concept
- Validator flags a placeholder pattern → choose wording that doesn't pattern-match
  (e.g. "sample input" instead of "your input here")
- Validator flags frontmatter description wording → reword the description
- Never edit the validator's regex/patterns/allowlist to make a specific skill pass

**Correction:** this lesson originally named `skill-scan-validate-resolver/scripts/validate.py`
as a second validator this rule applies to. Per the single-source-of-truth rule
(downstream tooling delegates to skill-creator's own `validate.py` rather than forking
it), there should be exactly one validator this rule needs to name — skill-creator's own.
