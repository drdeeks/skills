# Base Blockchain Troubleshooting

Common issues with Base blockchain queries.

## CoinGecko Rate Limits

Free tier: ~10-30 requests/minute. Use `--no-prices` for speed.

## Public RPC Rate Limits

For production, set `BASE_RPC_URL` to a private endpoint (Alchemy, QuickNode, Infura).

## Unknown Tokens

Only ~15 well-known Base tokens are checked by default. Use `token` command with specific contract address for others.

## Gas Estimates

Base L2 gas does not include L1 data posting fees. Estimates are for L2 execution only.

## Proxy Detection

Only EIP-1967 proxies are detected. Other proxy patterns (EIP-1167, custom storage slots) are not checked.
