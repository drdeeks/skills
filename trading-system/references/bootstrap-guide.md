# Bootstrap Guide — Account Creation & API Key Setup

Step-by-step procedures for self-registering on every supported platform, obtaining API credentials, and deploying wallets.

## Table of Contents

1. [Overview](#overview)
2. [Polymarket Setup](#polymarket-setup)
3. [Kalshi Setup](#kalshi-setup)
4. [Hyperliquid Setup](#hyperliquid-setup)
5. [Wallet Deployment](#wallet-deployment)
6. [Telegram Alerts](#telegram-alerts)
7. [Environment Variables](#environment-variables)
8. [Automated Bootstrap Flow](#automated-bootstrap-flow)

---

## Overview

The bootstrap process creates all necessary accounts, generates API credentials, and validates connectivity. It can run interactively (guided) or non-interactively (from environment variables).

**Priority order**: Polymarket (free, highest arb frequency) → Kalshi (regulated, good edge on sports/weather) → Hyperliquid (crypto perps, higher risk).

## Polymarket Setup

### Read-Only (No Key Required)

Scanning and arbitrage detection work without any API key. The Gamma API is public:

```bash
# Test — no auth needed
curl "https://gamma-api.polymarket.com/markets?limit=1"
```

### Trading (Private Key Required)

1. **Create Wallet**: Install MetaMask or use Coinbase Wallet
2. **Fund Wallet**: Bridge USDC to Polygon (Polymarket runs on Polygon)
3. **Connect to Polymarket**: Visit polymarket.com, connect wallet
4. **Complete Onboarding**: Accept terms, complete any required verification
5. **Export Private Key**: MetaMask → Account Details → Export Private Key

```bash
export POLYMARKET_PRIVATE_KEY="0x..."  # Your wallet private key
```

**Security**:
- Never commit private keys to git
- Use a dedicated trading wallet (not your main wallet)
- Start with small amounts ($50-100)

### API Endpoints

| Endpoint | Base URL | Auth |
|---|---|---|
| Gamma (search/browse) | `gamma-api.polymarket.com` | None |
| CLOB (trading) | `clob.polymarket.com` | EIP-712 signature |
| Data (trades/OI) | `data-api.polymarket.com` | None |

## Kalshi Setup

1. **Create Account**: Visit kalshi.com, sign up with email
2. **Verify Identity**: Upload ID + selfie (US residents required for trading)
3. **Generate API Key**:
   - Settings → API Keys → Generate New Key
   - Download the `.pem` private key file immediately (shown only once)
   - Note the Key ID
4. **Fund Account**: Bank transfer or wire (ACH takes 3-5 days)

```bash
export KALSHI_KEY_ID="your-key-id"
export KALSHI_PRIVATE_KEY_PATH="/path/to/kalshi-key.pem"
```

### Authentication Method

Kalshi uses RSA-PSS signatures:

```javascript
// Signing: timestamp + method + path (NO body)
const message = timestamp + "GET" + "/trade-api/v2/portfolio/balance";
const signature = crypto.sign("sha256", Buffer.from(message), {
    key: crypto.createPrivateKey(privateKey),
    padding: crypto.constants.RSA_PKCS1_PSS_PADDING,
    saltLength: 32
});
// Headers: KALSHI-ACCESS-KEY, KALSHI-ACCESS-TIMESTAMP, KALSHI-ACCESS-SIGNATURE
```

## Hyperliquid Setup

1. **Visit**: app.hyperliquid.xyz
2. **Connect Wallet**: MetaMask or WalletConnect (no KYC)
3. **Bridge USDC**: Use built-in bridge from Ethereum/Arbitrum
4. **Create API Wallet**:
   - Settings → API Wallet → Generate
   - Export the generated private key
   - Set trading permissions

```bash
export HYPERLIQUID_PRIVATE_KEY="0x..."
```

## Wallet Deployment

### Option A: Coinbase Smart Wallet (Recommended)

ERC-4337 smart wallet with gas sponsorship:

```bash
export TRADING_WALLET_KEY="0x..."  # Owner key
# Smart wallet deployed on Base Mainnet (chain 8453)
# Gas sponsored via paymaster — $0 transaction costs
```

### Option B: Standard EOA Wallet

For simpler setup:

```bash
export TRADING_WALLET_KEY="0x..."  # Direct private key
```

### Option C: Generate New Wallet

```python
from eth_account import Account
account = Account.create()
print(f"Address: {account.address}")
print(f"Key: {account.key.hex()}")
# Fund this address with USDC before trading
```

## Telegram Alerts

1. **Create Bot**: Message @BotFather on Telegram, send `/newbot`
2. **Get Token**: BotFather returns the bot token
3. **Get Chat ID**: Add bot to a group, send a message, then:
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/getUpdates"
   ```
   Find `chat.id` in the response.

```bash
export TELEGRAM_BOT_TOKEN="123456:ABC..."
export TELEGRAM_CHAT_ID="-1001234567890"
```

## Environment Variables

Complete list of all environment variables:

| Variable | Required | Platform | Description |
|---|---|---|---|
| `POLYMARKET_PRIVATE_KEY` | For trading | Polymarket | Ethereum private key for CLOB signing |
| `KALSHI_KEY_ID` | For trading | Kalshi | API key identifier |
| `KALSHI_PRIVATE_KEY_PATH` | For trading | Kalshi | Path to RSA private key .pem |
| `HYPERLIQUID_PRIVATE_KEY` | For trading | Hyperliquid | API wallet private key |
| `TRADING_WALLET_KEY` | For on-chain | Smart Wallet | Owner key for smart wallet |
| `TRADING_BANKROLL` | Recommended | All | Starting bankroll in USD |
| `TELEGRAM_BOT_TOKEN` | Optional | Alerts | Telegram bot API token |
| `TELEGRAM_CHAT_ID` | Optional | Alerts | Telegram chat/group ID |

## Automated Bootstrap Flow

The `bootstrap.py setup` command automates this entire process:

```
1. Create ~/.autonomous-trading-system/ directory tree
2. Read all environment variables
3. Write config.json with loaded credentials
4. Test connectivity to each platform API
5. Report readiness status
6. Default to paper trading mode (safe)
```

To go from zero to running:

```bash
# Set at minimum:
export TRADING_BANKROLL=100

# Run bootstrap
python3 scripts/bootstrap.py setup

# Start paper trading immediately (no API keys needed for scanning)
python3 scripts/trading_engine.py start --mode paper
```
