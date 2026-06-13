# Platform APIs — Integration Reference

API reference for all supported trading platforms. Endpoints, authentication, rate limits, and usage patterns.

## Table of Contents

1. [Polymarket](#polymarket)
2. [Kalshi](#kalshi)
3. [Hyperliquid](#hyperliquid)
4. [Smart Wallet (Base)](#smart-wallet-base)
5. [Data Sources](#data-sources)
6. [Telegram Bot API](#telegram-bot-api)

---

## Polymarket

### Three APIs

| API | Base URL | Auth | Purpose |
|---|---|---|---|
| Gamma | `gamma-api.polymarket.com` | None | Search, browse, discovery |
| CLOB | `clob.polymarket.com` | EIP-712 | Trading, orders, positions |
| Data | `data-api.polymarket.com` | None | Trades, open interest |

### Key Gamma Endpoints

```bash
# Search markets
GET /markets?limit=100&active=true&closed=false

# Search by keyword
GET /markets?tag=politics&limit=50

# Get specific market
GET /markets/{conditionId}

# Get events (parent of markets)
GET /events?limit=50&active=true
```

### Key CLOB Endpoints

```bash
# Get orderbook
GET /book?token_id={clobTokenId}

# Get price history
GET /prices-history?market={conditionId}&interval=1d&fidelity=60

# Place order (requires auth)
POST /order
{
    "tokenID": "...",
    "price": "0.50",
    "size": "100",
    "side": "BUY",
    "type": "GTC"
}
```

### Rate Limits

- Gamma: 4,000 requests / 10 seconds
- CLOB: 9,000 requests / 10 seconds
- Data: 1,000 requests / 10 seconds

### Parsing Notes

Fields `outcomePrices`, `outcomes`, `clobTokenIds` are **double-encoded JSON** — parse with `json.loads()` to get arrays.

```python
prices = json.loads(market["outcomePrices"])  # ["0.65", "0.35"]
token_ids = json.loads(market["clobTokenIds"])  # ["id1", "id2"]
```

## Kalshi

### Authentication

RSA-PSS signature over `timestamp + method + path`:

```python
import crypto
timestamp = str(int(time.time()))
message = f"{timestamp}GET/trade-api/v2/portfolio/balance"
signature = sign_rsa_pss(private_key, message)

headers = {
    "KALSHI-ACCESS-KEY": key_id,
    "KALSHI-ACCESS-TIMESTAMP": timestamp,
    "KALSHI-ACCESS-SIGNATURE": base64(signature)
}
```

### Key Endpoints

```bash
# Exchange status (no auth)
GET /trade-api/v2/exchange/status

# Browse events
GET /trade-api/v2/events?limit=100&status=open

# Get markets for event
GET /trade-api/v2/events/{event_ticker}/markets

# Get portfolio (auth required)
GET /trade-api/v2/portfolio/balance
GET /trade-api/v2/portfolio/positions

# Place order (auth required)
POST /trade-api/v2/portfolio/orders
{
    "ticker": "KXATPMATCH-26MAR12DRAMED-DRA",
    "side": "yes",
    "type": "limit",
    "count": 10,
    "yes_price": 38
}

# Cancel order
DELETE /trade-api/v2/portfolio/orders/{order_id}
```

### Rate Limits

- General: 100 requests / 10 seconds
- Orders: 20 orders / second

## Hyperliquid

### Authentication

Ethereum-style signing with API wallet:

```python
from eth_account import Account
account = Account.from_key(private_key)
signature = account.sign_message(message)
```

### Key Endpoints

```bash
# Base URL: https://api.hyperliquid.xyz

# Get market info
POST /info
{"type": "meta"}

# Get orderbook
POST /info
{"type": "l2Book", "coin": "ETH"}

# Place order
POST /exchange
{
    "action": {
        "type": "order",
        "orders": [{
            "a": 0,  # asset index (ETH=0)
            "b": true,  # isBuy
            "p": "3500",  # price
            "s": "0.1",  # size
            "r": false,  # reduceOnly
            "t": {"limit": {"tif": "Gtc"}}
        }],
        "grouping": "na"
    },
    "nonce": timestamp_ms,
    "signature": "0x..."
}

# Get positions
POST /info
{"type": "clearinghouseState", "user": "0x..."}
```

## Smart Wallet (Base)

### ERC-4337 Smart Wallet

```javascript
import { createBaseAccountSDK } from "@base-org/account";

const sdk = createBaseAccountSDK({
    appName: "AutonomousTradingSystem",
    appChainIds: [8453]  // Base Mainnet
});

// Send transaction (gas sponsored)
const tx = await sdk.sendTransaction({
    to: targetAddress,
    data: encodedCalldata,
    value: 0n
});

// Batch multiple trades atomically
const batch = await sdk.sendBatchTransaction([
    { to: addr1, data: data1, value: 0n },
    { to: addr2, data: data2, value: 0n }
]);
```

### Key Addresses (Base Mainnet)

| Contract | Address |
|---|---|
| USDC | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| WETH | `0x4200000000000000000000000000000000000006` |
| RPC | `https://mainnet.base.org` |
| Chain ID | 8453 |

## Data Sources

### yfinance (Free)

```python
import yfinance as yf
ticker = yf.Ticker("NVDA")
data = ticker.history(period="5d", interval="5m")
info = ticker.info  # Fundamentals
news = ticker.news  # Recent news
```

### Sofascore (Free — Scraping)

```python
# De-vig sports odds
# GET https://api.sofascore.com/api/v1/event/{id}/odds/1/all
# Parse bookmaker odds, remove vig to find true probabilities
```

### CoinGecko (Free Tier)

```python
# GET https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd
# Rate limit: 30 calls/minute on free tier
```

## Telegram Bot API

```python
import urllib.request

def send_alert(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = json.dumps({"chat_id": chat_id, "text": message, "parse_mode": "HTML"})
    req = urllib.request.Request(url, data=data.encode(),
                                 headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=10)
```
