#!/usr/bin/env python3
"""
Autonomous Trading System — Analytics & Reporting

Performance tracking, P&L reporting, trade journal analysis, and
daily/weekly summary generation.

Usage:
    python3 analytics.py daily              # Generate daily report
    python3 analytics.py weekly             # Generate weekly report
    python3 analytics.py pnl               # Current P&L summary
    python3 analytics.py journal           # Trade journal export
    python3 analytics.py health            # System health check
    python3 analytics.py status            # Analytics state
    python3 analytics.py --help
"""

import json
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict

# ── Configuration ──────────────────────────────────────────────
STATE_DIR = Path.home() / ".autonomous-trading-system"
CONFIG_PATH = STATE_DIR / "config.json"
ANALYTICS_DIR = STATE_DIR / "analytics"
TRADES_DIR = STATE_DIR / "trades"
REPORTS_DIR = STATE_DIR / "reports"
LOGS_DIR = STATE_DIR / "logs"


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def now_ts():
    return datetime.now(timezone.utc)


def append_jsonl(filepath, record):
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "a") as f:
        f.write(json.dumps(record) + "\n")


def read_jsonl(filepath):
    if not Path(filepath).exists():
        return []
    records = []
    for line in Path(filepath).read_text().strip().split("\n"):
        if line.strip():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def load_config():
    if not CONFIG_PATH.exists():
        return {"bankroll": 0, "target_daily_pct": 0.25}
    return json.loads(CONFIG_PATH.read_text())


# ── Report Generation ─────────────────────────────────────────

def generate_pnl_summary():
    """Generate current P&L summary."""
    trades = read_jsonl(TRADES_DIR / "trade_journal.jsonl")
    cycles = read_jsonl(ANALYTICS_DIR / "run_stats.jsonl")
    config = load_config()

    if not trades and not cycles:
        return {
            "operation": "pnl_summary",
            "timestamp": now_iso(),
            "status": "no_data",
            "message": "No trades recorded yet. Run the trading engine first."
        }

    # Calculate from trade journal
    total_pnl = 0.0
    total_trades = len(trades)
    winning_trades = 0
    losing_trades = 0
    total_volume = 0.0

    by_platform = defaultdict(lambda: {"trades": 0, "pnl": 0.0, "volume": 0.0})
    by_type = defaultdict(lambda: {"trades": 0, "pnl": 0.0})
    by_day = defaultdict(lambda: {"trades": 0, "pnl": 0.0})

    for trade in trades:
        size = trade.get("position_size", 0)
        edge = trade.get("edge", 0)
        pnl = size * edge * 0.7 if trade.get("mode") == "paper" else trade.get("realized_pnl", 0)
        total_pnl += pnl
        total_volume += size

        if pnl > 0:
            winning_trades += 1
        elif pnl < 0:
            losing_trades += 1

        platform = trade.get("platform", "unknown")
        by_platform[platform]["trades"] += 1
        by_platform[platform]["pnl"] += pnl
        by_platform[platform]["volume"] += size

        arb_type = trade.get("arb_type", "other")
        by_type[arb_type or "other"]["trades"] += 1
        by_type[arb_type or "other"]["pnl"] += pnl

        day = trade.get("timestamp", "")[:10]
        by_day[day]["trades"] += 1
        by_day[day]["pnl"] += pnl

    # Cycle stats
    total_cycles = len(cycles)
    total_scanned = sum(c.get("inputs", {}).get("markets_scanned", 0) for c in cycles)
    total_blocked = sum(c.get("outputs", {}).get("trades_blocked", 0) for c in cycles)
    avg_duration = (sum(c.get("duration_seconds", 0) for c in cycles) / total_cycles
                    if total_cycles > 0 else 0)

    bankroll = config.get("bankroll", 0)
    total_return_pct = (total_pnl / bankroll * 100) if bankroll > 0 else 0
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

    summary = {
        "operation": "pnl_summary",
        "timestamp": now_iso(),
        "status": "success",
        "duration_seconds": 0.0,
        "overview": {
            "total_pnl": round(total_pnl, 2),
            "total_return_pct": round(total_return_pct, 2),
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate_pct": round(win_rate, 2),
            "total_volume": round(total_volume, 2),
            "starting_bankroll": bankroll,
            "current_bankroll": round(bankroll + total_pnl, 2),
        },
        "by_platform": {k: {kk: round(vv, 2) if isinstance(vv, float) else vv
                             for kk, vv in v.items()} for k, v in by_platform.items()},
        "by_type": {k: {kk: round(vv, 2) if isinstance(vv, float) else vv
                         for kk, vv in v.items()} for k, v in by_type.items()},
        "by_day": dict(sorted(by_day.items(), reverse=True)[:7]),
        "engine": {
            "total_cycles": total_cycles,
            "total_scanned": total_scanned,
            "total_blocked": total_blocked,
            "avg_cycle_duration": round(avg_duration, 2)
        },
        "cost": {"tier": 0, "amount_usd": 0.0}
    }

    append_jsonl(ANALYTICS_DIR / "run_stats.jsonl", summary)
    return summary


def generate_daily_report():
    """Generate end-of-day report."""
    summary = generate_pnl_summary()
    config = load_config()
    safety_events = read_jsonl(LOGS_DIR / "safety_events.jsonl")

    today = now_ts().strftime("%Y-%m-%d")
    today_safety = [e for e in safety_events if e.get("timestamp", "").startswith(today)]

    report = {
        "operation": "daily_report",
        "timestamp": now_iso(),
        "date": today,
        "status": "success",
        "pnl_summary": summary.get("overview", {}),
        "platform_breakdown": summary.get("by_platform", {}),
        "strategy_breakdown": summary.get("by_type", {}),
        "safety_events": {
            "total": len(today_safety),
            "blocks": len([e for e in today_safety if not e.get("passed", True)]),
            "events": today_safety[-10:]  # Last 10
        },
        "target_progress": {
            "daily_target_pct": config.get("target_daily_pct", 0.25) * 100,
            "achieved_pct": summary.get("overview", {}).get("total_return_pct", 0),
            "on_track": (summary.get("overview", {}).get("total_return_pct", 0) >=
                          config.get("target_daily_pct", 0.25) * 100 * 0.5)
        },
        "recommendations": [],
        "cost": {"tier": 0, "amount_usd": 0.0}
    }

    # Generate recommendations
    overview = summary.get("overview", {})
    if overview.get("win_rate_pct", 0) < 50:
        report["recommendations"].append("Win rate below 50% — review edge calculations")
    if overview.get("total_trades", 0) < 5:
        report["recommendations"].append("Low trade count — consider expanding scan parameters")
    blocks = report["safety_events"]["blocks"]
    if blocks > 5:
        report["recommendations"].append(f"{blocks} safety blocks today — review risk parameters")
    if not report["recommendations"]:
        report["recommendations"].append("System operating within normal parameters")

    # Save report
    report_path = REPORTS_DIR / "daily" / f"{today}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))

    append_jsonl(ANALYTICS_DIR / "run_stats.jsonl", report)

    return report


def generate_weekly_report():
    """Generate weekly summary report."""
    config = load_config()
    trades = read_jsonl(TRADES_DIR / "trade_journal.jsonl")
    cycles = read_jsonl(ANALYTICS_DIR / "run_stats.jsonl")

    week_start = (now_ts() - timedelta(days=7)).isoformat()
    week_trades = [t for t in trades if t.get("timestamp", "") > week_start]
    week_cycles = [c for c in cycles if c.get("timestamp", "") > week_start
                   and c.get("operation") == "trade_cycle"]

    total_pnl = sum(
        t.get("position_size", 0) * t.get("edge", 0) * 0.7
        for t in week_trades if t.get("mode") == "paper"
    )

    report = {
        "operation": "weekly_report",
        "timestamp": now_iso(),
        "period": f"{week_start[:10]} to {now_ts().strftime('%Y-%m-%d')}",
        "status": "success",
        "summary": {
            "total_trades": len(week_trades),
            "total_cycles": len(week_cycles),
            "total_pnl": round(total_pnl, 2),
            "avg_trades_per_day": round(len(week_trades) / 7, 1),
            "avg_pnl_per_day": round(total_pnl / 7, 2),
        },
        "strategy_review": {
            "best_performing": "TBD — requires more data",
            "worst_performing": "TBD — requires more data",
            "recommendations": []
        },
        "risk_review": {
            "max_daily_drawdown": "TBD",
            "safety_activations": 0,
            "kill_switch_events": 0
        },
        "tier_review": {
            "current_tier": 0,
            "weekly_cost": 0.0,
            "roi_ratio": "N/A",
            "upgrade_recommended": False
        },
        "cost": {"tier": 0, "amount_usd": 0.0}
    }

    report_path = REPORTS_DIR / "weekly" / f"{now_ts().strftime('%Y-W%W')}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))

    append_jsonl(ANALYTICS_DIR / "run_stats.jsonl", report)

    return report


def export_trade_journal():
    """Export trade journal as formatted output."""
    trades = read_jsonl(TRADES_DIR / "trade_journal.jsonl")

    if not trades:
        print("No trades recorded yet.")
        return

    print(f"\nTrade Journal — {len(trades)} trades")
    print(f"{'='*90}")
    print(f"{'Time':>20s}  {'Platform':>12s}  {'Action':>6s}  {'Size':>10s}  "
          f"{'Edge':>6s}  {'Status':>8s}  {'Mode':>6s}")
    print(f"{'-'*90}")

    for t in trades[-50:]:  # Last 50
        ts = t.get("timestamp", "")[:19]
        platform = t.get("platform", "?")
        action = t.get("action", "?")
        size = f"${t.get('position_size', 0):.2f}"
        edge = f"{t.get('edge', 0)*100:.1f}%"
        status = t.get("status", "?")
        mode = t.get("mode", "?")
        print(f"{ts:>20s}  {platform:>12s}  {action:>6s}  {size:>10s}  "
              f"{edge:>6s}  {status:>8s}  {mode:>6s}")


def health_check():
    """Check system health across all components."""
    print(f"\nSystem Health Check")
    print(f"{'='*50}")

    checks = []

    # Config
    config_ok = CONFIG_PATH.exists()
    checks.append(("Configuration", "PASS" if config_ok else "FAIL",
                    "Found" if config_ok else "Missing — run bootstrap.py setup"))

    # State directories
    for name, path in [("Analytics", ANALYTICS_DIR), ("Trades", TRADES_DIR),
                        ("Logs", LOGS_DIR), ("Reports", REPORTS_DIR)]:
        exists = path.exists()
        checks.append((f"Dir: {name}", "PASS" if exists else "WARN",
                        "OK" if exists else "Missing"))

    # Trade journal
    trades = read_jsonl(TRADES_DIR / "trade_journal.jsonl")
    checks.append(("Trade Journal", "PASS" if trades else "INFO",
                    f"{len(trades)} records" if trades else "Empty"))

    # Analytics
    stats = read_jsonl(ANALYTICS_DIR / "run_stats.jsonl")
    checks.append(("Analytics Log", "PASS" if stats else "INFO",
                    f"{len(stats)} records" if stats else "Empty"))

    # Errors
    errors = read_jsonl(LOGS_DIR / "errors.jsonl")
    recent_errors = [e for e in errors if e.get("timestamp", "") >
                      (now_ts() - timedelta(hours=24)).isoformat()]
    err_status = "PASS" if len(recent_errors) < 5 else "WARN"
    checks.append(("Errors (24h)", err_status,
                    f"{len(recent_errors)} errors" if recent_errors else "None"))

    # Safety state
    safety_path = STATE_DIR / "safety_state.json"
    if safety_path.exists():
        safety = json.loads(safety_path.read_text())
        kill = safety.get("kill_switch", False)
        checks.append(("Kill Switch", "FAIL" if kill else "PASS",
                        f"ACTIVE: {safety.get('kill_switch_reason', '')}" if kill else "OFF"))
    else:
        checks.append(("Safety State", "INFO", "Not initialized"))

    for name, status, detail in checks:
        icon = {"PASS": "✓", "FAIL": "✗", "WARN": "⚠", "INFO": "ℹ"}.get(status, "?")
        print(f"  {icon} [{status}] {name}: {detail}")

    # Log health check
    report = {
        "operation": "health_check",
        "timestamp": now_iso(),
        "status": "success",
        "checks": [{"name": n, "status": s, "detail": d} for n, s, d in checks],
        "overall": "healthy" if all(s != "FAIL" for _, s, _ in checks) else "degraded",
        "cost": {"tier": 0, "amount_usd": 0.0}
    }
    append_jsonl(ANALYTICS_DIR / "run_stats.jsonl", report)


# ── Commands ───────────────────────────────────────────────────

def do_daily():
    report = generate_daily_report()
    print(json.dumps(report, indent=2))

def do_weekly():
    report = generate_weekly_report()
    print(json.dumps(report, indent=2))

def do_pnl():
    summary = generate_pnl_summary()
    print(json.dumps(summary, indent=2))

def do_journal():
    export_trade_journal()

def do_health():
    health_check()

def do_status():
    stats = read_jsonl(ANALYTICS_DIR / "run_stats.jsonl")
    print(f"\nAnalytics — {len(stats)} total records")
    by_type = defaultdict(int)
    for s in stats:
        by_type[s.get("operation", "unknown")] += 1
    for op, count in sorted(by_type.items()):
        print(f"  {op:30s}: {count}")


COMMANDS = {
    "daily": do_daily,
    "weekly": do_weekly,
    "pnl": do_pnl,
    "journal": do_journal,
    "health": do_health,
    "status": do_status,
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
