---
name: 8004scan
description: "Query the 8004scan public API to discover, search, and analyze ERC-8004 agents and validations across supported chains"
version: 0.0.3
license: MIT
allowed-tools: "Bash(curl:*) Bash(jq:*)"
metadata:
  openclaw:
    version: "1.0"
    category: blockchain
    complexity: standard
---

## Base URL

```
https://www.8004scan.io/api/v1/public
```

## Authentication

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

---

## Request Classification

1. **Search query** ("find agents that do X", "search for code review agents") → Search Agents endpoint.
2. **Agent detail** ("show agent 8453:17", "get agent details") → Get Agent endpoint.
3. **Browse query** ("list all agents", "agents on Base") → List Agents endpoint.
4. **Account query** ("what agents does 0x... own?") → Account Agents endpoint.
5. **Stats query** ("how many agents are registered?", "platform stats") → Stats endpoint.
6. **Chain query** ("which chains does 8004scan support?") → Chains endpoint.
7. **Feedback query** ("recent feedback", "feedback scores") → Feedbacks endpoint.
8. **Integration query** ("how to use the API?", "rate limits?") → Read `references/api-reference.md`.

---

## Endpoints Quick Reference

### 1. List Agents

```bash
curl -s "https://www.8004scan.io/api/v1/public/agents?limit=20&offset=0" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" | jq .
```

**Parameters**: `limit` (1-100, default 20), `offset`, `chainId`, `ownerAddress`, `protocol`, `sortBy`, `sortOrder`.

### 2. Get Agent Details

```bash
curl -s "https://www.8004scan.io/api/v1/public/agents/{chainId}/{tokenId}" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" | jq .
```

Returns full agent profile: name, description, endpoints, metadata, reputation, owner.

### 3. Search Agents

```bash
curl -s "https://www.8004scan.io/api/v1/public/agents/search?q=code+review&limit=10" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" | jq .
```

**Parameters**: `q` (search query), `limit`, `offset`, `chainId`, `semanticWeight` (0-1, balance keyword vs semantic).

### 4. Account Agents

```bash
curl -s "https://www.8004scan.io/api/v1/public/accounts/{address}/agents" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" | jq .
```

Address format: `^0x[a-fA-F0-9]{40}$`. Returns agents owned by the wallet.

### 5. Platform Stats

```bash
curl -s "https://www.8004scan.io/api/v1/public/stats" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" | jq .
```

Global statistics: total agents, chains, feedbacks, recent activity.

### 6. Supported Chains

```bash
curl -s "https://www.8004scan.io/api/v1/public/chains" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" | jq .
```

Returns all blockchain networks supported by 8004scan.

### 7. Feedbacks

```bash
curl -s "https://www.8004scan.io/api/v1/public/feedbacks?limit=20" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" | jq .
```

**Parameters**: `limit`, `offset`, `minScore` (0-5), `maxScore` (0-5).

---

## Response Format

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

---

## Standard Patterns

### Pagination

All list endpoints support `limit` + `offset`. Default limit: 20, max: 100. To iterate:

```bash
# Page 1
curl -s "https://www.8004scan.io/api/v1/public/agents?limit=100&offset=0" | jq .
# Page 2
curl -s "https://www.8004scan.io/api/v1/public/agents?limit=100&offset=100" | jq .
```

### Filtering by Chain

Most endpoints accept `chainId` parameter to scope results to a specific network:

```bash
# Only Base Mainnet agents
curl -s "https://www.8004scan.io/api/v1/public/agents?chainId=8453" | jq .
```

### Combining Search with Filters

```bash
# Semantic search on Ethereum mainnet
curl -s "https://www.8004scan.io/api/v1/public/agents/search?q=defi+trading&chainId=1&semanticWeight=0.7" | jq .
```

### Error Handling

- **400 BadRequest** — Check query parameters
- **404 NotFound** — Verify chainId and tokenId exist
- **429 RateLimitExceeded** — Wait for `X-RateLimit-Reset`, or upgrade API tier
- **500 InternalError** — Retry after brief delay

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
| `scripts/main.py` | 8004scan script | Run with python3 |

## Key References

- **API Reference**: [references/api-reference.md](references/api-reference.md)
- **Authentication**: [references/authentication.md](references/authentication.md)
- **Examples**: [references/examples.md](references/examples.md)

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