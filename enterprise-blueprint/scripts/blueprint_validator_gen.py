#!/usr/bin/env python3
"""
blueprint_validator_gen.py — Generate phase validators from blueprint deliverables.

The blueprint is the source of truth. Each phase declares:
- Deliverables (files/dirs that must exist)
- Validation Gate (description of what to validate)

This generates a validator script that checks EXACTLY what the blueprint declares.
No project-type registry — pure blueprint-driven validation.
"""

import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional


def extract_blueprint_deliverables(blueprint_path: Path) -> List[Dict[str, Any]]:
    """Extract deliverables and validation gates from blueprint per phase."""
    content = blueprint_path.read_text(encoding="utf-8")
    phases = []
    
    # First, try to find the Part VI implementation checklist tables.
    # Boundary matches init_blueprint.py's actual `# PART VI` (single hash)
    # heading and generate_checklist.py's identical boundary — kept in sync
    # so there is one shared definition of "where Part VI ends" (the old
    # `## PART VI...---\n` pattern both never matched the real heading and
    # could truncate early on any `---` inside Part VI).
    part_vi_match = re.search(
        r"#{1,2}\s*PART\s+VI\b.*?(?=\n#{1,2}\s*PART\s+|\n#{1,2}\s*CHANGE LOG\b|\Z)",
        content, re.DOTALL | re.IGNORECASE,
    )
    if part_vi_match:
        part_vi_content = part_vi_match.group(0)
        # Parse the tables for each phase
        lines = part_vi_content.split("\n")

        current_phase = None
        current_deliverables = []
        current_gate = ""
        col_idx = {}  # header-driven column-name -> index map, per table

        for line in lines:
            # Phase header
            phase_header_match = re.match(r"### PHASE-(\d+): ([^\n]+)", line)
            if phase_header_match:
                # Save previous phase
                if current_phase is not None:
                    phases.append({
                        "phase": current_phase["num"],
                        "title": current_phase["title"],
                        "tag": current_phase.get("tag", ""),
                        "flag": current_phase.get("flag", ""),
                        "deliverables": current_deliverables,
                        "validation_gate": current_gate,
                    })

                # Start new phase
                current_phase = {
                    "num": int(phase_header_match.group(1)),
                    "title": phase_header_match.group(2).strip(),
                }
                current_deliverables = []
                current_gate = ""
                col_idx = {}

            # Table row (inside a phase)
            elif current_phase and line.startswith("|") and "|" in line:
                cells = [p.strip() for p in line.split("|") if p.strip()]
                if not cells:
                    continue
                # Separator row (all dashes/colons) — skip, doesn't affect col_idx
                if all(re.match(r"^[-:]+$", c) for c in cells):
                    continue
                # Header row: first time we see "deliverable(s)" as a cell
                # name in this table, map every column by name instead of
                # trusting a fixed position — a reordered or renamed table
                # (e.g. "Gate" instead of "Validation Gate") still parses.
                lowered = [c.lower() for c in cells]
                if not col_idx and any("deliverable" in c for c in lowered):
                    for idx, cell in enumerate(lowered):
                        if "deliverable" in cell:
                            col_idx["deliverable"] = idx
                        elif "validation" in cell or cell == "gate":
                            col_idx["gate"] = idx
                    continue
                if "deliverable" not in col_idx or len(cells) <= col_idx["deliverable"]:
                    continue
                deliv_cell = cells[col_idx["deliverable"]]
                gate_cell = cells[col_idx["gate"]] if "gate" in col_idx and len(cells) > col_idx["gate"] else ""

                if deliv_cell and deliv_cell != "-":
                    # Split deliverables by comma, semicolon
                    for d in re.split(r"[,;]\s*", deliv_cell):
                        d = d.strip()
                        if d and d != "-":
                            current_deliverables.append(d)

                if gate_cell and gate_cell != "-":
                    current_gate = gate_cell

        # Don't forget the last phase
        if current_phase is not None:
            phases.append({
                "phase": current_phase["num"],
                "title": current_phase["title"],
                "tag": current_phase.get("tag", ""),
                "flag": current_phase.get("flag", ""),
                "deliverables": current_deliverables,
                "validation_gate": current_gate,
            })
    
    # Fallback: inline format (**Deliverable:** or init_blueprint.py's own
    # "### Deliverables" checkbox scaffold). Applied PER-PHASE to any phase
    # the primary table pass left with an empty deliverables list — not
    # gated behind "the whole phases list came back empty". A blueprint
    # with `### PHASE-N:` headers under Part VI but no pipe table (exactly
    # what init_blueprint.py's own checkbox scaffold produces) used to make
    # the primary pass "succeed" with phase entries that all had zero
    # deliverables, which meant this fallback — added in an earlier session
    # specifically to handle that scaffold — never actually ran, because it
    # was gated on `if not phases`, and `phases` was non-empty (just empty
    # *inside*). Confirmed via real end-to-end testing: every checkbox-style
    # blueprint silently generated an always-pass validator with an empty
    # deliverables list until this was scoped per-phase instead of
    # all-or-nothing.
    known_nums = {p["phase"] for p in phases}
    if not phases:
        phase_pattern = r"### PHASE-(\d+)[a-z]?: ([^>\n]+)"
        phase_matches = list(re.finditer(phase_pattern, content))
    else:
        phase_matches = []

    for phase_entry in phases:
        if phase_entry["deliverables"]:
            continue
        m = re.search(rf"### PHASE-{phase_entry['phase']}\b[a-z]?: [^\n]*", content)
        if not m:
            continue
        section = content[m.start():]
        next_phase = re.search(r"### PHASE-\d+", section[1:])
        if next_phase:
            section = section[:next_phase.start()]
        deliverables, validation_gate = _fallback_deliverables(section)
        if deliverables:
            phase_entry["deliverables"] = deliverables
        if validation_gate and not phase_entry["validation_gate"]:
            phase_entry["validation_gate"] = validation_gate

    for match in phase_matches:
        phase_num = int(match.group(1))
        if phase_num in known_nums:
            continue
        title = match.group(2).strip()

        section = content[match.start():]
        next_phase = re.search(r"### PHASE-\d+", section[1:])
        if next_phase:
            section = section[:next_phase.start()]

        tag_match = re.search(r"\*\*(?:Tag|Section Tag):\*\*\s*`?([^`\n]+)`?", section)
        tag = tag_match.group(1).strip() if tag_match else ""
        flag_match = re.search(r"\*\*(?:Flag|Feature Flag):\*\*\s*`?([^`\n]+)`?", section)
        flag = flag_match.group(1).strip() if flag_match else ""
        deliverables, validation_gate = _fallback_deliverables(section)

        phases.append({
            "phase": phase_num,
            "title": title,
            "tag": tag,
            "flag": flag,
            "deliverables": deliverables,
            "validation_gate": validation_gate,
        })

    return sorted(phases, key=lambda x: x["phase"])


def _fallback_deliverables(section: str):
    """Extract deliverables + validation gate from one phase's section text
    using either the '**Deliverable:**' bold-label format or
    init_blueprint.py's own '### Deliverables' checkbox scaffold."""
    deliverables = re.findall(r"\*\*Deliverable:\*\*\s*`?([^`\n]+)`?", section)
    gate_match = re.search(r"\*\*Validation Gate:\*\*\s*`?([^`\n]+)`?", section)
    validation_gate = gate_match.group(1).strip() if gate_match else ""

    if not deliverables:
        deliv_section_match = re.search(
            r"###\s*Deliverables\s*\n(.*?)(?=\n###\s|\Z)", section, re.DOTALL)
        if deliv_section_match:
            deliverables = [
                d.strip() for d in re.findall(
                    r"^-\s*\[[ xX]\]\s*\*\*PHASE-[\d.]+\*\*\s*(.+)$",
                    deliv_section_match.group(1), re.MULTILINE)
                if d.strip() and "[Define deliverable" not in d
            ]
        if not validation_gate:
            gate_section_match = re.search(
                r"###\s*Validation Gate\s*\n(.*?)(?=\n###\s|\Z)", section, re.DOTALL)
            if gate_section_match:
                quote_lines = re.findall(r"^>\s*(.+)$", gate_section_match.group(1), re.MULTILINE)
                validation_gate = " ".join(quote_lines).strip()

    return deliverables, validation_gate


_TYPE_TAG_RE = re.compile(
    r"\s*Type:\s*(file|glob|approval|external-check|review)"
    r"(?:\s+Validator:\s*([^\s,;]+))?\s*$",
    re.IGNORECASE,
)


def parse_deliverable(deliverable: str) -> Dict[str, Any]:
    """Parse a deliverable string into checkable components.

    Formats supported:
    - "config/database.yml" — file must exist
    - "scripts/*.sh" — glob pattern, at least one match
    - "modules/ (dir)" — directory must exist
    - "api/specs/openapi.json (valid JSON)" — file exists + content validation
    - "CHANGELOG.md (has CL- entries)" — file exists + pattern check
    - "decision.md Type: approval" — file exists + attestation fields present
    - "release sign-off Type: external-check Validator: scripts/check.py" —
      not auto-generatable; see references/blueprint-standard.md §6
    """
    deliverable = deliverable.strip()

    # Strip a trailing Type:/Validator: tag (blueprint-standard.md §6) before
    # anything else — it's metadata about *how* to check, not part of the
    # path/hint text itself.
    deliverable_type = "file"
    explicit_validator = ""
    type_match = _TYPE_TAG_RE.search(deliverable)
    if type_match:
        deliverable = deliverable[: type_match.start()].strip()
        deliverable_type = type_match.group(1).lower()
        explicit_validator = type_match.group(2) or ""

    # Check for inline validation hints in parentheses
    validation_hint = ""
    if "(" in deliverable and ")" in deliverable:
        hint_start = deliverable.rfind("(")
        hint_end = deliverable.rfind(")")
        if hint_end > hint_start:
            validation_hint = deliverable[hint_start+1:hint_end].strip()
            deliverable = deliverable[:hint_start].strip()

    # Determine type
    is_dir = deliverable.endswith("/") or deliverable.endswith(" (dir)")
    is_glob = deliverable_type == "glob" or "*" in deliverable or "?" in deliverable
    path = deliverable.replace(" (dir)", "").rstrip("/")

    return {
        "raw": deliverable,
        "path": path,
        "is_dir": is_dir,
        "is_glob": is_glob,
        "validation_hint": validation_hint,
        "type": deliverable_type,
        "validator": explicit_validator,
    }


def generate_validator_code(phase: Dict[str, Any]) -> str:
    """Generate a Python validator script for a phase based on its deliverables."""
    phase_num = phase["phase"]
    all_deliverables = [parse_deliverable(d) for d in phase.get("deliverables", [])]
    # external-check deliverables can't be auto-validated by a generic
    # generated script — they're enforced per-task by generate_checklist.py's
    # create_chain() instead (a real Validator: path, or a fails-closed
    # placeholder). Including them here would either silently skip them or
    # falsely fail on a path that was never meant to exist as a file.
    deliverables = [d for d in all_deliverables if d["type"] != "external-check"]
    skipped_external = [d for d in all_deliverables if d["type"] == "external-check"]
    validation_gate = phase.get("validation_gate", "")
    
    lines = []
    lines.append("#!/usr/bin/env python3")
    lines.append(f'"""')
    lines.append(f'Validator for Phase {phase_num}: {phase["title"]}')
    lines.append(f'Auto-generated from blueprint deliverables.')
    lines.append(f'Validation Gate: {validation_gate}')
    if skipped_external:
        lines.append(f'{len(skipped_external)} external-check deliverable(s) are enforced')
        lines.append('per-task by generate_checklist.py, not by this phase validator.')
    lines.append(f'"""')
    lines.append("")
    lines.append("import json")
    lines.append("import os")
    lines.append("import sys")
    lines.append("import re")
    lines.append("import glob")
    lines.append("from pathlib import Path")
    lines.append("")
    lines.append("def find_project_root(step_file):")
    lines.append('    """Walk up from step file to find project root (contains .blueprint-chain)."""')
    lines.append("    p = Path(step_file).resolve()")
    lines.append("    for parent in p.parents:")
    lines.append("        if (parent / '.blueprint-chain').exists():")
    lines.append("            return parent")
    lines.append("    return None")
    lines.append("")
    lines.append("def check_deliverable(project_root, deliverable):")
    lines.append('    """Check a single deliverable. Returns (ok, message)."""')
    lines.append("    path = deliverable['path']")
    lines.append("    full_path = project_root / path")
    lines.append("    is_dir = deliverable['is_dir']")
    lines.append("    is_glob = deliverable['is_glob']")
    lines.append("    hint = deliverable['validation_hint']")
    lines.append("    dtype = deliverable.get('type', 'file')")
    lines.append("")
    lines.append("    if is_glob:")
    lines.append("        matches = list(project_root.glob(path))")
    lines.append("        if not matches:")
    lines.append('            return False, f"No files matching glob: {path}"')
    lines.append('        return True, f"Found {len(matches)} matches for {path}: {[str(m.relative_to(project_root)) for m in matches]}"')
    lines.append("")
    lines.append("    if is_dir:")
    lines.append("        if not full_path.is_dir():")
    lines.append('            return False, f"Directory not found: {path}"')
    lines.append('        return True, f"Directory exists: {path}"')
    lines.append("")
    lines.append("    # File checks")
    lines.append("    if not full_path.exists():")
    lines.append('        return False, f"File not found: {path}"')
    lines.append("")
    lines.append("    # Type: approval — a sign-off marker, not a build artifact.")
    lines.append("    # Must contain both an 'Approved-By:' and a 'Date:' field, or")
    lines.append("    # it's just an empty file pretending to be an attestation.")
    lines.append("    if dtype == 'approval':")
    lines.append("        approval_content = full_path.read_text()")
    lines.append("        has_approver = re.search(r'Approved-By:\\s*\\S+', approval_content)")
    lines.append("        has_date = re.search(r'Date:\\s*\\S+', approval_content)")
    lines.append("        if not (has_approver and has_date):")
    lines.append('            return False, f"Approval marker {path} is missing Approved-By:/Date: fields"')
    lines.append('        return True, f"Approval attested: {path}"')
    lines.append("")
    lines.append("    # Type: review — Creative Orchestration Doctrine Principle V")
    lines.append("    # ('every creative layer has a corresponding reviewer'). Stricter")
    lines.append("    # than 'approval': the reviewer must be a DIFFERENT agent than")
    lines.append("    # whoever is assigned to this phase, not just anyone who signs.")
    lines.append("    if dtype == 'review':")
    lines.append("        review_content = full_path.read_text()")
    lines.append("        reviewer_m = re.search(r'Reviewed-By:\\s*(\\S+)', review_content)")
    lines.append("        has_date = re.search(r'Date:\\s*\\S+', review_content)")
    lines.append("        critique_m = re.search(r'Critique:\\s*(.+)', review_content)")
    lines.append("        if not (reviewer_m and has_date and critique_m):")
    lines.append('            return False, f"Review {path} is missing Reviewed-By:/Date:/Critique: fields"')
    lines.append("        if len(critique_m.group(1).strip()) < 10:")
    lines.append('            return False, f"Review {path} Critique: field is too short to be a real critique"')
    lines.append("        reviewer = reviewer_m.group(1).strip()")
    lines.append(f"        assignments_path = project_root / 'assignments.json'")
    lines.append("        assignee = None")
    lines.append("        if assignments_path.exists():")
    lines.append("            try:")
    lines.append("                adata = json.loads(assignments_path.read_text())")
    lines.append(f"                entry = adata.get('assignments', {{}}).get('PHASE-{phase_num}')")
    lines.append("                assignee = (entry or {}).get('agent')")
    lines.append("            except (json.JSONDecodeError, OSError):")
    lines.append("                pass")
    lines.append("        if assignee and reviewer == assignee:")
    lines.append('            return False, f"Review {path}: Reviewed-By ({reviewer}) is the same agent as the phase assignee — reviewer must be independent"')
    lines.append('        return True, f"Reviewed by {reviewer} (assignee: {assignee or \'unknown\'}): {path}"')
    lines.append("")
    lines.append("    # Content validation hints")
    lines.append("    if hint:")
    lines.append("        if 'valid JSON' in hint.lower() or 'json' in hint.lower():")
    lines.append("            try:")
    lines.append("                json.loads(full_path.read_text())")
    lines.append("            except json.JSONDecodeError as e:")
    lines.append('                return False, f"Invalid JSON in {path}: {e}"')
    lines.append('            return True, f"Valid JSON: {path}"')
    lines.append("        elif 'CL-' in hint or 'changelog' in hint.lower():")
    lines.append("            content = full_path.read_text()")
    lines.append("            if not re.search(r'CL-\\d+', content):")
    lines.append('                return False, f"No CL- entries in {path}"')
    lines.append('            return True, f"CHANGELOG has CL- entries: {path}"')
    lines.append("        elif 'executable' in hint.lower():")
    lines.append("            if not os.access(full_path, os.X_OK):")
    lines.append('                return False, f"Not executable: {path}"')
    lines.append('            return True, f"Executable: {path}"')
    lines.append("        elif 'yaml' in hint.lower() or 'yml' in hint.lower():")
    lines.append("            # No YAML parser is guaranteed available in an arbitrary")
    lines.append("            # target project (this validator ships standalone, outside")
    lines.append("            # enterprise-blueprint's own scripts/); degrade to a existence-only")
    lines.append("            # pass with a note rather than crash or assume PyYAML.")
    lines.append("            try:")
    lines.append("                import yaml as _y")
    lines.append("                _y.safe_load(full_path.read_text())")
    lines.append("                return True, f\"Valid YAML: {path}\"")
    lines.append("            except ImportError:")
    lines.append('                return True, f"YAML present but unverified (no parser available): {path}"')
    lines.append("            except Exception as e:")
    lines.append('                return False, f"Invalid YAML in {path}: {e}"')
    lines.append("")
    lines.append('    return True, f"File exists: {path}"')
    lines.append("")
    lines.append("def check_agent_assignment(project_root, phase_num):")
    lines.append('    """Real read side of agent delegation: this phase\'s gate FAILs')
    lines.append("    if assignments.json (written by assign_agents.py --assign or")
    lines.append("    --model-map) has no real agent on this phase — closes the gap")
    lines.append("    where assignment data was written but nothing ever consumed it.\"\"\"")
    lines.append("    assignments_path = project_root / 'assignments.json'")
    lines.append("    if not assignments_path.exists():")
    lines.append('        return False, f"No assignments.json — PHASE-{phase_num} has no assigned agent (run assign_agents.py)"')
    lines.append("    try:")
    lines.append("        data = json.loads(assignments_path.read_text())")
    lines.append("    except (json.JSONDecodeError, OSError) as e:")
    lines.append('        return False, f"Could not read assignments.json: {e}"')
    lines.append("    entry = data.get('assignments', {}).get(f'PHASE-{phase_num}')")
    lines.append("    agent = (entry or {}).get('agent', 'unassigned')")
    lines.append("    if not entry or agent == 'unassigned':")
    lines.append('        return False, f"PHASE-{phase_num} has no assigned agent in assignments.json"')
    lines.append('    return True, f"PHASE-{phase_num} assigned to {agent}"')
    lines.append("")
    lines.append("def main():")
    lines.append("    if len(sys.argv) < 2:")
    lines.append('        print("Usage: validator.py <step-file-path>")')
    lines.append("        sys.exit(1)")
    lines.append("")
    lines.append("    step_file = sys.argv[1]")
    lines.append("    project_root = find_project_root(step_file)")
    lines.append("    if not project_root:")
    lines.append('        print("ERROR: Could not find project root (.blueprint-chain)")')
    lines.append("        sys.exit(1)")
    lines.append("")
    
    # Add deliverable list
    lines.append("    deliverables = [")
    for d in deliverables:
        # Use Python True/False instead of JSON true/false
        d_python = d.copy()
        d_python['is_dir'] = d['is_dir']
        d_python['is_glob'] = d['is_glob']
        lines.append(f"        {repr(d_python)},")
    lines.append("    ]")
    lines.append("")
    lines.append("    all_ok = True")
    lines.append("    messages = []")
    lines.append("")
    lines.append("    # Agent delegation must be real, not just documented — this phase's")
    lines.append("    # gate fails if no agent is actually assigned (see check_agent_assignment).")
    lines.append(f"    a_ok, a_msg = check_agent_assignment(project_root, {phase_num})")
    lines.append("    messages.append(a_msg)")
    lines.append("    if not a_ok:")
    lines.append("        all_ok = False")
    lines.append("")
    lines.append("    for d in deliverables:")
    lines.append("        ok, msg = check_deliverable(project_root, d)")
    lines.append("        messages.append(msg)")
    lines.append("        if not ok:")
    lines.append("            all_ok = False")
    lines.append("")
    lines.append("    # Print all messages")
    lines.append("    for msg in messages:")
    lines.append('        print(msg)')
    lines.append("")
    lines.append("    if all_ok:")
    lines.append(f'        print(f"OK: Phase {phase_num} validation passed")')
    lines.append("        sys.exit(0)")
    lines.append("    else:")
    lines.append(f'        print(f"FAIL: Phase {phase_num} validation failed")')
    lines.append("        sys.exit(1)")
    lines.append("")
    lines.append("if __name__ == '__main__':")
    lines.append("    main()")
    
    return "\n".join(lines)


def generate_all_validators(blueprint_path: Path, output_dir: Path) -> List[Path]:
    """Generate validator scripts for all phases in blueprint."""
    output_dir.mkdir(parents=True, exist_ok=True)
    phases = extract_blueprint_deliverables(blueprint_path)
    generated = []
    
    for phase in phases:
        phase_num = phase["phase"]
        validator_code = generate_validator_code(phase)
        validator_path = output_dir / f"validate_phase{phase_num}_blueprint.py"
        validator_path.write_text(validator_code)
        validator_path.chmod(0o755)
        generated.append(validator_path)
        print(f"[OK] Generated {validator_path}")
    
    return generated


def get_validator_for_phase(blueprint_path: Path, phase_num: int, output_dir: Path) -> Optional[Path]:
    """Get (generate if needed) validator for specific phase."""
    validator_path = output_dir / f"validate_phase{phase_num}_blueprint.py"
    if validator_path.exists():
        return validator_path
    
    # Generate all and return the one requested
    generated = generate_all_validators(blueprint_path, output_dir)
    for v in generated:
        if f"validate_phase{phase_num}_blueprint.py" in str(v):
            return v
    return None


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate validators from blueprint deliverables")
    parser.add_argument("blueprint", help="Path to blueprint.md")
    parser.add_argument("--output-dir", "-o", help="Output directory for validators", default=".blueprint-chain/validators")
    parser.add_argument("--phase", type=int, help="Generate only for specific phase")
    args = parser.parse_args()
    
    bp_path = Path(args.blueprint)
    out_dir = Path(args.output_dir)

    if not bp_path.is_file():
        print(f"Error: blueprint not found: {bp_path}", file=sys.stderr)
        sys.exit(1)

    if args.phase:
        v = get_validator_for_phase(bp_path, args.phase, out_dir)
        if v:
            print(f"Generated: {v}")
        else:
            print(f"No deliverables found for phase {args.phase}")
            sys.exit(1)
    else:
        generated = generate_all_validators(bp_path, out_dir)
        print(f"Generated {len(generated)} validators in {out_dir}")