---
name: building-with-base-account
description: Integrates Base Account SDK for authentication and payments. Covers Sign
license: MIT
version: 0.0.5
---
# Building with Base Account

Base Account is an ERC-4337 smart wallet providing universal sign-on, one-tap USDC payments, and multi-chain support (Base, Arbitrum, Optimism, Zora, Polygon, BNB, Avalanche, Lordchain, Ethereum Mainnet).

## Quick Start

```bash
npm install @base-org/account @base-org/account-ui
```

```typescript
import { createBaseAccountSDK } from '@base-org/account';

const sdk = createBaseAccountSDK({
  appName: 'My App',
  appLogoUrl: 'https://example.com/logo.png',
  appChainIds: [8453], // Base Mainnet
});

const provider = sdk.getProvider();
```

## Feature References

Read the reference for the feature you're implementing:

| Feature | Reference | When to Read |
|---------|-----------|-------------|
| Sign in with Base | [references/authentication.md](references/authentication.md) | Wallet auth, SIWE, backend verification, SignInWithBaseButton, Wagmi/Privy setup |
| Base Pay | [references/payments.md](references/payments.md) | One-tap USDC payments, payerInfo, server-side verification, BasePayButton |
| Subscriptions | [references/subscriptions.md](references/subscriptions.md) | Recurring charges, spend permissions, CDP wallet setup, charge/revoke lifecycle |
| Sub Accounts | [references/sub-accounts.md](references/sub-accounts.md) | App-specific embedded wallets, key generation, funding |
| Capabilities | [references/capabilities.md](references/capabilities.md) | Batch transactions, gas sponsorship (paymasters), atomic execution, auxiliaryFunds, attribution |
| Prolinks | [references/prolinks.md](references/prolinks.md) | Shareable payment links, QR codes, encoded transaction URLs |
| Troubleshooting | [references/troubleshooting.md](references/troubleshooting.md) | Popup issues, gas usage, unsupported calls, migration, doc links |

## Critical Requirements

### Security

- **Track transaction IDs** to prevent replay attacks
- **Verify sender matches authenticated user** to prevent impersonation
- **Use a proxy** to protect Paymaster URLs from frontend exposure
- **Paymaster providers must be ERC-7677-compliant**
- **Never expose CDP credentials client-side** (subscription backend only)

### Popup Handling

- Generate nonces **before** user clicks "Sign in" to avoid popup blockers
- Use `Cross-Origin-Opener-Policy: same-origin-allow-popups`
- `same-origin` breaks the Base Account popup

### Base Pay

- Base Pay works independently from SIWB — no auth required for `pay()`
- `testnet` param in `getPaymentStatus()` must match `pay()` call
- Never disable actions based on onchain balance alone — check `auxiliaryFunds` capability

### Sub Accounts

- Call `wallet_addSubAccount` each session before use
- Ownership changes expected on new devices/browsers
- Only Coinbase Smart Wallet contracts supported for import

### Smart Wallets

- ERC-6492 wrapper enables signature verification before wallet deployment
- Viem's `verifyMessage`/`verifyTypedData` handle this automatically


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
| `scripts/main.py` | building-with-base-account script | Run with python3 |

## Key References

- **Sub Accounts**: [references/sub-accounts.md](references/sub-accounts.md)
- **Payments**: [references/payments.md](references/payments.md)
- **Skill**: [references/SKILL.md](references/SKILL.md)
- **Capabilities**: [references/capabilities.md](references/capabilities.md)
- **Troubleshooting**: [references/troubleshooting.md](references/troubleshooting.md)
- **Subscriptions**: [references/subscriptions.md](references/subscriptions.md)
- **Prolinks**: [references/prolinks.md](references/prolinks.md)
- **Authentication**: [references/authentication.md](references/authentication.md)

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

## For Edge Cases and Latest API Changes

- **AI-optimized docs**: [docs.base.org/llms.txt](https://docs.base.org/llms.txt)
- **Full reference**: [docs.base.org/base-account](https://docs.base.org/base-account)
