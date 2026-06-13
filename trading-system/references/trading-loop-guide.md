# Trading Loop Guide — Full Cycle Specification

Detailed specification for the autonomous trading loop, including each phase, timing, and decision logic.

## Table of Contents

1. [Loop Architecture](#loop-architecture)
2. [Phase 1: Market Scanning](#phase-1-market-scanning)
3. [Phase 2: Candidate Filtering](#phase-2-candidate-filtering)
4. [Phase 3: Multi-Agent Analysis](#phase-3-multi-agent-analysis)
5. [Phase 4: Position Sizing](#phase-4-position-sizing)
6. [Phase 5: Safety Gate](#phase-5-safety-gate)
7. [Phase 6: Execution](#phase-6-execution)
8. [Phase 7: Position Monitoring](#phase-7-position-monitoring)
9. [Phase 8: Logging & Analytics](#phase-8-logging--analytics)
10. [Adaptive Parameters](#adaptive-parameters)

---

## Loop Architecture

```
┌─────────────────────────────────────────────────────┐
│                 MAIN LOOP (every 5 min)             │
│                                                      │
│  ┌──────┐  ┌────────┐  ┌─────────┐  ┌──────────┐  │
│  │ SCAN │→ │ FILTER │→ │ ANALYZE │→ │   SIZE   │  │
│  └──────┘  └────────┘  └─────────┘  └──────────┘  │
│                                           │          │
│                                           ▼          │
│  ┌──────┐  ┌─────────┐  ┌─────────┐  ┌──────┐     │
│  │ LOG  │← │ MONITOR │← │ EXECUTE │← │SAFETY│     │
│  └──────┘  └─────────┘  └─────────┘  └──────┘     │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**Cycle frequency**: Default 300 seconds (5 minutes). Adaptive — can increase to 60s during high-activity periods.

**Concurrency**: Market scanning runs in parallel across platforms. Analysis runs sequentially per candidate to manage API load.

## Phase 1: Market Scanning

Scan all enabled platforms simultaneously for active markets.

### Polymarket Scanner

```python
# Gamma API: public, no auth, generous rate limits
GET https://gamma-api.polymarket.com/markets?limit=100&active=true&closed=false

# Parse response:
# - Extract outcomePrices (double-encoded JSON → parse twice)
# - Calculate prob_sum = sum of all outcome prices
# - Flag math arbs: prob_sum < 0.96 (buy arb) or > 1.04 (sell arb)
# - Record volume, question, conditionId, clobTokenIds
```

### Kalshi Scanner

```python
# Public events endpoint
GET https://trading-api.kalshi.com/trade-api/v2/events?limit=100&status=open

# Parse response:
# - Extract yes_bid/no_bid prices per market
# - Compare to de-vigged bookmaker odds (Sofascore, Odds API)
# - Calculate edge = true_probability - kalshi_price
```

### Output

Each scanner returns a list of market objects with standardized fields:
- `platform`, `market_id`, `question`, `prices`, `volume`, `edge`, `arb_type`

## Phase 2: Candidate Filtering

Apply minimum thresholds to reduce noise:

| Filter | Threshold | Rationale |
|---|---|---|
| Minimum volume | $100,000 | Liquidity — avoid thin markets |
| Minimum edge | 2% (half of trading threshold) | Pre-filter for analysis |
| Active status | Must be open/active | No expired markets |
| Time to expiry | >2 hours | Avoid last-minute volatility |

**Output**: Sorted list of candidates by edge (descending), capped at top 20 for analysis.

## Phase 3: Multi-Agent Analysis

Each candidate is analyzed by 4 specialist agents, followed by a bull/bear debate.

### Agent 1: Fundamental Analyst

Evaluates the structural basis of the opportunity:
- **Math arbs**: Validates probability sum, checks for data staleness
- **Prediction markets**: Assesses event fundamentals, base rates
- **Crypto/stocks**: Reviews financial metrics, on-chain data

**Output**: Score 0-1, reasoning text

### Agent 2: Technical Analyst

Evaluates price action and market microstructure:
- Price momentum and trend
- Bid-ask spread analysis
- Volume profile (increasing/decreasing)
- Order book depth (if available)

**Output**: Score 0-1, reasoning text

### Agent 3: Sentiment Analyst

Evaluates crowd positioning and mood:
- Volume as sentiment proxy
- Open interest changes
- Social media mentions (if available)
- Historical pattern of similar events

**Output**: Score 0-1, reasoning text

### Agent 4: News/Catalyst Analyst

Evaluates information edge:
- Recent news related to the event
- Upcoming catalysts (earnings, votes, matches)
- Information asymmetry potential
- Time-sensitivity of the opportunity

**Output**: Score 0-1, reasoning text

### Bull/Bear Debate Engine

After all 4 agents report, synthesize via adversarial debate:

```python
avg_score = mean(fundamental, technical, sentiment, news)

bull_case = aggregate positive signals + quantify edge
bear_case = aggregate risks + identify failure modes

# Winner determined by weighted average:
#   fundamental: 30% weight (structural edge matters most)
#   technical:   25% weight
#   sentiment:   20% weight
#   news:        25% weight

weighted_score = (fund * 0.30 + tech * 0.25 + sent * 0.20 + news * 0.25)
winner = "bull" if weighted_score > 0.55 else "bear"
```

**Output**: BUY / WATCH / SKIP recommendation with confidence score.

## Phase 4: Position Sizing

For BUY recommendations, calculate position size using adaptive Kelly criterion.

### Quarter-Kelly Formula

```python
edge = true_probability - market_price
odds = (1 / market_price) - 1
kelly_pct = (true_prob * odds - (1 - true_prob)) / odds
position_pct = kelly_pct * 0.25  # Quarter-Kelly

# Apply constraints:
position_pct = min(position_pct, max_position_pct)  # Hard cap at 12%
position_pct *= sizing_multiplier  # Drawdown adjustment (0.5-1.0)
position_size = position_pct * current_bankroll
position_size = max(position_size, min_position)  # Minimum $5
```

### Position Sizing for Arbs

For math arbs (buying all outcomes), split allocation by odds:

```python
# For 2-outcome arb with prices p1, p2 where p1 + p2 < 1.0:
weight_1 = (1/p1) / ((1/p1) + (1/p2))
weight_2 = (1/p2) / ((1/p1) + (1/p2))
amount_1 = total_position * weight_1
amount_2 = total_position * weight_2
```

## Phase 5: Safety Gate

Every trade passes through all 6 safety layers before execution. See [risk-management.md](risk-management.md) for the full specification.

**This gate is non-bypassable** — the safety net code runs independently from the trading logic and cannot be overridden.

## Phase 6: Execution

### Paper Mode

Simulate execution with realistic assumptions:
- Fill at displayed price (optimistic)
- Apply 2% taker fee estimate
- Record simulated P&L at 70% of theoretical edge (conservative)

### Live Mode

Platform-specific order placement:
- **Polymarket**: EIP-712 signed limit order via CLOB API
- **Kalshi**: RSA-PSS authenticated REST order
- **Hyperliquid**: Signed transaction via L1 API

All orders placed as **limit orders** (not market orders) to control slippage.

## Phase 7: Position Monitoring

Between cycles, monitor open positions:
- Check for filled/partially filled orders
- Update unrealized P&L
- Check stop-loss conditions
- Monitor for market resolution (prediction markets)

## Phase 8: Logging & Analytics

Every cycle generates a structured statistics record appended to `analytics/run_stats.jsonl`. See SKILL.md for the output format specification.

## Adaptive Parameters

The loop self-adjusts based on performance:

| Parameter | Default | Adaptation Rule |
|---|---|---|
| Scan interval | 300s | Decrease to 60s during high-edge periods |
| Min edge | 4% | Increase to 6% after losses, decrease to 3% during low-activity |
| Kelly fraction | 25% | Reduce to 15% during drawdown, increase to 30% during winning streaks |
| Max daily trades | 40 | Reduce after consecutive losses |
| Sizing multiplier | 1.0 | Set to 0.5 by drawdown guardian |
