#!/usr/bin/env python3
"""
enterprise-blueprint — Initialize a new blueprint project

Creates blueprint.md and checklist.md side by side, pre-populated with
all required sections, rollback tags, module registry placeholder,
change log stub, and phase scaffolding — scaled to the declared scope tier
(micro/task/project). See references/blueprint-standard.md for the full
tier specification.

Usage:
    python3 scripts/init_blueprint.py <project-name> --path <output-dir>
    python3 scripts/init_blueprint.py <project-name> --path <output-dir> --scope micro
    python3 scripts/init_blueprint.py <project-name> --path <output-dir> --scope task
    python3 scripts/init_blueprint.py <project-name> --path <output-dir> --phases "Pre-Build,Foundation,Auth,Core"
    python3 scripts/init_blueprint.py <project-name> --path <output-dir> --dry-run
    python3 scripts/init_blueprint.py <project-name> --path <output-dir> --json
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

VERSION = "1.0"

SCOPES = ("micro", "task", "project")

DEFAULT_PHASES = {
    "micro": [
        "Phase 0: Task Execution",
    ],
    "task": [
        "Phase 0: Implementation",
        "Phase 1: Verification",
    ],
    "project": [
        "Phase 0: Pre-Build",
        "Phase 1: Foundation",
        "Phase 2: Authentication & Identity",
        "Phase 3: Core Feature Build",
        "Phase 4: Integration Layer",
        "Phase 5: Testing & Hardening",
        "Phase 6: Launch & Live Ops",
    ],
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower().strip())
    return s.strip("-")


def _bare_title(phase_name):
    """Strip a leading 'Phase N:' prefix, if present. Default phases carry it
    baked into the string; --phases-supplied names never do — this normalizes
    both shapes to the same bare title before it's reused as a header/flag."""
    return re.sub(r"^phase\s*\d+[:\s]*", "", phase_name, flags=re.IGNORECASE).strip()


def flag_name(phase_name):
    slug = slugify(_bare_title(phase_name))
    return "FEAT_" + slug.upper().replace("-", "_")


def phase_tag(index):
    return f"[PHASE-{index}-v1]"


def na_rationale(hint):
    return f"N/A — Rationale: [{hint}]"


# ── Blueprint generation ───────────────────────────────────────────────────────

def blueprint_phase_section(i, phase):
    tag = phase_tag(i)
    flag = flag_name(phase)
    title = _bare_title(phase)
    lines = [
        f"### PHASE-{i}: {title}",
        "",
        f"**Section Tag:** `{tag}`",
        f"**Feature Flag:** `{flag}`",
        "**Assigned Agent:** _unassigned_",
        "**Reviewer Agent:** _unassigned_ — must differ from Assigned Agent (Creative Orchestration Doctrine Principle V)",
        "",
        "### Prerequisites",
        "",
        f"All Phase {i - 1 if i > 0 else 'N/A'} items must be complete, tests passing, and change log entry written.",
        "",
        "### Deliverables",
        "",
        f"- [ ] **PHASE-{i}.1** Type: file [Define deliverable 1]",
        f"- [ ] **PHASE-{i}.2** Type: file [Define deliverable 2]",
        f"- [ ] **PHASE-{i}.3** review-phase{i}.md Type: review",
        "",
        "### Validation Gate",
        "",
        "> No phase may begin until all prior checklist items are verified complete, all tests pass in CI, and a change log entry is appended.",
        "",
        "### Rollback Procedure",
        "",
        "1. Disable relevant feature flags immediately (no deployment required).",
        "2. Assess whether a code rollback or flag-only disable resolves the issue.",
        "3. If database migration rollback is required, obtain two-contributor approval.",
        "4. Write a post-incident change log entry within 24 hours.",
        "",
        "---",
        "",
    ]
    return "\n".join(lines)


def part_i_architecture_block(scope):
    if scope == "project":
        return [
            "```",
            "┌─────────────────────────────────────────────────────────────┐",
            "│                     ENTRY LAYER                              │",
            "└────────────────────┬────────────────────────────────────────┘",
            "                     │",
            "┌────────────────────▼────────────────────────────────────────┐",
            "│                  APPLICATION LAYER                           │",
            "└────────────────────┬────────────────────────────────────────┘",
            "                     │",
            "┌────────────────────▼────────────────────────────────────────┐",
            "│                   DATA LAYER                                 │",
            "└─────────────────────────────────────────────────────────────┘",
            "```",
            "",
            "> **PROJECT tier requires this diagram expanded to 50+ lines with",
            "> box-drawing characters before validation passes — this is a",
            "> starting skeleton, not the final diagram.**",
        ]
    if scope == "task":
        return [
            "```",
            "[Step/Component A] ──▶ [Step/Component B] ──▶ [Outcome]",
            "```",
            "",
            "> A short block diagram or flow description is sufficient at TASK scope.",
        ]
    return [
        "[One or two lines describing the flow of this task from input to",
        "outcome. A full diagram is not required at MICRO scope.]",
    ]


def part_ii_module_registry(scope):
    if scope == "micro":
        return [
            na_rationale("state why this task has no separable modules/components"),
        ]
    if scope == "task":
        return [
            "| Module ID | Name | Description | Feature Flag |",
            "|---|---|---|---|",
            "| MOD-001 | [Name] | [Description] | FEAT_[NAME] |",
        ]
    return [
        "| Module ID | Name | Description | Feature Flag |",
        "|---|---|---|---|",
        "| MOD-001 | [Name] | [Description] | FEAT_[NAME] |",
        "",
        "> **PROJECT tier requires 3+ modules** — add MOD-002, MOD-003, etc.",
    ]


def part_iii_feature_specs(scope):
    if scope == "micro":
        return [
            na_rationale("state why this task has no separate screen/feature specs"),
        ]
    header = [
        "Each specification follows this format:",
        "> ID, Module Ref, Rollback Tag, Feature Flag, Purpose,",
        "> Components, Rules, Error States, Fallback.",
        "",
        "[Insert screen and feature specifications here]",
    ]
    if scope == "project":
        header.append("")
        header.append("> **PROJECT tier requires 3+ feature specifications** with all fields.")
    return header


def part_iv_data_architecture(scope):
    if scope == "micro":
        return {
            "schemas": [na_rationale("state why this task has no persisted data/state")],
            "api": [na_rationale("state why this task has no interface/API contract")],
        }
    if scope == "task":
        return {
            "schemas": [
                "[Describe any data/state this task reads or writes — a single",
                "schema, a data shape, or `" + na_rationale("no data involved") + "` if genuinely none.]",
            ],
            "api": [
                "[Describe any interface/contract this task exposes or depends on,",
                "or `" + na_rationale("no interface involved") + "` if genuinely none.]",
            ],
        }
    return {
        "schemas": [
            "[Insert SQL schemas here]",
            "",
            "> **PROJECT tier requires 3+ `CREATE TABLE` schemas.**",
        ],
        "api": [
            "All API endpoints follow: `/api/v1/{resource}/{action}`.",
            "All responses follow the standard error envelope:",
            "  success, data, error (code + message), meta (requestId + timestamp).",
            "",
            "> **PROJECT tier requires 3+ documented endpoints.**",
        ],
    }


def part_vii_quality(scope):
    if scope == "micro":
        return [
            "## Error Handling",
            "",
            "[State in one sentence what happens if this task fails.]",
            "",
            "## Done Criteria",
            "",
            "[State at least one concrete criterion that proves this task succeeded.]",
        ]
    if scope == "task":
        return [
            "## Error Handling Standards",
            "",
            "1. [Level 1 — e.g. input validation]",
            "2. [Level 2 — e.g. execution failure]",
            "3. [Level 3 — e.g. reporting/notification failure]",
            "",
            "## Testing / Verification",
            "",
            "- [How correctness is confirmed — real test names/commands, or",
            "  manual verification steps.]",
            "",
            "## Done Criteria",
            "",
            "| Criterion | Target |",
            "|---|---|",
            "| [Criterion 1] | [Concrete value] |",
            "| [Criterion 2] | [Concrete value] |",
            "| [Criterion 3] | [Concrete value] |",
        ]
    return [
        "## Error Handling Standards",
        "",
        "1. Graceful degradation for all non-critical services.",
        "2. User-facing messages: friendly, non-technical, no stack traces exposed.",
        "3. Internal logging: full context — requestId, userId, error code, stack.",
        "4. Retry: exponential backoff on external calls (3 retries: 1s, 2s, 4s).",
        "5. Circuit breaker: 10 failures in 60s opens circuit for 5 minutes.",
        "",
        "## Testing Requirements",
        "",
        "- Unit tests: 80% line coverage on all core modules.",
        "- Integration tests: every API endpoint has success + error case.",
        "- E2E tests: all critical user flows have passing automated tests.",
        "",
        "## Performance Budgets",
        "",
        "| Metric | Budget |",
        "|---|---|",
        "| Page load LCP (3G) | < 2.0 seconds |",
        "| API response time p95 | < 500ms |",
        "| Background job completion | < 60 seconds |",
        "",
        "> **PROJECT tier requires 6+ concrete metrics with units.**",
    ]


def generate_blueprint(project_name, phases, scope):
    d = today()
    phase_block = "".join(blueprint_phase_section(i, p) for i, p in enumerate(phases))
    doc_class = "ENTERPRISE BLUEPRINT" if scope == "project" else "BLUEPRINT"

    parts = []
    parts.append(f"# {project_name} — {doc_class}")
    parts.append(f"## Version: 1.0 | Document Class: MASTER SPECIFICATION")
    parts.append(f"## Scope: {scope.upper()}")
    parts.append(f"### Generated: {d}")
    parts.append("")
    parts.append("> **READ FIRST — DOCUMENT AUTHORITY**")
    parts.append("> This document is the single source of truth. No feature may be built,")
    parts.append("> no schema migrated, and no API changed without this document as the")
    parts.append("> authoritative reference. All contributors MUST read Part V (Change")
    parts.append("> Control Protocol) before touching any file. This document's change")
    parts.append("> log is APPEND-ONLY. Prior sections may only be updated via a formal")
    parts.append("> amendment with a corresponding CL entry.")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("## TABLE OF CONTENTS")
    parts.append("")
    parts.append("```")
    parts.append("PART I    — SYSTEM OVERVIEW & ARCHITECTURE")
    parts.append("PART II   — MODULE REGISTRY")
    parts.append("PART III  — SCREEN & FEATURE SPECIFICATIONS")
    parts.append("PART IV   — DATA ARCHITECTURE")
    parts.append("PART V    — CHANGE CONTROL PROTOCOL")
    parts.append("PART VI   — MASTER IMPLEMENTATION CHECKLIST")
    parts.append("PART VII  — QUALITY & COMPLIANCE STANDARDS")
    parts.append("```")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("# PART I — SYSTEM OVERVIEW & ARCHITECTURE")
    parts.append("")
    parts.append("> **Rollback Tag:** `[SYS-OVERVIEW-v1]`")
    parts.append("")
    parts.append("## 1.1 Vision Statement")
    parts.append("")
    parts.append("[Describe the vision in 2-3 sentences. What does it do?")
    parts.append("Who uses it? What is the defining principle?]")
    parts.append("")
    parts.append("## 1.2 High-Level Architecture")
    parts.append("")
    parts.extend(part_i_architecture_block(scope))
    parts.append("")
    parts.append("## 1.3 Tech Stack" if scope == "project" else "## 1.3 Approach")
    parts.append("")
    parts.append("| Layer | Technology | Rationale |" if scope == "project" else "| Step | Approach | Rationale |")
    parts.append("|---|---|---|")
    parts.append("| [Layer] | [Technology] | [Why this was chosen] |")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("# PART II — MODULE REGISTRY")
    parts.append("")
    parts.append("> **Rollback Tag:** `[MODULE-REGISTRY-v1]`")
    parts.append("> **Rule:** Every change log entry MUST reference at least one Module ID")
    parts.append("> (unless this Part is N/A for this scope).")
    parts.append("")
    parts.extend(part_ii_module_registry(scope))
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("# PART III — SCREEN & FEATURE SPECIFICATIONS")
    parts.append("")
    parts.append("> **Rollback Tag:** `[SPECS-v1]`")
    parts.append("")
    parts.extend(part_iii_feature_specs(scope))
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("# PART IV — DATA ARCHITECTURE")
    parts.append("")
    parts.append("> **Rollback Tag:** `[DATA-ARCH-v1]`")
    parts.append("> **Rule:** All schema changes require a migration file named")
    parts.append("> `YYYYMMDD_NNN_description.sql` with a corresponding rollback file,")
    parts.append("> and must be referenced in the Global Change Log (where applicable).")
    parts.append("")
    data_blocks = part_iv_data_architecture(scope)
    parts.append("## 4.1 Core Database Schemas" if scope == "project" else "## 4.1 Core Data / State")
    parts.append("")
    parts.extend(data_blocks["schemas"])
    parts.append("")
    parts.append("## 4.2 API Contract Specifications" if scope == "project" else "## 4.2 Interface / API Contracts")
    parts.append("")
    parts.extend(data_blocks["api"])
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("# PART V — CHANGE CONTROL PROTOCOL")
    parts.append("")
    parts.append("> **Rollback Tag:** `[CHANGE-CONTROL-v1]`")
    parts.append("> **This section is permanent and non-negotiable.**")
    parts.append("> Every contributor must read this section before making any change.")
    parts.append("")
    parts.append("## Change Log Entry Format")
    parts.append("")
    parts.append("Every entry MUST include all fields below. Entries are permanent.")
    parts.append("No entry may be modified or deleted after writing.")
    parts.append("")
    parts.append("```")
    parts.append("Date        : YYYY-MM-DD HH:MM UTC")
    parts.append("Contributor : [name/handle]")
    parts.append("Modules     : [MOD-XXX, ...]")
    parts.append("Section Tags: [[TAG-NAME-v1], ...]")
    parts.append("Files Changed: [every file changed]")
    parts.append("Description : [What changed and why — minimum 3 sentences]")
    parts.append("Tests Passing: [test names, or 'none — pre-build']")
    parts.append("Phase       : [PHASE-N]")
    parts.append("Rollback Ref: [git commit hash or migration rollback filename]")
    parts.append("```")
    parts.append("")
    parts.append("## Contributor Rules")
    parts.append("")
    parts.append("1. No work merged without a change log entry in the same PR.")
    parts.append("2. No database migration without a rollback migration file.")
    if scope == "project":
        parts.append("3. Feature flags required for every Phase 2+ feature.")
        parts.append("4. Minimum: 1 unit test per new function, 1 integration test per endpoint.")
        parts.append("5. `CHANGELOG.md` CI append-only check must pass on every PR.")
        parts.append("6. No contributor may modify or delete an existing change log entry.")
    else:
        parts.append("3. No contributor may modify or delete an existing change log entry.")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("# PART VI — MASTER IMPLEMENTATION CHECKLIST")
    parts.append("")
    parts.append(phase_block)
    parts.append("---")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("# PART VII — QUALITY & COMPLIANCE STANDARDS")
    parts.append("")
    parts.append("> **Rollback Tag:** `[QUALITY-v1]`")
    parts.append("")
    parts.extend(part_vii_quality(scope))
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("# CHANGE LOG")
    parts.append("")
    parts.append("> This section is append-only. No entry may be modified or deleted.")
    parts.append("")
    parts.append("## CL-0000 — Document Initialization")
    parts.append("")
    parts.append("```")
    parts.append(f"Date        : {d}")
    parts.append("Contributor : [author]")
    parts.append("Modules     : [MOD-001]" if scope != "micro" else "Modules     : [N/A — no modules at MICRO scope]")
    parts.append("Section Tags: [[PHASE-0-v1]]")
    parts.append("Files Changed: [blueprint.md, checklist.md]")
    parts.append(f"Description : Initial blueprint created via enterprise-blueprint skill.")
    parts.append(f"              Project: {project_name}. Scope: {scope.upper()}. All sections")
    parts.append("              pre-populated with required structure awaiting content population.")
    parts.append("Tests Passing: none — pre-build")
    parts.append("Phase       : PHASE-0")
    parts.append("Rollback Ref: N/A — initial document creation")
    parts.append("```")

    return "\n".join(parts) + "\n"


def generate_changelog(project_name, phases, scope):
    """Generate standalone CHANGELOG.md from blueprint's changelog section."""
    d = today()
    parts = []
    parts.append(f"# {project_name} — CHANGELOG")
    parts.append("")
    parts.append("> This file is the append-only change log. No entry may be modified or deleted.")
    parts.append("> All entries must follow the format defined in blueprint.md Part V.")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("## CL-0000 — Document Initialization")
    parts.append("")
    parts.append("```")
    parts.append(f"Date        : {d}")
    parts.append("Contributor : [author]")
    parts.append("Modules     : [MOD-001]" if scope != "micro" else "Modules     : [N/A — no modules at MICRO scope]")
    parts.append("Section Tags: [[PHASE-0-v1]]")
    parts.append("Files Changed: [blueprint.md, checklist.md, CHANGELOG.md]")
    parts.append(f"Description : Initial blueprint created via enterprise-blueprint skill.")
    parts.append(f"              Project: {project_name}. Scope: {scope.upper()}. All sections")
    parts.append("              pre-populated with required structure awaiting content population.")
    parts.append("Tests Passing: none — pre-build")
    parts.append("Phase       : PHASE-0")
    parts.append("Rollback Ref: N/A — initial document creation")
    parts.append("```")
    parts.append("")
    return "\n".join(parts) + "\n"


# ── Checklist generation ───────────────────────────────────────────────────────

def checklist_phase_section(i, phase):
    tag = phase_tag(i)
    flag = flag_name(phase)
    title = _bare_title(phase)
    prior = f"Phase {i - 1}" if i > 0 else "N/A"
    lines = [
        f"### PHASE-{i}: {title}",
        "",
        f"**Section Tag:** `{tag}` | **Feature Flag:** `{flag}`",
        "**Status:** `NOT STARTED` | **Assigned Agent:** _unassigned_",
        f"**Prerequisite:** {prior} status must be `COMPLETE` and change log entry written.",
        "",
        "### Pre-Phase Gate",
        "",
        "Confirm all of the following before starting:",
        "",
        f"- [ ] Prior phase change log entry is written and appended to `CHANGELOG.md`.",
        "- [ ] All prior phase tests/verification are passing.",
        f"- [ ] Feature flags for `{flag}` are set to `disabled` in production (if applicable).",
        "- [ ] Agent assignment for this phase is confirmed in `assignments.json`.",
        "- [ ] Reviewer Agent (distinct from Assigned Agent) is confirmed for this phase.",
        "",
        "### Implementation Steps",
        "",
        "> Each step must be completed, verified, and logged before proceeding.",
        "",
        "- [ ] **Step 1:** [First concrete implementation action]",
        "  - _Validation:_ [How this step's correctness is confirmed.]",
        "  - _Rollback Ref:_ [How to undo this step if needed.]",
        "",
        "- [ ] **Step 2:** [Continue for all steps specific to this phase]",
        "  - _Validation:_ [How this step's correctness is confirmed.]",
        "  - _Rollback Ref:_ [How to undo this step if needed.]",
        "",
        "### Phase Validation Gate",
        "",
        "All of the following must be true before this phase is marked `COMPLETE`:",
        "",
        "- [ ] All implementation steps above are checked.",
        "- [ ] All verification introduced in this phase is passing.",
        "- [ ] Change log entry for this phase is written and appended.",
        "- [ ] Blueprint updated to reflect any deviations from specification.",
        "- [ ] Assigned agent has signed off (name + date below).",
        f"- [ ] `review-phase{i}.md` exists with Reviewed-By/Date/Critique fields, Reviewed-By ≠ Assigned Agent.",
        "",
        "### Agent Sign-Off",
        "",
        "```",
        f"Phase {i} Sign-Off:",
        "  Agent     : _________________",
        "  Date      : _________________",
        "  Notes     : _________________",
        "```",
        "",
        "---",
        "",
    ]
    return "\n".join(lines)


def generate_checklist(project_name, phases, scope):
    d = today()
    phase_block = "".join(checklist_phase_section(i, p) for i, p in enumerate(phases))
    doc_class = "ENTERPRISE CHECKLIST" if scope == "project" else "CHECKLIST"

    parts = []
    parts.append(f"# {project_name} — {doc_class}")
    parts.append(f"## Version: 1.0 | Scope: {scope.upper()} | Coexists with: blueprint.md")
    parts.append(f"### Generated: {d}")
    parts.append("")
    parts.append("> **CHECKLIST AUTHORITY**")
    parts.append("> This checklist is the enforcement companion to blueprint.md. It may")
    parts.append("> not diverge — every blueprint amendment requires a corresponding")
    parts.append("> checklist update in the same commit. Checked items are immutable;")
    parts.append("> corrections require a new line with explanation, never erasure.")
    parts.append(">")
    parts.append("> **Status values:** `NOT STARTED` | `IN PROGRESS` | `BLOCKED` | `COMPLETE`")
    parts.append("> **Blocking rule:** No phase may begin until the prior phase is `COMPLETE`.")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("## GLOBAL PREREQUISITES")
    parts.append("")
    parts.append("Before any phase begins:")
    parts.append("")
    if scope == "project":
        parts.append("- [ ] Repository created with `/app`, `/lib`, `/db`, `/contracts`, `/tests`, `/docs`.")
        parts.append("- [ ] `CHANGELOG.md` created with append-only CI enforcement check.")
        parts.append("- [ ] `global_change_log` database table created with INSERT-only trigger.")
        parts.append("- [ ] All module IDs registered in `modules` config table.")
        parts.append("- [ ] Feature flags system initialized; all flags default to `disabled`.")
        parts.append("- [ ] CI/CD pipeline configured: test → lint → build → staging deploy.")
        parts.append("- [ ] Monitoring and error tracking connected to staging environment.")
    else:
        parts.append("- [ ] `CHANGELOG.md` created with append-only convention noted.")
    parts.append("- [ ] `assignments.json` populated for at least Phase 0.")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append(phase_block)
    parts.append("---")
    parts.append("")
    parts.append("## GLOBAL COMPLETION CRITERIA")
    parts.append("")
    parts.append("This task is complete when:" if scope != "project" else "The project is production-complete when:")
    parts.append("")
    parts.append("- [ ] All phase statuses are `COMPLETE`.")
    if scope == "project":
        parts.append("- [ ] All feature flags are enabled in production.")
        parts.append("- [ ] Performance budgets verified by load test (results in change log).")
        parts.append("- [ ] Security audit of all auth and payment flows is complete.")
        parts.append("- [ ] Data export and deletion (GDPR compliance) is verified.")
        parts.append("- [ ] Post-launch monitoring dashboards live and alerting configured.")
    parts.append("- [ ] Final change log entry written documenting completion.")

    return "\n".join(parts) + "\n"


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Initialize a blueprint + checklist project, scaled to a scope tier."
    )
    parser.add_argument("project_name", help="Project name (used in headings)")
    parser.add_argument("--path", required=True, help="Output directory")
    parser.add_argument(
        "--scope",
        choices=SCOPES,
        default="project",
        help="Scope tier: micro (trivial task), task (multi-step assignment), "
             "project (full project, default — matches prior behavior)",
    )
    parser.add_argument(
        "--phases",
        default=None,
        help="Comma-separated list of phase names (default: scope's standard phase set)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    parser.add_argument("--json", action="store_true", help="Output JSON statistics only")
    args = parser.parse_args()

    started = now_iso()
    scope = args.scope
    phases = (
        [p.strip() for p in args.phases.split(",")]
        if args.phases
        else DEFAULT_PHASES[scope]
    )
    output_dir = Path(args.path)
    blueprint_path = output_dir / "blueprint.md"
    checklist_path = output_dir / "checklist.md"
    changelog_path = output_dir / "CHANGELOG.md"
    metadata_path = output_dir / "project.json"

    status = "dry_run" if args.dry_run else "success"
    error = None

    if not args.dry_run:
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            blueprint_path.write_text(
                generate_blueprint(args.project_name, phases, scope), encoding="utf-8"
            )
            checklist_path.write_text(
                generate_checklist(args.project_name, phases, scope), encoding="utf-8"
            )
            changelog_path.write_text(
                generate_changelog(args.project_name, phases, scope), encoding="utf-8"
            )
            metadata = {
                "project": args.project_name,
                "slug": slugify(args.project_name),
                "scope": scope,
                "phases": phases,
                "version": VERSION,
                "created_at": started,
                "blueprint": str(blueprint_path),
                "checklist": str(checklist_path),
                "changelog": str(changelog_path),
                "assignments": str(output_dir / "assignments.json"),
            }
            metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        except Exception as exc:
            status = "failed"
            error = str(exc)

    result = {
        "operation": "init_blueprint",
        "timestamp": now_iso(),
        "status": status,
        "project": args.project_name,
        "details": {
            "scope": scope,
            "phases": len(phases),
            "phase_names": phases,
            "output_dir": str(output_dir),
            "dry_run": args.dry_run,
            "files_created": (
                [] if args.dry_run
                else [str(blueprint_path), str(checklist_path), str(changelog_path), str(metadata_path)]
            ),
        },
        "cost": {"tier": 0, "amount_usd": 0.0, "service": "local"},
    }
    if error:
        result["error"] = error

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if args.dry_run:
            print("[DRY RUN] Would create:")
            print(f"  {blueprint_path}")
            print(f"  {checklist_path}")
            print(f"  {changelog_path}")
            print(f"  {metadata_path}")
            print(f"  Scope: {scope}")
            print(f"  Phases ({len(phases)}): {', '.join(phases)}")
        elif status == "success":
            print(f"[OK] Blueprint initialized ({scope}): {output_dir}")
            print(f"  blueprint.md  → {blueprint_path}")
            print(f"  checklist.md  → {checklist_path}")
            print(f"  CHANGELOG.md  → {changelog_path}")
            print(f"  project.json  → {metadata_path}")
        else:
            print(f"[ERROR] {error}")
            sys.exit(1)

        print()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
