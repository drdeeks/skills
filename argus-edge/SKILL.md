---
description: Argus-style prediction market edge detection and betting strategy. Computes
  expected value from TA-implied probability vs market odds, sizes bets via Kelly
  criterion, and applies freshness/consensus guards. Validated at 77.8% win rate on
  primary (fresh) Polymarket bets. Use for prediction market betting, EV calculation,
  Polymarket strategy, or market making.
name: argus-edge
version: 0.0.5
---

# Argus Edge — Prediction Market Betting Engine

The complete Argus strategy for finding and exploiting edge in crypto prediction markets.

## Core Formula

```
Edge = our_P(win) - market_implied_P(win)
Bet when: edge ≥ 10% AND fresh market (<30 min old) AND TA score ≥ ±2
Kelly stake = (edge × bankroll) / odds
```

## Strategy Rules

### Freshness Guard
- Skip markets >92% consensus (dead signal, L020)
- Prioritize markets <30 min old (primary window)
- Primary bets WR: 77.8% vs overall 56.6%

### Counter-Consensus Rule (L023)
TA score ≥+1 + market DOWN >80% + ≥20 min remaining → bet UP (counter-consensus has positive EV, validated at 5x+ payout)

### Asset Calibration
| Asset | TA Reliability | Bias | Min Score |
|-------|---------------|------|-----------|
| BTC | 0.75 | Neutral | ±3 |
| ETH | 0.80 | UP+0.05 | ±2 |
| SOL | 0.90 | UP+0.05 | ±1 |
| XRP | 0.70 | UP+0.08 | ±2 |

## Usage

```
Use argus-edge to find the best Polymarket bet right now

Use argus-edge to calculate edge on BTC 11am ET market

Use argus-edge for full market scan with Kelly sizing
```


## Provider Compatibility

| Provider | Compatibility | Notes |
|----------|---------------|-------|
| Claude (Anthropic) | Full | MCP servers, tool use |
| OpenAI / ChatGPT | Full | Function calling, Actions |
| Mistral / Le Chat | Full | Tool calling, script execution |
| Gemini (Google) | Full | Extensions, Vertex AI |
| Hermes (Nous) | Full | Tool-use fine-tuned |
| GitHub Copilot | Partial | Code generation; use external runner for scripts |
| Any LLM + tools | Full | Scripts are plain Python, provider-independent |


## Free-First Strategy

| Tier | Cost | Stack |
|------|------|-------|
| **Tier 0** | $0/mo | Python 3.8+ (all scripts use stdlib only) |
| **Tier 1** | $0-5/mo | + CI/CD for automated validation |
| **Tier 2** | $5-20/mo | + Hosted skill registry for team distribution |

The entire core toolchain is permanently $0.


## Enforced Output Statistics

Every script produces structured output on completion:

```json
{
  "operation": "script_name",
  "timestamp": "ISO8601",
  "status": "success | failed",
  "skill_name": "the-skill-name",
  "details": {},
  "cost": {"tier": 0, "amount_usd": 0.0, "service": "local"}
}
```


## Error Handling

| Error | Response |
|-------|----------|
| Invalid input | Validate and report with guidance |
| Missing dependency | Auto-install or report requirement |
| Network failure | Retry with exponential backoff |
| Permission denied | Report and suggest alternatives |
| Resource not found | Report with available options |


## Enhancement Hooks

| Skill | Enhancement | When to Add |
|-------|-------------|-------------|
| `skill-creator` | Basic skill creation | When creating simple skills |
| `skill-creator-pro` | Enterprise upgrade | When upgrading to enterprise |
| `html-report` | Visual validation dashboard | When auditing many skills |
| `xlsx` | Export validation results | When tracking skill quality metrics |


## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/validate.py` | argus-edge script | Run with python3 |
| `scripts/main.py` | argus-edge script | Run with python3 |

## Key References

- **Overview**: [references/overview.md](references/overview.md)
## Battle-Tested
Derived from 100+ live Polymarket bets. 25 documented lessons (L001–L025).