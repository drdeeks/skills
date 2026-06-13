---
name: zapper
description: "Zapper API integration — query portfolio balances, transaction history, and DeFi positions across EVM chains"
version: 0.0.2
license: MIT
metadata:
  openclaw:
    version: "1.0"
    category: blockchain
    complexity: standard
---

# Zapper

Zapper API integration for querying portfolio balances, transaction history, and DeFi positions across EVM-compatible chains.

## Features

- Multi-chain portfolio aggregation
- Token balance queries
- Transaction history retrieval
- DeFi position tracking
- NFT portfolio overview

## Quick Start

```bash
# Set your Zapper API key
export ZAPPER_API_KEY="your_key_here"

# Query portfolio
python3 scripts/main.py portfolio --address 0x123...
```

## API Endpoints

- `GET /v1/portfolio/balances` — Token balances
- `GET /v1/portfolio/transactions` — Transaction history
- `GET /v1/portfolio/defi-positions` — DeFi positions
- `GET /v1/portfolio/nfts` — NFT holdings

## Provider Compatibility

| Provider | Compatibility | Notes |
|----------|---------------|-------|
| Claude (Anthropic) | Full | Tool use, function calling |
| OpenAI / ChatGPT | Full | Function calling, Actions |
| Mistral / Le Chat | Full | Tool calling |
| Gemini (Google) | Full | Extensions |
| Hermes (Nous) | Full | Tool-use fine-tuned |
| Any LLM + tools | Full | Plain Python scripts |

## Free-First Strategy

| Tier | Cost | Stack |
|------|------|-------|
| **Tier 0** | $0/mo | Python 3.8+ (stdlib only) |
| **Tier 1** | $0-5/mo | CI/CD automation |
| **Tier 2** | $5-20/mo | Team distribution |

## Enforced Output Statistics

Every script produces structured JSON output on completion.

## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/main.py` | Main Zapper CLI | `python3 scripts/main.py --help` |

## Key References

- **API Docs**: [references/api-reference.md](references/api-reference.md)
- **Authentication**: [references/authentication.md](references/authentication.md)
- **Examples**: [references/examples.md](references/examples.md)
