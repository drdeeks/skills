---
name: base-agent-bootstrap
description: "Complete end-to-end setup for a Base agent: builder code registration, ERC-8021 attribution (viem), Pinata IPFS account via AgentMail, and workspace secrets organization. Use when setting up a new agent on Base with onchain attribution."
metadata:
  hermes:
    tags: [base, builder-code, erc-8021, pinata, agentmail, onboarding]
    related_skills: [registering-agent-base-dev, pinata-erc-8004, multi-agent-workspace-setup]
version: 0.0.5
---

# Base Agent Bootstrap

End-to-end setup for a new agent on Base with builder code attribution, Pinata IPFS, and proper secrets management.

## Prerequisites

- A wallet for the agent (dedicated, not personal)
- Workspace under `~/hermes-agent/workspaces/<agent-id>/`

## Step 1: Register Builder Code

Use `curl` (NOT `urllib` — it gets 403 on `api.base.dev`):

```bash
curl -s -X POST "https://api.base.dev/v1/agents/builder-codes" \
  -H "Content-Type: application/json" \
  -d '{"wallet_address": "0xYOUR_WALLET"}'
```

Response: `{"builderCode":"bc_xxxxxxxx", "walletAddress":"0x..."}`

Save to `src/constants/builderCode.ts` and `builderCode.ts` at project root.

**Gotcha:** If the API returns 403, retry with `curl`. The `urllib` Python approach consistently fails.

## Step 2: Wire ERC-8021 Attribution (viem)

Install: `npm i ox viem`

Create `src/walletClient.ts`:

```typescript
import { createWalletClient, http } from "viem"
import { base } from "viem/chains"
import { privateKeyToAccount } from "viem/accounts"
import { Attribution } from "ox/erc8021"
import { BUILDER_CODE } from "./constants/builderCode"

const DATA_SUFFIX = Attribution.toDataSuffix({ codes: [BUILDER_CODE] })
const account = privateKeyToAccount(process.env.PRIVATE_KEY as `0x${string}`)

export const walletClient = createWalletClient({
  account,
  chain: base,
  transport: http(),
  dataSuffix: DATA_SUFFIX,
})
```

Every transaction via `walletClient` automatically carries the builder code.

## Step 3: Set Up Pinata via AgentMail

### 3a: Create AgentMail inbox

```python
# Requires python3.12 explicitly (hermes venv is 3.11)
python3.12 -c "
from agentmail import AgentMail
client = AgentMail(api_key='YOUR_AGENTMAIL_KEY')
inbox = client.inboxes.create(client_id='agent-<id>-pinata')
print(inbox.inbox_id)
"
```

### 3b: Sign up for Pinata

1. Navigate to `https://app.pinata.cloud/auth/signup`
2. Fill form with AgentMail inbox address
3. Check inbox for verification link via AgentMail API
4. **Open verification link immediately** (expires in 10 minutes)
5. Complete onboarding, select Free plan
6. Go to Developers > API Keys, copy JWT

**Gotcha:** Pinata rate-limits aggressively. Wait 60-120s between sign-in attempts.

### 3c: Verify JWT works

```bash
curl -s -X GET "https://api.pinata.cloud/data/testAuthentication" \
  -H "Authorization: Bearer YOUR_JWT"
```

### 3d: Get gateway URL

```bash
curl -s -X GET "https://api.pinata.cloud/v3/ipfs/gateways" \
  -H "Authorization: Bearer YOUR_JWT"
```

Domain is in `data.rows[0].domain` → full URL: `https://DOMAIN.mypinata.cloud`

## Step 4: Organize Secrets

Per multi-agent workspace conventions:

```
.secrets/                          # mode 700
├── .wallet                        # mode 600 — PRIVATE_KEY + WALLET_ADDRESS
├── .pinata-access                 # mode 600 — PINATA_JWT, API_KEY, API_SECRET, GATEWAY_URL
└── .agentmail-agent-<id>          # mode 600 — AGENTMAIL_API_KEY, INBOX
```

`.env` should only have a comment referencing how to source them:
```bash
# source .secrets/.pinata-access && source .secrets/.agentmail-agent-<id> && source .secrets/.wallet
```

## Step 5: Update agent.json

Update `builderCode` and `builder_code_enforcement` sections with the new code and wallet.

## Verification

- [ ] `builderCode.ts` exists with correct code
- [ ] `src/walletClient.ts` compiles
- [ ] Pinata JWT passes testAuthentication
- [ ] `.secrets/` has mode 700, files have mode 600
- [ ] `agent.json` has updated builder code
- [ ] Systemd service `WorkingDirectory` points to workspace


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
| `scripts/main.py` | base-agent-bootstrap script | Run with python3 |

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

- **urllib vs curl**: `api.base.dev` returns 403 via Python urllib; always use curl
- **Python version**: hermes venv is 3.11, agentmail needs 3.12 — use `python3.12` explicitly
- **Rate limits**: Pinata sign-in is rate-limited; space attempts 60-120s apart
- **Verification expiry**: Email verification links expire in 10 minutes — act fast
- **Re-registration**: If `builderCode.ts` exists, do NOT re-register (generates new code, breaks existing one)
