# Blueprint Standard Reference

Complete specification of the enterprise blueprint structure: required parts,
section anatomy, rollback tag conventions, module registry format, screen
specification format, change log protocol, and quality thresholds.

## Table of Contents

1. [Required Document Structure](#1-required-document-structure)
2. [Document Header Standard](#2-document-header-standard)
3. [Part-by-Part Specification](#3-part-by-part-specification)
4. [Rollback Tag Convention](#4-rollback-tag-convention)
5. [Module Registry Format](#5-module-registry-format)
6. [Screen & Feature Specification Format](#6-screen--feature-specification-format)
7. [Change Log Protocol](#7-change-log-protocol)
8. [Amendment Procedure](#8-amendment-procedure)
9. [Quality Thresholds](#9-quality-thresholds)

---

## 1. Required Document Structure

Every enterprise blueprint MUST contain exactly these seven parts in order.
Additional parts may be appended but may not replace or reorder these seven.

```
PART I    — SYSTEM OVERVIEW & ARCHITECTURE
PART II   — MODULE REGISTRY
PART III  — SCREEN & FEATURE SPECIFICATIONS
PART IV   — DATA ARCHITECTURE
PART V    — CHANGE CONTROL PROTOCOL
PART VI   — MASTER IMPLEMENTATION CHECKLIST
PART VII  — QUALITY & COMPLIANCE STANDARDS
CHANGE LOG (appended after Part VII)
```

Each part opens with a Rollback Tag block and a brief statement of authority.
No part may be omitted, even if sparse at initialization — a placeholder is
preferable to a missing part.

---

## 2. Document Header Standard

The document header appears before the table of contents and must include
all four of the following elements:

```markdown
# Project Name — ENTERPRISE BLUEPRINT
## Version N.N | Document Class: MASTER SPECIFICATION
### Generated: YYYY-MM-DD

> **READ FIRST — DOCUMENT AUTHORITY**
> [Authority statement — at minimum 2 sentences stating this is the source
> of truth, that no changes may be made without it as reference, and that
> the change log is append-only.]
```

Version must increment on every formal amendment. A minor amendment (fixing
a factual error or adding a screen spec) increments the minor version (1.0 →
1.1). A structural amendment (adding a Part, changing the module registry
architecture) increments the major version (1.x → 2.0).

---

## 3. Part-by-Part Specification

### Part I — System Overview & Architecture

Required subsections:

| Subsection | Requirement |
|---|---|
| 1.1 Vision Statement | 2-3 sentences on what, who, and defining principle |
| 1.2 High-Level Architecture | ASCII diagram showing all layers |
| 1.3 Tech Stack | Table: Layer, Technology, Rationale |

Every technology choice must include a rationale. "Existing convention" is
a valid rationale. "No reason" is not.

### Part II — Module Registry

Required format: a table with exactly four columns — Module ID, Name,
Description, Feature Flag. Every module that will be developed must appear
here before implementation begins. The module registry is the authoritative
index of the system's components.

Module IDs follow the format `MOD-NNN` where NNN is zero-padded to three
digits. IDs are permanent — if a module is removed, its ID is retired, not
reassigned.

### Part III — Screen & Feature Specifications

Every screen or feature system is specified using this template:

```
SCREEN/FEATURE ID   — e.g. SCR-001 or FEAT-AUTH
MODULE REF          — MOD-NNN
ROLLBACK TAG        — [SECTION-NAME-v1]
FEATURE FLAG        — FEAT_FLAG_NAME
PURPOSE             — One sentence
COMPONENTS          — Bulleted list of all UI or logic elements
RULES               — Mandatory behavioral constraints (numbered)
ERROR STATES        — Every failure case and its user-facing handling
FALLBACK            — Degraded state if dependencies fail
```

No component may be listed without a corresponding rule. No rule may exist
without a testable definition of "passes."

### Part IV — Data Architecture

Required subsections:

| Subsection | Requirement |
|---|---|
| 4.1 Core Database Schemas | SQL CREATE TABLE statements for all tables |
| 4.2 API Contract Specifications | Endpoint list with method, path, description |

Every table must include: primary key, created_at, updated_at. Every
INSERT-only table (audit logs, change logs, resumés) must carry a comment
noting its insert-only nature and must have a corresponding database-level
trigger enforcing this.

### Part V — Change Control Protocol

Must contain: the full change log entry format with all required fields, the
contributor rules (minimum 6 rules), and the rollback procedure hierarchy
(flag → API → database → emergency).

### Part VI — Master Implementation Checklist

Each phase section must include: the section rollback tag, the feature flag,
the assigned agent field, the prerequisite statement, deliverables, a
validation gate statement, and a rollback procedure.

### Part VII — Quality & Compliance Standards

Must contain: error handling standards (the 5-level hierarchy), testing
requirements (unit, integration, E2E with coverage targets), and performance
budgets (at minimum: page load, API p95, background job).

---

## 4. Rollback Tag Convention

Rollback tags are the anchor system that links code changes to specification
sections and enables targeted rollback without full document reversion.

**Format:** `[SECTION-NAME-vN]`

Rules:
- All uppercase, hyphen-separated words.
- Version number starts at 1 and increments on each amendment to that section.
- Applied to every major section via a blockquote immediately after the
  section heading: `> **Rollback Tag:** \`[TAG-NAME-v1]\``
- Referenced in every change log entry via the `Section Tags:` field.
- Every database migration comment header must include the relevant tag.

**Reserved tag stems** (must exist in every blueprint):

| Tag Stem | Section |
|---|---|
| SYS-OVERVIEW | Part I |
| MODULE-REGISTRY | Part II |
| SPECS | Part III |
| DATA-ARCH | Part IV |
| CHANGE-CONTROL | Part V |
| QUALITY | Part VII |
| PHASE-N | Each implementation phase in Part VI |

---

## 5. Module Registry Format

```markdown
| Module ID | Name | Description | Feature Flag |
|---|---|---|---|
| MOD-001 | Auth | User authentication and session management | FEAT_AUTH |
| MOD-002 | Crafting | Core element combination and recipe engine | FEAT_CRAFTING |
```

Rules for the registry:
1. Every module must have a unique, sequential ID.
2. The Feature Flag column must contain a valid `FEAT_` prefixed flag name.
3. The Description column must be one sentence — detailed spec belongs in Part III.
4. Modules are never deleted. Retired modules have their Feature Flag set to
   `FEAT_RETIRED_[NAME]` and a `(retired)` suffix on their description.
5. Every change log entry referencing a code change must cite at least one
   Module ID from this registry.

---

## 6. Screen & Feature Specification Format

The specification must follow this canonical structure for every screen:

```markdown
## Screen N.N — Screen Title

SCREEN ID     : SCR-NNN
MODULE REF    : MOD-NNN
ROLLBACK TAG  : [SCR-NNN-v1]
FEATURE FLAG  : FEAT_SCREEN_NAME

**Purpose:** One sentence.

**Tab Structure:** (if applicable)
[ TAB 1 ] [ TAB 2 ] [ TAB 3 ]

**Components:**
- Component description (be precise — name every UI element)

**Rules:**
1. Rule stated as a testable constraint.
2. Rule stated as a testable constraint.

**Error States:**
- Failure case: user-facing message and system behavior.

**Fallback:** Degraded behavior when primary dependencies are unavailable.
```

Rules for specification quality:
- Components must be precise enough that a developer can implement without
  clarifying questions.
- Every rule must be unambiguous and testable.
- Every error state must define both the user-facing message (friendly,
  non-technical) and the internal system behavior (log, retry, fallback).
- "Unavailable" is not an error state. Define what unavailable means
  (timeout, 5xx, empty response) and what happens in each case.

---

## 7. Change Log Protocol

The change log lives at the bottom of the blueprint document and is
APPEND-ONLY. A database trigger on the `global_change_log` table enforces
this at the persistence layer. The `CHANGELOG.md` CI check enforces it at
the repository layer.

Every entry must include all nine fields:

```
Date        : YYYY-MM-DD HH:MM UTC
Contributor : [name/handle]
Modules     : [MOD-XXX, MOD-YYY]
Section Tags: [[TAG-v1], [TAG-v2]]
Files Changed: [complete list of every file]
Description : [Minimum 3 sentences: what changed, why it changed, what
               impact it has on adjacent systems or the overall specification.]
Tests Passing: [test names — never 'all tests']
Phase       : [PHASE-N]
Rollback Ref: [git commit hash or migration rollback filename]
```

**Correction entries:** If a prior entry contained an error, append a new
entry noting the correction. The prior entry is never modified. The
correction entry carries a note: `Amends CL-NNN: [brief description of
what was wrong and what the correction is]`.

---

## 8. Amendment Procedure

To formally amend a blueprint section:

1. Identify the section by its Rollback Tag stem.
2. Update the section's version: `[SECTION-NAME-v1]` → `[SECTION-NAME-v2]`.
3. Add the amendment note immediately after the document version header:
   `### Amendment: YYYY-MM-DD — [brief description]. See CL-NNN.`
4. Write and append the change log entry with the old and new section tags
   listed under `Section Tags:`.
5. Update `checklist.md` in the same commit if any checklist items are
   affected by the amendment.
6. If the amendment changes a database schema, a new migration + rollback
   file must be created and referenced in the change log entry.

---

## 9. Quality Thresholds

A blueprint is considered enterprise-grade when `validate_blueprint.py`
reports 0 FAIL and 0-4 WARN.

| Rating | FAIL | WARN |
|---|---|---|
| Enterprise Grade | 0 | 0-4 |
| Production Ready | 0 | 5-9 |
| Needs Hardening | 1-3 | any |
| Incomplete | 4+ | any |

A blueprint with any FAIL may not be used as the basis for production
implementation. Staging implementation may proceed at "Needs Hardening" at
the team's discretion, but all FAILs must be resolved before the first
production deployment.
