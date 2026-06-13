# Argus Edge Strategy Reference

Detailed strategy rules for prediction market betting.

## Kelly Criterion

The Kelly criterion optimizes bet sizing for maximum long-term growth:

```
f* = (bp - q) / b
```

Where:
- f* = fraction of bankroll to bet
- b = decimal odds - 1
- p = probability of winning
- q = probability of losing (1 - p)

## Edge Calculation

```
Edge = our_P(win) - market_implied_P(win)
```

Bet when:
- Edge >= 10%
- Market is fresh (< 30 min old)
- TA score >= threshold for asset
