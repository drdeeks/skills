---
name: connecting-to-base-network
description: Provides Base network configuration including RPC endpoints, chain IDs,
license: MIT
version: 0.0.4
---
# Connecting to Base Network

## Mainnet

| Property | Value |
|----------|-------|
| Network Name | Base |
| Chain ID | 8453 |
| RPC Endpoint | `https://mainnet.base.org` |
| Currency | ETH |
| Explorer | https://basescan.org |

## Testnet (Sepolia)

| Property | Value |
|----------|-------|
| Network Name | Base Sepolia |
| Chain ID | 84532 |
| RPC Endpoint | `https://sepolia.base.org` |
| Currency | ETH |
| Explorer | https://sepolia.basescan.org |

## Security

- **Never use public RPC endpoints in production** — they are rate-limited and offer no privacy guarantees; use a dedicated node provider or self-hosted node
- **Never embed RPC API keys in client-side code** — proxy requests through a backend to protect provider credentials
- **Validate chain IDs** before signing transactions to prevent cross-chain replay attacks
- **Use HTTPS RPC endpoints only** — reject any `http://` endpoints to prevent credential interception

## Critical Notes

- Public RPC endpoints are **rate-limited** - not for production
- For production: use node providers or run your own node
- Testnet ETH available from faucets in Base documentation


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
| `scripts/main.py` | connecting-to-base-network script | Run with python3 |

## Key References

- **Overview**: [references/overview.md](references/overview.md)

## Workflow

### Step 1: Installation

```bash
# Install dependencies if needed
```

### Step 2: Configuration

```bash
# Configure the skill
```

### Step 3: Usage

```bash
# Use the skill
python3 scripts/main.py
```

### Step 4: Validation

```bash
# Validate the skill
python3 scripts/validate.py
```

## Wallet Setup

1. Add network with chain ID and RPC from tables above
2. For testnet, use Sepolia configuration
3. Bridge ETH from Ethereum or use faucets
