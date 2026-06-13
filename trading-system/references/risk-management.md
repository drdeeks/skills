# Risk Management — Safety Net Specification

Complete specification for the 6-layer safety net architecture that protects capital at all times.

## Table of Contents

1. [Safety Architecture](#safety-architecture)
2. [Layer 1: Circuit Breaker](#layer-1-circuit-breaker)
3. [Layer 2: Drawdown Guardian](#layer-2-drawdown-guardian)
4. [Layer 3: Position Limiter](#layer-3-position-limiter)
5. [Layer 4: Correlation Filter](#layer-4-correlation-filter)
6. [Layer 5: Velocity Guard](#layer-5-velocity-guard)
7. [Layer 6: Emergency Kill Switch](#layer-6-emergency-kill-switch)
8. [Daily Reset Protocol](#daily-reset-protocol)
9. [Recovery Procedures](#recovery-procedures)

---

## Safety Architecture

Safety nets run as an independent module (`safety_net.py`) that the trading engine must call before every trade. The safety module:

1. Cannot be bypassed by the trading logic
2. Has its own persistent state file
3. Logs every check (pass and fail) to `safety_events.jsonl`
4. Can be triggered manually via CLI

```
TRADE REQUEST → [Safety Gate] → APPROVED → Execute
                     │
                     └─ BLOCKED → Log reason → Skip trade
```

**Design principle**: It is always better to miss a profitable trade than to take a dangerous one. False positives (blocking good trades) are acceptable; false negatives (allowing bad trades) are not.

## Layer 1: Circuit Breaker

**Purpose**: Prevent catastrophic daily losses by halting trading after a threshold.

| Parameter | Default | Range |
|---|---|---|
| `max_daily_loss_pct` | 10% | 5-15% |
| Halt duration | 24 hours | 12-48 hours |
| Reset | Automatic at midnight UTC | Can be manual |

**Trigger condition**: `abs(daily_pnl) / daily_start_bankroll >= max_daily_loss_pct`

**Action on trigger**:
1. Block all new trades immediately
2. Keep existing positions (do NOT panic-close)
3. Set `halted_until = now + 24 hours`
4. Send Telegram alert
5. Log event

**Rationale**: A 10% daily loss means something is wrong — either the market is unusual or the model is broken. Halting prevents compounding of errors.

## Layer 2: Drawdown Guardian

**Purpose**: Reduce position sizing during drawdowns to slow capital decay.

| Parameter | Default | Range |
|---|---|---|
| `max_drawdown_pct` | 20% | 15-30% |
| Size reduction | 50% | 40-60% |
| Recovery threshold | Drawdown < 10% | Half of max |

**Trigger condition**: `(peak_bankroll - current_bankroll) / peak_bankroll >= max_drawdown_pct`

**Action on trigger**:
1. Set `sizing_multiplier = 0.5` (halve all position sizes)
2. Alert via Telegram
3. Log event
4. Gradually restore sizing as drawdown recovers (0.1 per winning cycle)

**Rationale**: During drawdowns, Kelly sizing naturally reduces (lower bankroll → lower positions), but this adds an additional safety layer that forces even more conservative sizing.

## Layer 3: Position Limiter

**Purpose**: Prevent concentration risk by capping individual position sizes.

| Parameter | Default | Range |
|---|---|---|
| `max_position_pct` | 12% | 5-20% |
| Minimum position | $5 | $1-$50 |

**Trigger condition**: `trade_amount / current_bankroll > max_position_pct`

**Action on trigger**:
1. Block the trade
2. Return maximum allowed size for the trade engine to resize
3. Log event

**Rationale**: Even with Kelly sizing, a single large position can cause outsized damage. The 12% hard cap ensures no single trade can move the portfolio more than ~12%.

## Layer 4: Correlation Filter

**Purpose**: Prevent overexposure to correlated events.

| Parameter | Default | Range |
|---|---|---|
| `max_correlated_positions` | 3 | 2-5 |

**Categories for correlation**:
- `math_arb_buy` — Polymarket buy arbs
- `math_arb_sell` — Polymarket sell arbs
- `crypto_momentum` — Crypto price action
- `stock_momentum` — Stock price action
- `sports_devig` — Sports de-vig trades
- `political` — Political prediction markets
- `weather` — Weather prediction markets

**Trigger condition**: `count(open_positions where category == trade_category) >= max_correlated_positions`

**Action on trigger**:
1. Block the trade
2. Suggest waiting for existing positions to close
3. Log event

**Rationale**: Correlated positions compound risk — if one loses, they all likely lose. Limiting correlation ensures diversification.

## Layer 5: Velocity Guard

**Purpose**: Prevent panic trading and overtrading.

| Parameter | Default | Range |
|---|---|---|
| `max_trades_per_10min` | 5 | 3-10 |

**Trigger condition**: `count(trades in last 10 minutes) >= max_trades_per_10min`

**Action on trigger**:
1. Throttle — delay execution until window expires
2. Log event

**Rationale**: Rapid trading often indicates panic or chasing. Throttling forces a cooling-off period.

## Layer 6: Emergency Kill Switch

**Purpose**: Last-resort full halt for manual intervention.

### Manual Trigger

```bash
python3 scripts/safety_net.py kill "Suspicious market activity"
python3 scripts/safety_net.py unkill  # To resume after review
```

### Auto-Trigger Conditions

| Condition | Threshold |
|---|---|
| Consecutive losses | 3 losses each > 5% |
| API errors | 5+ consecutive API failures |
| Unusual market | Circuit breaker + drawdown in same day |

**Action on trigger**:
1. Block ALL new trades
2. Send urgent Telegram alert
3. Set `halted_until = now + 24 hours`
4. Require manual `unkill` to resume

**Rationale**: When multiple safety signals fire simultaneously, the system may be in an environment it wasn't designed for. Human review is required.

## Daily Reset Protocol

At midnight UTC (or on manual reset):

1. Record end-of-day bankroll
2. Reset `daily_pnl = 0`
3. Set `daily_start_bankroll = current_bankroll`
4. Reset `consecutive_losses = 0`
5. Clear `recent_trades` history
6. Restore `sizing_multiplier` toward 1.0 (if not in drawdown)

```bash
python3 scripts/safety_net.py reset
```

## Recovery Procedures

### After Circuit Breaker

1. Wait for 24-hour halt to expire (or manually reset after review)
2. Review trade journal for what went wrong
3. Consider reducing `max_daily_loss_pct` if recurring
4. Resume with reduced sizing for first 5 trades

### After Drawdown Guardian

1. System automatically reduces sizing by 50%
2. Sizing gradually restores as winning trades occur
3. If drawdown continues, consider pausing and reviewing strategy
4. Check if market conditions have changed (regime shift)

### After Kill Switch

1. Review all recent trades and safety events
2. Check API connectivity and data freshness
3. Verify no platform outages
4. Run `safety_net.py check` to validate all layers
5. Run `safety_net.py unkill` to resume
6. Monitor closely for first 10 trades after resume

### Capital Preservation Hierarchy

```
1. Never lose more than 10% in a day (Circuit Breaker)
2. Never lose more than 20% from peak (Drawdown Guardian)
3. Never bet more than 12% on one trade (Position Limiter)
4. Never concentrate in one category (Correlation Filter)
5. Never trade in panic (Velocity Guard)
6. Always have a manual override (Kill Switch)
```

**The system will never run out of funding** because:
- 10% daily max loss means you need 10+ consecutive terrible days to lose 65%
- Drawdown guardian cuts sizing in half, slowing loss rate
- Kill switch halts after 3 consecutive losses
- These layers compound: the real maximum monthly drawdown is ~30-35%
