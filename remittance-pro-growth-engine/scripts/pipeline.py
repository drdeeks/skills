#!/usr/bin/env python3
"""
Remittance Pro Growth Engine — Lead Pipeline
Multi-stage lead processing: discovery → qualification → outreach → conversion tracking.

Commands:
  ingest     — Add leads from a source file or manual entry
  qualify    — Score and filter leads by corridor relevance
  process    — Move qualified leads through outreach stages
  status     — Show pipeline stage counts
  export     — Export leads to CSV for external tools
  help       — Show usage

Usage:
  python3 pipeline.py ingest --source leads.json
  python3 pipeline.py ingest --manual '{"name":"OFW Group","corridor":"US→PH","channel":"facebook","contact":"fb.com/ofwgroup","size":5000}'
  python3 pipeline.py qualify --min-score 40
  python3 pipeline.py process --stage outreach --batch 20
  python3 pipeline.py status
  python3 pipeline.py export --stage qualified --output leads_export.csv
  python3 pipeline.py --dry-run process --stage outreach
"""

import json
import csv
import os
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(os.environ.get("GROWTH_ENGINE_DIR", "."))
PIPELINE_DIR = BASE_DIR / "pipeline"

# Stage files
STAGES = {
    "discovered": PIPELINE_DIR / "discovered.jsonl",
    "qualified": PIPELINE_DIR / "qualified.jsonl",
    "outreach_pending": PIPELINE_DIR / "outreach_pending.jsonl",
    "outreach_sent": PIPELINE_DIR / "outreach_sent.jsonl",
    "responded": PIPELINE_DIR / "responded.jsonl",
    "converted": PIPELINE_DIR / "converted.jsonl",
    "rejected": PIPELINE_DIR / "rejected.jsonl",
}

# Scoring weights for lead qualification
SCORING = {
    "corridor_priority": {
        "US→Mexico": 95, "UAE→India": 90, "US→Philippines": 85,
        "Saudi→Pakistan": 75, "UK→Nigeria": 70, "Canada→India": 65,
        "US→Guatemala": 60, "US→Colombia": 60, "Italy→Romania": 55,
        "Korea→Philippines": 55, "Japan→Philippines": 50,
    },
    "channel_weight": {
        "whatsapp": 20, "telegram": 18, "facebook": 15, "email": 14,
        "instagram": 12, "tiktok": 10, "twitter": 8, "linkedin": 12,
        "discord": 10, "viber": 15, "youtube": 8, "blog": 6,
        "governance_forum": 18, "conference": 16,
    },
    "size_tiers": [
        (100_000, 30), (50_000, 25), (10_000, 20), (5_000, 15),
        (1_000, 10), (500, 5), (0, 2),
    ],
    "type_weight": {
        "community_group": 15, "influencer": 18, "organization": 20,
        "dao": 22, "platform": 25, "media": 12, "individual": 5,
    },
}


def ensure_dirs():
    PIPELINE_DIR.mkdir(parents=True, exist_ok=True)


def append_jsonl(filepath, record):
    ensure_dirs()
    with open(filepath, "a") as f:
        f.write(json.dumps(record) + "\n")


def read_jsonl(filepath):
    if not filepath.exists():
        return []
    with open(filepath) as f:
        return [json.loads(line) for line in f if line.strip()]


def score_lead(lead):
    score = 0
    corridor = lead.get("corridor", "")
    score += SCORING["corridor_priority"].get(corridor, 30)

    channel = lead.get("channel", "")
    score += SCORING["channel_weight"].get(channel, 5)

    size = lead.get("size", 0)
    for threshold, points in SCORING["size_tiers"]:
        if size >= threshold:
            score += points
            break

    lead_type = lead.get("type", "individual")
    score += SCORING["type_weight"].get(lead_type, 5)

    return min(score, 200)


def cmd_ingest(args):
    dry_run = "--dry-run" in args
    source = None
    manual = None
    for i, a in enumerate(args):
        if a == "--source" and i + 1 < len(args):
            source = args[i + 1]
        if a == "--manual" and i + 1 < len(args):
            manual = args[i + 1]

    leads = []
    if source:
        with open(source) as f:
            data = json.load(f)
            leads = data if isinstance(data, list) else [data]
    elif manual:
        leads = [json.loads(manual)]
    else:
        print("Provide --source <file.json> or --manual '<json>'")
        return

    count = 0
    for lead in leads:
        lead["ingested_at"] = datetime.utcnow().isoformat()
        lead["score"] = score_lead(lead)
        prefix = "[DRY RUN] " if dry_run else ""
        print(f"{prefix}Ingested: {lead.get('name', '?')} | corridor={lead.get('corridor', '?')} | score={lead['score']}")
        if not dry_run:
            append_jsonl(STAGES["discovered"], lead)
        count += 1

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Total ingested: {count}")


def cmd_qualify(args):
    dry_run = "--dry-run" in args
    min_score = 40
    for i, a in enumerate(args):
        if a == "--min-score" and i + 1 < len(args):
            min_score = int(args[i + 1])

    leads = read_jsonl(STAGES["discovered"])
    qualified = read_jsonl(STAGES["qualified"])
    existing_names = {l.get("name") for l in qualified}

    new_qualified = 0
    rejected = 0
    for lead in leads:
        if lead.get("name") in existing_names:
            continue
        score = lead.get("score", score_lead(lead))
        if score >= min_score:
            lead["qualified_at"] = datetime.utcnow().isoformat()
            lead["score"] = score
            if not dry_run:
                append_jsonl(STAGES["qualified"], lead)
            new_qualified += 1
        else:
            lead["rejected_reason"] = f"Score {score} < {min_score}"
            if not dry_run:
                append_jsonl(STAGES["rejected"], lead)
            rejected += 1

    prefix = "[DRY RUN] " if dry_run else ""
    print(f"{prefix}Qualified: {new_qualified} | Rejected: {rejected}")


def cmd_process(args):
    dry_run = "--dry-run" in args
    stage = "outreach"
    batch = 20
    for i, a in enumerate(args):
        if a == "--stage" and i + 1 < len(args):
            stage = args[i + 1]
        if a == "--batch" and i + 1 < len(args):
            batch = int(args[i + 1])

    if stage == "outreach":
        qualified = read_jsonl(STAGES["qualified"])
        already_sent = {l.get("name") for l in read_jsonl(STAGES["outreach_sent"])}
        pending = [l for l in qualified if l.get("name") not in already_sent][:batch]

        prefix = "[DRY RUN] " if dry_run else ""
        for lead in pending:
            lead["outreach_queued_at"] = datetime.utcnow().isoformat()
            print(f"{prefix}Queued for outreach: {lead.get('name', '?')} via {lead.get('channel', '?')}")
            if not dry_run:
                append_jsonl(STAGES["outreach_pending"], lead)

        print(f"\n{prefix}Queued: {len(pending)}")


def cmd_status(args):
    print(f"{'STAGE':20s} {'COUNT':>8s}")
    print("-" * 32)
    total = 0
    for stage_name, filepath in STAGES.items():
        count = len(read_jsonl(filepath))
        total += count
        print(f"{stage_name:20s} {count:8d}")
    print("-" * 32)
    print(f"{'TOTAL':20s} {total:8d}")


def cmd_export(args):
    stage = "qualified"
    output = "leads_export.csv"
    for i, a in enumerate(args):
        if a == "--stage" and i + 1 < len(args):
            stage = args[i + 1]
        if a == "--output" and i + 1 < len(args):
            output = args[i + 1]

    leads = read_jsonl(STAGES.get(stage, STAGES["qualified"]))
    if not leads:
        print(f"No leads in stage: {stage}")
        return

    keys = list(leads[0].keys())
    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(leads)
    print(f"Exported {len(leads)} leads to {output}")


def print_usage():
    print(__doc__)


COMMANDS = {
    "ingest": cmd_ingest,
    "qualify": cmd_qualify,
    "process": cmd_process,
    "status": cmd_status,
    "export": cmd_export,
    "help": lambda a: print_usage(),
}


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("--help", "help"):
        print_usage()
        return

    cmd = args[0]
    if cmd in COMMANDS:
        COMMANDS[cmd](args[1:])
    else:
        print(f"Unknown command: {cmd}")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
