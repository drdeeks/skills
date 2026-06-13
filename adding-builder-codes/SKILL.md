---
name: adding-builder-codes
description: Integrate Base Builder Codes (ERC-8021) into web3 applications for onchain
license: MIT
version: 0.0.4
---
# Adding Builder Codes

Integrate [Base Builder Codes](https://base.dev) into an onchain application. Builder Codes append an ERC-8021 attribution suffix to transaction calldata so Base can attribute activity to your app and you can earn referral fees. No smart contract changes required.

## When to Use This Skill

Use this skill when a developer asks to:

- "Add builder codes to my application"
- "How do I append a builder code to my transactions?"
- "I want to earn referral fees on Base transactions"
- "Integrate builder codes"
- Set up transaction attribution on Base

## Prerequisites

- A Builder Code from [base.dev](https://base.dev) > Settings > Builder Codes
- The `ox` library for generating ERC-8021 suffixes: `npm install ox`

## Integration Workflow

Copy this checklist and track progress:

```
Builder Codes Integration:
- [ ] Step 1: Detect framework (Required First Step)
- [ ] Step 2: Install dependencies
- [ ] Step 3: Generate the dataSuffix constant
- [ ] Step 4: Apply attribution (framework-specific)
- [ ] Step 5: Verify attribution is working
```

## Framework Detection (Required First Step)

Before implementing, determine the framework in use.

### 1. Read package.json and scan source files

```bash
# Check for framework dependencies
grep -E "wagmi|@privy-io/react-auth|viem|ethers" package.json

# Check for smart wallet / account abstraction usage
grep -rn "useSendCalls\|sendCalls\|ERC-4337\|useSmartWallets" src/

# Check for EOA transaction patterns
grep -rn "useSendTransaction\|sendTransaction\|writeContract\|useWriteContract" src/

# Check Privy version if present
grep "@privy-io/react-auth" package.json
```

### 2. Classify into one framework

| Framework | Detection Signal |
|-----------|-----------------|
| `privy`   | `@privy-io/react-auth` in package.json or imports |
| `wagmi`   | `wagmi` in package.json or imports (without Privy) |
| `viem`    | `viem` in package.json, no React framework |
| `rpc`     | `ethers`, `window.ethereum`, or no Web3 library detected |

Priority order if multiple are detected: **Privy > Wagmi > Viem > Standard RPC**

### 3. Confirm with user

Before proceeding, confirm the detected framework:

> "I detected you are using [Framework]. I'll implement builder codes using the [Framework] approach — does that sound right?"

Wait for user confirmation before implementing.

### Implementation Path

- **Privy** (`@privy-io/react-auth` v3.13.0+) → See [references/privy.md](references/privy.md)
- **Wagmi** (without Privy) → See [references/wagmi.md](references/wagmi.md)
- **Viem only** (no React framework) → See [references/viem.md](references/viem.md)
- **Standard RPC** (ethers.js or raw `window.ethereum`) → See [references/rpc.md](references/rpc.md)

### Step 2: Install dependencies

```bash
npm install ox
```

Requires `viem >= 2.45.0` for Wagmi/Viem paths. Privy requires `@privy-io/react-auth >= 3.13.0`.

### Step 3: Generate the dataSuffix constant

Create a shared constant (e.g., `src/lib/attribution.ts` or `src/constants/builderCode.ts`):

```typescript
import { Attribution } from "ox/erc8021";

export const DATA_SUFFIX = Attribution.toDataSuffix({
  codes: ["YOUR-BUILDER-CODE"], // Replace with your code from base.dev
});
```

### Step 4: Apply attribution

Follow the framework-specific guide:

#### Privy Implementation

See [references/privy.md](references/privy.md) — plugin-based, one config change required.

#### Wagmi Implementation

See [references/wagmi.md](references/wagmi.md) — add `dataSuffix` to Wagmi client config.

#### Viem Implementation

See [references/viem.md](references/viem.md) — add `dataSuffix` to wallet client.

#### Standard RPC Implementation

See [references/rpc.md](references/rpc.md) — append `DATA_SUFFIX` to transaction data for ethers.js or raw `window.ethereum`.

**Preferred approach**: Configure at the **client level** so all transactions are automatically attributed. Only use the per-transaction approach if you need conditional attribution.

For Smart Wallets (EIP-5792 `sendCalls`): See [references/smart-wallets.md](references/smart-wallets.md) — pass via `capabilities`.

### Step 5: Verify attribution

1. **base.dev**: Check Onchain > Total Transactions for attribution counts
2. **Block explorer**: Find tx hash, view input data, confirm last 16 bytes are `8021` repeating
3. **Validation tool**: Use [builder-code-checker.vercel.app](https://builder-code-checker.vercel.app/)

## Key Facts

- Builder Codes are ERC-721 NFTs minted on Base
- The suffix is appended to calldata; smart contracts ignore it (no upgrades needed)
- Gas cost is negligible: 16 gas per non-zero byte
- Analytics on base.dev currently support Smart Account (AA) transactions; EOA support is coming (attribution data is preserved)
- The `dataSuffix` plugin in Privy appends to **all chains**, not just Base. If chain-specific behavior is needed, contact Privy
- Privy's `dataSuffix` plugin is NOT yet supported with `@privy-io/wagmi` adapter


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
| `scripts/main.py` | adding-builder-codes script | Run with python3 |

## Key References

- **Privy**: [references/privy.md](references/privy.md)
- **Skill**: [references/SKILL.md](references/SKILL.md)
- **Viem**: [references/viem.md](references/viem.md)
- **Smart Wallets**: [references/smart-wallets.md](references/smart-wallets.md)
- **Wagmi**: [references/wagmi.md](references/wagmi.md)
- **Rpc**: [references/rpc.md](references/rpc.md)

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

## Finding Transaction Call Sites

When retrofitting an existing project, search for these patterns:

```bash
# React hooks (Wagmi)
grep -rn "useSendTransaction\|useSendCalls\|useWriteContract\|useContractWrite" src/

# Viem client calls
grep -rn "sendTransaction\|writeContract\|sendRawTransaction" src/

# Privy embedded wallet calls
grep -rn "sendTransaction\|signTransaction" src/

# ethers.js
grep -rn "signer\.sendTransaction\|contract\.connect" src/

# Raw window.ethereum
grep -rn "window\.ethereum\|eth_sendTransaction" src/
```

For client-level integration (Wagmi/Viem/Privy), you typically only need to modify the config file — individual transaction call sites remain unchanged.

## Sources

- **Base Builder Codes**: https://docs.base.org
- **ERC-8021 Attribution**: https://eips.ethereum.org/EIPS/eip-8021
- **Vercel Deployment**: https://vercel.com/docs
- **ox Library**: https://oxcl.sh
