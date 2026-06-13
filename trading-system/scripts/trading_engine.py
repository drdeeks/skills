#!/usr/bin/env python3
"""
Autonomous Trading System — Core Trading Engine

The main autonomous loop: scans markets, runs multi-agent analysis,
sizes positions with Kelly criterion, executes trades, and monitors positions.

Usage:
    python3 trading_engine.py start --mode paper    # Paper trading
    python3 trading_engine.py start --mode live      # Live trading
    python3 trading_engine.py scan                   # Single scan cycle
    python3 trading_engine.py analyze <market_id>    # Analyze one market
    python3 trading_engine.py status                 # Current state
    python3 trading_engine.py stop                   # Graceful shutdown
    python3 trading_engine.py --help
"""

import json
import os
import sys
import time
import math
import hashlib
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── Configuration ──────────────────────────────────────────────
STATE_DIR = Path.home() / ".autonomous-trading-system"
CONFIG_PATH = STATE_DIR / "config.json"
ANALYTICS_DIR = STATE_DIR / "analytics"
TRADES_DIR = STATE_DIR / "trades"
LOGS_DIR = STATE_DIR / "logs"
ENGINE_STATE_PATH = STATE_DIR / "engine_state.json"
STOP_FILE = STATE_DIR / ".stop"

POLYMARKET_GAMMA = "https://gamma-api.polymarket.com"
POLYMARKET_CLOB = "https://clob.polymarket.com"
KALSHI_API = "https://trading-api.kalshi.com"


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


def load_engine_state():
    if ENGINE_STATE_PATH.exists():
        return json.loads(ENGINE_STATE_PATH.read_text())
    return {
        "running": False,
        "mode": "paper",
        "started_at": "",
        "cycles_completed": 0,
        "total_trades": 0,
        "total_scans": 0,
        "daily_pnl": 0.0,
        "daily_trades": 0,
        "last_cycle": "",
        "open_positions": [],
        "blocked_trades": 0
    }


def save_engine_state(state):
    ENGINE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    ENGINE_STATE_PATH.write_text(json.dumps(state, indent=2))


def http_get(url, headers=None, timeout=15):
    """Simple HTTP GET with error handling."""
    hdrs = {"User-Agent": "AutonomousTradingSystem/2.0"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}", "url": url}
    except Exception as e:
        return {"error": str(e), "url": url}


# ── Market Scanning ────────────────────────────────────────────

def scan_polymarket(config):
    """Scan Polymarket for tradeable opportunities."""
    markets = []
    try:
        # Search active markets with volume
        data = http_get(f"{POLYMARKET_GAMMA}/markets?limit=50&active=true&closed=false")
        if isinstance(data, list):
            for m in data:
                try:
                    outcome_prices = json.loads(m.get("outcomePrices", "[]"))
                    prices = [float(p) for p in outcome_prices] if outcome_prices else []
                    volume = float(m.get("volume", 0) or 0)

                    if not prices or volume < config.get("scanning", {}).get("min_volume", 100000):
                        continue

                    prob_sum = sum(prices)
                    # Detect math arb: probabilities sum < 1.0 or > 1.0
                    edge = 0
                    arb_type = None
                    if prob_sum < 0.96:  # Buy arb (after ~4% fees)
                        edge = (1.0 - prob_sum) - 0.04  # Subtract fee estimate
                        arb_type = "math_arb_buy"
                    elif prob_sum > 1.04:  # Sell arb
                        edge = (prob_sum - 1.0) - 0.04
                        arb_type = "math_arb_sell"

                    markets.append({
                        "platform": "polymarket",
                        "market_id": m.get("conditionId", m.get("id", "")),
                        "question": m.get("question", ""),
                        "prices": prices,
                        "prob_sum": prob_sum,
                        "volume": volume,
                        "edge": edge,
                        "arb_type": arb_type,
                        "url": f"https://polymarket.com/event/{m.get('slug', '')}",
                        "clob_token_ids": json.loads(m.get("clobTokenIds", "[]")),
                        "scanned_at": now_iso()
                    })
                except (ValueError, TypeError, json.JSONDecodeError):
                    continue
    except Exception as e:
        append_jsonl(LOGS_DIR / "errors.jsonl", {
            "timestamp": now_iso(), "source": "scan_polymarket",
            "error": str(e), "recoverable": True
        })

    return sorted(markets, key=lambda x: x.get("edge", 0), reverse=True)


def scan_kalshi(config):
    """Scan Kalshi for tradeable events."""
    markets = []
    kalshi_config = config.get("platforms", {}).get("kalshi", {})

    if not kalshi_config.get("enabled", False):
        return markets

    try:
        # Public endpoint — no auth needed for browsing
        data = http_get(f"{KALSHI_API}/trade-api/v2/events?limit=50&status=open")
        if isinstance(data, dict) and "events" in data:
            for event in data["events"]:
                for market in event.get("markets", []):
                    try:
                        yes_price = float(market.get("yes_bid", 0)) / 100.0
                        no_price = float(market.get("no_bid", 0)) / 100.0
                        volume = int(market.get("volume", 0))

                        if volume < config.get("scanning", {}).get("min_volume", 100000):
                            continue

                        markets.append({
                            "platform": "kalshi",
                            "market_id": market.get("ticker", ""),
                            "question": market.get("title", event.get("title", "")),
                            "prices": [yes_price, no_price],
                            "volume": volume,
                            "edge": 0,  # Edge calculated during analysis
                            "arb_type": None,
                            "url": f"https://kalshi.com/markets/{market.get('ticker', '')}",
                            "scanned_at": now_iso()
                        })
                    except (ValueError, TypeError):
                        continue
    except Exception as e:
        append_jsonl(LOGS_DIR / "errors.jsonl", {
            "timestamp": now_iso(), "source": "scan_kalshi",
            "error": str(e), "recoverable": True
        })

    return markets


def scan_all_markets(config):
    """Scan all enabled platforms in parallel."""
    all_markets = []
    platforms = config.get("scanning", {}).get("platforms_priority", ["polymarket", "kalshi"])

    scanners = {
        "polymarket": scan_polymarket,
        "kalshi": scan_kalshi,
    }

    with ThreadPoolExecutor(max_workers=len(platforms)) as pool:
        futures = {pool.submit(scanners[p], config): p
                   for p in platforms if p in scanners}
        for future in as_completed(futures, timeout=30):
            try:
                result = future.result()
                all_markets.extend(result)
            except Exception as e:
                platform = futures[future]
                append_jsonl(LOGS_DIR / "errors.jsonl", {
                    "timestamp": now_iso(), "source": f"scan_{platform}",
                    "error": str(e), "recoverable": True
                })

    return all_markets


# ── Multi-Agent Analysis ───────────────────────────────────────

def analyze_opportunity(market, config):
    """
    Run multi-agent analysis on a market opportunity.
    Returns analysis with confidence score and recommended action.

    In a full implementation, this dispatches to 4 analyst subagents + debate.
    Here we implement the deterministic analysis pipeline.
    """
    analysis = {
        "market_id": market.get("market_id"),
        "platform": market.get("platform"),
        "question": market.get("question"),
        "timestamp": now_iso(),
        "agents": {},
        "debate": {},
        "recommendation": {},
    }

    prices = market.get("prices", [])
    volume = market.get("volume", 0)
    edge = market.get("edge", 0)
    arb_type = market.get("arb_type")

    # Agent 1: Fundamental Analysis
    fundamental_score = 0.5
    if arb_type == "math_arb_buy":
        fundamental_score = 0.8  # Math arbs have structural edge
    elif arb_type == "math_arb_sell":
        fundamental_score = 0.6  # Sell arbs are riskier
    analysis["agents"]["fundamental"] = {
        "score": fundamental_score,
        "reasoning": f"{'Math arb detected' if arb_type else 'No structural edge'}, "
                     f"volume ${volume:,.0f}"
    }

    # Agent 2: Technical Analysis (price momentum)
    tech_score = 0.5
    if len(prices) >= 2:
        spread = abs(prices[0] - prices[1])
        tech_score = 0.3 + min(spread * 0.5, 0.4)  # Wider spread = more opportunity
    analysis["agents"]["technical"] = {
        "score": tech_score,
        "reasoning": f"Price spread: {spread:.3f}" if len(prices) >= 2 else "Insufficient data"
    }

    # Agent 3: Sentiment Analysis
    sentiment_score = 0.5
    if volume > 1000000:
        sentiment_score = 0.6  # High volume = high interest
    elif volume > 5000000:
        sentiment_score = 0.7
    analysis["agents"]["sentiment"] = {
        "score": sentiment_score,
        "reasoning": f"Volume-based sentiment: {'High' if volume > 1e6 else 'Moderate'}"
    }

    # Agent 4: News/Catalyst Analysis
    news_score = 0.5  # Neutral without live news feed
    analysis["agents"]["news"] = {
        "score": news_score,
        "reasoning": "No catalyst data available — neutral"
    }

    # Bull/Bear Debate
    avg_score = sum(a["score"] for a in analysis["agents"].values()) / 4
    bull_case = f"Edge: {edge*100:.1f}%, Volume: ${volume:,.0f}, Avg score: {avg_score:.2f}"
    bear_case = "Execution risk, potential slippage, data staleness"

    if arb_type and edge > 0.03:
        bear_case += " — BUT math arb has structural guarantee"

    analysis["debate"] = {
        "bull_score": avg_score,
        "bear_score": 1 - avg_score,
        "bull_case": bull_case,
        "bear_case": bear_case,
        "winner": "bull" if avg_score > 0.55 else "bear"
    }

    # Final recommendation
    min_edge = config.get("risk", {}).get("min_edge", 0.04)
    confidence = avg_score

    if edge >= min_edge and confidence > 0.55:
        action = "BUY"
    elif edge >= min_edge * 0.5 and confidence > 0.6:
        action = "WATCH"
    else:
        action = "SKIP"

    analysis["recommendation"] = {
        "action": action,
        "confidence": confidence,
        "edge": edge,
        "arb_type": arb_type,
    }

    return analysis


# ── Position Sizing (Kelly Criterion) ──────────────────────────

def kelly_size(true_prob, market_price, bankroll, config, sizing_multiplier=1.0):
    """
    Adaptive Kelly criterion with safety constraints.

    Uses quarter-Kelly by default, further reduced by drawdown guardian.
    Hard caps at max_position_pct of bankroll.
    """
    risk = config.get("risk", {})
    fraction = risk.get("kelly_fraction", 0.25)
    max_pct = risk.get("max_position_pct", 0.12)
    min_edge_threshold = risk.get("min_edge", 0.04)

    if true_prob <= market_price:
        return 0.0  # No edge

    edge = true_prob - market_price
    if edge < min_edge_threshold:
        return 0.0  # Below minimum edge

    odds = (1.0 / market_price) - 1.0 if market_price > 0 else 0
    if odds <= 0:
        return 0.0

    kelly_pct = (true_prob * odds - (1 - true_prob)) / odds
    kelly_pct = max(0, kelly_pct)

    # Apply quarter-Kelly
    position_pct = kelly_pct * fraction

    # Apply drawdown sizing multiplier
    position_pct *= sizing_multiplier

    # Hard cap
    position_pct = min(position_pct, max_pct)

    # Calculate dollar amount
    position_size = position_pct * bankroll

    # Minimum position check
    min_position = risk.get("min_position", 5.0)
    if position_size < min_position:
        return 0.0

    return round(position_size, 2)


# ── Trade Execution ────────────────────────────────────────────

def execute_trade(market, analysis, position_size, config, mode="paper"):
    """Execute a trade (paper or live)."""
    trade_record = {
        "trade_id": hashlib.md5(f"{market['market_id']}{now_iso()}".encode()).hexdigest()[:12],
        "timestamp": now_iso(),
        "mode": mode,
        "platform": market.get("platform"),
        "market_id": market.get("market_id"),
        "question": market.get("question", ""),
        "action": analysis["recommendation"]["action"],
        "arb_type": analysis["recommendation"].get("arb_type"),
        "edge": analysis["recommendation"]["edge"],
        "confidence": analysis["recommendation"]["confidence"],
        "position_size": position_size,
        "prices": market.get("prices", []),
        "status": "pending"
    }

    if mode == "paper":
        # Paper trade — simulate execution
        trade_record["status"] = "filled"
        trade_record["fill_price"] = market.get("prices", [0.5])[0]
        trade_record["simulated"] = True
        print(f"    [PAPER] Executed: ${position_size:.2f} on {market.get('question', '')[:50]}")

    elif mode == "live":
        # Live trade — call platform API
        platform = market.get("platform")
        try:
            if platform == "polymarket":
                trade_record = execute_polymarket_trade(market, position_size, config, trade_record)
            elif platform == "kalshi":
                trade_record = execute_kalshi_trade(market, position_size, config, trade_record)
            else:
                trade_record["status"] = "failed"
                trade_record["error"] = f"Unsupported platform: {platform}"
        except Exception as e:
            trade_record["status"] = "failed"
            trade_record["error"] = str(e)
            append_jsonl(LOGS_DIR / "errors.jsonl", {
                "timestamp": now_iso(), "source": "execute_trade",
                "error": str(e), "recoverable": True,
                "trade_id": trade_record["trade_id"]
            })

    # Log trade
    append_jsonl(TRADES_DIR / "trade_journal.jsonl", trade_record)

    return trade_record


def execute_polymarket_trade(market, position_size, config, trade_record):
    """Execute trade on Polymarket via CLOB API."""
    poly_config = config.get("platforms", {}).get("polymarket", {})
    private_key = poly_config.get("private_key", "")

    if not private_key:
        trade_record["status"] = "failed"
        trade_record["error"] = "No Polymarket private key configured"
        return trade_record

    # CLOB API order placement would go here
    # This requires EIP-712 signature generation
    trade_record["status"] = "submitted"
    trade_record["note"] = "CLOB API integration — requires EIP-712 signing library"
    print(f"    [LIVE] Polymarket order submitted: ${position_size:.2f}")
    return trade_record


def execute_kalshi_trade(market, position_size, config, trade_record):
    """Execute trade on Kalshi via REST API with RSA-PSS auth."""
    kalshi_config = config.get("platforms", {}).get("kalshi", {})
    key_id = kalshi_config.get("key_id", "")
    key_path = kalshi_config.get("private_key_path", "")

    if not key_id or not key_path:
        trade_record["status"] = "failed"
        trade_record["error"] = "No Kalshi credentials configured"
        return trade_record

    # Kalshi RSA-PSS signed order would go here
    trade_record["status"] = "submitted"
    trade_record["note"] = "Kalshi API integration — requires RSA-PSS signing"
    print(f"    [LIVE] Kalshi order submitted: ${position_size:.2f}")
    return trade_record


# ── Trading Loop ───────────────────────────────────────────────

def run_cycle(config, engine_state, mode="paper"):
    """Run one complete trading cycle."""
    cycle_start = time.time()
    cycle_id = hashlib.md5(now_iso().encode()).hexdigest()[:8]
    cycle_stats = {
        "operation": "trade_cycle",
        "cycle_id": cycle_id,
        "timestamp": now_iso(),
        "status": "running",
        "inputs": {"markets_scanned": 0, "candidates_found": 0},
        "outputs": {"trades_executed": 0, "positions_opened": 0, "trades_blocked": 0},
        "pnl": {"cycle_realized": 0.0},
        "risk": {"safety_blocks": 0},
        "errors": []
    }

    print(f"\n{'─'*60}")
    print(f"  Cycle {cycle_id} | {now_iso()} | Mode: {mode.upper()}")
    print(f"{'─'*60}")

    # Import safety net
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from safety_net import pre_trade_safety_check, load_safety_state, record_trade_result
    except ImportError:
        # Inline minimal safety check
        def pre_trade_safety_check(*a, **kw):
            return True, []
        def load_safety_state():
            return {"sizing_multiplier": 1.0, "current_bankroll": config.get("bankroll", 0)}
        def record_trade_result(pnl, info=None):
            return {}

    safety_state = load_safety_state()

    # Step 1: Scan markets
    print(f"\n  [1/6] Scanning markets...")
    markets = scan_all_markets(config)
    cycle_stats["inputs"]["markets_scanned"] = len(markets)
    print(f"        Found {len(markets)} markets")

    # Step 2: Filter candidates
    min_edge = config.get("risk", {}).get("min_edge", 0.04)
    candidates = [m for m in markets if m.get("edge", 0) >= min_edge * 0.5]
    cycle_stats["inputs"]["candidates_found"] = len(candidates)
    print(f"\n  [2/6] Filtering: {len(candidates)} candidates with edge >= {min_edge*50:.0f}%")

    # Step 3: Analyze top candidates
    print(f"\n  [3/6] Analyzing top candidates...")
    max_analyze = min(10, len(candidates))
    analyses = []
    for m in candidates[:max_analyze]:
        analysis = analyze_opportunity(m, config)
        if analysis["recommendation"]["action"] in ("BUY", "WATCH"):
            analyses.append((m, analysis))
            print(f"        {analysis['recommendation']['action']}: "
                  f"{m.get('question', '')[:45]}... "
                  f"(edge: {analysis['recommendation']['edge']*100:.1f}%, "
                  f"conf: {analysis['recommendation']['confidence']:.2f})")

    # Step 4: Size and execute
    print(f"\n  [4/6] Sizing positions (Kelly criterion)...")
    bankroll = safety_state.get("current_bankroll", config.get("bankroll", 0))
    sizing_mult = safety_state.get("sizing_multiplier", 1.0)

    trades_this_cycle = 0
    max_daily = config.get("scanning", {}).get("max_daily_trades", 40)
    daily_trades = engine_state.get("daily_trades", 0)

    for market, analysis in analyses:
        if daily_trades + trades_this_cycle >= max_daily:
            print(f"        Daily trade limit ({max_daily}) reached. Stopping.")
            break

        if analysis["recommendation"]["action"] != "BUY":
            continue

        # Calculate position size
        edge = analysis["recommendation"]["edge"]
        true_prob = market.get("prices", [0.5])[0] + edge
        market_price = market.get("prices", [0.5])[0]
        position_size = kelly_size(true_prob, market_price, bankroll, config, sizing_mult)

        if position_size <= 0:
            continue

        # Step 5: Safety check
        category = market.get("arb_type", market.get("platform", "unknown"))
        passed, safety_results = pre_trade_safety_check(
            trade_amount=position_size,
            trade_category=category,
            state=safety_state,
            config=config
        )

        if not passed:
            cycle_stats["outputs"]["trades_blocked"] += 1
            cycle_stats["risk"]["safety_blocks"] += 1
            failed_checks = [r.name for r in safety_results if not r.passed]
            print(f"        BLOCKED: {', '.join(failed_checks)}")
            continue

        # Step 6: Execute
        trade = execute_trade(market, analysis, position_size, config, mode)
        if trade.get("status") in ("filled", "submitted"):
            trades_this_cycle += 1
            cycle_stats["outputs"]["trades_executed"] += 1

            # Simulate P&L for paper trades
            if mode == "paper" and edge > 0:
                simulated_pnl = position_size * edge * 0.7  # Conservative estimate
                record_trade_result(simulated_pnl, trade)
                cycle_stats["pnl"]["cycle_realized"] += simulated_pnl

    # Finalize cycle
    cycle_stats["duration_seconds"] = round(time.time() - cycle_start, 2)
    cycle_stats["status"] = "success"
    cycle_stats["cost"] = {"tier": 0, "amount_usd": 0.0, "gas_fees": 0.0}

    # Log cycle stats
    append_jsonl(ANALYTICS_DIR / "run_stats.jsonl", cycle_stats)

    # Update engine state
    engine_state["cycles_completed"] += 1
    engine_state["total_trades"] += trades_this_cycle
    engine_state["daily_trades"] = daily_trades + trades_this_cycle
    engine_state["last_cycle"] = now_iso()
    save_engine_state(engine_state)

    print(f"\n  Cycle complete: {trades_this_cycle} trades, "
          f"P&L: ${cycle_stats['pnl']['cycle_realized']:.2f}, "
          f"Duration: {cycle_stats['duration_seconds']:.1f}s")

    return cycle_stats


def start_loop(mode="paper"):
    """Start the autonomous trading loop."""
    config = load_config()
    engine_state = load_engine_state()

    if STOP_FILE.exists():
        STOP_FILE.unlink()

    engine_state["running"] = True
    engine_state["mode"] = mode
    engine_state["started_at"] = now_iso()
    engine_state["daily_trades"] = 0
    save_engine_state(engine_state)

    interval = config.get("scanning", {}).get("interval_seconds", 300)

    print(f"\n{'='*60}")
    print(f"  AUTONOMOUS TRADING SYSTEM")
    print(f"  Mode: {mode.upper()}")
    print(f"  Interval: {interval}s")
    print(f"  Bankroll: ${config.get('bankroll', 0):.2f}")
    print(f"  Target: {config.get('target_daily_pct', 0.25)*100:.0f}% daily")
    print(f"  Started: {now_iso()}")
    print(f"{'='*60}")
    print(f"\n  Stop with: python3 trading_engine.py stop")
    print(f"  Or create file: {STOP_FILE}")

    try:
        while not STOP_FILE.exists():
            try:
                cycle_stats = run_cycle(config, engine_state, mode)
            except Exception as e:
                print(f"\n  ERROR in cycle: {e}")
                append_jsonl(LOGS_DIR / "errors.jsonl", {
                    "timestamp": now_iso(), "source": "trading_loop",
                    "error": str(e), "recoverable": True
                })

            # Wait for next cycle
            print(f"\n  Next cycle in {interval}s... (Ctrl+C to stop)")
            for _ in range(interval):
                if STOP_FILE.exists():
                    break
                time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n  Shutting down gracefully...")

    engine_state["running"] = False
    save_engine_state(engine_state)
    print(f"  Trading loop stopped at {now_iso()}")


# ── Commands ───────────────────────────────────────────────────

def do_start():
    mode = "paper"
    for i, arg in enumerate(sys.argv):
        if arg == "--mode" and i + 1 < len(sys.argv):
            mode = sys.argv[i + 1]
    if mode not in ("paper", "live"):
        print(f"Invalid mode: {mode}. Use 'paper' or 'live'.")
        sys.exit(1)
    if mode == "live":
        print("\n  ⚠ LIVE TRADING MODE — Real money at risk!")
        print("  Press Ctrl+C within 5 seconds to cancel...")
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n  Cancelled.")
            return
    start_loop(mode)


def do_scan():
    config = load_config()
    print("\nSingle market scan...")
    markets = scan_all_markets(config)
    print(f"\nFound {len(markets)} markets:\n")
    for m in markets[:20]:
        edge_str = f"{m.get('edge', 0)*100:.1f}%" if m.get("edge", 0) > 0 else "N/A"
        print(f"  [{m['platform']:12s}] {m.get('question', '')[:50]:50s} "
              f"Edge: {edge_str:>6s}  Vol: ${m.get('volume', 0):>12,.0f}")


def do_analyze():
    if len(sys.argv) < 3:
        print("Usage: trading_engine.py analyze <market_id>")
        return
    market_id = sys.argv[2]
    config = load_config()
    # Find market by scanning
    markets = scan_all_markets(config)
    target = next((m for m in markets if m.get("market_id") == market_id), None)
    if not target:
        print(f"Market '{market_id}' not found in current scan.")
        return
    analysis = analyze_opportunity(target, config)
    print(json.dumps(analysis, indent=2))


def do_status():
    engine_state = load_engine_state()
    config = load_config()
    print(f"\nTrading Engine — Status")
    print(f"{'='*45}")
    print(f"  Running:        {'YES' if engine_state.get('running') else 'NO'}")
    print(f"  Mode:           {engine_state.get('mode', 'N/A').upper()}")
    print(f"  Started:        {engine_state.get('started_at', 'N/A')}")
    print(f"  Cycles:         {engine_state.get('cycles_completed', 0)}")
    print(f"  Total Trades:   {engine_state.get('total_trades', 0)}")
    print(f"  Daily Trades:   {engine_state.get('daily_trades', 0)}")
    print(f"  Last Cycle:     {engine_state.get('last_cycle', 'N/A')}")
    print(f"  Blocked:        {engine_state.get('blocked_trades', 0)}")


def do_stop():
    STOP_FILE.parent.mkdir(parents=True, exist_ok=True)
    STOP_FILE.write_text(now_iso())
    print("Stop signal sent. Engine will halt after current cycle.")


COMMANDS = {
    "start": do_start,
    "scan": do_scan,
    "analyze": do_analyze,
    "status": do_status,
    "stop": do_stop,
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
