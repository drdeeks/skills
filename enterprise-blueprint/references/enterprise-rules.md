# Enterprise Rules Reference

The complete enforcement rule set for enterprise blueprints: mandatory
compliance requirements, the full validation check catalog, error
classification, and recovery procedures for every failure mode.

## Table of Contents

1. [Mandatory Compliance Requirements](#1-mandatory-compliance-requirements)
2. [Validation Check Catalog](#2-validation-check-catalog)
3. [Error Classification](#3-error-classification)
4. [Recovery Procedures](#4-recovery-procedures)
5. [Enforcement Hierarchy](#5-enforcement-hierarchy)
6. [Compliance Verification Schedule](#6-compliance-verification-schedule)

---

## 1. Mandatory Compliance Requirements

These requirements are non-negotiable. A blueprint that does not meet all
FAIL-class requirements may not be used as the basis for production
implementation. Staging implementation may proceed at the team's discretion
but all FAILs must be resolved before the first production deployment.

### Document Integrity

- The blueprint must be the single source of truth. Any system characteristic
  described elsewhere (in a wiki, in a PR description, in a Slack message)
  that is not reflected in the blueprint is unofficial and carries no
  authority.
- The change log is append-only with no exceptions. No prior entry may be
  edited, redacted, or deleted under any circumstance. Corrections are
  made via new entries.
- Every change log entry must reference at least one Module ID from the
  Module Registry. An entry that cannot reference a module indicates that
  either the module registry is incomplete or the change is undocumented.
- The checklist version must match the blueprint version at all times.
  A version mismatch (blueprint at 1.2, checklist at 1.1) constitutes
  a compliance violation that blocks phase progression.

### Structural Completeness

- All seven required parts must be present (Part I through Part VII).
  A part may be sparse during early phases but it must exist as a named
  section with its rollback tag applied.
- Every module in Part II must have a corresponding feature flag. A module
  without a flag cannot be disabled in production — this violates the
  rollback hierarchy.
- Every Phase section in Part VI must have a rollback procedure defined.
  The rollback procedure must be specific (names the flag, migration file,
  or deployment action) — not generic ("roll back the code").

### Change Safety

- Every database migration must have a rollback migration file committed
  in the same PR. No forward migration may merge without its rollback.
- Feature flags must be created and confirmed disabled in production before
  any code for that feature merges to the main branch.
- No business logic may live in the client. All validation, authorization,
  and data transformation logic must be server-side. This is a security
  and rollback requirement, not just an architectural preference.

---

## 2. Validation Check Catalog

The following is the complete catalog of checks run by `validate_blueprint.py`.
Each check lists its classification (FAIL or WARN), what it validates, and
the fix guidance.

### FAIL — Must Fix Before Production

| Check | What It Validates | Fix |
|---|---|---|
| blueprint.md exists and is readable | File present and UTF-8 readable | Create via `init_blueprint.py` or check path |
| Version number in header | `Version N.N` in first 500 chars | Add `## Version 1.0` to document header |
| READ FIRST preamble | Authority statement in first 1000 chars | Add the READ FIRST blockquote from the standard template |
| PART I present | `# PART I` heading exists | Add the System Overview part |
| PART II present | `# PART II` heading exists | Add the Module Registry part |
| PART III present | `# PART III` heading exists | Add the Specifications part |
| PART IV present | `# PART IV` heading exists | Add the Data Architecture part |
| PART V present | `# PART V` heading exists | Add the Change Control part |
| PART VI present | `# PART VI` heading exists | Add the Implementation Checklist part |
| PART VII present | `# PART VII` heading exists | Add the Quality Standards part |
| At least 1 PHASE tag | `[PHASE-N-v1]` exists | Add phase tags to implementation phases |
| Vision Statement | Section 1.1 present | Add a 1.1 Vision Statement subsection |
| Module ID column | `Module ID` in registry table | Add the four-column registry table |
| Change Log entry format | `Date :` or `YYYY` pattern in change log | Add the CL entry format block to Part V |
| Contributor Rules | `Contributor Rules` heading | Add the six contributor rules to Part V |
| CHANGE LOG section | `# CHANGE LOG` heading | Add the change log section after Part VII |
| At least one CL entry | `## CL-` heading | Add the initialization CL-000 entry |
| Migration naming convention | `YYYYMMDD` pattern | Add migration naming rule to Part V |
| At least 1 module (MOD-NNN) | `MOD-NNN` in content | Populate the module registry |
| At least 1 feature flag | `FEAT_` pattern | Add feature flags to module registry |
| Error Handling Standards | `Error Handling Standards` heading | Add the five-level error hierarchy to Part VII |
| Testing Requirements | `Testing Requirements` heading | Add coverage targets to Part VII |
| Performance Budgets | `Performance Budgets` heading | Add metric budgets table to Part VII |

### WARN — Should Fix Before Staging

| Check | What It Validates | Fix |
|---|---|---|
| Date in header | `Generated YYYY-MM-DD` in first 500 chars | Add the generation date to the header |
| Table of contents | TOC block present | Add the standard TABLE OF CONTENTS code block |
| 6+ section rollback tags | Six or more `[TAG-vN]` patterns | Add rollback tags to all major sections |
| SYS-OVERVIEW tag | `SYS-OVERVIEW` in a tag | Add `[SYS-OVERVIEW-v1]` to Part I |
| MODULE-REGISTRY tag | `MODULE-REGISTRY` in a tag | Add `[MODULE-REGISTRY-v1]` to Part II |
| SPECS tag | `SPECS` in a tag | Add `[SPECS-v1]` to Part III |
| DATA-ARCH tag | `DATA-ARCH` in a tag | Add `[DATA-ARCH-v1]` to Part IV |
| CHANGE-CONTROL tag | `CHANGE-CONTROL` in a tag | Add `[CHANGE-CONTROL-v1]` to Part V |
| QUALITY tag | `QUALITY` in a tag | Add `[QUALITY-v1]` to Part VII |
| 3+ modules defined | Three or more `MOD-NNN` patterns | Define all planned modules |
| 3+ feature flags | Three or more `FEAT_` patterns | Add flags for all modules |
| Append-only rule stated | `append-only` or `permanent` text | Add the append-only statement to the change log section |
| Database schema present | `CREATE TABLE` or `PRIMARY KEY` | Add SQL schemas to Part IV |
| API contracts present | `/api/v` or `POST /` pattern | Add endpoint list to Part IV |
| p95 budget specified | `p95` or `percentile` pattern | Add p95 target to performance budgets table |
| Test coverage target | `coverage` percentage pattern | Add coverage % target to testing requirements |
| Circuit breaker policy | `circuit breaker` or `exponential backoff` | Add retry/circuit breaker to error handling standards |
| Architecture section | Section with `architecture` in title | Add the 1.2 High-Level Architecture subsection |
| Tech Stack section | `tech stack` heading | Add the 1.3 Tech Stack subsection with rationale table |
| No [TODO] markers | Zero `[TODO` occurrences | Replace all placeholder markers with real content |
| ≤5 unfilled placeholders | Fewer than 6 `[Define`/`[Describe` patterns | Populate the blueprint before marking phases complete |
| Document substantial | > 100 lines | Add missing content — a short blueprint is an incomplete blueprint |

---

## 3. Error Classification

All errors produced by the enterprise-blueprint scripts follow this
four-class taxonomy.

**Class A — Structural (FAIL):** The blueprint is missing a required component.
No implementation work may begin on affected phases until resolved. These
errors indicate the specification is incomplete.

**Class B — Convention (WARN):** The blueprint exists but does not follow
the enterprise convention for a specific element. Staging implementation
may proceed, but these must be resolved before production. These errors
indicate technical debt in the documentation itself.

**Class C — Sync (operational):** The checklist has diverged from the
blueprint, or `assignments.json` is inconsistent with `project.json`. These
do not block implementation but they reduce the reliability of the enforcement
system. Resolve within one working day of detection.

**Class D — Process (audit):** A contributor rule was violated (missing change
log entry, missing rollback file, business logic in the client). These are
detected by CI checks or during code review. They require a corrective change
log entry and a process retrospective note. They never block hotfixes in
production but must be addressed in the next sprint.

---

## 4. Recovery Procedures

### Class A Recovery (Structural FAIL)

1. Run `validate_blueprint.py --verbose` to enumerate all FAILs.
2. Fix FAIL items in the order they appear in the validation report
   (earlier FAILs often cause later FAILs to appear spuriously).
3. After fixing a batch of related FAILs, re-run the validator rather
   than fixing all FAILs before any re-validation. This prevents cascading
   fixes that inadvertently introduce new issues.
4. When all FAILs are resolved, re-run `generate_checklist.py --sync`
   to propagate any structural changes into the checklist.
5. Write a change log entry documenting what was added and why it was
   missing from the initial document.

### Class B Recovery (Convention WARN)

The same process as Class A, but WARNs may be batched across multiple
sessions. Each batch of WARN fixes is committed as a single PR with a
single change log entry labeled `Convention Compliance — CL-NNN`.

### Class C Recovery (Sync)

Run `generate_checklist.py --sync` and `assign_agents.py --report`. Review
the output for divergence. If phases have been added to the blueprint but
are absent from the checklist, the sync adds them. If `assignments.json`
references phases that no longer exist in `project.json`, remove the stale
entries manually and write a change log entry noting the correction.

### Class D Recovery (Process Violation)

1. Write a corrective change log entry immediately. The entry must include:
   what rule was violated, what was done without the rule being followed,
   and what remediation has been applied.
2. If the violation involved a missing rollback file: create the rollback
   file retroactively, test it against a staging database, and reference
   it in the corrective change log entry.
3. If the violation involved business logic in the client: move the logic
   server-side as a P1 task. Do not defer this to a future sprint.
4. Append a process note to the relevant phase block in the checklist
   documenting the violation for future reference.

### Emergency Rollback

If production must be rolled back while the blueprint is in mid-phase:

1. Disable the relevant feature flags immediately (no deployment required
   for a flag-only rollback).
2. Assess whether the flag disable resolves the issue. If yes, document
   and stop here.
3. If a code rollback is required: deploy the previous release tag. Log
   the deployment in the change log.
4. If a database rollback is required: obtain two-contributor approval,
   take a point-in-time backup, execute the rollback migration file,
   and verify schema integrity. Log every step in the change log.
5. Write a post-incident change log entry within 24 hours covering what
   happened, what was rolled back, what data (if any) was affected, and
   what the remediation plan is.

---

## 5. Enforcement Hierarchy

The enforcement system has four independent layers, each providing a
different class of protection. All four layers must be active on a
compliant project.

**Layer 1 — Schema enforcement (database):** INSERT-only triggers on
`global_change_log` and other audit tables. Prevents modification of
immutable records at the database level. This layer operates even if
application code is compromised.

**Layer 2 — CI enforcement (repository):** The `CHANGELOG.md` append-only
check that fails PRs attempting to modify existing lines. The migration
rollback file check. The test coverage threshold. These run on every push
and every PR merge attempt.

**Layer 3 — Script enforcement (development):** `validate_blueprint.py`
run as a pre-implementation gate. Produces the scored report. Should be
run at the start of every phase and before every production deployment.

**Layer 4 — Process enforcement (governance):** The contributor rules,
the two-approver requirement for database rollbacks, the gate-based phase
progression, and the agent sign-off requirements. These cannot be automated
but are documented clearly enough to be auditable.

When layers conflict (e.g., a developer bypasses the CI check with a force
push), the highest layer takes precedence. A force push does not make a
change log modification legitimate — it creates a Class D violation that
requires a corrective entry.

---

## 6. Compliance Verification Schedule

Enterprise blueprints should be validated on this schedule throughout the
project lifecycle.

| Trigger | Action | Who |
|---|---|---|
| Before Phase N begins | Run `validate_blueprint.py` | Phase N assigned agent |
| After any blueprint amendment | Run `validate_blueprint.py --verbose`; run `generate_checklist.py --sync` | Amending contributor |
| Before staging deployment | Run `validate_blueprint.py --json`; store result in change log | DevOps role |
| Before production deployment | Run `validate_blueprint.py --json`; must return 0 FAIL | DevOps + Security roles |
| After any production incident | Run `validate_blueprint.py`; assess if incident was caused by a gap in the spec | Architect role |
| Monthly (for long-running projects) | Run `validate_blueprint.py --verbose`; run `assign_agents.py --metrics` | Architect role |

Validation results at staging and production deployment gates must be
stored: the JSON output of `validate_blueprint.py --json` is appended to
the relevant change log entry under an additional `validation_report`
field. This creates a permanent audit trail of the specification quality
at every significant milestone.
