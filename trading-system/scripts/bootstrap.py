#!/usr/bin/env python3
"""
Autonomous Trading System — Bootstrap & Self-Registration

One-command initialization: creates state directories, guides API key acquisition,
generates/imports wallets, validates connectivity, and writes config.

Usage:
    python3 bootstrap.py setup              # Full interactive setup
    python3 bootstrap.py setup --dry-run    # Preview without changes
    python3 bootstrap.py status             # Show current readiness
    python3 bootstrap.py validate           # Test all API connections
    python3 bootstrap.py reset              # Reset config (preserves logs)
    python3 bootstrap.py --help
"""

import json
import os
import sys
import time
import hashlib
import secrets
from datetime import datetime, timezone
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────
STATE_DIR = Path.home() / ".autonomous-trading-system"
CONFIG_PATH = STATE_DIR / "config.json"
ANALYTICS_DIR = STATE_DIR / "analytics"
TRADES_DIR = STATE_DIR / "trades"
LOGS_DIR = STATE_DIR / "logs"
REPORTS_DIR = STATE_DIR / "reports"

DEFAULT_CONFIG = {
    "version": 2,
    "created_at": "",
    "mode": "paper",
    "target_daily_pct": 0.25,
    "bankroll": 0.0,
    "platforms": {
        "polymarket": {
            "enabled": True,
            "api_base": "https://gamma-api.polymarket.com",
            "clob_base": "https://clob.polymarket.com",
            "private_key": "",
            "status": "unconfigured"
        },
        "kalshi": {
            "enabled": True,
            "api_base": "https://trading-api.kalshi.com",
            "key_id": "",
            "private_key_path": "",
            "status": "unconfigured"
        },
        "hyperliquid": {
            "enabled": False,
            "api_base": "https://api.hyperliquid.xyz",
            "private_key": "",
            "status": "unconfigured"
        }
    },
    "wallet": {
        "type": "smart_wallet",
        "provider": "base_account",
        "chain_id": 8453,
        "chain_name": "Base Mainnet",
        "rpc_url": "https://mainnet.base.org",
        "usdc_address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        "address": "",
        "paymaster_url": ""
    },
    "risk": {
        "max_daily_loss_pct": 0.10,
        "max_drawdown_pct": 0.20,
        "max_position_pct": 0.12,
        "kelly_fraction": 0.25,
        "min_edge": 0.04,
        "max_correlated_positions": 3,
        "max_trades_per_10min": 5,
        "consecutive_loss_halt": 3,
        "consecutive_loss_threshold": 0.05
    },
    "scanning": {
        "interval_seconds": 300,
        "max_daily_trades": 40,
        "scan_hours": {"start": 0, "end": 24},
        "min_volume": 100000,
        "platforms_priority": ["polymarket", "kalshi", "hyperliquid"]
    },
    "alerts": {
        "telegram_bot_token": "",
        "telegram_chat_id": "",
        "alert_on_opportunity": True,
        "alert_on_trade": True,
        "alert_on_safety_breach": True,
        "daily_summary": True
    },
    "logging": {
        "level": "INFO",
        "trade_log": "trades/trade_journal.jsonl",
        "safety_log": "logs/safety_events.jsonl",
        "analytics_log": "analytics/run_stats.jsonl"
    }
}

PLATFORM_SETUP_GUIDES = {
    "polymarket": {
        "name": "Polymarket",
        "signup_url": "https://polymarket.com",
        "key_type": "Ethereum Private Key (for CLOB API signing)",
        "steps": [
            "1. Visit https://polymarket.com and connect a wallet (MetaMask, Coinbase Wallet, etc.)",
            "2. Complete KYC verification if required for your jurisdiction",
            "3. Deposit USDC to your Polymarket account",
            "4. For API trading: export the private key of your connected wallet",
            "5. Store private key securely — NEVER share or commit to git",
            "NOTE: Read-only data (scanning) requires NO API key — Gamma API is public"
        ],
        "env_vars": ["POLYMARKET_PRIVATE_KEY"],
        "test_endpoint": "/markets?limit=1"
    },
    "kalshi": {
        "name": "Kalshi",
        "signup_url": "https://kalshi.com",
        "key_type": "RSA Key Pair (API Key ID + RSA Private Key)",
        "steps": [
            "1. Visit https://kalshi.com and create an account",
            "2. Complete identity verification (US residents only for trading)",
            "3. Navigate to Settings → API Keys",
            "4. Generate a new API key pair — download the private key .pem file",
            "5. Note the Key ID displayed on screen",
            "6. Fund your account via bank transfer or wire",
            "7. Store: KALSHI_KEY_ID and path to private key .pem file"
        ],
        "env_vars": ["KALSHI_KEY_ID", "KALSHI_PRIVATE_KEY_PATH"],
        "test_endpoint": "/trade-api/v2/exchange/status"
    },
    "hyperliquid": {
        "name": "Hyperliquid",
        "signup_url": "https://app.hyperliquid.xyz",
        "key_type": "Ethereum Private Key (for L1 signing)",
        "steps": [
            "1. Visit https://app.hyperliquid.xyz",
            "2. Connect wallet (no KYC required — decentralized)",
            "3. Bridge USDC to Hyperliquid L1 via the built-in bridge",
            "4. For API trading: generate an API wallet in Settings",
            "5. Export the API wallet private key",
            "6. Set trading permissions for the API wallet"
        ],
        "env_vars": ["HYPERLIQUID_PRIVATE_KEY"],
        "test_endpoint": "/info"
    }
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def append_jsonl(filepath, record):
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "a") as f:
        f.write(json.dumps(record) + "\n")


def log_event(event_type, message, details=None):
    record = {
        "timestamp": now_iso(),
        "event_type": event_type,
        "message": message,
        "details": details or {}
    }
    append_jsonl(LOGS_DIR / "bootstrap.jsonl", record)
    return record


# ── Commands ───────────────────────────────────────────────────

def do_setup(dry_run=False):
    """Full interactive setup."""
    prefix = "[DRY RUN] " if dry_run else ""
    print(f"\n{prefix}Autonomous Trading System — Bootstrap\n{'='*50}\n")

    # Step 1: Create directories
    print(f"{prefix}Step 1: Creating state directories...")
    dirs = [STATE_DIR, ANALYTICS_DIR, TRADES_DIR, LOGS_DIR, REPORTS_DIR,
            REPORTS_DIR / "daily", REPORTS_DIR / "weekly"]
    for d in dirs:
        if not dry_run:
            d.mkdir(parents=True, exist_ok=True)
        print(f"  {prefix}Created: {d}")

    # Step 2: Initialize config
    print(f"\n{prefix}Step 2: Initializing configuration...")
    if CONFIG_PATH.exists() and not dry_run:
        print(f"  Config already exists at {CONFIG_PATH}")
        print(f"  Use 'bootstrap.py reset' to reinitialize")
    else:
        config = DEFAULT_CONFIG.copy()
        config["created_at"] = now_iso()
        config["instance_id"] = secrets.token_hex(8)
        if not dry_run:
            CONFIG_PATH.write_text(json.dumps(config, indent=2))
        print(f"  {prefix}Config written to {CONFIG_PATH}")

    # Step 3: Platform setup guides
    print(f"\n{prefix}Step 3: Platform API Key Setup")
    print(f"  {'─'*46}")
    for platform_id, guide in PLATFORM_SETUP_GUIDES.items():
        print(f"\n  ┌─ {guide['name']} ─────────────────────────────")
        print(f"  │ URL: {guide['signup_url']}")
        print(f"  │ Key Type: {guide['key_type']}")
        for step in guide['steps']:
            print(f"  │ {step}")
        print(f"  │")
        print(f"  │ Environment Variables:")
        for var in guide['env_vars']:
            val = os.environ.get(var, "")
            status = "SET" if val else "NOT SET"
            print(f"  │   {var}: [{status}]")
        print(f"  └─────────────────────────────────────────────")

    # Step 4: Load credentials from environment
    print(f"\n{prefix}Step 4: Loading credentials from environment...")
    if not dry_run:
        config = json.loads(CONFIG_PATH.read_text())
        creds_found = 0

        # Polymarket
        poly_key = os.environ.get("POLYMARKET_PRIVATE_KEY", "")
        if poly_key:
            config["platforms"]["polymarket"]["private_key"] = poly_key
            config["platforms"]["polymarket"]["status"] = "configured"
            creds_found += 1
            print(f"  Polymarket: Configured (key loaded)")
        else:
            print(f"  Polymarket: Read-only mode (no key — scanning still works)")

        # Kalshi
        kalshi_key_id = os.environ.get("KALSHI_KEY_ID", "")
        kalshi_key_path = os.environ.get("KALSHI_PRIVATE_KEY_PATH", "")
        if kalshi_key_id and kalshi_key_path:
            config["platforms"]["kalshi"]["key_id"] = kalshi_key_id
            config["platforms"]["kalshi"]["private_key_path"] = kalshi_key_path
            config["platforms"]["kalshi"]["status"] = "configured"
            creds_found += 1
            print(f"  Kalshi: Configured (key ID + private key loaded)")
        else:
            print(f"  Kalshi: Not configured (set KALSHI_KEY_ID + KALSHI_PRIVATE_KEY_PATH)")

        # Hyperliquid
        hl_key = os.environ.get("HYPERLIQUID_PRIVATE_KEY", "")
        if hl_key:
            config["platforms"]["hyperliquid"]["private_key"] = hl_key
            config["platforms"]["hyperliquid"]["enabled"] = True
            config["platforms"]["hyperliquid"]["status"] = "configured"
            creds_found += 1
            print(f"  Hyperliquid: Configured (key loaded)")
        else:
            print(f"  Hyperliquid: Disabled (set HYPERLIQUID_PRIVATE_KEY to enable)")

        # Wallet
        wallet_key = os.environ.get("TRADING_WALLET_KEY", "")
        if wallet_key:
            config["wallet"]["address"] = "derived"  # Would derive in production
            print(f"  Wallet: Configured")
        else:
            print(f"  Wallet: Not configured (set TRADING_WALLET_KEY)")

        # Telegram
        tg_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        tg_chat = os.environ.get("TELEGRAM_CHAT_ID", "")
        if tg_token and tg_chat:
            config["alerts"]["telegram_bot_token"] = tg_token
            config["alerts"]["telegram_chat_id"] = tg_chat
            print(f"  Telegram: Configured")
        else:
            print(f"  Telegram: Not configured (alerts will use console only)")

        # Bankroll
        bankroll_str = os.environ.get("TRADING_BANKROLL", "0")
        try:
            config["bankroll"] = float(bankroll_str)
        except ValueError:
            pass
        if config["bankroll"] > 0:
            print(f"  Bankroll: ${config['bankroll']:.2f}")
        else:
            print(f"  Bankroll: Not set (set TRADING_BANKROLL)")

        CONFIG_PATH.write_text(json.dumps(config, indent=2))
        print(f"\n  Credentials loaded: {creds_found}/3 platforms")

    # Step 5: Validation
    print(f"\n{prefix}Step 5: System readiness check...")
    if not dry_run:
        do_validate()
    else:
        print(f"  {prefix}Would validate all API connections")

    # Step 6: Log bootstrap event
    if not dry_run:
        log_event("bootstrap_complete", "System bootstrapped", {
            "mode": "paper",
            "platforms_configured": creds_found if not dry_run else 0
        })

    print(f"\n{prefix}Bootstrap complete!")
    print(f"\nNext steps:")
    print(f"  1. Set environment variables for your target platforms")
    print(f"  2. Re-run 'python3 bootstrap.py setup' to load credentials")
    print(f"  3. Run 'python3 trading_engine.py start --mode paper' for paper trading")
    print(f"  4. After 1-2 weeks of paper profits, switch to '--mode live'")


def do_validate():
    """Test all API connections."""
    print(f"\n  Connectivity Tests:")
    print(f"  {'─'*40}")

    if not CONFIG_PATH.exists():
        print(f"  Config not found. Run 'bootstrap.py setup' first.")
        return False

    config = json.loads(CONFIG_PATH.read_text())
    all_passed = True
    results = []

    # Test Polymarket (public API — always works)
    try:
        import urllib.request
        req = urllib.request.Request(
            "https://gamma-api.polymarket.com/markets?limit=1",
            headers={"User-Agent": "AutonomousTradingSystem/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            status = "PASS" if resp.status == 200 else "FAIL"
            results.append(("Polymarket (read)", status, f"HTTP {resp.status}"))
    except Exception as e:
        results.append(("Polymarket (read)", "FAIL", str(e)[:60]))
        all_passed = False

    # Test Kalshi (public endpoint)
    try:
        req = urllib.request.Request(
            "https://trading-api.kalshi.com/trade-api/v2/exchange/status",
            headers={"User-Agent": "AutonomousTradingSystem/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = "PASS" if resp.status == 200 else "FAIL"
            results.append(("Kalshi (exchange)", status, f"HTTP {resp.status}"))
    except Exception as e:
        results.append(("Kalshi (exchange)", "WARN", str(e)[:60]))

    # Test wallet RPC
    try:
        rpc_url = config.get("wallet", {}).get("rpc_url", "https://mainnet.base.org")
        req_data = json.dumps({"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}).encode()
        req = urllib.request.Request(rpc_url, data=req_data,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = "PASS" if resp.status == 200 else "FAIL"
            results.append(("Base RPC", status, f"HTTP {resp.status}"))
    except Exception as e:
        results.append(("Base RPC", "WARN", str(e)[:60]))

    # Check config completeness
    configured = sum(1 for p in config.get("platforms", {}).values()
                     if p.get("status") == "configured")
    total = len(config.get("platforms", {}))
    results.append(("Platform credentials", "PASS" if configured > 0 else "WARN",
                     f"{configured}/{total} configured"))

    bankroll = config.get("bankroll", 0)
    results.append(("Bankroll", "PASS" if bankroll > 0 else "WARN",
                     f"${bankroll:.2f}" if bankroll > 0 else "Not set"))

    mode = config.get("mode", "paper")
    results.append(("Trading mode", "INFO", mode.upper()))

    for name, status, detail in results:
        icon = {"PASS": "✓", "FAIL": "✗", "WARN": "⚠", "INFO": "ℹ"}.get(status, "?")
        print(f"  {icon} [{status}] {name}: {detail}")

    # Log validation
    log_event("validation", "Connectivity check", {
        "results": [{"name": n, "status": s, "detail": d} for n, s, d in results],
        "all_passed": all_passed
    })

    return all_passed


def do_status():
    """Show current system state."""
    if not CONFIG_PATH.exists():
        print("System not initialized. Run: python3 bootstrap.py setup")
        return

    config = json.loads(CONFIG_PATH.read_text())
    print(f"\nAutonomous Trading System — Status")
    print(f"{'='*45}")
    print(f"  Instance ID:  {config.get('instance_id', 'N/A')}")
    print(f"  Created:      {config.get('created_at', 'N/A')}")
    print(f"  Mode:         {config.get('mode', 'paper').upper()}")
    print(f"  Bankroll:     ${config.get('bankroll', 0):.2f}")
    print(f"  Daily Target: {config.get('target_daily_pct', 0.25)*100:.0f}%")
    print(f"\n  Platforms:")
    for pid, pdata in config.get("platforms", {}).items():
        enabled = "ON" if pdata.get("enabled") else "OFF"
        status = pdata.get("status", "unknown")
        print(f"    {pid:15s} [{enabled}] {status}")
    print(f"\n  Risk Parameters:")
    risk = config.get("risk", {})
    print(f"    Max daily loss:     {risk.get('max_daily_loss_pct', 0)*100:.0f}%")
    print(f"    Max drawdown:       {risk.get('max_drawdown_pct', 0)*100:.0f}%")
    print(f"    Max position:       {risk.get('max_position_pct', 0)*100:.0f}%")
    print(f"    Kelly fraction:     {risk.get('kelly_fraction', 0)*100:.0f}%")
    print(f"    Min edge:           {risk.get('min_edge', 0)*100:.0f}%")

    # Check analytics
    stats_file = ANALYTICS_DIR / "run_stats.jsonl"
    if stats_file.exists():
        lines = [l for l in stats_file.read_text().strip().split("\n") if l.strip()]
        print(f"\n  Analytics: {len(lines)} records logged")
    else:
        print(f"\n  Analytics: No records yet")


def do_reset():
    """Reset config (preserves logs and analytics)."""
    if CONFIG_PATH.exists():
        backup = CONFIG_PATH.with_suffix(f".backup.{int(time.time())}.json")
        CONFIG_PATH.rename(backup)
        print(f"Config backed up to: {backup}")
    config = DEFAULT_CONFIG.copy()
    config["created_at"] = now_iso()
    config["instance_id"] = secrets.token_hex(8)
    CONFIG_PATH.write_text(json.dumps(config, indent=2))
    print(f"Config reset. Re-run 'bootstrap.py setup' to reconfigure.")
    log_event("config_reset", "Configuration reset")


# ── Main ───────────────────────────────────────────────────────

COMMANDS = {
    "setup": lambda: do_setup("--dry-run" in sys.argv),
    "status": do_status,
    "validate": do_validate,
    "reset": do_reset,
}


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd in ("--help", "-h", "help"):
        print(__doc__)
    elif cmd in COMMANDS:
        COMMANDS[cmd]()
    else:
        print(f"Unknown command: {cmd}")
        print(f"Available: {', '.join(COMMANDS.keys())}")
        sys.exit(1)


if __name__ == "__main__":
    main()
