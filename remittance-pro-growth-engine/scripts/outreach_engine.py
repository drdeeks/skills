#!/usr/bin/env python3
"""
Remittance Pro Growth Engine — Outreach Engine
Generates, personalizes, and tracks multi-channel outreach messages.

Commands:
  generate    — Create outreach messages for a target audience/lead
  templates   — List available outreach templates
  personalize — Customize a template for a specific lead
  track       — Log outreach result (sent, opened, replied, converted)
  report      — Outreach performance summary
  help        — Show usage

Usage:
  python3 outreach_engine.py templates
  python3 outreach_engine.py generate --template dao_proposal --target "Uniswap DAO"
  python3 outreach_engine.py generate --template expat_community --corridor "US→Mexico" --language es
  python3 outreach_engine.py track --lead "Uniswap DAO" --status replied
  python3 outreach_engine.py report
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(os.environ.get("GROWTH_ENGINE_DIR", "."))
OUTREACH_DIR = BASE_DIR / "outreach"
ANALYTICS_DIR = BASE_DIR / "analytics"

TRACKING_FILE = OUTREACH_DIR / "tracking.jsonl"

# --- Outreach Templates ---
TEMPLATES = {
    "dao_proposal": {
        "channel": "governance_forum",
        "subject": "Proposal: Streamlined Global Contributor Payouts via Email",
        "body": """To the {target} Treasury/Governance Committee,

I am proposing integration of Email Remittance Pro as an offramp for global contributor payouts.

THE PROBLEM: Paying contributors in tokens creates last-mile friction — they must navigate exchanges, pay high fees, and wait days to access fiat value.

THE SOLUTION: Send value to any email address. Recipients choose their payout:
1. Auto-generated crypto wallet (instant, exportable)
2. Gift card (Amazon, Visa, Walmart — usable in 30 seconds, no wallet needed)

WHY THIS MATTERS FOR {target}:
- Reduces contributor payout friction to near-zero
- Expands the eligible contributor pool to include non-crypto-native talent
- 1.5% flat fee (vs 3-8% via exchanges + bank transfers)
- Smart contract escrow — funds are safe until claimed or auto-reclaimed after 30 days
- ZK identity verification (Self Protocol) — compliant without surveillance

PROOF OF CONCEPT: Live on Celo, Base, and Monad mainnet with verified smart contracts.

I would welcome a technical walkthrough at your convenience.

Best regards,
Email Remittance Pro Team""",
        "languages": ["en"],
    },
    "expat_community": {
        "channel": "social_dm",
        "subject": "A faster, cheaper way to send money to {destination}",
        "body": """Hi {leader_name},

I wanted to share a new option for community members who send money to {destination}.

Email Remittance Pro lets you send value using just an email address — 1.5% flat fee (vs 8-12% at Western Union).

Your family receives a link and chooses how to get paid:
- Instant gift card ({gift_cards} — usable immediately)
- Secure digital wallet (if they prefer crypto)

No bank account needed. No crypto knowledge needed. Just an email.

I'd love to share a demo with the group if you think members would find it useful.

Best,
Email Remittance Pro Team""",
        "languages": ["en", "es", "tl", "hi", "ar", "ur"],
    },
    "expat_community_es": {
        "channel": "social_dm",
        "subject": "Una forma mas rapida y barata de enviar dinero a {destination}",
        "body": """Hola {leader_name},

Quiero compartir una nueva opcion para los miembros de la comunidad que envian dinero a {destination}.

Email Remittance Pro permite enviar valor usando solo un correo electronico — 1.5% de comision fija (vs 8-12% en Western Union).

Tu familia recibe un enlace y elige como recibir el pago:
- Tarjeta de regalo instantanea ({gift_cards} — usable de inmediato)
- Billetera digital segura (si prefieren cripto)

No se necesita cuenta bancaria. No se necesita conocimiento de cripto. Solo un correo.

Me encantaria compartir una demostracion con el grupo si crees que seria util.

Saludos,
Equipo Email Remittance Pro""",
        "languages": ["es"],
    },
    "b2b_payroll": {
        "channel": "email",
        "subject": "API Integration: Instant crypto-to-gift-card payouts for your contractors",
        "body": """Hi {contact_name},

I'm reaching out because {target} serves thousands of global contractors who face friction converting crypto payments to local spending value.

Email Remittance Pro offers a white-label API that adds instant gift card offramps:
- 3 lines of code to integrate
- Recipients get Amazon, Visa, Walmart, or 1000+ other retailers
- 1.5% fee (revenue share available)
- We handle compliance, fraud detection (Venice AI), and settlement

Use case: You pay a developer in Nigeria in USDC. They click the email link and get a Jumia gift card in 30 seconds. Zero exchange friction.

Would you be open to a 15-minute API walkthrough?

Best,
Email Remittance Pro Team""",
        "languages": ["en"],
    },
    "influencer_pitch": {
        "channel": "social_dm",
        "subject": "Paid partnership: Help your audience send money cheaper",
        "body": """Hi {influencer_name},

I noticed your content about {topic} resonates with the {corridor} community.

Email Remittance Pro is a new service that lets people send money home at 1.5% (vs 8%+ at traditional services). Recipients choose gift cards or crypto — no wallet needed.

We'd love to partner with you:
- Sponsored content deal (rate negotiable)
- Unique referral link with $5 credit per signup
- We provide demo footage, talking points, and graphics

Your audience saves money. You earn from referrals. Everyone wins.

Interested in discussing terms?

Best,
Email Remittance Pro Team""",
        "languages": ["en", "es", "tl"],
    },
    "freelance_platform": {
        "channel": "email",
        "subject": "Gift card payouts for your global contributor base",
        "body": """Hi {contact_name},

{target} enables global contributors to earn crypto, but many face friction converting to local spending value.

Email Remittance Pro adds a one-click gift card offramp:
- Contributors receive email with claim link
- Choose Amazon, Visa, or 1000+ retailers in their country
- Claimed in 30 seconds, no exchange or KYC needed
- 1.5% fee, smart contract escrow for safety

This expands your addressable contributor pool to non-crypto-native talent and reduces payout support tickets.

Happy to demo or share our API docs.

Best,
Email Remittance Pro Team""",
        "languages": ["en"],
    },
    "seo_article": {
        "channel": "blog",
        "subject": "How to Send Money to {destination} Instantly (2026 Guide)",
        "body": """# How to Send Money to {destination} Instantly — 2026 Guide

Sending money to {destination} traditionally costs 5-12% in fees and takes 2-5 days. Here's a faster, cheaper alternative.

## The Problem with Traditional Remittances
- Western Union charges 8-12% fees
- Bank wires cost $25-50 and take 3-5 days
- Cash pickup locations are inconvenient and unsafe

## Email Remittance Pro: A Better Way
Send money to any email address at 1.5% flat fee. Recipient chooses:
- **Gift card**: {gift_cards} — usable immediately
- **Crypto wallet**: Auto-generated, exportable

No bank account needed. No crypto knowledge needed.

## How It Works
1. Connect your wallet or use service mode
2. Enter recipient email and amount
3. Recipient clicks link, chooses payout method
4. Done — instant delivery

## Fee Comparison
| Service | Fee | Speed | Recipient Needs |
|---------|-----|-------|-----------------|
| Western Union | 8-12% | 2-3 days | ID + pickup |
| Wise | 0.5-2% | 1-3 days | Bank account |
| **Email Remittance Pro** | **1.5%** | **Instant** | **Email only** |

Try it today: [link]""",
        "languages": ["en", "es"],
    },
}


def ensure_dirs():
    OUTREACH_DIR.mkdir(parents=True, exist_ok=True)
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)


def append_jsonl(filepath, record):
    ensure_dirs()
    with open(filepath, "a") as f:
        f.write(json.dumps(record) + "\n")


def read_jsonl(filepath):
    if not filepath.exists():
        return []
    with open(filepath) as f:
        return [json.loads(line) for line in f if line.strip()]


def cmd_templates(args):
    print(f"{'TEMPLATE':25s} {'CHANNEL':18s} {'LANGUAGES':20s}")
    print("-" * 65)
    for name, t in TEMPLATES.items():
        langs = ", ".join(t["languages"])
        print(f"{name:25s} {t['channel']:18s} {langs:20s}")


def cmd_generate(args):
    template_name = None
    target = "TARGET"
    corridor = ""
    language = "en"
    params = {}

    for i, a in enumerate(args):
        if a == "--template" and i + 1 < len(args):
            template_name = args[i + 1]
        elif a == "--target" and i + 1 < len(args):
            target = args[i + 1]
        elif a == "--corridor" and i + 1 < len(args):
            corridor = args[i + 1]
        elif a == "--language" and i + 1 < len(args):
            language = args[i + 1]

    if not template_name or template_name not in TEMPLATES:
        print(f"Unknown template: {template_name}")
        print(f"Available: {', '.join(TEMPLATES.keys())}")
        return

    tmpl = TEMPLATES[template_name]

    # Build substitution dict
    subs = {
        "target": target,
        "destination": corridor.split("→")[-1].strip() if "→" in corridor else "their home country",
        "corridor": corridor,
        "leader_name": "[Community Leader]",
        "contact_name": "[Contact]",
        "influencer_name": "[Influencer]",
        "gift_cards": "Amazon, Walmart, Visa",
        "topic": "remittances and expat life",
    }

    subject = tmpl["subject"]
    body = tmpl["body"]
    for k, v in subs.items():
        subject = subject.replace("{" + k + "}", v)
        body = body.replace("{" + k + "}", v)

    print(f"=== OUTREACH: {template_name} ===")
    print(f"Channel: {tmpl['channel']}")
    print(f"Subject: {subject}")
    print(f"Language: {language}")
    print(f"\n{body}")


def cmd_track(args):
    lead = None
    status = None
    for i, a in enumerate(args):
        if a == "--lead" and i + 1 < len(args):
            lead = args[i + 1]
        elif a == "--status" and i + 1 < len(args):
            status = args[i + 1]

    if not lead or not status:
        print("Provide --lead <name> --status <sent|opened|replied|converted|rejected>")
        return

    record = {
        "lead": lead,
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
    }
    append_jsonl(TRACKING_FILE, record)
    print(f"Tracked: {lead} → {status}")


def cmd_report(args):
    records = read_jsonl(TRACKING_FILE)
    if not records:
        print("No outreach tracking data yet.")
        return

    stats = {}
    for r in records:
        s = r.get("status", "unknown")
        stats[s] = stats.get(s, 0) + 1

    total = len(records)
    print(f"\nOutreach Performance Report ({total} total interactions)\n")
    funnel_order = ["sent", "opened", "replied", "converted", "rejected"]
    for stage in funnel_order:
        count = stats.get(stage, 0)
        pct = (count / total * 100) if total > 0 else 0
        bar = "#" * int(pct / 2)
        print(f"  {stage:12s}: {count:5d} ({pct:5.1f}%) {bar}")

    if stats.get("sent", 0) > 0:
        conv_rate = stats.get("converted", 0) / stats["sent"] * 100
        reply_rate = stats.get("replied", 0) / stats["sent"] * 100
        print(f"\n  Reply rate: {reply_rate:.1f}%")
        print(f"  Conversion rate: {conv_rate:.1f}%")


def print_usage():
    print(__doc__)


COMMANDS = {
    "templates": cmd_templates,
    "generate": cmd_generate,
    "personalize": cmd_generate,  # alias
    "track": cmd_track,
    "report": cmd_report,
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
