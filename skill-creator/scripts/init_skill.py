#!/usr/bin/env python3
"""
Skill Creator — Unified Skill Initializer

Creates a new skill directory from template. Supports both standard and
enterprise-grade scaffolding via the --enterprise flag.

Usage:
    python3 init_skill.py <skill-name> --path <output-dir>
    python3 init_skill.py <skill-name> --path <output-dir> --resources scripts,references,assets
    python3 init_skill.py <skill-name> --path <output-dir> --enterprise
    python3 init_skill.py <skill-name> --path <output-dir> --examples
    python3 init_skill.py <skill-name> --path <output-dir> --dry-run
    python3 init_skill.py --help

Flags:
    --enterprise    Scaffold with all 8 enterprise pillars pre-populated
    --resources     Comma-separated: scripts,references,assets (default: none for standard, all for enterprise)
    --examples      Create example placeholder files in resource directories
    --dry-run       Preview what would be created without writing files
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

MAX_SKILL_NAME_LENGTH = 64
ALLOWED_RESOURCES = {"scripts", "references", "references/lessons", "assets"}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def normalize_skill_name(skill_name):
    normalized = skill_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = normalized.strip("-")
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized


def title_case(name):
    return " ".join(w.capitalize() for w in name.split("-"))


# ── Standard Skill Template ──────────────────────────────────────

STANDARD_SKILL_MD = """---
name: {name}
description: [TODO: Complete and informative explanation of what the skill does and when to use it. Include WHEN to use this skill - specific scenarios, file types, or tasks that trigger it.]
version: 0.0.1
---

# {title}

## Overview

[TODO: 1-2 sentences explaining what this skill enables]

## Workflow: [Primary Workflow]

[TODO: Step-by-step primary workflow]

## Resources

[TODO: Add scripts/, references/, or assets/ as needed. Delete this section if no resources are required.]
"""


# ── Enterprise Skill Template ────────────────────────────────────

ENTERPRISE_SKILL_MD = '''---
name: {name}
description: "[TODO: WHAT this skill does — 1-2 sentences]. Provider-agnostic: works with any LLM backend (OpenAI, Claude, Mistral, Gemini, Hermes, Copilot, or any agent with tool use). Free-first: starts with $0 tools before requiring paid services. Use when: [TODO: specific trigger scenarios and keywords]."
version: 0.0.1
---

# {title}

[TODO: 1-2 sentence overview of what this skill enables]

## Provider Compatibility

| Provider | Compatibility | Notes |
|---|---|---|
| MuleRun | Full | Native session, compute, drive support |
| Claude (Anthropic) | Full | MCP servers, tool use |
| OpenAI / ChatGPT | Full | Function calling, Actions |
| Mistral / Vibe | Full | Tool calling, script execution |
| Gemini (Google) | Full | Extensions, Vertex AI |
| Hermes (Nous) | Full | Tool-use fine-tuned |
| GitHub Copilot | Partial | [TODO: note limitations] |
| Any LLM + tools | Full | Scripts are provider-independent |

## Free-First Strategy

| Tier | Cost | Stack | When to Use |
|---|---|---|---|
| **Tier 0** | $0/mo | [TODO: free tools] | Starting out, validating approach |
| **Tier 1** | $0-15/mo | [TODO: one paid service] | Validated and generating value |
| **Tier 2** | $15-50/mo | [TODO: full paid stack] | Proven ROI justifies cost |

Escalation rule: Never upgrade until current tier's value covers next tier's cost with 2x margin.

See [references/free-first-strategy.md](references/free-first-strategy.md) for full alternatives and upgrade decision matrix.

## Core Stack

| Component | Role | Cost | Free Alternative |
|---|---|---|---|
| [TODO: Primary tool] | [What it does] | $X/mo | [Free option] ($0) |

## Workflow: [Primary Workflow Name]

[TODO: Step-by-step primary workflow]

See [references/workflow-guide.md](references/workflow-guide.md) for detailed procedures.

## Scripts

| Script | Purpose |
|---|---|
| `scripts/setup.py` | One-command initialization and deployment |
| `scripts/pipeline.py` | Core operational pipeline with queue management |

## Enforced Output Statistics

Every operation MUST conclude with a structured statistics block:

```json
{{{{
  "operation": "operation_name",
  "timestamp": "ISO8601",
  "status": "success | partial | failed",
  "duration_seconds": 0.0,
  "inputs": {{{{"count": 0}}}},
  "outputs": {{{{"count": 0}}}},
  "errors": [],
  "cost": {{{{"tier": 0, "amount_usd": 0.0}}}}
}}}}
```

Enforcement: Statistics output is non-negotiable. If data is unavailable, use `[pending]` markers.

## Error Handling

See [references/error-handling.md](references/error-handling.md) for the full error catalog and recovery procedures.

| Error Type | Response |
|---|---|
| Network failure | Retry with exponential backoff (3 attempts) |
| Auth failure | Log alert, attempt key refresh |
| Rate limiting | Respect Retry-After, queue for next window |
| Partial completion | Save progress, enable resume |

## Enhancement Hooks

| Skill | Enhancement | When to Add |
|---|---|---|
| `html-report` | Visual analytics with charts | When generating reports |
| `xlsx` | Spreadsheet export | When data needs external analysis |
| `playwright-cli` | Browser automation | When scraping or registration needed |

## Key References

- **Detailed workflow procedures**: [references/workflow-guide.md](references/workflow-guide.md)
- **Error catalog and recovery**: [references/error-handling.md](references/error-handling.md)
- **Free alternatives and cost tiers**: [references/free-first-strategy.md](references/free-first-strategy.md)
'''


ENTERPRISE_SETUP_SCRIPT = '''#!/usr/bin/env python3
"""
{title} — Setup & Deployment

One-command initialization for the {name} skill.

Usage:
    python3 setup.py                 # Full setup
    python3 setup.py --dry-run       # Preview without changes
    python3 setup.py --status        # Show current state
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path.home() / ".{name}"
CONFIG_PATH = STATE_DIR / "config.json"

DEFAULT_CONFIG = {{
    "version": 1,
    "created_at": "",
    "status": "initializing",
}}

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def setup(dry_run=False):
    prefix = "[DRY RUN] " if dry_run else ""
    print(f"{{prefix}}Setting up {name}...\\n")
    dirs = [STATE_DIR, STATE_DIR / "analytics", STATE_DIR / "reports", STATE_DIR / "logs"]
    for d in dirs:
        if not dry_run:
            d.mkdir(parents=True, exist_ok=True)
        print(f"  {{prefix}}Directory: {{d}}")
    if not dry_run and not CONFIG_PATH.exists():
        config = DEFAULT_CONFIG.copy()
        config["created_at"] = now_iso()
        CONFIG_PATH.write_text(json.dumps(config, indent=2))
    print(f"\\n{{prefix}}Setup complete.")

def show_status():
    if CONFIG_PATH.exists():
        print(json.dumps(json.loads(CONFIG_PATH.read_text()), indent=2))
    else:
        print(f"Not initialized. Run: python3 setup.py")

def main():
    if "--dry-run" in sys.argv:
        setup(dry_run=True)
    elif "--status" in sys.argv:
        show_status()
    elif "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
    else:
        setup()

if __name__ == "__main__":
    main()
'''


ENTERPRISE_PIPELINE_SCRIPT = '''#!/usr/bin/env python3
"""
{title} — Core Pipeline

Queue-based processing pipeline with parallel execution and retry logic.

Usage:
    python3 pipeline.py process [--max-concurrent 5]
    python3 pipeline.py status
    python3 pipeline.py retry
    python3 pipeline.py --help
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path.home() / ".{name}"
QUEUE_FILE = STATE_DIR / "queue.jsonl"
RETRY_FILE = STATE_DIR / "retry_queue.jsonl"
ANALYTICS_DIR = STATE_DIR / "analytics"
MAX_RETRIES = 3

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def read_jsonl(filepath):
    if not Path(filepath).exists():
        return []
    records = []
    for line in Path(filepath).read_text().strip().split("\\n"):
        if line.strip():
            records.append(json.loads(line))
    return records

def append_jsonl(filepath, record):
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "a") as f:
        f.write(json.dumps(record) + "\\n")

def do_process():
    pending = [r for r in read_jsonl(QUEUE_FILE) if r.get("status") == "pending"]
    if not pending:
        print("Queue empty.")
        return
    print(f"Processing {{len(pending)}} items...")

def do_status():
    queue = read_jsonl(QUEUE_FILE)
    retry = read_jsonl(RETRY_FILE)
    pending = len([r for r in queue if r.get("status") == "pending"])
    print(json.dumps({{"pending": pending, "retry": len(retry), "total": len(queue)}}, indent=2))

def do_retry():
    retries = read_jsonl(RETRY_FILE)
    requeued = 0
    for item in retries:
        if item.get("retries", 0) < MAX_RETRIES:
            item["status"] = "pending"
            append_jsonl(QUEUE_FILE, item)
            requeued += 1
    if retries:
        Path(RETRY_FILE).write_text("")
    print(f"Requeued: {{requeued}}")

COMMANDS = {{"process": do_process, "status": do_status, "retry": do_retry}}

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd in ("--help", "-h", "help"):
        print(__doc__)
    elif cmd in COMMANDS:
        COMMANDS[cmd]()
    else:
        print(f"Unknown: {{cmd}}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''


ENTERPRISE_WORKFLOW_GUIDE = '''# {title} — Workflow Guide

Detailed procedures for all {name} workflows.

## Table of Contents

1. [Primary Workflow](#1-primary-workflow)
2. [Configuration](#2-configuration)
3. [Scheduling](#3-scheduling)

---

## 1. Primary Workflow

[TODO: Detailed step-by-step workflow with examples]

## 2. Configuration

Configuration is stored in `~/.{name}/config.json`:

```json
{{
  "version": 1,
  "created_at": "ISO8601",
  "status": "active"
}}
```

## 3. Scheduling

If recurring execution is needed, set up cron jobs using the setup script.
'''


ENTERPRISE_ERROR_HANDLING = '''# {title} — Error Handling

Error catalog and recovery procedures.

## Table of Contents

1. [Error Categories](#error-categories)
2. [Recovery Procedures](#recovery-procedures)
3. [Error Logging](#error-logging)

---

## Error Categories

| Category | Examples | Response |
|---|---|---|
| **Network** | API timeout, DNS failure | Retry 3x with exponential backoff |
| **Authentication** | Expired key, invalid token | Log alert, attempt refresh |
| **Rate Limiting** | 429 response, quota exceeded | Respect Retry-After header |
| **Invalid Input** | Malformed data, missing file | Validate before processing |
| **Partial Completion** | N/M items processed | Save progress, enable resume |
| **Service Down** | Third-party API outage | Fallback or queue for retry |

## Recovery Procedures

### Automatic Recovery
- Failed items move to `retry_queue.jsonl`
- Retry up to 3 times with exponential backoff
- After 3 failures: permanent failure log

### Manual Recovery
1. `pipeline.py status` — Check queue state
2. `pipeline.py retry` — Requeue failed items
3. Check logs in `~/.{name}/logs/`

## Error Logging

```json
{{
  "timestamp": "ISO8601",
  "error_type": "network | auth | rate_limit | input | partial | service_down",
  "operation": "operation_name",
  "message": "Human-readable description",
  "recoverable": true,
  "retry_count": 0,
  "resolution": "retried | queued | fallback | failed_permanent"
}}
```
'''


ENTERPRISE_FREE_FIRST = '''# {title} — Free-First Strategy

Cost tiers and free alternatives.

## Free Alternatives

| Paid Component | Cost | Free Alternative | Trade-offs |
|---|---|---|---|
| [TODO: Component 1] | $X/mo | [Free option] | [What you lose] |

## Cost Tiers

| Tier | Cost | Stack | Escalation Criteria |
|---|---|---|---|
| Tier 0 | $0/mo | Free tools only | Default starting point |
| Tier 1 | $0-15/mo | One paid service | Value > 2x cost |
| Tier 2 | $15-50/mo | Full paid stack | Proven ROI |

## Upgrade Decision Matrix

| Metric | Hold at Free | Evaluate | Upgrade |
|---|---|---|---|
| Volume / day | Low | Medium | High |
| Quality gap | Comparable | Noticeable | Significant |
| Time cost | <30min/day | 30-60min/day | >60min/day |
'''


def parse_resources(raw_resources):
    if not raw_resources:
        return []
    resources = [item.strip() for item in raw_resources.split(",") if item.strip()]
    invalid = sorted({item for item in resources if item not in ALLOWED_RESOURCES})
    if invalid:
        allowed = ", ".join(sorted(ALLOWED_RESOURCES))
        print(f"[ERROR] Unknown resource type(s): {', '.join(invalid)}")
        print(f"   Allowed: {allowed}")
        sys.exit(1)
    return list(dict.fromkeys(resources))


def init_standard(name, skill_dir, resources, examples, dry_run):
    """Initialize a standard skill."""
    title = title_case(name)
    prefix = "[DRY RUN] " if dry_run else ""

    # SKILL.md
    if not dry_run:
        (skill_dir / "SKILL.md").write_text(STANDARD_SKILL_MD.format(name=name, title=title))
    print(f"  {prefix}Created SKILL.md")

    # Resource directories
    for res in resources:
        res_dir = skill_dir / res
        if not dry_run:
            res_dir.mkdir(parents=True, exist_ok=True)
        if examples and not dry_run:
            if res == "scripts":
                p = res_dir / "example.py"
                p.write_text(f'#!/usr/bin/env python3\n"""Example script for {name}"""\n\ndef main():\n    print("Hello from {name}")\n\nif __name__ == "__main__":\n    main()\n')
                p.chmod(0o755)
            elif res == "references":
                (res_dir / "api_reference.md").write_text(f"# {title} — API Reference\n\n[TODO: Add reference content]\n")
            elif res == "references/lessons":
                (res_dir / ".gitkeep").write_text("")
            elif res == "assets":
                (res_dir / "example_asset.txt").write_text("# Placeholder asset file\n")
        print(f"  {prefix}Created {res}/")


def init_enterprise(name, skill_dir, dry_run):
    """Initialize an enterprise-grade skill with all 8 pillars."""
    title = title_case(name)
    prefix = "[DRY RUN] " if dry_run else ""

    if dry_run:
        print(f"  {prefix}Would create:")
        print(f"    SKILL.md")
        print(f"    scripts/setup.py")
        print(f"    scripts/pipeline.py")
        print(f"    references/workflow-guide.md")
        print(f"    references/error-handling.md")
        print(f"    references/free-first-strategy.md")
        print(f"    references/lessons/")
        return

    # SKILL.md
    (skill_dir / "SKILL.md").write_text(ENTERPRISE_SKILL_MD.format(name=name, title=title))
    print(f"  Created SKILL.md (enterprise template)")

    # Scripts
    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "setup.py").write_text(ENTERPRISE_SETUP_SCRIPT.format(name=name, title=title))
    (scripts_dir / "pipeline.py").write_text(ENTERPRISE_PIPELINE_SCRIPT.format(name=name, title=title))
    for f in scripts_dir.glob("*.py"):
        f.chmod(0o755)
    print(f"  Created scripts/setup.py, scripts/pipeline.py")

    # References
    refs_dir = skill_dir / "references"
    refs_dir.mkdir()
    (refs_dir / "workflow-guide.md").write_text(ENTERPRISE_WORKFLOW_GUIDE.format(name=name, title=title))
    (refs_dir / "error-handling.md").write_text(ENTERPRISE_ERROR_HANDLING.format(name=name, title=title))
    (refs_dir / "free-first-strategy.md").write_text(ENTERPRISE_FREE_FIRST.format(name=name, title=title))
    lessons_dir = refs_dir / "lessons"
    lessons_dir.mkdir()
    print(f"  Created references/workflow-guide.md, error-handling.md, free-first-strategy.md")
    print(f"  Created references/lessons/")


def main():
    parser = argparse.ArgumentParser(
        description="Create a new skill directory with template SKILL.md.",
        epilog="Use --enterprise to scaffold with all 8 enterprise pillars."
    )
    parser.add_argument("skill_name", help="Skill name (normalized to hyphen-case)")
    parser.add_argument("--path", required=True, help="Output directory for the skill")
    parser.add_argument("--resources", default="", help="Comma-separated: scripts,references,assets")
    parser.add_argument("--examples", action="store_true", help="Create example files in resource dirs")
    parser.add_argument("--enterprise", action="store_true", help="Use enterprise-grade template with all 8 pillars")
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating files")
    args = parser.parse_args()

    raw_name = args.skill_name
    name = normalize_skill_name(raw_name)
    if not name:
        print("[ERROR] Skill name must include at least one letter or digit.")
        sys.exit(1)
    if len(name) > MAX_SKILL_NAME_LENGTH:
        print(f"[ERROR] Name '{name}' too long ({len(name)} chars). Max: {MAX_SKILL_NAME_LENGTH}.")
        sys.exit(1)
    if name != raw_name:
        print(f"Note: Normalized '{raw_name}' to '{name}'.")

    skill_dir = Path(args.path).resolve() / name

    if skill_dir.exists() and not args.dry_run:
        print(f"[ERROR] Directory already exists: {skill_dir}")
        sys.exit(1)

    prefix = "[DRY RUN] " if args.dry_run else ""
    mode = "enterprise" if args.enterprise else "standard"
    print(f"{prefix}Initializing {mode} skill: {name}")
    print(f"   Location: {skill_dir}\n")

    if not args.dry_run:
        skill_dir.mkdir(parents=True, exist_ok=False)

    if args.enterprise:
        init_enterprise(name, skill_dir, args.dry_run)
    else:
        resources = parse_resources(args.resources)
        if args.examples and not resources:
            print("[ERROR] --examples requires --resources.")
            sys.exit(1)
        init_standard(name, skill_dir, resources, args.examples, args.dry_run)

    print(f"\n{prefix}Skill '{name}' initialized at {skill_dir}")
    if not args.dry_run:
        print(f"\nNext: Edit SKILL.md to replace [TODO] placeholders.")
        if args.enterprise:
            print(f"Validate: python3 scripts/validate_pro.py {skill_dir} --verbose")
        else:
            print(f"Validate: python3 scripts/validate.py {skill_dir}")


if __name__ == "__main__":
    main()
