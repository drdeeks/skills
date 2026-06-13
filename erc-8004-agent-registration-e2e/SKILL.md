---
name: erc-8004-agent-registration-e2e
description: "End-to-end agent registration: Base builder code, AgentMail inbox, Pinata IPFS, ERC-8004 NFT mint, and ownership transfer. Complete walkthrough for registering an AI agent on-chain."
version: 0.0.5
---

# ERC-8004 Agent Registration — End-to-End

Complete workflow for registering an AI agent on-chain from scratch. Covers:
1. Base builder code registration (ERC-8021 attribution)
2. AgentMail inbox creation (for service signups)
3. Pinata account setup and IPFS storage
4. Agent card creation and upload
5. ERC-8004 NFT minting on Base mainnet
6. Ownership transfer

## Prerequisites
- Node.js with `viem`, `ox` packages installed
- AgentMail Python SDK (`pip install agentmail`)
- A funded wallet (ETH on Base mainnet for gas)

## Step 1: Register Builder Code

```bash
curl -s -X POST "https://api.base.dev/v1/agents/builder-codes" \
  -H "Content-Type: application/json" \
  -d '{"wallet_address": "0xYOUR_WALLET"}'
```

Save the `builder_code` value to `src/constants/builderCode.ts`.

## Step 2: Create AgentMail Inbox

```python
from agentmail import AgentMail
client = AgentMail()
inbox = client.inboxes.create(client_id="my-agent")
print(inbox.inbox_id)  # my-agent@agentmail.to
```

Use this inbox email to sign up for Pinata.

## Step 3: Set Up Pinata

1. Sign up at https://app.pinata.cloud/auth/signup using the AgentMail inbox
2. Verify email via AgentMail inbox
3. Get JWT from https://app.pinata.cloud/developers/api-keys
4. Save to `.secrets/.pinata-access`

## Step 4: Upload Avatar to IPFS

```bash
PINATA_JWT=$(grep PINATA_JWT .secrets/.pinata-access | cut -d= -f2-)
curl -s -X POST "https://uploads.pinata.cloud/v3/files" \
  -H "Authorization: Bearer $PINATA_JWT" \
  -F "file=@assets/images/avatar.png" \
  -F "name=agent-avatar.png" \
  -F "network=public"
```

## Step 5: Create and Upload Agent Card

Create `agent-card.json`:
```json
{
  "name": "Agent Name",
  "description": "What this agent does",
  "image": "ipfs://AVATAR_CID",
  "endpoints": { "a2a": "https://..." },
  "trustModels": ["stake-secured"],
  "paymentWallet": "0xYOUR_WALLET",
  "builderCode": "bc_YOUR_CODE"
}
```

Upload to Pinata (same curl as above, different file).

## Step 6: Register On-Chain (Base Mainnet)

**Critical: Use object ABI format for viem, NOT strings.**

```js
const REGISTRY = '0x8004A169FB4a3325136EB29fA0ceB6D2e539a432';
const ABI_SET_URI = [{
  inputs: [{name:'agentId',type:'uint256'},{name:'newURI',type:'string'}],
  name: 'setAgentURI', outputs: [], stateMutability: 'nonpayable', type: 'function'
}];

// 1. Register (mint NFT)
const hash = await wc.writeContract({
  address: REGISTRY,
  abi: [{ inputs: [], name: 'register', outputs: [{type:'uint256'}], stateMutability:'nonpayable', type:'function' }],
  functionName: 'register'
});
const receipt = await pc.waitForTransactionReceipt({ hash });
const tokenId = BigInt(receipt.logs.find(l => l.topics[0] === '0xddf252ad...').topics[3]);

// 2. Set URI
await wc.writeContract({
  address: REGISTRY, abi: ABI_SET_URI,
  functionName: 'setAgentURI',
  args: [tokenId, 'ipfs://AGENT_CARD_CID']
});
```

## Step 7: Transfer Ownership (Optional)

```js
await wc.writeContract({
  address: REGISTRY,
  abi: [{ inputs: [{name:'from',type:'address'},{name:'to',type:'address'},{name:'tokenId',type:'uint256'}],
          name: 'transferFrom', outputs: [], stateMutability: 'nonpayable', type: 'function' }],
  functionName: 'transferFrom',
  args: [myWallet, newOwnerWallet, tokenId]
});
```

**After transfer:** Only the new owner can call `setAgentURI`. Update the agent card JSON with the new owner and re-upload to IPFS, then have the new owner update the on-chain URI.

## Step 8: Wire Builder Code Attribution

Every transaction must include the ERC-8021 data suffix:

```js
import { Attribution } from 'ox/erc8021';
const DATA_SUFFIX = Attribution.toDataSuffix({ codes: ['bc_YOUR_CODE'] });

const walletClient = createWalletClient({
  account, chain: base, transport: http(), dataSuffix: DATA_SUFFIX
});
```

## Secrets Structure

```
.secrets/             (mode 700)
├── .wallet           — PRIVATE_KEY + WALLET_ADDRESS
├── .pinata-access    — PINATA_JWT, API key/secret, gateway
├── .agentmail-NAME   — AGENTMAIL_API_KEY, inbox address
```

## Supported Networks

| Network | Chain ID | Registry |
|---------|----------|----------|
| Base Mainnet | 8453 | `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` |
| Ethereum Mainnet | 1 | `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` |
| Base Sepolia | 84532 | `0x8004A818BFB912233c491871b3d84c89A494BD9e` |
| Monad Testnet | 10143 | `0x8004BAa17C55a88189AE136b182e5fdA19dE9b63` |


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
| `scripts/main.py` | erc-8004-agent-registration-e2e script | Run with python3 |

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

## Pitfalls

- **viem ABI must be object array** — string ABIs or wrong key ordering causes cryptic reverts
- **"Not authorized" after transfer** — only current owner can set URI
- **Private key needs 0x prefix** — `0x' + key.replace(/^0x/, '')`
- **AgentMail CLI vs Python** — `pip install agentmail` needs Python 3.12+, not the hermes venv (3.11)
- **Pinata rate limits** — browser signup hits rate limits fast; use API for bulk operations
