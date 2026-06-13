# Base Agent Bootstrap Reference

Quick reference for Base agent setup components.

## Builder Code Registration

Use `curl` (NOT `urllib`) to register:
```bash
curl -s -X POST "https://api.base.dev/v1/agents/builder-codes" \
  -H "Content-Type: application/json" \
  -d '{"wallet_address": "0xYOUR_WALLET"}'
```

## ERC-8021 Attribution

Requires `ox` and `viem` packages:
```bash
npm i ox viem
```

## Pinata IPFS Setup

1. Create AgentMail inbox
2. Sign up at app.pinata.cloud
3. Verify email via AgentMail
4. Extract JWT from Developers > API Keys
