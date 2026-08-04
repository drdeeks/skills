# Blueprint Standard Reference (v3)

Complete specification of the blueprint structure: scope tiers, required
parts, section anatomy, deliverable types, rollback tag conventions, module
registry format, screen specification format, change log protocol, and
quality thresholds.

## Table of Contents

1. [Scope Tiers](#1-scope-tiers)
2. [Required Document Structure](#2-required-document-structure)
3. [Document Header Standard](#3-document-header-standard)
4. [Part-by-Part Specification](#4-part-by-part-specification)
5. [N/A + Rationale Rule](#5-na--rationale-rule)
6. [Deliverable Type Taxonomy](#6-deliverable-type-taxonomy)
7. [Rollback Tag Convention](#7-rollback-tag-convention)
8. [Module Registry Format](#8-module-registry-format)
9. [Screen & Feature Specification Format](#9-screen--feature-specification-format)
10. [Change Log Protocol](#10-change-log-protocol)
11. [Amendment Procedure](#11-amendment-procedure)
12. [Immutability Check](#12-immutability-check)
13. [Quality Thresholds Per Tier](#13-quality-thresholds-per-tier)
14. [Minimum Completeness Requirements Per Tier](#14-minimum-completeness-requirements-per-tier)

---

## 1. Scope Tiers

A blueprint is written **once**, for whatever scope the assigned task
actually has. Scope changes what depth Parts II–IV need, not whether the
document structure exists — every blueprint, regardless of tier, still has
all seven parts, still uses Part VI as the enforcement source of truth for
`generate_checklist.py`, and still gets a real `chain.py`-gated execution
loop. Scope only changes how much of Parts II–IV must be substantively
populated versus legitimately marked N/A (§5).

| Tier | For | Parts II–IV | Rigor bar |
|---|---|---|---|
| `MICRO` | A trivial single- or few-step task (e.g. "check the weather and report back") | May be `N/A — Rationale: ...` if genuinely inapplicable | Low line-count floor; Part VI (deliverables + validation gates) and Part VII (quality bar for that step) are still real and fully enforced |
| `TASK` | A multi-step assignment or a single feature | Populated proportionately to actual scope; N/A only where genuinely inapplicable, with rationale | Mid line-count floor; at least 1 real module/workstream, at least 1 real feature/deliverable spec |
| `PROJECT` | A full, complete, multi-phase project | Full population required, no N/A allowed on Parts II–IV | Full enterprise bar unchanged from the original standard (1500+ line floor, 50+ line ASCII diagram, 3+ modules, 3+ feature specs, 3+ SQL schemas, 3+ API endpoints, 3+ phase deliverables/gates each) |

**Default is `PROJECT`.** Tiers are an explicit opt-down (`--scope micro` /
`--scope task` on `init_blueprint.py` and `validate_blueprint.py`), never an
opt-up — a caller who doesn't specify scope gets the same full-rigor
behavior the standard has always required, so existing blueprints and
tooling are unaffected.

Declare the tier in the document header (§3): `## Scope: MICRO | TASK |
PROJECT`. `validate_blueprint.py` reads this line and applies the matching
tier's rule set; `--scope` on the CLI is a cross-check, not an override — a
mismatch between the declared header and the CLI flag is a FAIL (prevents
someone quietly relaxing the bar on the command line without it being
visible in the document itself).

---

## 2. Required Document Structure

Every blueprint, at every tier, MUST contain exactly these seven parts in
order. This does not change by tier — what changes is how much of Parts
II–IV is substantive content versus a justified N/A (§5).

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

## 3. Document Header Standard

```markdown
# Project Name — BLUEPRINT
## Version: N.N | Document Class: MASTER SPECIFICATION
## Scope: MICRO | TASK | PROJECT
### Generated: YYYY-MM-DD

> **READ FIRST — DOCUMENT AUTHORITY**
> [Authority statement — minimum 2 sentences]
```

## 4. Part-by-Part Specification

### Part I — System Overview & Architecture

| Subsection | Requirement (all tiers) |
|---|---|
| 1.1 Vision Statement | 2-3 sentences on what, who, and defining principle |
| 1.2 High-Level Architecture | Diagram or flow description; MICRO/TASK may use a short block diagram, PROJECT requires the full 50+ line ASCII diagram with box-drawing characters (┌┐└┘├┤┬┴┼─│) |
| 1.3 Tech Stack / Approach | Table: Layer or Step, Approach, Rationale |
| 1.4 Guiding Principles | At minimum 1 (MICRO), 3 (TASK), 6 (PROJECT) numbered items |
| 1.5 Components Involved | Table: Component, Role, Technology/Method, Location — may be a single row at MICRO |

Part I is never N/A — even a trivial task needs a stated vision and
approach; it just needs less of it.

### Part II — Module Registry

Table with exactly four columns: Module ID, Name, Description, Feature
Flag. Module IDs: `MOD-NNN` (zero-padded).

| Tier | Minimum modules |
|---|---|
| MICRO | 0 — may be N/A + rationale if the task has no separable components |
| TASK | 1+ |
| PROJECT | 3+ |

### Part III — Screen & Feature Specifications

ALL fields are mandatory when a spec is written:
```
FEATURE ID, MODULE REF, ROLLBACK TAG, FEATURE FLAG,
PURPOSE, COMPONENTS (5+ at PROJECT, 1+ at TASK), RULES, ERROR STATES, FALLBACK
```

| Tier | Minimum feature specs |
|---|---|
| MICRO | 0 — may be N/A + rationale |
| TASK | 1+ |
| PROJECT | 3+ with all fields |

### Part IV — Data Architecture

| Subsection | Requirement |
|---|---|
| 4.1 Core Data/State | PROJECT: SQL `CREATE TABLE` statements, 3+ tables. TASK: whatever data/state the task actually touches (may be prose, a single schema, or N/A + rationale). MICRO: N/A + rationale unless the task genuinely persists state. |
| 4.2 API / Interface Contracts | PROJECT: endpoint list, 3+, method+path+description. TASK: interface/contract description proportionate to scope, or N/A + rationale. MICRO: N/A + rationale unless applicable. |

Every table that IS defined: PRIMARY KEY, created_at, updated_at.

### Part V — Change Control Protocol

Never N/A, any tier. 9-field change log entry format (§10), contributor
rules scaled to tier (6+ at PROJECT, at minimum "no entry may be modified
or deleted" at MICRO), rollback hierarchy, migration naming
`YYYYMMDD_NNN_description.sql` where applicable.

### Part VI — Master Implementation Checklist

Never N/A, any tier — this is the section `generate_checklist.py` parses as
the single source of truth for enforcement. Every phase MUST have: Section
Tag, Feature Flag, Prerequisite, **Assigned Agent**, **Reviewer Agent**
(§6 — a `Type: review` deliverable enforces reviewer ≠ assignee),
**Deliverables** (each tagged with a `Type:`, §6), **Validation Gate**,
Rollback Procedure. A MICRO blueprint may have exactly one phase; a
PROJECT blueprint requires 3+ phases each with 3+ deliverables and gates.

### Part VII — Quality & Compliance Standards

Never N/A, any tier, scaled by tier:

| Requirement | MICRO | TASK | PROJECT |
|---|---|---|---|
| Error handling | What happens on failure, stated in 1+ sentence | 3-level hierarchy | 5-level hierarchy (Input Validation → API → Module → Network → System) |
| Testing | How correctness is confirmed (may be manual) | Real test names/commands | Unit ≥80%, integration, E2E |
| Performance / done-criteria | 1+ concrete success criterion | 3+ concrete metrics | 6+ concrete metrics with units |
| Retry / resilience | N/A allowed + rationale | Stated if applicable | Circuit breaker / retry policy required |

## 5. N/A + Rationale Rule

Any subsection of Parts II–IV (and, per §4, the specific Part VII rows
marked "N/A allowed") may be written as:

```
N/A — Rationale: <one sentence minimum explaining why this genuinely does
not apply to this task>
```

`validate_blueprint.py` treats a bare `N/A` (no `Rationale:` clause) as a
FAIL at any tier. This is the mechanism that lets scope scale down without
ever becoming a silent way to skip required thinking — every skip must be
justified in the document itself, permanently, as part of the one-time
generation.

## 6. Deliverable Type Taxonomy

Every deliverable listed in a Part VI table or checklist may declare a
`Type:` (default `file` if omitted, preserving old blueprints):

| Type | Meaning | How it's checked |
|---|---|---|
| `file` | A specific file must exist at a given path | `Path.exists()` |
| `glob` | A file matching a glob pattern must exist | `Path.glob(pattern)` non-empty |
| `approval` | A human/agent sign-off or decision, not a build artifact | An attestation marker file must exist and contain required attestation fields (who, when, what was approved) |
| `external-check` | Correctness can only be judged by a dedicated validator script supplied with the blueprint | **Fails closed**: if no validator is wired to the step at chain-init time, the step can never move past `pending_verify` — there is no silent auto-pass, unlike an unvalidated `file`/`glob` step |
| `review` | The phase's required independent critique (Creative Orchestration Doctrine Principle V) | A critique marker file must exist and contain `Reviewed-By:`, `Date:`, and a non-trivial `Critique:` field, **and** `Reviewed-By:` must differ from the phase's `assignments.json` agent — fails if the reviewer is the implementer, not just if the file is missing |

`external-check` exists specifically so that non-artifact, judgment-based
deliverables (a decision, a conclusion) don't either force a fake
file-existence check or get an unenforced free pass — the doctrine that
"agents never validate their own work" (see
`references/enforcer-validation-architecture.md`) extends to this deliverable
type explicitly.

`review` is the structural implementation of Principle V ("every creative
layer has a corresponding reviewer... creation without evaluation produces
inconsistency, evaluation without creation produces stagnation"). Every
phase's Part VI deliverable list MUST include exactly one `Type: review`
deliverable (any tier — see §14). It's deliberately distinct from
`approval`: an `approval` only needs *a* sign-off; a `review` specifically
needs a sign-off from someone who is **not** the phase's implementer. The
system cannot judge the *quality* of a critique any more than it can judge
the quality of an approval — that stays a human/agent judgment call — but
it CAN and DOES mechanically enforce that the critique came from a
different agent than the one being critiqued, which is exactly the
structural guarantee the doctrine asks for.

## 7-11. Rollback Tags, Module Registry, Spec Format, Change Log, Amendment

See `enterprise-rules.md` for full detail; unchanged by scope tier except
where §4/§5 above note a tier-specific minimum.

## 12. Immutability Check

A blueprint is written once and referenced, not silently rewritten — Part V
already states this in prose ("this document's change log is APPEND-ONLY").
`generate_checklist.py generate` now enforces it operationally: it stamps
`sha256(blueprint.md)`, the declared tier, and a timestamp into
`project.json` at generation time. On any later `generate` or `status` call,
if the blueprint's current hash differs from the stamped hash **and** no
`CL-####` entry's timestamp postdates the stamped generation time, the tool
emits a WARN: the blueprint changed without a corresponding Change Control
entry. This doesn't block anything by itself (Part V amendments are
legitimate), but it makes an undocumented edit visible instead of silent.

## 13. Quality Thresholds Per Tier

| Rating | FAIL | WARN |
|---|---|---|
| Enterprise Grade | 0 | 0-4 |
| Production Ready | 0 | 5-9 |
| Needs Hardening | 0 | 10-14 |
| Incomplete | 1-3 | any |
| Not Enterprise Grade | 4+ | any |

This rating scale applies at every tier — a MICRO blueprint that fully
meets the MICRO bar (§14) can still score "Enterprise Grade" for its tier;
tiers scale *what* is required, not the pass/fail scoring logic itself.

## 14. Minimum Completeness Requirements Per Tier

| Requirement | MICRO | TASK | PROJECT | Enforcement |
|---|---|---|---|---|
| Document length | 40+ lines | 150+ lines | 1500+ lines | FAIL |
| ASCII architecture diagram | not required | short diagram/flow OK | 50+ lines, box-drawing chars | FAIL (PROJECT only) |
| Modules defined | 0 (N/A OK) | 1+ | 3+ | FAIL if below tier minimum |
| Feature specifications | 0 (N/A OK) | 1+ | 3+ with all fields | FAIL if below tier minimum |
| Data schemas / contracts | N/A OK | proportionate | 3+ SQL / 3+ endpoints | WARN |
| Phase deliverables + gates | 1+ each | 1+ each | 3+ each | FAIL |
| Error handling depth | 1 sentence | 3-level | 5-level hierarchy | WARN |
| Performance / success criteria | 1+ | 3+ | 6+ concrete metrics | WARN |
| Rollback procedures | 1 per phase | 1 per phase | 1 per phase | WARN |
| Change log entries | 1+ with 9 fields | 1+ with 9 fields | 1+ with 9 fields | FAIL |
| No TODOs/placeholders | 0 `[TODO]`, ≤2 `[Define...]` | 0, ≤3 | 0, ≤5 | WARN |
| N/A without rationale | 0 allowed | 0 allowed | 0 allowed (N/A itself disallowed on II-IV) | FAIL |
| Reviewer Agent field present per phase | 1+ | 1+ | 1+ per phase | FAIL |
| `Type: review` deliverable per phase | 1+ | 1+ | 1+ per phase | FAIL |
