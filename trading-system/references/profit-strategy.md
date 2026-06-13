# Profit Strategy — Targeting 25% Daily Returns

How the system pursues aggressive daily returns while maintaining capital preservation as the non-negotiable constraint.

## Table of Contents

1. [Strategy Philosophy](#strategy-philosophy)
2. [Edge Sources](#edge-sources)
3. [Compounding Mechanics](#compounding-mechanics)
4. [Daily Execution Plan](#daily-execution-plan)
5. [Realistic Expectations](#realistic-expectations)
6. [Strategy Selection Matrix](#strategy-selection-matrix)

---

## Strategy Philosophy

The 25% daily target is pursued through **volume and edge stacking**, not through oversized positions or excessive leverage. The system executes many small-edge trades that compound throughout the day.

**Core principle**: 25% is an *aspiration ceiling*, not a *mandate floor*. If the market doesn't offer edge, the system sits in cash. Capital preservation always wins.

```
Daily Target: 25% of starting bankroll

Achievable through:
  15-40 trades/day × 1-5% edge per trade × compounding
  = Cumulative return potential of 15-75% (theoretical max)
  = Realized return of 5-25% after fees, slippage, and losses
```

## Edge Sources

### Source 1: Math Arbitrage (Prediction Markets)

**Expected edge**: 3-7% per trade (after fees)
**Frequency**: 2-5 opportunities per day on Polymarket
**Risk**: Very low (structural guarantee if executable)

```
Example:
  Event: "Who wins the election?" (3 candidates)
  Prices: Candidate A: 45%, B: 35%, C: 15%
  Sum: 95% → Buy all three for 95¢, guaranteed $1 payout
  Gross edge: 5%
  After fees (2% × 3 legs = 6%): Net edge = -1%  ← NOT profitable with 3 legs

  Better: 2-outcome market
  Prices: Yes: 48%, No: 45%
  Sum: 93%
  After fees (2% × 2 legs = 4%): Net edge = 3%  ← Profitable
```

**Key insight**: Only trade math arbs on 2-outcome markets where net edge > 3% after fees.

### Source 2: Cross-Market Arbitrage

**Expected edge**: 2-5% per trade
**Frequency**: 1-3 opportunities per day
**Risk**: Low-medium (execution timing risk)

Same event priced differently across platforms:
- Polymarket vs Kalshi
- Different Polymarket markets covering the same event
- Prediction market vs bookmaker odds

### Source 3: Momentum Scalps (Crypto/Stocks)

**Expected edge**: 1-3% per trade
**Frequency**: 5-15 opportunities per day
**Risk**: Medium (requires good entry/exit timing)

Technical breakout patterns:
- RSI divergence entries
- MACD crossover signals
- Bollinger band mean reversion
- Support/resistance breakouts

### Source 4: News Catalyst Trading

**Expected edge**: 2-10% per trade
**Frequency**: 1-5 opportunities per day
**Risk**: Medium-high (information speed critical)

Fast reaction to breaking events:
- Earnings surprises
- Political announcements
- Sports results (before prediction markets update)
- Regulatory decisions

### Source 5: De-Vig Edge (Sports/Events)

**Expected edge**: 4-15% per trade
**Frequency**: 3-10 opportunities per day (seasonal)
**Risk**: Medium (true probability estimation uncertainty)

```
Bookmaker odds: Team A 1.50, Team B 2.80
Implied: A = 66.7%, B = 35.7%, Total = 102.4%
De-vigged: A = 65.1%, B = 34.9%

Kalshi price: Team A at 58¢
Edge: 65.1% - 58% = 7.1%  ← Strong edge
```

**Best edge sources** (from battle-tested experience):
- Tennis qualifying/challengers: 5-40% EV gaps
- NCAAB small conference tournaments: 4-9% EV
- Weather markets: high variance but NWS data provides edge

## Compounding Mechanics

The 25% target benefits from intra-day compounding:

```
Starting bankroll: $1,000
Trade 1: $100 position, 3% edge → +$3 → Bankroll: $1,003
Trade 2: $100 position, 4% edge → +$4 → Bankroll: $1,007
Trade 3: $120 position, 5% edge → +$6 → Bankroll: $1,013
...
Trade 20: $150 position, 3% edge → +$4.50
...

After 30 trades with avg 3% realized edge and avg $120 position:
Cumulative P&L ≈ $108 → 10.8% daily return
```

**Compounding rule**: After every 5 winning trades, recalculate bankroll for Kelly sizing using the updated balance. This lets winners compound without requiring a winning streak.

## Daily Execution Plan

| Hour (UTC) | Activity | Target Trades |
|---|---|---|
| 00:00-06:00 | Asian session: crypto momentum, overnight arbs | 3-5 |
| 06:00-08:00 | EU open: scan prediction markets, sports events | 2-4 |
| 08:00-14:00 | Peak hours: arb scanning, de-vig sports, news catalysts | 8-15 |
| 14:00-20:00 | US session: Kalshi markets, US sports, earnings | 5-10 |
| 20:00-24:00 | Evening: close positions, scan overnight setups | 2-5 |

**Total target**: 20-40 trades/day

## Realistic Expectations

| Scenario | Daily Trades | Avg Edge | Win Rate | Daily Return |
|---|---|---|---|---|
| **Excellent day** | 35+ | 4%+ | 70%+ | 15-25%+ |
| **Good day** | 20-35 | 3-4% | 60-70% | 8-15% |
| **Average day** | 10-20 | 2-3% | 55-65% | 3-8% |
| **Poor day** | 5-10 | 1-2% | 45-55% | -2% to 3% |
| **Bad day** | <5 | <1% | <50% | -5% to -2% |

**Important**: The 25% target is achievable on excellent days but should not be expected daily. The system design accepts that many days will produce 5-15% returns, and some days will be negative. The safety nets ensure that bad days never exceed 10% loss.

## Strategy Selection Matrix

| Market Condition | Primary Strategy | Secondary | Avoid |
|---|---|---|---|
| **High volatility** | Momentum scalps | News catalysts | Math arbs (data stale) |
| **Low volatility** | Math arbs | De-vig sports | Momentum (no movement) |
| **Trending** | Momentum + breakouts | News catalysts | Mean reversion |
| **Ranging** | Math arbs + mean reversion | De-vig | Momentum |
| **High volume** | All strategies | — | — |
| **Low volume** | Math arbs only | Skip thin markets | Momentum (slippage) |
| **Weekend** | Sports de-vig | Crypto momentum | Stock-based strategies |
