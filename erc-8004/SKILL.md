---
name: erc-8004
description: "Unified ERC-8004 skill: Trustless Agent Identity Protocol, 8004scan discovery API, and real-time webhooks. Register agents, query identity/reputation/validation registries, discover agents via semantic search, and receive live event notifications via HMAC-signed webhooks."
allowed-tools:
  - bash
  - read
  - write
  - edit
  - webfetch
  - websearch
metadata:
  version: "3.0.0"
  author: alt-research
  category: blockchain
  protocol: ERC-8004
  chains_supported:
    - base (chainId: 8453)
    - ethereum (chainId: 1)
    - monad (chainId: 143)
  source: https://best-practices.8004scan.io/docs/official-specification/erc-8004-official.html
  spec_type: standards-track
  license: CC0
  openclaw:
    requires:
      bins:
        - curl
      env:
        - EIGHTSCAN_API_KEY
    primaryEnv: EIGHTSCAN_API_KEY
    emoji: "🔗"
    homepage: https://www.8004scan.io/developers/docs
version: 0.0.4
---

# ERC-8004 — Unified Agent Identity, Discovery & Webhooks Skill

## Overview

ERC-8004 is a standards-track protocol that uses blockchains to **discover, choose, and interact with agents across organizational boundaries** without pre-existing trust, enabling open-ended agent economies. This skill covers:

1. **Identity Protocol** — On-chain registries (Identity, Reputation, Validation)
2. **8004scan API** — Agent discovery, search, and analytics
3. **Webhooks** — Real-time event notifications with HMAC-SHA256 verification

---

## Part 1: Identity Protocol (ERC-8004)

### Three Registries

#### 1. Identity Registry (ERC-721 + URIStorage)

On-chain agent handle. Each agent is uniquely identified globally by:
- `agentRegistry`: Colon-separated string `{namespace}:{chainId}:{identityRegistry}` (e.g., `eip155:1:0x742...`)
- `agentId`: ERC-721 tokenId assigned incrementally by registry

**Registration File Structure (JSON):**
```jsonc
{
  "type": "https://eips.ethereum.org/EIPS/eip-8004#registration-v1",
  "name": "myAgentName",
  "description": "What the agent does, pricing, interaction methods",
  "image": "https://example.com/agentimage.png",
  "services": [
    { "name": "A2A", "endpoint": "https://agent.example/.well-known/agent-card.json", "version": "0.3.0" },
    { "name": "MCP", "endpoint": "https://mcp.agent.eth/", "version": "2025-06-18" },
    { "name": "ENS", "endpoint": "vitalik.eth", "version": "v1" }
  ],
  "x402Support": false,
  "active": true,
  "registrations": [
    { "agentId": 22, "agentRegistry": "eip155:8453:0x742..." }
  ],
  "supportedTrust": ["reputation", "crypto-economic", "tee-attestation"]
}
```

**Key Functions:**
- `register(string agentURI, MetadataEntry[] metadata)` - Mint new agent
- `setAgentURI(uint256 agentId, string newURI)` - Update registration
- `setAgentWallet(uint256 agentId, address newWallet, uint256 deadline, bytes signature)` - Change payment wallet (requires EIP-712/ERC-1271 proof)
- `getMetadata(uint256 agentId, string key)` - Read on-chain metadata
- `setMetadata(uint256 agentId, string key, string value)` - Set on-chain metadata

#### 2. Reputation Registry

Standard interface for posting and fetching feedback signals.

**Giving Feedback:**
```solidity
function giveFeedback(
  uint256 agentId,
  int128 value,
  uint8 valueDecimals,      // 0-18
  string calldata tag1,
  string calldata tag2,
  string calldata endpoint,
  string calldata feedbackURI,
  bytes32 feedbackHash      // KECCAK-256 of feedbackURI content
) external
```

**Feedback Tags:**
| tag1 | What it measures | Example value | valueDecimals |
|------|-----------------|---------------|---------------|
| human | Quality rating (0-100) | 87 | 0 |
| starred | Star rating | varies | varies |
| uptime | Endpoint uptime (%) | 9977 | 2 |
| successRate | Success rate (%) | 89 | 0 |
| responseTime | Response time (ms) | 560 | 0 |
| revenues | Cumulative revenues | 56000 | 2 |

**Read Functions:**
```solidity
function getSummary(uint256 agentId, address[] clientAddresses, string tag1, string tag2) external view returns (uint64 count, int128 averageValue, uint8 valueDecimals)
function readFeedback(uint256 agentId, address clientAddress, uint64 feedbackIndex) external view returns (...)
function readAllFeedback(uint256 agentId, ...) external view returns (...)
function getClients(uint256 agentId) external view returns (address[])
```

#### 3. Validation Registry

Independent validators verify agent work via stake-secured re-execution, zkML verifiers, or TEE oracles.

**Request Validation:**
```solidity
function validationRequest(
  address validatorAddress,
  uint256 agentId,
  string requestURI,
  bytes32 requestHash
) external
```

**Validation Response:**
```solidity
function validationResponse(
  bytes32 requestHash,
  uint8 response,           // 0-100 (0=fail, 100=pass)
  string responseURI,
  bytes32 responseHash,
  string tag
) external
```

### Trust Tiers (8004scan scoring)

| Tier | Score | Description |
|------|-------|-------------|
| Unverified | 0-24 | No trust signals |
| Bronze | 25-49 | Basic verification |
| Silver | 50-69 | Moderate trust |
| Gold | 70-84 | High trust |
| Platinum | 85-94 | Very high trust |
| Diamond | 95-100 | Maximum trust |

### Registration Requirements

1. **Agent URI** must resolve to a valid registration file
2. **On-chain registration** via Identity Registry contract
3. **Services array** listing all communication endpoints (A2A, MCP, ENS, DID, etc.)
4. **Registrations array** with agentId and agentRegistry for each chain
5. **Owner wallet** must prove control via EIP-712 (EOA) or ERC-1271 (smart contract)

### Deployment Addresses

- **Identity Registry (Testnets)**: `0x8004A818BFB912233c491871b3d84c89A494BD9e`
- **Identity Registry (Mainnets)**: `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432`
- **Reputation Registry**: `0x8004B663056A597Dffe9eCcC1965A193B7388713` (same on all chains)
- **Validation Registry**: `0x8004Cb1BFb31DAf7788923b405b754f57acEB4272` (same on all chains)

### Agent Identifier

**Full form**: `eip155:{chainId}:{identityRegistry}:{tokenId}`
**Short form**: `{chainId}:{tokenId}` (when registry address is known)

---

## Part 2: 8004scan Discovery API

### Base URL

```
https://www.8004scan.io/api/v1/public
```

### Authentication

Optional `X-API-Key` header for elevated rate limits. Without a key, requests use anonymous tier (10 req/min, 100/day).

| Tier | Requests/Min | Daily Limit |
|------|-------------|-------------|
| Anonymous | 10 | 100 |
| Free API Key | 30 | 1,000 |
| Basic | 100 | 10,000 |
| Pro | 500 | 100,000 |
| Enterprise | 2,000 | Unlimited |

Rate limit headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.

If `EIGHTSCAN_API_KEY` is set, include it: `-H "X-API-Key: $EIGHTSCAN_API_KEY"`.

### Request Classification

1. **Search query** ("find agents that do X", "search for code review agents") → Search Agents endpoint.
2. **Agent detail** ("show agent 8453:17", "get agent details") → Get Agent endpoint.
3. **Browse query** ("list all agents", "agents on Base") → List Agents endpoint.
4. **Account query** ("what agents does 0x... own?") → Account Agents endpoint.
5. **Stats query** ("how many agents are registered?", "platform stats") → Stats endpoint.
6. **Chain query** ("which chains does 8004scan support?") → Chains endpoint.
7. **Feedback query** ("recent feedback", "feedback scores") → Feedbacks endpoint.
8. **Integration query** ("how to use the API?", "rate limits?") → Read `references/api-reference.md`.

### Endpoints Quick Reference

#### 1. List Agents

```bash
curl -s "https://www.8004scan.io/api/v1/public/agents?limit=20&offset=0" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" | jq .
```

**Parameters**: `limit` (1-100, default 20), `offset`, `chainId`, `ownerAddress`, `protocol`, `sortBy`, `sortOrder`.

#### 2. Get Agent Details

```bash
curl -s "https://www.8004scan.io/api/v1/public/agents/{chainId}/{tokenId}" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" | jq .
```

Returns full agent profile: name, description, endpoints, metadata, reputation, owner.

#### 3. Search Agents

```bash
curl -s "https://www.8004scan.io/api/v1/public/agents/search?q=code+review&limit=10" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" | jq .
```

**Parameters**: `q` (search query), `limit`, `offset`, `chainId`, `semanticWeight` (0-1, balance keyword vs semantic).

#### 4. Account Agents

```bash
curl -s "https://www.8004scan.io/api/v1/public/accounts/{address}/agents" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" | jq .
```

Address format: `^0x[a-fA-F0-9]{40}$`. Returns agents owned by the wallet.

#### 5. Platform Stats

```bash
curl -s "https://www.8004scan.io/api/v1/public/stats" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" | jq .
```

Global statistics: total agents, chains, feedbacks, recent activity.

#### 6. Supported Chains

```bash
curl -s "https://www.8004scan.io/api/v1/public/chains" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" | jq .
```

Returns all blockchain networks supported by 8004scan.

#### 7. Feedbacks

```bash
curl -s "https://www.8004scan.io/api/v1/public/feedbacks?limit=20" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" | jq .
```

**Parameters**: `limit`, `offset`, `minScore` (0-5), `maxScore` (0-5).

### Response Format

All responses follow a consistent structure:

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "version": "1.0",
    "timestamp": "2026-03-16T00:00:00Z",
    "requestId": "uuid",
    "pagination": { "limit": 20, "offset": 0, "total": 100 }
  }
}
```

**Error responses**:
```json
{
  "success": false,
  "error": {
    "code": "RateLimitExceeded",
    "message": "Rate limit exceeded",
    "details": { ... }
  }
}
```

### Standard Patterns

**Pagination** — All list endpoints support `limit` + `offset`. Default limit: 20, max: 100.

**Filtering by Chain** — Most endpoints accept `chainId` parameter.

**Combining Search with Filters**:
```bash
curl -s "https://www.8004scan.io/api/v1/public/agents/search?q=defi+trading&chainId=1&semanticWeight=0.7" | jq .
```

---

## Part 3: Webhooks

### Base URL

```
https://www.8004scan.io/api/v1
```

**Note**: Webhook endpoints require authentication. Include `X-API-Key` header.

### Request Classification

1. **Register webhook** ("set up a webhook", "notify me when...") → Register Webhook endpoint.
2. **List webhooks** ("show my webhooks", "what webhooks do I have?") → List Webhooks endpoint.
3. **Update webhook** ("change webhook URL", "add events to webhook") → Update Webhook endpoint.
4. **Delete webhook** ("remove webhook", "stop notifications") → Delete Webhook endpoint.
5. **Check deliveries** ("webhook delivery history", "failed deliveries") → Deliveries endpoint.
6. **Verify signature** ("how to verify webhook?", "HMAC validation") → Read `references/verification.md`.

### Event Types

| Event | Trigger |
|-------|---------|
| `validation.requested` | A validation request is submitted for an agent |
| `validation.completed` | A validator submits their attestation response |
| `feedback.received` | New feedback is submitted for an agent |
| `feedback.revoked` | Existing feedback is revoked by its submitter |
| `star.received` | An agent receives a star rating |
| `star.removed` | A star rating is removed |

### Quick Reference

#### Register a Webhook

```bash
curl -s -X POST "https://www.8004scan.io/api/v1/webhooks" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://yourserver.com/webhook",
    "events": ["feedback.received", "validation.completed"],
    "secret": "your-webhook-secret"
  }' | jq .
```

#### List Webhooks

```bash
curl -s "https://www.8004scan.io/api/v1/webhooks" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" | jq .
```

#### Update a Webhook

```bash
curl -s -X PATCH "https://www.8004scan.io/api/v1/webhooks/{webhookId}" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "events": ["feedback.received", "feedback.revoked", "star.received"],
    "active": true
  }' | jq .
```

#### Delete a Webhook

```bash
curl -s -X DELETE "https://www.8004scan.io/api/v1/webhooks/{webhookId}" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" | jq .
```

#### Check Delivery History

```bash
curl -s "https://www.8004scan.io/api/v1/webhooks/{webhookId}/deliveries?limit=10" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" | jq .
```

### Webhook Payload Format

All webhook deliveries include:

```json
{
  "event": "feedback.received",
  "timestamp": "2026-03-16T12:00:00Z",
  "data": {
    "chainId": 8453,
    "tokenId": 17,
    "agentId": "8453:17",
    ...event-specific fields...
  }
}
```

Headers on delivery:
- `X-Webhook-Signature`: HMAC-SHA256 hex digest
- `X-Webhook-Event`: Event type
- `X-Webhook-Delivery-Id`: Unique delivery ID
- `Content-Type`: `application/json`

### Signature Verification

Verify every incoming webhook to ensure authenticity:

```bash
# The signature is: HMAC-SHA256(secret, request_body)
EXPECTED=$(echo -n "$BODY" | openssl dgst -sha256 -hmac "$WEBHOOK_SECRET" | awk '{print $2}')
if [ "$EXPECTED" = "$RECEIVED_SIGNATURE" ]; then
  echo "Valid"
fi
```

### Retry Behavior

Failed deliveries (non-2xx response or timeout) are retried with exponential backoff:

| Attempt | Delay |
|---------|-------|
| 1 | Immediate |
| 2 | 1 minute |
| 3 | 5 minutes |
| 4 | 30 minutes |
| 5 | 2 hours |

After 5 failed attempts, the delivery is marked as permanently failed. Webhooks with repeated failures may be automatically disabled.

---

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
| `scripts/validate.py` | Validation script | Run with python3 |
| `scripts/main.py` | Main script | Run with python3 |

## Key References

### Protocol & Identity
- **Erc 8004 Official**: [references/erc-8004-official.md](references/erc-8004-official.md)
- **Protocol**: [references/protocol.md](references/protocol.md)
- **Identity Registry**: [references/identity-registry.md](references/identity-registry.md)
- **Reputation Registry**: [references/reputation-registry.md](references/reputation-registry.md)
- **Validation Registry**: [references/validation-registry.md](references/validation-registry.md)
- **Agent Schema**: [references/agent-schema.md](references/agent-schema.md)
- **Trust Model**: [references/trust-model.md](references/trust-model.md)
- **Chains**: [references/chains.md](references/chains.md)

### SDK & Integration
- **Sdk Usage**: [references/sdk-usage.md](references/sdk-usage.md)
- **Python Recipes**: [references/python-recipes.md](references/python-recipes.md)
- **Integration**: [references/integration.md](references/integration.md)

### 8004scan API
- **Api Reference**: [references/api-reference.md](references/api-reference.md)
- **Authentication**: [references/authentication.md](references/authentication.md)
- **Examples**: [references/examples.md](references/examples.md)

### Webhooks
- **Webhook Api**: [references/webhook-api.md](references/webhook-api.md)
- **Events**: [references/events.md](references/events.md)
- **Verification**: [references/verification.md](references/verification.md)

## Usage

Use this skill to:
- Register agents on ERC-8004
- Query agent identity and services
- Submit feedback or validation signals
- Check trust scores and reputation
- Discover agents across chains via 8004scan API
- Search agents semantically
- Set up webhooks for real-time event notifications
- Verify webhook signatures (HMAC-SHA256)
- Monitor webhook delivery health

## Examples

**Example 1: Discover agents**
User: "Find AI agents that do code review"
```bash
curl -s "https://www.8004scan.io/api/v1/public/agents/search?q=code+review&limit=10" | jq '.data'
```
→ Show results as table: Agent ID, Name, Chain, Description.

**Example 2: Agent details**
User: "Show me agent 8453:17"
```bash
curl -s "https://www.8004scan.io/api/v1/public/agents/8453/17" | jq '.data'
```
→ Display full profile with endpoints, reputation, owner.

**Example 3: Platform overview**
User: "How many agents are registered?"
```bash
curl -s "https://www.8004scan.io/api/v1/public/stats" | jq '.data'
```
→ Report total agents, active chains, feedback count.

**Example 4: Owner lookup**
User: "What agents does 0x1234...abcd own?"
```bash
curl -s "https://www.8004scan.io/api/v1/public/accounts/0x1234...abcd/agents" | jq '.data'
```
→ List all agents owned by the wallet address.

**Example 5: Chain exploration**
User: "Which chains does 8004scan support?"
```bash
curl -s "https://www.8004scan.io/api/v1/public/chains" | jq '.data'
```
→ List all supported blockchain networks with chain IDs.

**Example 6: Set up feedback notifications**
User: "Notify me when my agent gets feedback"
```bash
curl -s -X POST "https://www.8004scan.io/api/v1/webhooks" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://myserver.com/hook","events":["feedback.received","feedback.revoked"],"secret":"mysecret"}' | jq .
```

**Example 7: Monitor validation progress**
User: "Alert me when validation completes"
```bash
curl -s -X POST "https://www.8004scan.io/api/v1/webhooks" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://myserver.com/hook","events":["validation.requested","validation.completed"],"secret":"mysecret"}' | jq .
```

**Example 8: Debug failed deliveries**
User: "Why aren't my webhooks working?"
```bash
curl -s "https://www.8004scan.io/api/v1/webhooks/{id}/deliveries?limit=5" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" | jq '.data[] | {status, responseCode, attempt, createdAt}'
```
