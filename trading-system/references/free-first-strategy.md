# Free-First Strategy — Cost Tiers & Alternatives

Zero-cost path for the autonomous trading system. Every paid component has a free alternative documented.

## Table of Contents

1. [Free Alternatives Table](#free-alternatives-table)
2. [Cost Tier Ladder](#cost-tier-ladder)
3. [Upgrade Decision Matrix](#upgrade-decision-matrix)
4. [Config Toggle](#config-toggle)
5. [Cost Tracking](#cost-tracking)

---

## Free Alternatives Table

| Component | Paid Option | Cost | Free Alternative | Trade-offs |
|---|---|---|---|---|
| Stock prices | Polygon.io | $29/mo | yfinance | 15-min delay, less reliability |
| Crypto prices | CoinGecko Pro | $129/mo | CoinGecko free API | Rate limited (30/min) |
| Prediction markets | — | $0 | Polymarket Gamma API | Already free |
| Sports odds | The Odds API | $20/mo | Sofascore scraping | Fewer sports, slower updates |
| Technical indicators | TradingView | $15/mo | Computed from price data | Requires implementation |
| News feed | NewsAPI | $449/mo | yfinance news + free RSS | Less coverage, slower |
| Alerts | Telegram Premium | — | Telegram Bot API | Already free |
| Execution | — | Gas fees | Smart Wallet (paymaster) | Gas sponsored on Base |
| Storage | Cloud DB | $10/mo | Local JSONL files | Single-machine only |
| Monitoring | Datadog | $15/mo | Console + JSONL logs | No web dashboard |

## Cost Tier Ladder

### Tier 0: $0/month — Validation Phase

**Stack**: yfinance + Polymarket Gamma API + computed indicators + JSONL storage + Telegram alerts

**Capabilities**:
- Full prediction market scanning (Polymarket)
- Stock/crypto price analysis
- Paper trading with full analytics
- All safety nets active
- Console + Telegram monitoring

**Limitations**:
- 15-minute delayed stock prices
- No Kalshi trading (read-only until API key)
- Rate limited on some data sources
- Single machine operation

**When to use**: Starting out, learning the system, validating that the strategy works in paper trading.

### Tier 1: $0-20/month — Live Micro-Trading

**Stack**: Tier 0 + The Odds API free tier ($0-20) + Kalshi account

**Added capabilities**:
- Sports de-vigging with real bookmaker odds
- Kalshi trading (after account approval)
- Better edge calculation on sports events

**Upgrade trigger**: Paper trading profitable for 2+ weeks with 60%+ win rate.

### Tier 2: $20-75/month — Scaling Up

**Stack**: Tier 1 + Polygon.io ($29) + CoinGecko Pro (optional)

**Added capabilities**:
- Real-time stock/crypto prices
- Higher API rate limits
- Better data reliability

**Upgrade trigger**: Live trading profitable for 1+ months, bankroll > $500, monthly profit covers cost with 3x margin.

### Tier 3: $75+/month — Full Scale

**Stack**: Tier 2 + dedicated VPS ($20-50) + premium data feeds

**Added capabilities**:
- 24/7 autonomous operation
- Low-latency execution
- Multiple simultaneous strategies

**Upgrade trigger**: Consistent profitability, bankroll > $2,000, demonstrable ROI.

## Upgrade Decision Matrix

| Metric | Stay at Free | Evaluate Upgrade | Upgrade |
|---|---|---|---|
| Weekly profit | <$10 | $10-50 | >$50 |
| Win rate | <55% | 55-65% | >65% |
| Missed opportunities (data delay) | <2/week | 2-5/week | >5/week |
| Time managing free tools | <15min/day | 15-30min/day | >30min/day |
| Bankroll | <$200 | $200-1000 | >$1000 |

**Golden rule**: Never upgrade until current tier's weekly profit exceeds the next tier's monthly cost by at least 3x.

## Config Toggle

Backend selection via config:

```json
{
    "data_backends": {
        "stock_prices": "yfinance",
        "crypto_prices": "coingecko_free",
        "sports_odds": "sofascore",
        "news": "yfinance_news"
    },
    "cost_tier": 0
}
```

Switching backends requires only changing the config value — no code changes. Each backend implements the same interface.

## Cost Tracking

Every analytics report includes a cost section:

```json
{
    "cost": {
        "tier": 0,
        "amount_usd": 0.0,
        "breakdown": {
            "data_feeds": 0.0,
            "gas_fees": 0.0,
            "platform_fees": 0.0
        },
        "monthly_projection": 0.0,
        "roi_ratio": "N/A"
    }
}
```

Weekly reports include:
- Total cost for the week
- Revenue generated
- ROI ratio (revenue / cost)
- Recommendation: hold tier, upgrade, or downgrade
