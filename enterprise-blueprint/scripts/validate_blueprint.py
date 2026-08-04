#!/usr/bin/env python3
"""
Blueprint Validation Script

Validates a blueprint.md against the tier-scaled standard defined in
references/blueprint-standard.md (MICRO / TASK / PROJECT). Rules are a
data-driven table (see RULES below) — each rule declares the minimum tier
it applies to, so tier-conditional validation never requires branching
logic duplicated per-tier.
"""

import argparse
import re
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

TIER_ORDER = ["micro", "task", "project"]
TIER_RANK = {t: i for i, t in enumerate(TIER_ORDER)}

MIN_LINES = {"micro": 40, "task": 150, "project": 1500}
MIN_MODULES = {"micro": 0, "task": 1, "project": 3}
MIN_FEATURE_SPECS = {"micro": 0, "task": 1, "project": 3}
MIN_DELIVERABLE_SECTIONS = {"micro": 1, "task": 1, "project": 3}
MIN_ERROR_LEVELS = {"micro": 1, "task": 3, "project": 5}
MIN_PERF_METRICS = {"micro": 1, "task": 3, "project": 6}
MAX_PLACEHOLDERS = {"micro": 2, "task": 3, "project": 5}

REQUIRED_TAG_STEMS = [
    "SYS-OVERVIEW-v1", "MODULE-REGISTRY-v1", "SPECS-v1",
    "DATA-ARCH-v1", "CHANGE-CONTROL-v1", "QUALITY-v1",
]
FEATURE_SPEC_FIELDS = [
    "FEATURE ID", "MODULE REF", "ROLLBACK TAG", "FEATURE FLAG", "PURPOSE",
    "COMPONENTS", "RULES", "ERROR STATES", "FALLBACK",
]
BOX_DRAWING_CHARS = "┌┐└┘├┤┬┴┼─│"


def tier_at_least(tier, minimum):
    return TIER_RANK.get(tier, TIER_RANK["project"]) >= TIER_RANK.get(minimum, 0)


class BlueprintValidator:
    def __init__(self, blueprint_path, tier=None):
        self.path = Path(blueprint_path)
        if not self.path.is_file():
            raise FileNotFoundError(f"Blueprint not found: {self.path}")
        self.content = self.path.read_text()
        self.results = []

        declared = re.search(r"##\s*Scope:\s*(MICRO|TASK|PROJECT)", self.content, re.IGNORECASE)
        self.declared_tier = declared.group(1).lower() if declared else None
        self.cli_tier = tier
        # No CLI tier given: trust the document's own declaration, defaulting
        # to the full "project" bar for documents written before scope tiers
        # existed (never silently relaxes an old blueprint's requirements).
        self.tier = tier or self.declared_tier or "project"

    def check(self, name, condition, severity="FAIL", detail=""):
        passed = bool(condition)
        self.results.append({
            "name": name,
            "severity": severity,
            "passed": passed,
            "detail": detail if not passed else "",
        })
        return passed

    # ── section extraction helpers ──────────────────────────────────────

    def _part(self, roman):
        """Extract the body of `# PART {roman} —...` up to the next `# PART`
        or `# CHANGE LOG` heading. Returns '' if the part isn't found."""
        m = re.search(
            rf"#\s*PART\s+{roman}\b.*?\n(.*?)(?=\n#\s*PART\s+|\n#\s*CHANGE LOG\b|\Z)",
            self.content, re.DOTALL | re.IGNORECASE,
        )
        return m.group(1) if m else ""

    @staticmethod
    def _first_substantive_block(section_text):
        """Skip leading blank lines and '>'-prefixed blockquote boilerplate
        (rollback tag / rule callouts every Part opens with) and return the
        first real paragraph of body content."""
        lines = section_text.strip("\n").splitlines()
        i = 0
        while i < len(lines) and (not lines[i].strip() or lines[i].lstrip().startswith(">")):
            i += 1
        body = "\n".join(lines[i:]).strip()
        return body.split("\n\n", 1)[0] if body else ""

    @classmethod
    def _is_na_without_rationale(cls, section_text):
        """True if a Part's first substantive paragraph is a bare 'N/A' with
        no 'Rationale:' clause anywhere in that same short block."""
        first_block = cls._first_substantive_block(section_text)
        if not re.match(r"^N/A\b", first_block, re.IGNORECASE):
            return False
        return "rationale:" not in first_block.lower()

    @classmethod
    def _is_na(cls, section_text):
        first_block = cls._first_substantive_block(section_text)
        return bool(re.match(r"^N/A\b", first_block, re.IGNORECASE))

    # ── rule table ───────────────────────────────────────────────────────
    # Each entry is a bound-method name; run() executes them in order.
    # A rule internally decides its own tier applicability via
    # tier_at_least()/self.tier — this keeps tier logic local to the one
    # rule it affects instead of scattered branches in run().

    RULES = [
        "rule_document_basics",
        "rule_scope_declaration",
        "rule_version_and_date",
        "rule_read_first",
        "rule_required_parts",
        "rule_phase_tags",
        "rule_section_tags",
        "rule_required_tag_stems",
        "rule_na_rationale",
        "rule_module_registry",
        "rule_feature_specs",
        "rule_change_log",
        "rule_data_architecture",
        "rule_ascii_diagram",
        "rule_deliverables_and_gates",
        "rule_review_gate",
        "rule_error_hierarchy",
        "rule_performance_metrics",
        "rule_rollback_procedures",
        "rule_placeholders",
        "rule_document_length",
    ]

    def run(self):
        for rule_name in self.RULES:
            getattr(self, rule_name)()

        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = sum(1 for r in self.results if not r["passed"] and r["severity"] == "FAIL")
        warned = sum(1 for r in self.results if not r["passed"] and r["severity"] == "WARN")

        return {
            "operation": "validate",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "blueprint": str(self.path),
            "tier": self.tier,
            "declared_tier": self.declared_tier,
            "checks": self.results,
            "summary": {"total": total, "passed": passed, "failed": failed, "warned": warned},
            "cost": {"tier": 0, "amount_usd": 0.0, "service": "local"},
        }

    # ── individual rules ─────────────────────────────────────────────────

    def rule_document_basics(self):
        self.check("blueprint.md exists and is readable", self.path.exists() and self.path.is_file())

    def rule_scope_declaration(self):
        self.check("Scope tier declared in header (## Scope: MICRO|TASK|PROJECT)",
                    self.declared_tier is not None, "WARN")
        if self.cli_tier and self.declared_tier:
            self.check(
                "Declared scope matches --tier flag",
                self.cli_tier == self.declared_tier,
                detail=f"--tier={self.cli_tier} but document declares Scope: {self.declared_tier.upper()}",
            )

    def rule_version_and_date(self):
        self.check("Version number in document header", bool(re.search(r"Version:\s*", self.content)))
        self.check("Date in document header", bool(re.search(r"(?:Date|Generated):\s*\d{4}-\d{2}-\d{2}", self.content)), "WARN")

    def rule_read_first(self):
        self.check("READ FIRST / Document Authority preamble",
                    "READ FIRST" in self.content or "Document Authority" in self.content)

    def rule_required_parts(self):
        for part in ["PART I", "PART II", "PART III", "PART IV", "PART V", "PART VI", "PART VII"]:
            self.check(f"Contains {part}", part in self.content)

    def rule_phase_tags(self):
        phase_tags = len(re.findall(r"\[PHASE-\d+-v\d+\]", self.content))
        self.check("At least 1 PHASE rollback tag present", phase_tags >= 1)

    def rule_section_tags(self):
        section_tags = len(re.findall(r"\[.*?-v\d+\]", self.content))
        self.check("6+ section rollback tags across the document", section_tags >= 6, "WARN")

    def rule_required_tag_stems(self):
        for tag in REQUIRED_TAG_STEMS:
            self.check(f"Rollback tag [{tag}] present", tag in self.content, "WARN")

    def rule_na_rationale(self):
        for roman, label in [("II", "Module Registry"), ("III", "Feature Specifications"), ("IV", "Data Architecture")]:
            section = self._part(roman)
            self.check(
                f"Part {roman} ({label}): N/A, if used, has a Rationale",
                not self._is_na_without_rationale(section),
                detail=f"Part {roman} is marked N/A without a 'Rationale:' clause",
            )

    def rule_module_registry(self):
        part_ii = self._part("II")
        na = self._is_na(part_ii)
        mod_count = len(re.findall(r"MOD-\d{3}", self.content))
        minimum = MIN_MODULES[self.tier]
        if na and minimum == 0:
            return
        self.check(
            f"At least {max(minimum, 1)} module(s) defined (MOD-NNN) for {self.tier} tier",
            mod_count >= max(minimum, 1) if minimum > 0 else mod_count >= 1,
        )
        if tier_at_least(self.tier, "project"):
            self.check("3+ modules defined", mod_count >= 3, "WARN")
        feat_count = len(re.findall(r"FEAT_[A-Z][A-Z_]*", self.content))
        if not (na and minimum == 0):
            self.check("Feature flags (FEAT_*) referenced", feat_count >= 1)
        if tier_at_least(self.tier, "project"):
            self.check("3+ feature flags defined", feat_count >= 3, "WARN")

    def rule_feature_specs(self):
        part_iii = self._part("III")
        na = self._is_na(part_iii)
        minimum = MIN_FEATURE_SPECS[self.tier]
        spec_count = len(re.findall(r"FEATURE ID", self.content, re.IGNORECASE))
        if na and minimum == 0:
            return
        if minimum > 0:
            self.check(f"{minimum}+ feature specification(s) for {self.tier} tier", spec_count >= minimum)
        if tier_at_least(self.tier, "project") and spec_count > 0:
            for field in FEATURE_SPEC_FIELDS:
                field_count = len(re.findall(re.escape(field), self.content, re.IGNORECASE))
                self.check(
                    f"Feature spec field '{field}' present for every spec ({spec_count}+)",
                    field_count >= spec_count,
                    detail=f"Only {field_count}/{spec_count} specs have a '{field}' field",
                )

    def rule_change_log(self):
        self.check("CHANGE LOG section present", "CHANGE LOG" in self.content.upper())
        cl_count = len(re.findall(r"CL-\d{4}", self.content))
        self.check("At least one CL-NNNN entry present", cl_count >= 1)

    def rule_data_architecture(self):
        part_iv = self._part("IV")
        na = self._is_na(part_iv)
        if na and self.tier != "project":
            return
        self.check("Database schema defined in Part IV", "CREATE TABLE" in self.content, "WARN")
        self.check("API/interface contracts defined in Part IV",
                    bool(re.search(r"/v1/|/api/", self.content, re.IGNORECASE)), "WARN")
        self.check(
            "Migration naming convention stated",
            bool(re.search(r"YYYYMMDD_NNN_description|V\{NNN\}__", self.content)),
            "WARN",
        )
        if tier_at_least(self.tier, "project"):
            schema_count = len(re.findall(r"CREATE TABLE", self.content, re.IGNORECASE))
            self.check("3+ SQL table schemas", schema_count >= 3, "WARN")
            endpoint_count = len(re.findall(r"(?:GET|POST|PUT|PATCH|DELETE)\s+/", self.content))
            self.check("3+ API endpoints documented", endpoint_count >= 3, "WARN")

    def rule_ascii_diagram(self):
        if not tier_at_least(self.tier, "project"):
            return
        m = re.search(r"1\.2 High-Level Architecture\s*\n(.*?)(?=\n##\s|\n---)", self.content, re.DOTALL)
        block = m.group(1) if m else ""
        fence = re.search(r"```(.*?)```", block, re.DOTALL)
        diagram = fence.group(1) if fence else block
        diagram_lines = [l for l in diagram.splitlines() if l.strip()]
        has_box_chars = any(c in diagram for c in BOX_DRAWING_CHARS)
        self.check(
            "50+ line ASCII architecture diagram with box-drawing characters",
            len(diagram_lines) >= 50 and has_box_chars,
            detail=f"Found {len(diagram_lines)} non-blank lines in the 1.2 diagram block",
        )

    def rule_deliverables_and_gates(self):
        deliverable_sections = len(re.findall(r"###\s*Deliverables", self.content, re.IGNORECASE))
        gate_sections = len(re.findall(r"###\s*Validation Gate", self.content, re.IGNORECASE))
        minimum = MIN_DELIVERABLE_SECTIONS[self.tier]
        self.check(f"{minimum}+ phase Deliverables section(s)", deliverable_sections >= minimum)
        self.check(f"{minimum}+ phase Validation Gate section(s)", gate_sections >= minimum)

    def rule_review_gate(self):
        """Creative Orchestration Doctrine Principle V: every phase needs a
        Reviewer Agent field and a Type: review deliverable, at every tier
        (see blueprint-standard.md §6/§14). This only checks structural
        presence in the document — whether the reviewer is genuinely
        distinct from the assignee is a runtime check (assignments.json +
        the generated phase validator), not something knowable from the
        blueprint text alone."""
        phase_headers = list(re.finditer(r"###\s*PHASE-(\d+)[a-z]?:\s*([^\n]+)", self.content))
        if not phase_headers:
            return
        for idx, m in enumerate(phase_headers):
            phase_num = m.group(1)
            start = m.end()
            end = phase_headers[idx + 1].start() if idx + 1 < len(phase_headers) else len(self.content)
            section = self.content[start:end]
            self.check(
                f"PHASE-{phase_num} declares a Reviewer Agent field",
                bool(re.search(r"\*\*Reviewer Agent:\*\*", section)),
            )
            self.check(
                f"PHASE-{phase_num} has a Type: review deliverable",
                bool(re.search(r"Type:\s*review\b", section, re.IGNORECASE)),
            )

    def rule_error_hierarchy(self):
        m = re.search(r"Error Handling[^\n]*\n(.*?)(?=\n##\s|\n---)", self.content, re.DOTALL | re.IGNORECASE)
        block = m.group(1) if m else ""
        levels = len(re.findall(r"^\s*\d+\.\s", block, re.MULTILINE))
        minimum = MIN_ERROR_LEVELS[self.tier]
        self.check(f"Error handling depth ({minimum}+ levels stated) for {self.tier} tier", levels >= minimum, "WARN")

    def rule_performance_metrics(self):
        metrics = len(re.findall(r"\d+(?:\.\d+)?\s*(?:ms|s|seconds|minutes|GB|MB|req/s|%)\b", self.content))
        minimum = MIN_PERF_METRICS[self.tier]
        self.check(f"{minimum}+ concrete performance/success metrics with units for {self.tier} tier",
                    metrics >= minimum, "WARN")
        self.check("Test coverage / verification method specified",
                    "80%" in self.content or "coverage" in self.content.lower() or "verification" in self.content.lower(),
                    "WARN")
        if tier_at_least(self.tier, "project"):
            self.check("Circuit breaker / retry policy specified",
                        "circuit breaker" in self.content.lower() or "retry" in self.content.lower(), "WARN")

    def rule_rollback_procedures(self):
        phase_count = max(len(re.findall(r"\[PHASE-\d+-v\d+\]", self.content)), 1)
        rollback_count = len(re.findall(r"###\s*Rollback Procedure", self.content, re.IGNORECASE))
        self.check(f"Rollback procedure per phase ({phase_count} phase(s) detected)",
                    rollback_count >= phase_count, "WARN")

    def rule_placeholders(self):
        todo_count = self.content.count("[TODO")
        self.check("No [TODO] markers remaining", todo_count == 0, "WARN")

        legacy_count = (
            self.content.count("TODO") + self.content.count("FIXME")
            + self.content.count("TBD") + self.content.count("WIP")
        )
        self.check("Minimal unfilled TODO/FIXME/TBD/WIP markers", legacy_count == 0, "WARN")

        bracket_placeholders = len(re.findall(r"\[(?:Define|Describe|Insert)[^\]]*\]", self.content, re.IGNORECASE))
        maximum = MAX_PLACEHOLDERS[self.tier]
        self.check(f"≤{maximum} unfilled [Define.../Describe.../Insert...] placeholders for {self.tier} tier",
                    bracket_placeholders <= maximum, "WARN")

    def rule_document_length(self):
        line_count = len(self.content.splitlines())
        minimum = MIN_LINES[self.tier]
        self.check(f"Document meets {self.tier} tier length floor (>{minimum} lines)", line_count > minimum)
        if tier_at_least(self.tier, "project"):
            self.check("Document is thorough (> 2500 lines)", line_count > 2500, "WARN")


def main():
    parser = argparse.ArgumentParser(
        description="Validate a blueprint.md against the tier-scaled blueprint standard."
    )
    parser.add_argument("blueprint", help="Path to blueprint.md")
    parser.add_argument("--tier", choices=TIER_ORDER, default=None,
                         help="Scope tier to validate against (default: read from the "
                              "document's own '## Scope:' header, falling back to 'project')")
    parser.add_argument("--json", action="store_true", help="Output JSON report only")
    args = parser.parse_args()

    try:
        validator = BlueprintValidator(args.blueprint, tier=args.tier)
        result = validator.run()
    except (FileNotFoundError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    as_json = args.json

    if as_json:
        print(json.dumps(result, indent=2))
    else:
        for check in result["checks"]:
            status = "✓" if check["passed"] else "✗"
            sev = check["severity"]
            print(f"[{status}] [{sev}] {check['name']}")
            if check["detail"]:
                print(f"       {check['detail']}")

        print(f"\nTier: {result['tier']} (declared: {result['declared_tier']})")
        print(f"Summary: {result['summary']['passed']}/{result['summary']['total']} passed, "
              f"{result['summary']['failed']} failed, {result['summary']['warned']} warned")

    sys.exit(1 if result["summary"]["failed"] > 0 else 0)


if __name__ == "__main__":
    main()
