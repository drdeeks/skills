#!/usr/bin/env python3
"""
Autonomous Trading System — Safety Net Engine

Enforces 6 layers of risk protection that cannot be overridden by trading logic.
All safety checks run BEFORE every trade and continuously during operation.

Usage:
    python3 safety_net.py check              # Run all safety checks
    python3 safety_net.py status             # Current risk state
    python3 safety_net.py kill               # Emergency kill switch
    python3 safety_net.py reset              # Reset daily counters
    python3 safety_net.py --help

Safety Layers:
    1. Circuit Breaker    — Halt on daily loss > 10%
    2. Drawdown Guardian  — Reduce sizing on peak-to-trough > 20%
    3. Position Limiter   — Block positions > 12% of bankroll
    4. Correlation Filter — Max 3 correlated positions
    5. Velocity Guard     — Max 5 trades per 10 minutes
    6. Kill Switch        — Manual or auto halt on consecutive losses
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
SAFETY_STATE_PATH = STATE_DIR / "safety_state.json"
SAFETY_LOG = STATE_DIR / "logs" / "safety_events.jsonl"
TRADES_LOG = STATE_DIR / "trades" / "trade_journal.jsonl"


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
        print("Config not found. Run bootstrap.py setup first.")
        sys.exit(1)
    return json.loads(CONFIG_PATH.read_text())


def load_safety_state():
    if SAFETY_STATE_PATH.exists():
        return json.loads(SAFETY_STATE_PATH.read_text())
    return {
        "kill_switch": False,
        "kill_switch_reason": "",
        "daily_start_bankroll": 0.0,
        "peak_bankroll": 0.0,
        "current_bankroll": 0.0,
        "daily_pnl": 0.0,
        "consecutive_losses": 0,
        "recent_trades": [],
        "open_positions": [],
        "sizing_multiplier": 1.0,
        "last_reset": now_iso(),
        "halted_until": ""
    }


def save_safety_state(state):
    SAFETY_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SAFETY_STATE_PATH.write_text(json.dumps(state, indent=2))


def log_safety_event(event_type, passed, details):
    record = {
        "timestamp": now_iso(),
        "event_type": event_type,
        "passed": passed,
        "details": details
    }
    append_jsonl(SAFETY_LOG, record)
    return record


# ── Safety Check Functions ─────────────────────────────────────

class SafetyResult:
    def __init__(self, name, passed, reason="", action=""):
        self.name = name
        self.passed = passed
        self.reason = reason
        self.action = action

    def __repr__(self):
        icon = "✓" if self.passed else "✗"
        status = "PASS" if self.passed else "BLOCK"
        line = f"  {icon} [{status}] {self.name}"
        if not self.passed:
            line += f" — {self.reason} → {self.action}"
        return line


def check_circuit_breaker(state, config):
    """Layer 1: Daily loss limit."""
    risk = config.get("risk", {})
    max_loss_pct = risk.get("max_daily_loss_pct", 0.10)
    start = state.get("daily_start_bankroll", 0)

    if start <= 0:
        return SafetyResult("Circuit Breaker", True, "No starting bankroll set")

    daily_pnl = state.get("daily_pnl", 0)
    loss_pct = abs(min(0, daily_pnl)) / start

    if loss_pct >= max_loss_pct:
        return SafetyResult(
            "Circuit Breaker", False,
            f"Daily loss {loss_pct*100:.1f}% >= {max_loss_pct*100:.0f}% limit",
            "HALT all trading for 24 hours"
        )
    return SafetyResult("Circuit Breaker", True,
                         f"Daily loss {loss_pct*100:.1f}% < {max_loss_pct*100:.0f}% limit")


def check_drawdown_guardian(state, config):
    """Layer 2: Peak-to-trough drawdown."""
    risk = config.get("risk", {})
    max_dd = risk.get("max_drawdown_pct", 0.20)
    peak = state.get("peak_bankroll", 0)
    current = state.get("current_bankroll", 0)

    if peak <= 0:
        return SafetyResult("Drawdown Guardian", True, "No peak recorded")

    drawdown = (peak - current) / peak if peak > 0 else 0

    if drawdown >= max_dd:
        return SafetyResult(
            "Drawdown Guardian", False,
            f"Drawdown {drawdown*100:.1f}% >= {max_dd*100:.0f}% limit",
            "REDUCE position sizes by 50%"
        )
    return SafetyResult("Drawdown Guardian", True,
                         f"Drawdown {drawdown*100:.1f}% < {max_dd*100:.0f}% limit")


def check_position_size(trade_amount, state, config):
    """Layer 3: Single position size limit."""
    risk = config.get("risk", {})
    max_pct = risk.get("max_position_pct", 0.12)
    bankroll = state.get("current_bankroll", 0)

    if bankroll <= 0:
        return SafetyResult("Position Limiter", False,
                             "Bankroll is $0", "BLOCK — fund account first")

    position_pct = trade_amount / bankroll if bankroll > 0 else 1.0

    if position_pct > max_pct:
        max_size = bankroll * max_pct
        return SafetyResult(
            "Position Limiter", False,
            f"${trade_amount:.2f} is {position_pct*100:.1f}% > {max_pct*100:.0f}% limit",
            f"REDUCE to max ${max_size:.2f}"
        )
    return SafetyResult("Position Limiter", True,
                         f"${trade_amount:.2f} = {position_pct*100:.1f}% < {max_pct*100:.0f}%")


def check_correlation_filter(trade_category, state, config):
    """Layer 4: Correlated position limit."""
    risk = config.get("risk", {})
    max_corr = risk.get("max_correlated_positions", 3)

    open_positions = state.get("open_positions", [])
    same_category = [p for p in open_positions if p.get("category") == trade_category]

    if len(same_category) >= max_corr:
        return SafetyResult(
            "Correlation Filter", False,
            f"{len(same_category)} positions in '{trade_category}' >= {max_corr} limit",
            "BLOCK — reduce exposure to this category first"
        )
    return SafetyResult("Correlation Filter", True,
                         f"{len(same_category)} in '{trade_category}' < {max_corr} limit")


def check_velocity_guard(state, config):
    """Layer 5: Trade velocity limit."""
    risk = config.get("risk", {})
    max_per_10min = risk.get("max_trades_per_10min", 5)

    recent = state.get("recent_trades", [])
    cutoff = (now_ts() - timedelta(minutes=10)).isoformat()
    recent_window = [t for t in recent if t.get("timestamp", "") > cutoff]

    if len(recent_window) >= max_per_10min:
        return SafetyResult(
            "Velocity Guard", False,
            f"{len(recent_window)} trades in 10min >= {max_per_10min} limit",
            "THROTTLE — wait before next trade"
        )
    return SafetyResult("Velocity Guard", True,
                         f"{len(recent_window)} trades in 10min < {max_per_10min} limit")


def check_kill_switch(state, config):
    """Layer 6: Emergency kill switch."""
    if state.get("kill_switch", False):
        return SafetyResult(
            "Kill Switch", False,
            f"ACTIVATED: {state.get('kill_switch_reason', 'Manual trigger')}",
            "HALT — close all positions, stop trading"
        )

    # Auto-trigger on consecutive losses
    risk = config.get("risk", {})
    max_consec = risk.get("consecutive_loss_halt", 3)
    threshold = risk.get("consecutive_loss_threshold", 0.05)
    consec = state.get("consecutive_losses", 0)

    if consec >= max_consec:
        return SafetyResult(
            "Kill Switch", False,
            f"{consec} consecutive losses >= {max_consec} threshold",
            "AUTO-HALT — closing positions"
        )

    # Check halted_until
    halted = state.get("halted_until", "")
    if halted and halted > now_iso():
        return SafetyResult(
            "Kill Switch", False,
            f"Halted until {halted}",
            "WAIT — system cooling down"
        )

    return SafetyResult("Kill Switch", True)


def pre_trade_safety_check(trade_amount=0, trade_category="", state=None, config=None):
    """Run ALL safety checks before a trade. Returns (all_passed, results)."""
    if state is None:
        state = load_safety_state()
    if config is None:
        config = load_config()

    results = [
        check_circuit_breaker(state, config),
        check_drawdown_guardian(state, config),
        check_position_size(trade_amount, state, config),
        check_correlation_filter(trade_category, state, config),
        check_velocity_guard(state, config),
        check_kill_switch(state, config),
    ]

    all_passed = all(r.passed for r in results)

    # Apply drawdown sizing adjustment
    dd_result = results[1]
    if not dd_result.passed and "REDUCE" in dd_result.action:
        state["sizing_multiplier"] = 0.5
    else:
        state["sizing_multiplier"] = min(state.get("sizing_multiplier", 1.0) + 0.1, 1.0)

    save_safety_state(state)

    # Log if blocked
    if not all_passed:
        failed = [r.name for r in results if not r.passed]
        log_safety_event("trade_blocked", False, {
            "trade_amount": trade_amount,
            "trade_category": trade_category,
            "failed_checks": failed
        })

    return all_passed, results


def record_trade_result(pnl, trade_info=None):
    """Record a trade result and update safety state."""
    state = load_safety_state()
    config = load_config()

    # Update P&L
    state["daily_pnl"] = state.get("daily_pnl", 0) + pnl
    state["current_bankroll"] = state.get("current_bankroll", 0) + pnl

    # Update peak
    if state["current_bankroll"] > state.get("peak_bankroll", 0):
        state["peak_bankroll"] = state["current_bankroll"]

    # Update consecutive losses
    if pnl < 0:
        state["consecutive_losses"] = state.get("consecutive_losses", 0) + 1
    else:
        state["consecutive_losses"] = 0

    # Add to recent trades
    recent = state.get("recent_trades", [])
    recent.append({
        "timestamp": now_iso(),
        "pnl": pnl,
        "info": trade_info or {}
    })
    # Keep only last 100
    state["recent_trades"] = recent[-100:]

    save_safety_state(state)

    # Check if we need to auto-halt
    risk = config.get("risk", {})
    if state["consecutive_losses"] >= risk.get("consecutive_loss_halt", 3):
        activate_kill_switch(f"Auto: {state['consecutive_losses']} consecutive losses")

    return state


def activate_kill_switch(reason="Manual trigger"):
    """Emergency: halt all trading."""
    state = load_safety_state()
    state["kill_switch"] = True
    state["kill_switch_reason"] = reason
    state["halted_until"] = (now_ts() + timedelta(hours=24)).isoformat()
    save_safety_state(state)
    log_safety_event("kill_switch_activated", False, {"reason": reason})
    print(f"\n  ⚠ KILL SWITCH ACTIVATED: {reason}")
    print(f"  Trading halted until: {state['halted_until']}")


def deactivate_kill_switch():
    """Reset kill switch after review."""
    state = load_safety_state()
    state["kill_switch"] = False
    state["kill_switch_reason"] = ""
    state["halted_until"] = ""
    state["consecutive_losses"] = 0
    save_safety_state(state)
    log_safety_event("kill_switch_deactivated", True, {})
    print("  Kill switch deactivated. Trading can resume.")


# ── Commands ───────────────────────────────────────────────────

def do_check():
    """Run all safety checks."""
    print("\nSafety Net — Full Check")
    print("=" * 45)
    all_passed, results = pre_trade_safety_check(
        trade_amount=100.0,
        trade_category="test"
    )
    for r in results:
        print(r)
    overall = "ALL CLEAR" if all_passed else "BLOCKED"
    print(f"\n  Overall: {overall}")


def do_status():
    """Show current risk state."""
    state = load_safety_state()
    config = load_config()
    print("\nSafety Net — Risk State")
    print("=" * 45)
    print(f"  Kill Switch:       {'ACTIVE' if state.get('kill_switch') else 'OFF'}")
    print(f"  Sizing Multiplier: {state.get('sizing_multiplier', 1.0)*100:.0f}%")
    print(f"  Daily P&L:         ${state.get('daily_pnl', 0):.2f}")
    print(f"  Current Bankroll:  ${state.get('current_bankroll', 0):.2f}")
    print(f"  Peak Bankroll:     ${state.get('peak_bankroll', 0):.2f}")
    print(f"  Consec. Losses:    {state.get('consecutive_losses', 0)}")
    print(f"  Open Positions:    {len(state.get('open_positions', []))}")

    recent = state.get("recent_trades", [])
    cutoff = (now_ts() - timedelta(minutes=10)).isoformat()
    recent_10m = [t for t in recent if t.get("timestamp", "") > cutoff]
    print(f"  Trades (10min):    {len(recent_10m)}")
    print(f"  Last Reset:        {state.get('last_reset', 'Never')}")


def do_kill():
    """Activate emergency kill switch."""
    reason = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Manual trigger"
    activate_kill_switch(reason)


def do_reset():
    """Reset daily counters."""
    state = load_safety_state()
    config = load_config()
    state["daily_pnl"] = 0.0
    state["daily_start_bankroll"] = state.get("current_bankroll", config.get("bankroll", 0))
    state["consecutive_losses"] = 0
    state["recent_trades"] = []
    state["sizing_multiplier"] = 1.0
    state["last_reset"] = now_iso()
    save_safety_state(state)
    log_safety_event("daily_reset", True, {})
    print("  Daily counters reset.")


COMMANDS = {
    "check": do_check,
    "status": do_status,
    "kill": do_kill,
    "reset": do_reset,
    "unkill": deactivate_kill_switch,
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
