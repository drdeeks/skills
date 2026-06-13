#!/usr/bin/env python3
"""
Remittance Pro Growth Engine — Market Scanner
Discovers new corridors, audiences, and partnership opportunities.

Commands:
  corridors       — Analyze and rank global remittance corridors
  audiences       — Discover audience segments for a corridor
  partnerships    — Scan for B2B partnership targets
  competitors     — Analyze competitor presence in a corridor
  opportunities   — Generate ranked opportunity list
  help            — Show usage

Usage:
  python3 market_scanner.py corridors
  python3 market_scanner.py corridors --min-volume 5000000000
  python3 market_scanner.py audiences --corridor "US→Mexico"
  python3 market_scanner.py partnerships --type dao
  python3 market_scanner.py competitors --corridor "UAE→India"
  python3 market_scanner.py opportunities --top 10
"""

import json
import sys
from datetime import datetime

# --- Global Corridor Database ---
# Source: World Bank bilateral remittance data, 2024 estimates
CORRIDORS = [
    {"from": "US", "to": "Mexico", "annual_volume_usd": 63_000_000_000, "avg_fee_pct": 5.2, "digital_pct": 55, "smartphone_pct": 82, "gift_card_relevance": 95, "competition": "high"},
    {"from": "UAE", "to": "India", "annual_volume_usd": 20_000_000_000, "avg_fee_pct": 3.8, "digital_pct": 62, "smartphone_pct": 75, "gift_card_relevance": 90, "competition": "medium"},
    {"from": "US", "to": "Philippines", "annual_volume_usd": 18_000_000_000, "avg_fee_pct": 4.5, "digital_pct": 48, "smartphone_pct": 70, "gift_card_relevance": 85, "competition": "medium"},
    {"from": "Saudi", "to": "Pakistan", "annual_volume_usd": 8_000_000_000, "avg_fee_pct": 4.0, "digital_pct": 35, "smartphone_pct": 55, "gift_card_relevance": 70, "competition": "low"},
    {"from": "UK", "to": "Nigeria", "annual_volume_usd": 6_500_000_000, "avg_fee_pct": 7.1, "digital_pct": 42, "smartphone_pct": 65, "gift_card_relevance": 75, "competition": "medium"},
    {"from": "Canada", "to": "India", "annual_volume_usd": 5_000_000_000, "avg_fee_pct": 4.2, "digital_pct": 58, "smartphone_pct": 75, "gift_card_relevance": 88, "competition": "medium"},
    {"from": "US", "to": "Guatemala", "annual_volume_usd": 4_800_000_000, "avg_fee_pct": 5.8, "digital_pct": 30, "smartphone_pct": 55, "gift_card_relevance": 60, "competition": "low"},
    {"from": "US", "to": "Colombia", "annual_volume_usd": 4_200_000_000, "avg_fee_pct": 5.5, "digital_pct": 40, "smartphone_pct": 70, "gift_card_relevance": 72, "competition": "low"},
    {"from": "Italy", "to": "Romania", "annual_volume_usd": 3_800_000_000, "avg_fee_pct": 6.0, "digital_pct": 50, "smartphone_pct": 80, "gift_card_relevance": 65, "competition": "low"},
    {"from": "Korea", "to": "Philippines", "annual_volume_usd": 3_200_000_000, "avg_fee_pct": 4.8, "digital_pct": 55, "smartphone_pct": 70, "gift_card_relevance": 82, "competition": "low"},
    {"from": "Japan", "to": "Philippines", "annual_volume_usd": 2_800_000_000, "avg_fee_pct": 5.0, "digital_pct": 60, "smartphone_pct": 70, "gift_card_relevance": 80, "competition": "low"},
    {"from": "US", "to": "India", "annual_volume_usd": 12_000_000_000, "avg_fee_pct": 3.5, "digital_pct": 65, "smartphone_pct": 75, "gift_card_relevance": 90, "competition": "high"},
    {"from": "UK", "to": "India", "annual_volume_usd": 4_500_000_000, "avg_fee_pct": 4.0, "digital_pct": 60, "smartphone_pct": 75, "gift_card_relevance": 88, "competition": "medium"},
    {"from": "US", "to": "Dominican Republic", "annual_volume_usd": 3_500_000_000, "avg_fee_pct": 5.3, "digital_pct": 38, "smartphone_pct": 65, "gift_card_relevance": 68, "competition": "low"},
    {"from": "US", "to": "El Salvador", "annual_volume_usd": 3_200_000_000, "avg_fee_pct": 4.5, "digital_pct": 35, "smartphone_pct": 60, "gift_card_relevance": 62, "competition": "low"},
]

# Audience segment templates per corridor type
AUDIENCE_SEGMENTS = {
    "migrant_workers": {"description": "Blue-collar workers sending regular remittances", "channels": ["whatsapp", "telegram", "facebook"], "avg_tx": 150, "frequency": "monthly"},
    "professionals": {"description": "White-collar professionals supporting family", "channels": ["email", "linkedin", "instagram"], "avg_tx": 300, "frequency": "monthly"},
    "students": {"description": "International students receiving family support", "channels": ["instagram", "tiktok", "whatsapp"], "avg_tx": 500, "frequency": "quarterly"},
    "small_business": {"description": "Cross-border micro-merchants and traders", "channels": ["whatsapp", "email", "facebook"], "avg_tx": 800, "frequency": "weekly"},
    "freelancers": {"description": "Remote workers receiving crypto/fiat payments", "channels": ["twitter", "discord", "telegram"], "avg_tx": 400, "frequency": "biweekly"},
    "elderly_recipients": {"description": "Recipients who need simplest possible UX (gift card)", "channels": ["family_referral", "community_leader"], "avg_tx": 100, "frequency": "monthly"},
}

B2B_TARGETS = {
    "dao": [
        {"name": "Uniswap DAO", "treasury_usd": 2_000_000_000, "contributors": 500, "contact": "governance.uniswap.org"},
        {"name": "Arbitrum Foundation", "treasury_usd": 3_500_000_000, "contributors": 800, "contact": "arbitrum.foundation/grants"},
        {"name": "Optimism Collective", "treasury_usd": 1_800_000_000, "contributors": 600, "contact": "optimism.io/governance"},
        {"name": "Gitcoin", "treasury_usd": 200_000_000, "contributors": 2000, "contact": "gitcoin.co/partnerships"},
        {"name": "Coordinape", "treasury_usd": 50_000_000, "contributors": 300, "contact": "coordinape.com"},
        {"name": "Aave DAO", "treasury_usd": 500_000_000, "contributors": 200, "contact": "governance.aave.com"},
        {"name": "Compound DAO", "treasury_usd": 300_000_000, "contributors": 150, "contact": "compound.finance/governance"},
    ],
    "payroll": [
        {"name": "Deel", "employees_served": 500_000, "contact": "deel.com/partners"},
        {"name": "Remote.com", "employees_served": 200_000, "contact": "remote.com/partners"},
        {"name": "Rise Works", "employees_served": 50_000, "contact": "riseworks.io"},
        {"name": "Papaya Global", "employees_served": 150_000, "contact": "papayaglobal.com"},
        {"name": "Oyster HR", "employees_served": 80_000, "contact": "oysterhr.com"},
    ],
    "freelance": [
        {"name": "Dework", "users": 50_000, "contact": "dework.xyz"},
        {"name": "Layer3", "users": 100_000, "contact": "layer3.xyz"},
        {"name": "Superfluid", "users": 30_000, "contact": "superfluid.finance"},
        {"name": "CryptoTask", "users": 20_000, "contact": "cryptotask.org"},
    ],
    "exchange": [
        {"name": "Coinbase", "users": 110_000_000, "contact": "coinbase.com/partners"},
        {"name": "Binance", "users": 150_000_000, "contact": "binance.com/partners"},
        {"name": "OKX", "users": 50_000_000, "contact": "okx.com/partners"},
    ],
}


def score_corridor(c):
    """Score a corridor for Email Remittance Pro suitability (0-100)."""
    score = 0
    # Volume (30 pts max)
    vol = c["annual_volume_usd"]
    if vol >= 20e9: score += 30
    elif vol >= 10e9: score += 25
    elif vol >= 5e9: score += 20
    elif vol >= 2e9: score += 15
    else: score += 10

    # Fee differential — higher incumbent fees = bigger opportunity (20 pts max)
    fee_diff = c["avg_fee_pct"] - 1.5  # our fee
    score += min(int(fee_diff * 5), 20)

    # Digital readiness (15 pts max)
    score += int(c["digital_pct"] * 0.15)

    # Gift card relevance (20 pts max)
    score += int(c["gift_card_relevance"] * 0.2)

    # Competition inverse (15 pts max)
    comp_map = {"low": 15, "medium": 10, "high": 5}
    score += comp_map.get(c["competition"], 5)

    return min(score, 100)


def cmd_corridors(args):
    min_vol = 0
    for i, a in enumerate(args):
        if a == "--min-volume" and i + 1 < len(args):
            min_vol = int(args[i + 1])

    filtered = [c for c in CORRIDORS if c["annual_volume_usd"] >= min_vol]
    scored = [(score_corridor(c), c) for c in filtered]
    scored.sort(key=lambda x: -x[0])

    print(f"{'RANK':4s} {'CORRIDOR':25s} {'VOLUME':>15s} {'FEE%':>6s} {'SCORE':>6s} {'COMPETITION':>12s}")
    print("-" * 75)
    for rank, (score, c) in enumerate(scored, 1):
        corridor = f"{c['from']}→{c['to']}"
        vol = f"${c['annual_volume_usd']/1e9:.1f}B"
        print(f"{rank:4d} {corridor:25s} {vol:>15s} {c['avg_fee_pct']:>5.1f}% {score:>6d} {c['competition']:>12s}")


def cmd_audiences(args):
    corridor = None
    for i, a in enumerate(args):
        if a == "--corridor" and i + 1 < len(args):
            corridor = args[i + 1]

    if not corridor:
        print("Provide --corridor 'FROM→TO'")
        return

    print(f"\nAudience segments for corridor: {corridor}\n")
    print(f"{'SEGMENT':20s} {'AVG TX':>8s} {'FREQ':>12s} {'CHANNELS':40s}")
    print("-" * 85)
    for name, seg in AUDIENCE_SEGMENTS.items():
        channels = ", ".join(seg["channels"])
        print(f"{name:20s} ${seg['avg_tx']:>6d} {seg['frequency']:>12s} {channels:40s}")


def cmd_partnerships(args):
    ptype = "dao"
    for i, a in enumerate(args):
        if a == "--type" and i + 1 < len(args):
            ptype = args[i + 1]

    targets = B2B_TARGETS.get(ptype, [])
    if not targets:
        print(f"Unknown type: {ptype}. Available: {', '.join(B2B_TARGETS.keys())}")
        return

    print(f"\nB2B Partnership Targets — {ptype.upper()}\n")
    for t in targets:
        print(f"  {t['name']}")
        for k, v in t.items():
            if k != "name":
                print(f"    {k}: {v}")
        print()


def cmd_competitors(args):
    corridor = None
    for i, a in enumerate(args):
        if a == "--corridor" and i + 1 < len(args):
            corridor = args[i + 1]

    competitors = {
        "Western Union": {"fee": "8-12%", "speed": "2-3 days", "requires": "ID + pickup location", "weakness": "High fees, slow, inconvenient"},
        "MoneyGram": {"fee": "5-10%", "speed": "1-3 days", "requires": "ID + pickup", "weakness": "High fees, limited digital"},
        "Wise": {"fee": "0.5-2%", "speed": "1-3 days", "requires": "Bank account", "weakness": "Requires recipient bank account"},
        "Remitly": {"fee": "3-5%", "speed": "1-3 days", "requires": "Bank or pickup", "weakness": "Medium fees, no crypto option"},
        "WorldRemit": {"fee": "3-6%", "speed": "1-2 days", "requires": "Bank or mobile money", "weakness": "No gift card option"},
        "Strike": {"fee": "0.5%", "speed": "Instant", "requires": "Lightning wallet", "weakness": "Requires crypto knowledge"},
    }

    print(f"\nCompetitor Analysis{f' — {corridor}' if corridor else ''}\n")
    print(f"{'COMPETITOR':18s} {'FEE':>10s} {'SPEED':>12s} {'REQUIRES':>20s}")
    print("-" * 65)
    for name, info in competitors.items():
        print(f"{name:18s} {info['fee']:>10s} {info['speed']:>12s} {info['requires']:>20s}")

    print(f"\n{'Email Remittance Pro':18s} {'1.5%':>10s} {'Instant':>12s} {'Email only':>20s}")
    print(f"\nKey differentiator: Gift card + crypto optionality with email-only identity layer")


def cmd_opportunities(args):
    top = 10
    for i, a in enumerate(args):
        if a == "--top" and i + 1 < len(args):
            top = int(args[i + 1])

    scored = [(score_corridor(c), c) for c in CORRIDORS]
    scored.sort(key=lambda x: -x[0])

    opportunities = []
    for rank, (score, c) in enumerate(scored[:top], 1):
        corridor = f"{c['from']}→{c['to']}"
        fee_savings = c["avg_fee_pct"] - 1.5
        capturable = c["annual_volume_usd"] * 0.001  # 0.1% market share
        revenue = capturable * 0.015  # 1.5% fee
        opportunities.append({
            "rank": rank,
            "corridor": corridor,
            "score": score,
            "annual_volume": c["annual_volume_usd"],
            "fee_savings_pct": round(fee_savings, 1),
            "capturable_volume_01pct": capturable,
            "potential_annual_revenue": revenue,
        })

    print(json.dumps(opportunities, indent=2))


def print_usage():
    print(__doc__)


COMMANDS = {
    "corridors": cmd_corridors,
    "audiences": cmd_audiences,
    "partnerships": cmd_partnerships,
    "competitors": cmd_competitors,
    "opportunities": cmd_opportunities,
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
