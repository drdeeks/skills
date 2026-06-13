# Base Network Configuration

Network configuration for Base L2 queries.

## RPC Endpoints

| Network | URL | Chain ID |
|---------|-----|----------|
| Mainnet | https://mainnet.base.org | 8453 |
| Sepolia | https://sepolia.base.org | 84532 |

## Environment Variables

```bash
export BASE_RPC_URL="https://mainnet.base.org"
```

## Rate Limits

- Public RPC: ~100 requests/minute
- CoinGecko free: ~10-30 requests/minute
- Private RPC: Higher limits (varies by provider)
