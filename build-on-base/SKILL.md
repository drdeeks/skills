---
name: build-on-base
description: >
  Complete Base development playbook. Covers: (1) Network — Base RPC URLs, chain IDs (8453/84532),
  explorer config, testnet setup, connect to Base, Base Sepolia; (2) Contracts — Foundry deployment,
  forge create, BaseScan verification, CDP faucet, testnet ETH, deploy contract to Base;
  (3) Builder Codes — ERC-8021 attribution suffix, referral fees, dataSuffix for Wagmi/Viem/Privy/
  ethers.js/window.ethereum, transaction attribution, earn referral fees, append builder code;
  (4) Base Account SDK — Sign in with Base (SIWB), Base Pay, USDC payments, paymasters, gas
  sponsorship, sub-accounts, spend permissions, prolinks, batch transactions, smart wallet,
  payment link, recurring subscription; (5) Agent registration — trading bots, AI agents, automated
  senders, ERC-8021 attribution wiring, base.dev API, register agent, builder code registration;
  (6) Node operation — run Base node, Reth setup, hardware requirements, self-hosted RPC, sync;
  (7) Migrations — migrate OnchainKit, OnchainKitProvider to WagmiProvider, wagmi
version: 0.0.5
---

# Base Development

Complete playbook for building on Base L2 — network setup, smart contracts, wallet auth, payments,
developer tool attribution, and framework migrations.

## Default Stack

| Layer | Default |
|-------|---------|
| Network | Base Mainnet (8453) / Base Sepolia testnet (84532) |
| Contracts | Foundry (`forge create` + BaseScan verification) |
| Wallet auth | Base Account SDK (`@base-org/account`) |
| Payments | Base Pay — USDC, gasless, settles in <2s |
| Transactions | wagmi + viem |
| Attribution | Builder Codes — ERC-8021 via `ox/erc8021` |
| RPC (prod) | Dedicated node provider or self-hosted Reth |

## Safety Guardrails

- **Never commit private keys** — use `cast wallet import` for Foundry keystores
- **Never expose RPC API keys or CDP credentials client-side** — proxy through backend
- **Never skip server-side payment verification** — always call `getPaymentStatus()` server-side and verify `sender`, `amount`, `recipient`; track processed tx IDs to prevent replay attacks
- **Never send transactions without Builder Code attribution** — silent data loss, no errors, no warnings
- **Validate all user-provided shell inputs** before constructing forge/cast commands (no spaces, semicolons, pipes)
- **COOP headers for Base Account popups** — use `same-origin-allow-popups`, not `same-origin`

## Task Routing

Read the reference for your task:

| Task | When to Use | Reference |
|------|-------------|-----------|
| **Network config** | RPC URLs, chain IDs, explorer links, testnet setup | [references/network.md](references/network.md) |
| **Deploy contracts** | Foundry deployment, BaseScan verification, faucet | [references/deploy-contracts.md](references/deploy-contracts.md) |
| **Run a Base node** | Self-hosted RPC, Reth, hardware requirements | [references/run-node.md](references/run-node.md) |
| **Builder Codes** | Add ERC-8021 attribution to transactions | [references/builder-codes/overview.md](references/builder-codes/overview.md) |
| **Base Account SDK** | SIWB, Base Pay, subscriptions, sub-accounts | [references/base-account/overview.md](references/base-account/overview.md) |
| **Register AI agent/bot** | Register wallet, get builder code, wire attribution | [references/agents/register.md](references/agents/register.md) |
| **Migrate from OnchainKit** | OnchainKitProvider → wagmi, wallet/tx components | [references/migrations/onchainkit/overview.md](references/migrations/onchainkit/overview.md) |
| **MiniKit → Farcaster SDK** | `@coinbase/onchainkit/minikit` → `@farcaster/miniapp-sdk` | [references/migrations/minikit-to-farcaster/overview.md](references/migrations/minikit-to-farcaster/overview.md) |
| **Farcaster miniapp → regular app** | Remove Mini App host coupling, convert to Base/web app | [references/migrations/farcaster-miniapp-to-app.md](references/migrations/farcaster-miniapp-to-app.md) |

## Operating Procedure

1. **Classify the task** using the table above
2. **Read the relevant reference** before implementing
3. **Confirm the framework** with the user when multiple options exist (e.g., Privy vs wagmi for Builder Codes)
4. **Implement** with explicit chain ID, security requirements, and all required validations
5. **Deliver** diffs, install commands, and any manual steps (env vars, API key setup, wallet registration)

## For Edge Cases and Latest API Changes

- **AI-optimized docs**: [docs.base.org/llms.txt](https://docs.base.org/llms.txt)
- **Base Account reference**: [docs.base.org/base-account](https://docs.base.org/base-account)
- **Base chain docs**: [docs.base.org](https://docs.base.org)


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
| `scripts/analyze_project.py` | build-on-base script | Run with python3 |
| `scripts/validate_conversion.py` | build-on-base script | Run with python3 |

## Key References

- **Network**: [references/network.md](references/network.md)
- **Run Node**: [references/run-node.md](references/run-node.md)
- **Skill**: [references/SKILL.md](references/SKILL.md)
- **Deploy Contracts**: [references/deploy-contracts.md](references/deploy-contracts.md)

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

## Installation

```bash
npx skills add base/skills --skill build-on-base
```
