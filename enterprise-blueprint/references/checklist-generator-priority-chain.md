# Checklist Generator — Phase Extraction (Current Behavior)

> **Correction (scope-tier generalization pass):** this document previously
> described a "3-try priority chain" (Part VI complex pattern → SPEC
> headers → PHASE headers fallback) with several documented bugs. That
> chain does not exist in the current `generate_checklist.py` — reading the
> script directly confirms there is exactly **one** phase-extraction path.
> Whether the 3-try chain ever existed in an earlier version or this
> document was aspirational, it no longer matches the code; replaced below
> with what the script actually does.

## The One Path

`ChecklistGenerator.extract_phases()` does two passes over the whole
document, not a fallback chain gated behind blueprint shape:

1. **Phase headers**, always, everywhere in the document:
   ```python
   phase_headers = re.finditer(r"### PHASE-(\d+)[a-z]?: ([^>\n]+)", self.content)
   ```
   Every `### PHASE-N: Title` header becomes a phase, in document order.
   There is no SPEC-NNN grouping path, no Module-Ref-driven phase creation.

2. **Tasks per phase**, tried in this order for each phase:
   - **Part VI table** (primary): locate the phase's own table under its
     `### PHASE-N:` header inside the Part VI block (boundary:
     `#{1,2}\s*PART\s+VI\b` through the next `#{1,2}\s*PART\s+`/`CHANGE LOG`
     heading or end of document — fixed to match the actual `# PART VI`
     single-hash heading `init_blueprint.py` generates; the old `## PART
     VI` boundary never matched a real blueprint). Table columns are
     matched **by header name**, not fixed position — a `Deliverables`
     column, wherever it sits, maps correctly; likewise `Validation
     Gate`/`Gate`, `Prerequisite`, `Feature Flag`, `Rollback`. Each
     deliverable cell is comma/semicolon-split into one task per item, and
     each item may carry a trailing `Type: file|glob|approval|external-check`
     (optionally `Validator: <path>`) tag — see
     `references/blueprint-standard.md` §6.
   - **Checkbox fallback**: if no table task was found for that phase,
     `- [ ] **PHASE-N.M** <text>` checkbox lines within the phase's own
     section (from its header to the next `### PHASE-` header) become
     tasks instead. This is what `init_blueprint.py`'s own scaffold
     produces by default.

There is no SPEC-header path and no separate Module-Ref regex in
`extract_phases()` — module extraction is a completely separate function
(`extract_modules()`) that only reads the Part II registry table, unrelated
to phase/task extraction.

## Practical Guidance

- Use `### PHASE-N: Title` headers in Part VI — this is the only header
  format `extract_phases()` recognizes, at any scope tier.
- Prefer the Part VI table format (it carries `validation`/`rollback`/
  `prerequisite`/`feature_flag` per task); the checkbox fallback only
  carries a description, no structured metadata.
- If a table isn't producing tasks, the most common cause is a
  `Deliverables`-named column not being present in the header row at all
  (an empty/missing header cell) — not column *order*, since order no
  longer matters.
