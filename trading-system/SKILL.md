---
name: trading-system
description: "Autonomous multi-agent trading system with cognitive loop, strategy analysis, risk management, and self-bootstrapping. Runs multi-agent analysis (fundamental, technical, sentiment, news), bull/bear debate, Kelly-sized execution, and adaptive safety nets. Provider-agnostic (works with any LLM backend). Free-first (starts with $0 data sources). Triggers: autonomous trading, prediction market arbitrage, trading strategy analysis, next-wave mindset, self-bootstrapping trader, smart wallet trading, Kelly criterion sizing, multi-agent trading system, automated API key setup, trading bot, or run trading loop."
license: MIT
version: 0.0.3
---

# Autonomous Trading System

Self-bootstrapping, cognitively aggressive autonomous trading framework. Spawns specialized analyst agents, conducts adversarial bull/bear debates, executes trades via smart wallets, and enforces hard safety nets — all while targeting aggressive daily returns with capital preservation as the non-negotiable constraint.

## Mission

$100K → $150K ASAP on Account 1. Aggressive. Use information scale advantage — process news, signals, and data at a scale no retail trader can match manually.

---

## Provider Compatibility

| Provider | Compatibility | Notes |
|---|---|---|
| MuleRun | Full | Native session, compute, drive, scheduled tasks |
| Claude (Anthropic) | Full | MCP servers, tool use, computer use for browser bootstrap |
| OpenAI / ChatGPT | Full | Function calling, Assistants API for subagents |
| Mistral / Vibe | Full | Tool calling, script execution |
| Gemini (Google) | Full | Extensions, Vertex AI |
| Hermes (Nous) | Full | Tool-use fine-tuned |
| GitHub Copilot | Partial | Code-focused; use external scheduler for trading loop |
| Any LLM + tools | Full | All scripts are pure Python, provider-independent |

## Free-First Strategy

| Tier | Cost | Stack | When to Use |
|---|---|---|---|
| **Tier 0** | $0/mo | yfinance, Polymarket public API, computed indicators | Validation and paper trading |
| **Tier 1** | $0-20/mo | + Alpha Vantage, The Odds API free tier | Live micro-trading ($50-100) |
| **Tier 2** | $20-75/mo | + Polygon.io, premium data feeds | Proven profitability, scaling up |
| **Tier 3** | $75+/mo | + Co-located execution, websocket feeds | High-frequency, >$5K bankroll |

Escalation rule: Never upgrade until current tier generates 3x the next tier's cost in weekly profit.

See [references/free-first-strategy.md](references/free-first-strategy.md) for full alternatives and upgrade matrix.

## Core Stack

| Component | Role | Cost | Free Alternative |
|---|---|---|---|
| yfinance | Stock/crypto price data | $0 | N/A (already free) |
| Polymarket Gamma API | Prediction market data | $0 | N/A (already free) |
| Kalshi API | Prediction market trading | $0 | N/A (free API) |
| Coinbase Smart Wallet | On-chain execution | $0 (gas sponsored) | Private key wallet |
| Sofascore | Sports odds de-vigging | $0 | Manual odds collection |
| Telegram Bot API | Alerts and monitoring | $0 | Console logging |
| SQLite | Trade/analytics storage | $0 | JSONL files |

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                   BOOTSTRAP LAYER (One-Time)                     │
│  ┌──────────┐ ┌──────────────┐ ┌────────────┐ ┌─────────────┐  │
│  │ Account  │ │ API Key      │ │ Wallet     │ │ Config      │  │
│  │ Creator  │ │ Generator    │ │ Deployer   │ │ Validator   │  │
│  └──────────┘ └──────────────┘ └────────────┘ └─────────────┘  │
└──────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                   ANALYST TEAM (Per Opportunity)                 │
│  ┌────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │Fundamental │ │Technical │ │Sentiment │ │ News / Catalyst  │ │
│  │  Analyst   │ │ Analyst  │ │ Analyst  │ │    Analyst       │ │
│  └─────┬──────┘ └────┬─────┘ └────┬─────┘ └────────┬─────────┘ │
│        └─────────────┴────────────┴────────────────┘            │
│                            │                                     │
│                            ▼                                     │
│              ┌──────────────────────────┐                       │
│              │  Bull/Bear Debate Engine │                       │
│              └──────────────────────────┘                       │
└──────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                   DECISION & SIZING ENGINE                       │
│  ┌──────────────┐ ┌──────────────┐ ┌─────────────────────────┐ │
│  │ Edge Calc    │ │ Kelly Sizer  │ │ Correlation Filter      │ │
│  │ (true prob   │ │ (quarter-K,  │ │ (max 3 correlated,      │ │
│  │  vs market)  │ │  hard caps)  │ │  portfolio heat check)  │ │
│  └──────────────┘ └──────────────┘ └─────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                    EXECUTION LAYER                               │
│  ┌────────────┐ ┌────────────────┐ ┌─────────────────────────┐ │
│  │ Polymarket │ │ Kalshi         │ │ CEX/DEX (Hyperliquid,   │ │
│  │ (CLOB API) │ │ (RSA-PSS Auth) │ │  dYdX, GMX)            │ │
│  └────────────┘ └────────────────┘ └─────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                  SAFETY NET LAYER (Always Active)                 │
│  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Circuit  │ │ Drawdown  │ │ Position │ │ Emergency        │ │
│  │ Breaker  │ │ Guardian  │ │ Limiter  │ │ Kill Switch      │ │
│  └──────────┘ └───────────┘ └──────────┘ └──────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

## Strategy Analysis: The Core Edge

### Information Scale

By processing news, signals, and data at scale no retail trader can match manually, you gain an information advantage.

**Sources to scan (in order of freshness):**
1. **Serper (Google News)** — fresher than Brave for breaking news
2. **X/Twitter** — breaking news, political signals, sentiment
3. **Polymarket** — prediction market odds shifts >10% = tradeable signal
4. **Reddit** — r/wallstreetbets (meme/sentiment), r/stocks, r/cryptocurrency
5. **SCMP / FT** — Asia/China macro, Taiwan, trade war signals

**What to look for:**
- Geopolitical shifts (wars, sanctions, tariffs, elections)
- Fed signals (rate decisions, Powell tone, PCE/CPI surprises)
- Earnings surprises + guidance beats/misses
- Social media viral moments (meme stocks, crypto pumps)
- Policy announcements with clear market impact

### Next Wave Mindset

**Don't chase what's already high. Find what's NEXT.**

By the time CNBC is talking about it, the easy money is gone.

**The 3-Act Framework:**
```
Act 1 — Early: Ignored, boring, hated. Smart money quietly accumulating.
Act 2 — Mid:   CNBC coverage, analyst upgrades, retail arrives. Good but crowded.
Act 3 — Late:  Euphoria, everyone knows. Risk/reward terrible. AVOID.
```

**How to Find Act 1:**
- What does the current hot sector **depend on upstream**? (AI → power → cooling → rare earth)
- What gets **built because of** the trend? (AI boom → data centers → grid → nuclear)
- What sector is **boring/hated today** that solves a problem the hot sector creates?
- What did **Buffett/sovereign funds/insiders** quietly buy 6-12 months ago?

### Entry Signals

- Breaking news with clear, direct market impact
- Polymarket odds shift >10% on a tradeable event
- Earnings surprise + guidance beat
- Policy announcement (tariffs, sanctions, rate changes)
- Social media momentum building (not after it's viral)

### Position Types

- **News trade** — quick in/out, hours to 1 day
- **Macro bet** — hold weeks/months on a policy theme
- **Earnings play** — pre/post earnings momentum
- **Next wave** — early position, hold until Act 2 begins

---

## Workflow: Self-Bootstrap

One-command setup that creates all accounts, obtains API keys, funds wallets, and validates the system.

```bash
python3 scripts/bootstrap.py setup --dry-run    # Preview
python3 scripts/bootstrap.py setup              # Full setup
python3 scripts/bootstrap.py status             # Check readiness
```

The bootstrap script:
1. Creates `~/.autonomous-trading-system/` state directory
2. Guides through API key acquisition for each platform (Kalshi, Polymarket, exchanges)
3. Generates or imports wallet keys (Smart Wallet or private key)
4. Writes validated `config.json` with all credentials
5. Runs connectivity tests against every API endpoint
6. Initializes paper trading mode by default (live requires explicit `--mode live`)

See [references/bootstrap-guide.md](references/bootstrap-guide.md) for platform-specific signup flows and key generation.

## Workflow: Autonomous Trading Loop

The core loop runs continuously, scanning for opportunities and executing trades.

```bash
python3 scripts/trading_engine.py start --mode paper   # Paper trading
python3 scripts/trading_engine.py start --mode live     # Live trading
python3 scripts/trading_engine.py status                # Current state
python3 scripts/trading_engine.py stop                  # Graceful shutdown
```

### Loop Cycle (every 5 minutes)

1. **Scan** — Pull markets from all enabled platforms (Polymarket, Kalshi, exchanges)
2. **Filter** — Apply minimum volume, edge, and liquidity thresholds
3. **Analyze** — Dispatch multi-agent analysis on top candidates (4 analysts + debate)
4. **Size** — Calculate position via adaptive Kelly criterion
5. **Safety Check** — Verify against all safety nets before execution
6. **Execute** — Place orders via platform APIs
7. **Monitor** — Track open positions, update stop-losses, check exit conditions
8. **Log** — Record everything to analytics JSONL

See [references/trading-loop-guide.md](references/trading-loop-guide.md) for the full loop specification.

## Workflow: Profit Strategy

The daily target is pursued through volume and edge stacking, not reckless sizing.

**Strategy**: Execute 15-40 trades/day across multiple platforms with 1-5% edge per trade, compounding winners.

| Lever | Mechanism | Contribution |
|---|---|---|
| Math arbitrage | Probability sum gaps on prediction markets | 3-7% per arb |
| Cross-market arb | Same event, different platform prices | 2-5% per arb |
| Momentum scalps | Technical breakouts on crypto/stocks | 1-3% per trade |
| News catalysts | Fast reaction to breaking events | 2-10% per trade |
| De-vig edge | Sports odds vs Kalshi prices | 4-15% per trade |
| Compound effect | Reinvest profits intra-day | Multiplicative |

**Safety constraint**: The target is an *aspiration*, not a mandate. The system never compromises safety rules to chase the target. If the market doesn't offer edge, the system sits in cash.

See [references/profit-strategy.md](references/profit-strategy.md) for the full strategy breakdown.

## Safety Net Architecture

The system enforces 6 layers of protection that cannot be overridden by the trading logic.

| Layer | Rule | Action on Breach |
|---|---|---|
| **Circuit Breaker** | Daily loss > 10% of starting bankroll | Halt all trading for 24h |
| **Drawdown Guardian** | Peak-to-trough > 20% | Reduce position sizes by 50%, alert |
| **Position Limiter** | No single position > 12% of bankroll | Reject oversized orders |
| **Correlation Filter** | Max 3 correlated positions | Block new correlated trades |
| **Velocity Guard** | Max 5 trades in 10 minutes | Throttle to prevent panic trading |
| **Emergency Kill Switch** | Manual trigger or 3 consecutive losses > 5% each | Close all positions, halt |

```python
# Safety nets are checked BEFORE every trade — non-negotiable
def pre_trade_safety_check(trade, portfolio, config):
    checks = [
        check_daily_loss_limit(portfolio, config),
        check_drawdown_guardian(portfolio, config),
        check_position_size(trade, portfolio, config),
        check_correlation_limit(trade, portfolio, config),
        check_velocity_guard(portfolio, config),
        check_kill_switch(config),
    ]
    if not all(c.passed for c in checks):
        log_blocked_trade(trade, checks)
        return False
    return True
```

See [references/risk-management.md](references/risk-management.md) for the full safety specification.

## Risk Management Rules

| Rule | Value | Rationale |
|------|-------|-----------|
| Max position size | 15% bankroll | Single bet risk limit |
| Min edge | 4% | Cover fees + margin of error |
| Kelly fraction | 25% | Conservative sizing |
| Daily loss limit | 10% bankroll | Stop trading after bad day |
| Correlation limit | 3 | Max correlated positions |
| Max drawdown | 20% | Reduce sizing when losing |

---

## Scripts

| Script | Purpose |
|---|---|
| `scripts/bootstrap.py` | Self-registration: account creation, API key setup, wallet deployment, config validation |
| `scripts/trading_engine.py` | Core autonomous trading loop with multi-agent analysis and execution |
| `scripts/safety_net.py` | Risk management engine: circuit breakers, drawdown guards, kill switch |
| `scripts/analytics.py` | Performance tracking, P&L reporting, trade journal, daily/weekly summaries |

## Enforced Output Statistics

Every operation MUST conclude with a structured statistics block:

```json
{
  "operation": "trade_cycle | scan | analysis | execution | safety_check",
  "timestamp": "ISO8601",
  "cycle_id": "uuid",
  "status": "success | blocked | partial | failed",
  "duration_seconds": 0.0,
  "inputs": {"markets_scanned": 0, "candidates_found": 0},
  "outputs": {"trades_executed": 0, "positions_opened": 0, "positions_closed": 0},
  "pnl": {"realized": 0.0, "unrealized": 0.0, "daily_total": 0.0, "daily_pct": 0.0},
  "risk": {"current_exposure_pct": 0.0, "daily_loss_pct": 0.0, "safety_blocks": 0},
  "errors": [],
  "cost": {"tier": 0, "amount_usd": 0.0, "gas_fees": 0.0}
}
```

**Enforcement**: Statistics output is non-negotiable. Every cycle logs to `analytics/run_stats.jsonl`. If data is unavailable, use `[pending]` markers.

| Report | Frequency | Content |
|---|---|---|
| **Per-Cycle** | Every 5 minutes | Scan results, trades, P&L delta |
| **Hourly Digest** | Every hour | Cumulative P&L, open positions, safety status |
| **Daily Summary** | End of day | Full P&L, trade journal, win rate, edge realized vs expected |
| **Weekly Review** | Weekly | WoW trends, strategy performance, risk assessment, tier review |

## Error Handling

| Error Type | Response |
|---|---|
| API timeout / network | Retry 3x with exponential backoff (2s, 4s, 8s) |
| Auth failure (expired key) | Attempt key refresh, alert via Telegram, pause platform |
| Rate limiting (429) | Respect Retry-After, queue for next window |
| Insufficient funds | Block new trades, alert, continue monitoring existing |
| Execution failure (slippage) | Cancel order, recalculate, retry at new price or skip |
| Partial fill | Accept partial, adjust position tracking |
| Platform outage | Failover to alternate platforms, queue for retry |

See [references/error-handling.md](references/error-handling.md) for the full error catalog and recovery procedures.

## Enhancement Hooks

| Skill | Enhancement | When to Add |
|---|---|---|
| `playwright-cli` | Browser automation for account self-registration | During bootstrap if APIs unavailable |
| `html-report` | Visual P&L dashboards and analytics reports | When generating daily/weekly reports |
| `xlsx` | Spreadsheet export for trade journals | When data needs external analysis |
| `technical-analysis` | Deep chart analysis for entry/exit signals | During momentum trading |
| `sentiment-analyst` | Market mood and positioning analysis | During sentiment scanning |
| `news-briefing` | Breaking news detection and reaction | During catalyst trading |
| `market-intel` | On-chain whale/institution tracking | During crypto trading |
| `mulerun-computer-schedule` | Persistent 24/7 trading loop on VM | For always-on autonomous operation |
| `mulerun-session` | Parallel subagent spawning for multi-market analysis | When analyzing >10 candidates simultaneously |

## Key References

- **Account creation, API keys, wallet setup**: [references/bootstrap-guide.md](references/bootstrap-guide.md) — Read during initial setup
- **Full trading loop specification and cycle details**: [references/trading-loop-guide.md](references/trading-loop-guide.md) — Read when understanding or modifying the loop
- **Daily target strategy and trade selection**: [references/profit-strategy.md](references/profit-strategy.md) — Read when reviewing profit approach
- **Safety nets, circuit breakers, kill switch**: [references/risk-management.md](references/risk-management.md) — Read when reviewing risk controls
- **Error catalog and recovery procedures**: [references/error-handling.md](references/error-handling.md) — Read when handling failures
- **Cost tiers and free alternatives**: [references/free-first-strategy.md](references/free-first-strategy.md) — Read during setup or cost review
- **Platform API reference (Polymarket, Kalshi, exchanges)**: [references/platform-apis.md](references/platform-apis.md) — Read when integrating or debugging platform calls

## Communication Rules

- **Morning report only** — don't ping mid-day
- **Exception:** Alert immediately if >5% swing on any position
- Keep reports tight
- Document every trade: thesis, outcome, lesson learned
