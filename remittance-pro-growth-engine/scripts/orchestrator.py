#!/usr/bin/env python3
"""
Remittance Pro Growth Engine — Orchestrator
Multi-agent dispatch, polling, decision engine for client acquisition campaigns.

Commands:
  dispatch   — Launch subagent campaigns across channels
  poll       — Check status of running campaigns
  report     — Generate campaign performance report
  decide     — Run decision engine on latest metrics
  health     — Verify all service dependencies
  help       — Show usage

Usage:
  python3 orchestrator.py dispatch --campaign corridor_uae_india
  python3 orchestrator.py dispatch --campaign b2b_dao_outreach
  python3 orchestrator.py poll
  python3 orchestrator.py report --period daily
  python3 orchestrator.py decide
  python3 orchestrator.py health
  python3 orchestrator.py --dry-run dispatch --campaign corridor_uae_india
"""

import json
import os
import sys
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

# --- State files ---
BASE_DIR = Path(os.environ.get("GROWTH_ENGINE_DIR", "."))
ANALYTICS_DIR = BASE_DIR / "analytics"
STATE_DIR = BASE_DIR / "state"

CAMPAIGNS_FILE = STATE_DIR / "campaigns.jsonl"
RUN_STATS_FILE = ANALYTICS_DIR / "run_stats.jsonl"
DECISIONS_FILE = ANALYTICS_DIR / "decisions.jsonl"

# --- Campaign Definitions ---
CAMPAIGNS = {
    # B2C Corridor campaigns
    "corridor_uae_india": {
        "type": "b2c_corridor",
        "corridor": "UAE → India",
        "channels": ["telegram", "whatsapp", "facebook", "instagram"],
        "audience": "Indian migrant workers in UAE (2.5M+)",
        "gift_cards": ["Amazon India", "Flipkart", "Big Bazaar"],
        "subagents": [
            {"role": "community_infiltrator", "task": "Join and engage in 10+ expat Telegram/WhatsApp groups daily"},
            {"role": "content_creator", "task": "Create corridor-specific testimonial content and infographics"},
            {"role": "outreach_sender", "task": "Send personalized DMs to community admins and influencers"},
            {"role": "ad_manager", "task": "Deploy and optimize Facebook/Instagram ads targeting NRI workers"},
        ],
        "volume_target_monthly_usd": 500_000,
        "estimated_tx_avg_usd": 150,
    },
    "corridor_us_mexico": {
        "type": "b2c_corridor",
        "corridor": "US → Mexico",
        "channels": ["facebook", "whatsapp", "instagram", "tiktok"],
        "audience": "Hispanic diaspora in TX, CA, AZ (12M+ remitters)",
        "gift_cards": ["Walmart Mexico", "Soriana", "Oxxo", "Coppel"],
        "subagents": [
            {"role": "community_infiltrator", "task": "Engage in 15+ FB groups for Mexicanos en USA"},
            {"role": "content_creator", "task": "Create Spanish-language video demos and comparison graphics"},
            {"role": "outreach_sender", "task": "Contact community leaders, churches, cultural orgs"},
            {"role": "influencer_scout", "task": "Identify and pitch micro-influencers (5K-50K followers)"},
        ],
        "volume_target_monthly_usd": 800_000,
        "estimated_tx_avg_usd": 200,
    },
    "corridor_us_philippines": {
        "type": "b2c_corridor",
        "corridor": "US → Philippines",
        "channels": ["facebook", "email", "viber", "tiktok"],
        "audience": "Filipino nurses, caregivers, OFWs in USA (4M+)",
        "gift_cards": ["SM Store", "Robinson's", "Puregold", "Globe Load"],
        "subagents": [
            {"role": "community_infiltrator", "task": "Engage PNA chapters, OFW FB groups, Viber communities"},
            {"role": "content_creator", "task": "Create Tagalog/English comparison content vs Western Union"},
            {"role": "outreach_sender", "task": "Email campaigns to Filipino professional associations"},
            {"role": "partnership_scout", "task": "Connect with Filipino remittance bloggers and podcasters"},
        ],
        "volume_target_monthly_usd": 400_000,
        "estimated_tx_avg_usd": 180,
    },
    "corridor_saudi_pakistan": {
        "type": "b2c_corridor",
        "corridor": "Saudi → Pakistan",
        "channels": ["whatsapp", "facebook", "youtube"],
        "audience": "Pakistani workers in Saudi Arabia (2.5M+)",
        "gift_cards": ["Daraz", "Carrefour Pakistan", "Foodpanda"],
        "subagents": [
            {"role": "community_infiltrator", "task": "Engage Pakistani worker WhatsApp networks in Riyadh/Jeddah"},
            {"role": "content_creator", "task": "Create Urdu-language video demos"},
            {"role": "outreach_sender", "task": "Contact community leaders and labor camp welfare officers"},
        ],
        "volume_target_monthly_usd": 300_000,
        "estimated_tx_avg_usd": 120,
    },
    "corridor_uk_nigeria": {
        "type": "b2c_corridor",
        "corridor": "UK → Nigeria",
        "channels": ["twitter", "whatsapp", "instagram", "telegram"],
        "audience": "Nigerian diaspora in UK (250K+ remitters)",
        "gift_cards": ["Jumia Nigeria", "Shoprite", "MTN Airtime"],
        "subagents": [
            {"role": "community_infiltrator", "task": "Engage Nigerian UK diaspora Twitter/WhatsApp communities"},
            {"role": "content_creator", "task": "Create Naira savings comparison content"},
            {"role": "outreach_sender", "task": "DM Nigerian fintech bloggers and community admins"},
        ],
        "volume_target_monthly_usd": 200_000,
        "estimated_tx_avg_usd": 100,
    },
    # B2B campaigns
    "b2b_dao_outreach": {
        "type": "b2b_partnership",
        "targets": ["Uniswap DAO", "Arbitrum Foundation", "Optimism Collective", "Gitcoin", "Coordinape"],
        "channels": ["governance_forums", "email", "twitter", "discord"],
        "subagents": [
            {"role": "proposal_writer", "task": "Draft governance proposals for bounty payout integration"},
            {"role": "relationship_builder", "task": "Engage delegates and stewards on forums and Discord"},
            {"role": "demo_coordinator", "task": "Prepare and deliver live technical walkthroughs"},
        ],
        "volume_target_monthly_usd": 500_000,
    },
    "b2b_payroll_platforms": {
        "type": "b2b_partnership",
        "targets": ["Deel", "Remote.com", "Rise Works", "Papaya Global", "Oyster HR"],
        "channels": ["email", "linkedin", "conferences"],
        "subagents": [
            {"role": "outreach_sender", "task": "Send personalized integration proposals to partnership teams"},
            {"role": "content_creator", "task": "Create API integration one-pagers and ROI calculators"},
            {"role": "relationship_builder", "task": "Engage on LinkedIn, attend fintech/HR conferences"},
        ],
        "volume_target_monthly_usd": 800_000,
    },
    "b2b_freelance_platforms": {
        "type": "b2b_partnership",
        "targets": ["CryptoTask", "Dework", "Layer3", "Superfluid", "Utopia Labs"],
        "channels": ["discord", "twitter", "email"],
        "subagents": [
            {"role": "outreach_sender", "task": "Pitch gift-card offramp as payout option for contributors"},
            {"role": "demo_coordinator", "task": "Run live demos in partner Discord servers"},
        ],
        "volume_target_monthly_usd": 300_000,
    },
    # Growth & Viral campaigns
    "seo_content_engine": {
        "type": "growth_channel",
        "channels": ["blog", "youtube", "tiktok"],
        "subagents": [
            {"role": "seo_researcher", "task": "Find high-volume, low-competition remittance keywords per corridor"},
            {"role": "content_creator", "task": "Write SEO-optimized comparison articles and how-to guides"},
            {"role": "video_creator", "task": "Create 30-60s demo reels for TikTok/YouTube Shorts"},
        ],
    },
    "referral_viral_loop": {
        "type": "growth_channel",
        "channels": ["in_app", "email", "social"],
        "subagents": [
            {"role": "campaign_designer", "task": "Design referral reward tiers ($5, $10, $25 credits)"},
            {"role": "content_creator", "task": "Create shareable referral graphics and link tracking"},
        ],
    },
}


def ensure_dirs():
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def append_jsonl(filepath, record):
    ensure_dirs()
    with open(filepath, "a") as f:
        f.write(json.dumps(record) + "\n")


def read_jsonl(filepath):
    if not filepath.exists():
        return []
    with open(filepath) as f:
        return [json.loads(line) for line in f if line.strip()]


def generate_id(campaign_name):
    ts = datetime.utcnow().isoformat()
    return hashlib.sha256(f"{campaign_name}:{ts}".encode()).hexdigest()[:12]


# --- Commands ---

def cmd_dispatch(args):
    dry_run = "--dry-run" in args
    campaign_name = None
    for i, a in enumerate(args):
        if a == "--campaign" and i + 1 < len(args):
            campaign_name = args[i + 1]

    if not campaign_name:
        print("Available campaigns:")
        for name, cfg in CAMPAIGNS.items():
            ctype = cfg["type"]
            channels = ", ".join(cfg.get("channels", []))
            print(f"  {name:30s}  type={ctype:20s}  channels=[{channels}]")
        return

    if campaign_name == "all":
        for name in CAMPAIGNS:
            _dispatch_one(name, dry_run)
        return

    if campaign_name not in CAMPAIGNS:
        print(f"Unknown campaign: {campaign_name}")
        print(f"Available: {', '.join(CAMPAIGNS.keys())}")
        sys.exit(1)

    _dispatch_one(campaign_name, dry_run)


def _dispatch_one(campaign_name, dry_run=False):
    cfg = CAMPAIGNS[campaign_name]
    run_id = generate_id(campaign_name)
    record = {
        "run_id": run_id,
        "campaign": campaign_name,
        "type": cfg["type"],
        "status": "dispatched",
        "dispatched_at": datetime.utcnow().isoformat(),
        "subagents": len(cfg.get("subagents", [])),
        "channels": cfg.get("channels", []),
        "dry_run": dry_run,
    }
    prefix = "[DRY RUN] " if dry_run else ""
    print(f"{prefix}Dispatching campaign: {campaign_name} (run_id={run_id})")
    print(f"  Type: {cfg['type']}")
    print(f"  Channels: {', '.join(cfg.get('channels', []))}")
    for sa in cfg.get("subagents", []):
        print(f"  → Subagent [{sa['role']}]: {sa['task']}")

    if not dry_run:
        append_jsonl(CAMPAIGNS_FILE, record)
        append_jsonl(RUN_STATS_FILE, {
            "operation": "campaign_dispatch",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "campaign": campaign_name,
            "run_id": run_id,
            "inputs": {"campaign_config": cfg},
            "outputs": {"subagents_dispatched": len(cfg.get("subagents", []))},
            "errors": [],
            "metrics": {},
            "cost": {"tier": 0, "amount_usd": 0.0, "service": "orchestrator"},
        })
    print(f"{prefix}Done.\n")


def cmd_poll(args):
    records = read_jsonl(CAMPAIGNS_FILE)
    if not records:
        print("No campaigns dispatched yet.")
        return
    print(f"{'RUN_ID':14s} {'CAMPAIGN':32s} {'STATUS':12s} {'DISPATCHED':22s} {'AGENTS':6s}")
    print("-" * 90)
    for r in records[-20:]:
        print(f"{r.get('run_id','?'):14s} {r.get('campaign','?'):32s} {r.get('status','?'):12s} {r.get('dispatched_at','?'):22s} {r.get('subagents',0):6d}")


def cmd_report(args):
    period = "daily"
    for i, a in enumerate(args):
        if a == "--period" and i + 1 < len(args):
            period = args[i + 1]

    stats = read_jsonl(RUN_STATS_FILE)
    campaigns = read_jsonl(CAMPAIGNS_FILE)

    now = datetime.utcnow()
    cutoff_map = {"daily": 1, "weekly": 7, "monthly": 30}
    days = cutoff_map.get(period, 1)
    cutoff = (now - timedelta(days=days)).isoformat()

    recent = [s for s in stats if s.get("timestamp", "") >= cutoff]

    report = {
        "operation": f"{period}_report",
        "timestamp": now.isoformat(),
        "status": "success",
        "period": period,
        "metrics": {
            "total_dispatches": len([r for r in recent if r.get("operation") == "campaign_dispatch"]),
            "total_campaigns_active": len(campaigns),
            "campaigns_by_type": {},
        },
        "cost": {"tier": 0, "amount_usd": 0.0, "service": "orchestrator"},
    }

    for c in campaigns:
        ctype = c.get("type", "unknown")
        report["metrics"]["campaigns_by_type"][ctype] = report["metrics"]["campaigns_by_type"].get(ctype, 0) + 1

    print(json.dumps(report, indent=2))
    append_jsonl(RUN_STATS_FILE, report)


def cmd_decide(args):
    stats = read_jsonl(RUN_STATS_FILE)
    campaigns = read_jsonl(CAMPAIGNS_FILE)

    decisions = []

    # Volume gap analysis
    total_target = 5_000_000  # $5M goal
    # Placeholder: in production, pull actual volume from API
    estimated_monthly = sum(
        CAMPAIGNS[c.get("campaign", "")].get("volume_target_monthly_usd", 0)
        for c in campaigns if c.get("campaign") in CAMPAIGNS
    )

    if estimated_monthly < total_target / 12:
        gap = (total_target / 12) - estimated_monthly
        decisions.append({
            "signal": "EXPAND",
            "reason": f"Monthly volume target gap: ${gap:,.0f}",
            "action": "Activate additional corridors or increase campaign intensity",
        })

    if len(campaigns) < 5:
        decisions.append({
            "signal": "SCALE",
            "reason": "Fewer than 5 active campaigns",
            "action": "Dispatch additional corridor and B2B campaigns",
        })

    decision_record = {
        "operation": "decision_engine",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "success",
        "decisions": decisions,
        "inputs": {"campaigns_active": len(campaigns), "estimated_monthly_volume": estimated_monthly},
        "target": {"total_value_processed": total_target},
    }

    print(json.dumps(decision_record, indent=2))
    append_jsonl(DECISIONS_FILE, decision_record)


def cmd_health(args):
    checks = {
        "state_dir": STATE_DIR.exists(),
        "analytics_dir": ANALYTICS_DIR.exists(),
        "campaigns_file": CAMPAIGNS_FILE.exists(),
        "run_stats_file": RUN_STATS_FILE.exists(),
        "campaign_definitions": len(CAMPAIGNS),
        "total_subagent_roles": sum(len(c.get("subagents", [])) for c in CAMPAIGNS.values()),
    }
    print(json.dumps(checks, indent=2))
    all_ok = all(v for k, v in checks.items() if isinstance(v, bool))
    print(f"\nHealth: {'OK' if all_ok else 'ISSUES DETECTED'}")


def print_usage():
    print(__doc__)


COMMANDS = {
    "dispatch": cmd_dispatch,
    "poll": cmd_poll,
    "report": cmd_report,
    "decide": cmd_decide,
    "health": cmd_health,
    "help": lambda a: print_usage(),
}


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]

    if not args or args[0] == "--help":
        print_usage()
        return

    cmd = args[0]
    if cmd in COMMANDS:
        if dry_run:
            args.append("--dry-run")
        COMMANDS[cmd](args[1:])
    else:
        print(f"Unknown command: {cmd}")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
