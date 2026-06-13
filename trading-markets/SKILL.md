---
name: trading-markets
description: "Prediction market and trading toolkit. Polymarket API querying, arbitrage detection, Kalshi integration with RSA-PSS auth, Kelly criterion sizing, wallet setup, ERC-8004 agent identity, multi-agent analysis prompts. Covers Polymarket, Kalshi, OpinionLaps, and crypto perps. Triggers: prediction market data, arbitrage detection, Kalshi trading, Kelly sizing, wallet configuration, on-chain agent identity, or multi-agent trading analysis."
license: MIT
version: 0.0.3
---

# Trading Markets — Prediction Market & Trading Toolkit

Unified toolkit for prediction market data, arbitrage detection, platform integration, and trading infrastructure. Covers Polymarket (read-only + trading), Kalshi (RSA-PSS auth), arbitrage detection and execution, Kelly criterion position sizing, wallet setup, and ERC-8004 agent identity.

## Table of Contents

- [Polymarket](#polymarket)
- [Polymarket Arbitrage](#polymarket-arbitrage)
- [Kalshi Integration](#kalshi-integration)
- [Kelly Criterion Position Sizing](#kelly-criterion-position-sizing)
- [Wallet Setup](#wallet-setup)
- [ERC-8004 Agent Identity](#erc-8004-agent-identity)
- [Multi-Agent Analysis Prompts](#multi-agent-analysis-prompts)
- [Scripts Reference](#scripts-reference)

---

## Polymarket

Query prediction market data from Polymarket using their public REST APIs. All endpoints are read-only and require zero authentication.

See [references/api-endpoints.md](references/api-endpoints.md) for the full endpoint reference with curl examples.

### When to Use

- User asks about prediction markets, betting odds, or event probabilities
- User wants to know "what are the odds of X happening?"
- User wants market prices, orderbook data, or price history
- User asks to monitor or track prediction market movements

### Key Concepts

- **Events** contain one or more **Markets** (1:many relationship)
- **Markets** are binary outcomes with Yes/No prices between 0.00 and 1.00
- Prices ARE probabilities: price 0.65 means the market thinks 65% likely
- `outcomePrices` field: JSON-encoded array like `["0.80", "0.20"]`
- `clobTokenIds` field: JSON-encoded array of two token IDs [Yes, No] for price/book queries
- `conditionId` field: hex string used for price history queries
- Volume is in USDC (US dollars)

### Three Public APIs

1. **Gamma API** at `gamma-api.polymarket.com` — Discovery, search, browsing
2. **CLOB API** at `clob.polymarket.com` — Real-time prices, orderbooks, history
3. **Data API** at `data-api.polymarket.com` — Trades, open interest

### Typical Workflow

1. **Search** using the Gamma API public-search endpoint with their query
2. **Parse** the response — extract events and their nested markets
3. **Present** market question, current prices as percentages, and volume
4. **Deep dive** if asked — use clobTokenIds for orderbook, conditionId for history

### Presenting Results

Format prices as percentages for readability:
- outcomePrices `["0.652", "0.348"]` becomes "Yes: 65.2%, No: 34.8%"
- Always show the market question and probability
- Include volume when available

Example: `"Will X happen?" — 65.2% Yes ($1.2M volume)`

### Parsing Double-Encoded Fields

The Gamma API returns `outcomePrices`, `outcomes`, and `clobTokenIds` as JSON strings inside JSON responses (double-encoded). When processing with Python, parse them with `json.loads(market['outcomePrices'])` to get the actual array.

### Rate Limits

- Gamma: 4,000 requests per 10 seconds
- CLOB: 9,000 requests per 10 seconds
- Data: 1,000 requests per 10 seconds

---

## Polymarket Arbitrage

Find and execute arbitrage opportunities on Polymarket prediction markets.

### Quick Start

```bash
# Single scan
python scripts/fetch_markets.py --output markets.json --min-volume 50000
python scripts/detect_arbitrage.py markets.json --min-edge 3.0 --output arbs.json

# Continuous monitoring
python scripts/monitor.py --interval 300 --min-edge 3.0
```

### Arbitrage Types Detected

**Math Arbitrage (Primary Focus)**

Type A: Buy All Outcomes (prob sum < 100%)
- Safest type. Guaranteed profit if executable.
- Example: 48% + 45% = 93% → 7% edge, ~5% net after fees

Type B: Sell All Outcomes (prob sum > 100%)
- Riskier (requires liquidity). Need capital to collateralize. Avoid until experienced.

**Cross-Market Arbitrage** — Same event priced differently across markets (requires semantic matching).

**Orderbook Arbitrage** — Requires real-time orderbook data (homepage shows midpoints, not executable prices).

See [references/arbitrage_types.md](references/arbitrage_types.md) for detailed examples and strategies.

### Fee Structure

Polymarket charges:
- **Maker fee:** 0%
- **Taker fee:** 2%

Conservative assumption: 2% per leg (assume taker)

**Breakeven calculation:**
- 2-outcome market: 2% × 2 = 4% gross edge needed
- 3-outcome market: 2% × 3 = 6% gross edge needed
- N-outcome market: 2% × N gross edge needed

**Target:** 3-5% NET profit (after fees)

### Risk Management

1. **Maximum position size:** 5% of bankroll per opportunity
2. **Minimum edge:** 3% net (after fees)
3. **Daily loss limit:** 10% of bankroll
4. **Focus on buy arbs:** Avoid sell-side until experienced

### Red Flags

- Edge >10% (likely stale data)
- Volume <$100k (liquidity risk)
- Probabilities recently updated (arb might close)
- Sell-side arbs (capital + liquidity requirements)

### Workflow Phases

**Phase 1: Paper Trading (1-2 weeks)** — Run monitor 2-3x/day, log opportunities, check availability.

**Phase 2: Micro Testing ($50-100)** — Manual trades only, max $5-10 per opportunity.

**Phase 3: Scale Up ($500)** — Increase bankroll, max 5% per trade ($25), still manual.

**Phase 4: Automation** — Requires wallet integration, API access, execution logic. Only after consistent manual profitability.

See [references/getting_started.md](references/getting_started.md) for detailed setup instructions.

### Execution Speed

Arbs disappear fast. If planning automation:
- Use websocket connections (not polling)
- Place limit orders simultaneously
- Have capital pre-deposited
- Monitor gas fees on Polygon

---

## Kalshi Integration

Trade prediction markets on Kalshi with edge detection, de-vigging, and Kelly-sized execution.

### Pipeline

1. **Scan** — Pull open markets from Kalshi API by category (sports, weather, politics, economics)
2. **De-vig** — Get bookmaker odds from Sofascore, remove vig to find true probabilities
3. **Compare** — Find gaps between Kalshi price and true probability (minimum 4% edge)
4. **Size** — Quarter-Kelly criterion for position sizing (max 15% of bankroll per trade)
5. **Execute** — Place limit orders via Kalshi API with RSA-PSS authentication
6. **Monitor** — Track positions, P&L, and exit on profit targets

### Requirements

- **Kalshi API credentials** — `KALSHI_KEY_ID` and `KALSHI_PRIVATE_KEY` (RSA private key, inline or .pem)
- **Node.js 18+** — for crypto.sign with RSA-PSS

### Quick Start

```bash
# Set credentials
export KALSHI_KEY_ID=your_key_id
export KALSHI_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"

# Scan for edges
node scripts/scan-edges.js --category tennis

# Place a trade (dry run)
node scripts/trade.js --ticker KXATPMATCH-26MAR12DRAMED-DRA --side yes --price 38 --count 10 --dry

# Check portfolio
node scripts/portfolio.js
```

### Kalshi API Authentication

Kalshi uses RSA-PSS signatures. The signing message is: `timestamp + method + path` (NO request body in signature).

```javascript
const crypto = require('crypto');
const timestamp = Math.floor(Date.now() / 1000).toString();
const message = timestamp + 'GET' + '/trade-api/v2/portfolio/balance';
const signature = crypto.sign('sha256', Buffer.from(message), {
  key: crypto.createPrivateKey(privateKey),
  padding: crypto.constants.RSA_PKCS1_PSS_PADDING,
  saltLength: 32
});
```

Headers: `KALSHI-ACCESS-KEY`, `KALSHI-ACCESS-TIMESTAMP`, `KALSHI-ACCESS-SIGNATURE` (base64)

### De-Vigging Methodology

Bookmaker odds include a margin (vig). Remove it to find true probabilities:

```
implied_prob_A = 1 / decimal_odds_A
implied_prob_B = 1 / decimal_odds_B
total = implied_prob_A + implied_prob_B  (always > 1.0)
true_prob_A = implied_prob_A / total
true_prob_B = implied_prob_B / total
```

### Market Categories

See [references/market-categories.md](references/market-categories.md) for Kalshi series tickers and best edge sources.

**Best edge sources (battle-tested):**
- Tennis qualifying/challengers: 5-40% EV gaps
- NCAAB small conference tournaments: 4-9% EV
- Weather markets: high variance, NWS data helps

### Risk Rules

See [references/risk-rules.md](references/risk-rules.md) for full risk management.

**Hard rules:**
- Minimum edge: 4%
- Quarter-Kelly sizing (25% of Kelly fraction)
- Max 15% bankroll per position
- Max 30% total exposure
- 5% max drawdown — stop trading if hit
- No duplicate positions (YES on Player A = NO on Player B)
- Min 60% confidence in probability estimate
- Document every trade BEFORE placing it

### Lessons Learned

See [references/lessons-learned.md](references/lessons-learned.md) for common mistakes.

**Critical pitfalls to avoid:**
- Inverted probabilities: Odds API `outcomes[]` order is NOT home/away — match by `outcomes[i].name`
- Duplicate positions: YES on Player A + NO on Player B in same match = same position doubled
- Full-port on coin flips: Quarter-Kelly max, always
- Fragment matching: Never use fragment matching for event identification

---

## Kelly Criterion Position Sizing

Mathematical framework for optimal bet sizing based on edge and probability.

### The Formula

```
f* = (p * b - q) / b

where:
  f* = fraction of bankroll to bet
  p  = probability of winning
  q  = probability of losing (1 - p)
  b  = odds received on the bet (net odds, e.g., 2:1 = 2)
```

### Simplified for Prediction Markets

For a binary market where you buy at price `c` with true probability `p`:

```
edge = p - c
odds = (1/c) - 1
kelly = (p * odds - (1-p)) / odds
      = (p - c) / (1 - c)
      = edge / (1 - c)
```

### Example Calculation

**Scenario:** True probability 60%, Market price 50¢, Bankroll $1,000

```
edge = 0.60 - 0.50 = 0.10 (10% edge)
kelly = 0.10 / (1 - 0.50) = 0.20 (20%)
position = $1,000 × 0.20 = $200
```

### Fractional Kelly

| Fraction | Risk Level | Typical Use |
|----------|------------|-------------|
| 100% | Aggressive | Never recommended |
| 50% | Moderate | Experienced traders |
| 25% | Conservative | **Recommended** |
| 10% | Very conservative | Risk-averse |

### Position Size Caps

```python
def safe_kelly(true_prob, market_price, bankroll, kelly_fraction=0.25):
    if true_prob <= market_price:
        return 0  # No edge
    
    edge = true_prob - market_price
    kelly = edge / (1 - market_price)
    
    size = kelly * kelly_fraction * bankroll
    
    MAX_POSITION_PCT = 0.15
    MIN_POSITION = 5.0
    
    size = min(size, bankroll * MAX_POSITION_PCT)
    size = max(size, 0) if size >= MIN_POSITION else 0
    
    return round(size, 2)
```

### Math Arbitrage Sizing

```python
def arb_position_size(prob_sum, outcomes, bankroll, kelly_fraction=0.25):
    if prob_sum >= 1.0:
        return 0
    
    gross_return = (1 / prob_sum) - 1
    fee_rate = 0.02
    net_return = gross_return - (fee_rate * len(outcomes))
    
    if net_return <= 0:
        return 0
    
    kelly = net_return
    size = min(kelly * kelly_fraction * bankroll, bankroll * 0.15)
    return round(size, 2)
```

### Allocation Across Outcomes

For multi-outcome arbitrage, allocate to guarantee equal profit:

```python
def allocate_across_outcomes(total_size, outcomes):
    total_inv_price = sum(1/p for _, p in outcomes)
    allocation = {}
    for name, price in outcomes:
        weight = (1/price) / total_inv_price
        allocation[name] = round(total_size * weight, 2)
    return allocation
```

### Kelly for Futures/Leverage

```
leveraged_kelly = kelly / leverage

# Example: 5× leverage
kelly = 10%
safe_size = 10% / 5 = 2% of capital
```

### Common Mistakes

1. Overestimating edge — Your model isn't perfect
2. Full Kelly betting — Too much variance
3. Ignoring fees — They compound
4. Correlated bets — Reduce exposure
5. No hard caps — Always have max position limits

### Recommended Settings

```json
{
  "kelly_fraction": 0.25,
  "max_position_pct": 0.15,
  "min_edge": 0.04,
  "min_position": 5.0,
  "max_correlated_positions": 3,
  "max_daily_loss_pct": 0.10
}
```

---

## Wallet Setup

Configure smart wallet or private key for autonomous trading execution.

### Option 1: Coinbase Smart Wallet (Recommended)

ERC-4337 account abstraction wallet with best security and UX.

**Benefits:**
- No private key management — Keys secured by passkeys/biometrics
- Gasless transactions — Paymaster sponsors gas fees
- Batch operations — Execute multiple trades atomically
- Social recovery — Recover wallet without seed phrase
- Multi-chain — Base, Ethereum, Arbitrum, Polygon, etc.

```typescript
import { createBaseAccountSDK } from '@base-org/account';

const sdk = createBaseAccountSDK({
  appName: 'Trading Agents',
  appChainIds: [8453], // Base Mainnet
});

const provider = sdk.getProvider();
const { accounts } = await provider.request({
  method: 'wallet_connect',
  params: [{ version: '1' }]
});
```

**When to use:** User-facing apps, web/mobile apps, security-critical, batch operations.
**Avoid for:** Server-side bots, high-frequency trading (popup latency).

### Option 2: Private Key Wallet

For server-side autonomous operation.

```bash
export TRADING_PRIVATE_KEY=0x...
```

```python
import os
from web3 import Web3
from eth_account import Account

private_key = os.environ['TRADING_PRIVATE_KEY']
account = Account.from_key(private_key)
w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))
```

**Security best practices:**
1. Never commit private key to code
2. Use environment variables only
3. Limit funds in hot wallet — Only what's needed for trading
4. Separate wallets — Different wallets for different purposes
5. Monitor for unusual activity

### Option 3: Hardware Wallet (Hybrid)

For manual approval of larger trades while keeping some automation.

1. Bot scans for opportunities
2. Bot sends alert with opportunity details
3. Human reviews and approves
4. Human signs with hardware wallet
5. Bot monitors execution

### Funding the Wallet

**USDC Addresses:**

| Chain | USDC Address |
|-------|--------------|
| Base Mainnet | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| Base Sepolia | `0x036CbD53842c5426634e7929541eC2318f3dCF7e` |
| Polygon | `0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359` |
| Arbitrum | `0xaf88d065e77c8cC2239327C5EDb3A432268e5831` |

### Configuration File

```json
{
  "wallet": {
    "type": "smart_wallet",
    "provider": "base_account",
    "chain_id": 8453,
    "rpc_url": "https://mainnet.base.org",
    "paymaster_url": ""
  }
}
```

### Verifying Setup

```bash
# Smart wallet
node scripts/verify-wallet.js

# Private key
python scripts/wallet_setup.py --verify --chain base

# Check balance
python scripts/wallet_setup.py --balance 0xYOUR_ADDRESS --chain base
```

---

## ERC-8004 Agent Identity

On-chain agent identity standard for trustless agent economies.

### Overview

ERC-8004 provides:
- **Identity Registry** — ERC-721 NFT representing agent identity
- **Reputation Registry** — On-chain feedback and scoring
- **Validation Registry** — Third-party verification hooks

### Contract Addresses

| Chain | Chain ID | Registry Address |
|-------|----------|------------------|
| Base Mainnet | 8453 | `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` |
| Celo Mainnet | 42220 | `0xaC3DF9ABf80d0F5c020C06B04Cced27763355944` |

### Quick Start

```bash
# Register new agent on Base
python scripts/onboard_agent.py \
  --name "TradingBot" \
  --chain base \
  --description "Autonomous prediction market trader"

# With ownership transfer to operator
python scripts/onboard_agent.py \
  --name "TradingBot" \
  --chain base \
  --operator 0x12F1B38DC35AA65B50E5849d02559078953aE24b

# Lookup existing agent
python scripts/onboard_agent.py --chain base --lookup 42
```

### What You Get

- **ERC-721 NFT** — Portable, censorship-resistant identity
- **Certificate URL** — `https://8004.way.je/agent/{chain}:{id}`
- **Agent Wallet** — On-chain address for receiving payments
- **Reputation Hooks** — Compatible with ERC-8004 reputation registries

### Key Functions

```solidity
function register(string agentURI) external returns (uint256 agentId);
function setAgentWallet(uint256 agentId, address newWallet, uint256 deadline, bytes signature) external;
function getAgentWallet(uint256 agentId) external view returns (address);
function setMetadata(uint256 agentId, string key, bytes value) external;
```

### wayMint API

Base URL: `https://8004.way.je`

```bash
# Pin metadata to IPFS
curl -X POST https://8004.way.je/api/pin \
  -H "Content-Type: application/json" \
  -d '{"name": "my-agent", "description": "What I do", "services": [{"name": "trading", "endpoint": "autonomous"}]}'

# Lookup agent
GET https://8004.way.je/api/agent/base/42
```

### Ed25519 Self-Registration (Celo)

```bash
python scripts/onboard_agent.py --name "MyAgent" --chain celo --use-openclaw-key
```

See [references/erc8004-identity.md](references/erc8004-identity.md) for full documentation.

---

## Multi-Agent Analysis Prompts

Complete system prompts for each agent in the trading framework.

### Analyst Team (4 Agents)

**Fundamentals Analyst** — Analyzes financial documents, company profile, basic financials, and financial history. Tools: `get_fundamentals`, `get_balance_sheet`, `get_cashflow`, `get_income_statement`.

**Technical Analyst** — Analyzes historical prices, technical indicators, and significant price levels. Tools: `get_stock_data`, `get_indicators`.

**Sentiment Analyst** — Analyzes social media sentiment, public opinion trends, and sentiment scores. Tools: `get_news` (used for sentiment derivation).

**News/Catalyst Analyst** — Analyzes recent news and global events that might impact the stock. Tools: `get_news`, `get_global_news`, `get_insider_transactions`.

### Bull/Bear Debate

After all 4 agents report, synthesize via adversarial debate:

```
weighted_score = (fund * 0.30 + tech * 0.25 + sent * 0.20 + news * 0.25)
winner = "bull" if weighted_score > 0.55 else "bear"
```

**Output**: BUY / WATCH / SKIP recommendation with confidence score.

### Risk Team (3 Analysts)

- **Aggressive Risk Analyst** — Favors maximizing returns through higher-conviction positions
- **Neutral Risk Analyst** — Balances risk and reward, seeking optimal risk-adjusted returns
- **Conservative Risk Analyst** — Prioritizes capital preservation over return maximization

### Portfolio Manager

Synthesizes the risk analysts' debate and delivers the final trading decision.

**Rating Scale**: Buy / Overweight / Hold / Underweight / Sell

See [references/agent-prompts.md](references/agent-prompts.md) for full system prompts.

---

## Scripts Reference

### Polymarket Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/polymarket.py` | Polymarket API client | Python module |
| `scripts/validate.py` | Validate Polymarket connectivity | Run with python3 |

### Arbitrage Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/fetch_markets.py` | Scrape Polymarket for active markets | Run with python3 |
| `scripts/detect_arbitrage.py` | Analyze markets for arbitrage | Run with python3 |
| `scripts/monitor.py` | Continuous monitoring with alerting | Run with python3 |

### Kalshi Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/kalshi-auth.js` | Kalshi API client with RSA-PSS auth | Node.js |
| `scripts/scan-edges.js` | Scan markets and compare to de-vig | Node.js |
| `scripts/trade.js` | Place/cancel orders with safety checks | Node.js |
| `scripts/portfolio.js` | Check balance, positions, P&L | Node.js |

### Trading Agents Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/analyze.py` | Single stock multi-agent analysis | Run with python3 |
| `scripts/batch_analyze.py` | Batch analysis of multiple tickers | Run with python3 |
| `scripts/backtest.py` | Historical signal backtesting | Run with python3 |
| `scripts/arb_scanner.py` | Prediction market arbitrage detection | Run with python3 |
| `scripts/autonomous.py` | Full autonomous trading loop | Run with python3 |
| `scripts/wallet_setup.py` | Configure and test wallet | Run with python3 |
| `scripts/onboard_agent.py` | Agent onboarding and setup | Run with python3 |

---

## Key References

- **Polymarket API endpoints**: [references/api-endpoints.md](references/api-endpoints.md) — Full REST API reference
- **Arbitrage types and strategies**: [references/arbitrage_types.md](references/arbitrage_types.md) — Math, cross-market, orderbook arb
- **Getting started guide**: [references/getting_started.md](references/getting_started.md) — Paper trading to live setup
- **Kelly criterion math**: [references/kelly-sizing.md](references/kelly-sizing.md) — Position sizing formulas
- **Wallet configuration**: [references/wallet-setup.md](references/wallet-setup.md) — Smart wallet and private key setup
- **ERC-8004 identity**: [references/erc8004-identity.md](references/erc8004-identity.md) — On-chain agent identity
- **Agent prompts**: [references/agent-prompts.md](references/agent-prompts.md) — Multi-agent system prompts
- **Kalshi market categories**: [references/market-categories.md](references/market-categories.md) — Series tickers and edge sources
- **Kalshi risk rules**: [references/risk-rules.md](references/risk-rules.md) — Position sizing and risk management
- **Kalshi lessons learned**: [references/lessons-learned.md](references/lessons-learned.md) — Common mistakes to avoid

## Limitations

- **Not financial advice** — Research tool only
- **LLM latency** — Full analysis takes 30-90s
- **Market efficiency** — Good arbs disappear fast
- **Execution risk** — Slippage and liquidity
- **API limits** — Free tiers have rate limits
- **Geographic restrictions** — Trading restrictions vary by jurisdiction
