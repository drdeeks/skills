---
name: "8004"
description: "Agent identity, discovery, and trust protocol (ERC-8004). Enables open-ended agent economies via on-chain identity registry, reputation registry, and validation registry."
allowed-tools:
  - bash
  - read
  - write
  - edit
  - webfetch
  - websearch
metadata:
  version: "2.0.0"
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
version: 0.0.1
---

# 8004 - Trustless Agent Identity Protocol

## Overview

ERC-8004 is a standards-track protocol that uses blockchains to **discover, choose, and interact with agents across organizational boundaries** without pre-existing trust, enabling open-ended agent economies.

## Three Registries

### 1. Identity Registry (ERC-721 + URIStorage)

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

### 2. Reputation Registry

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

### 3. Validation Registry

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

## Trust Tiers (8004scan scoring)

| Tier | Score | Description |
|------|-------|-------------|
| Unverified | 0-24 | No trust signals |
| Bronze | 25-49 | Basic verification |
| Silver | 50-69 | Moderate trust |
| Gold | 70-84 | High trust |
| Platinum | 85-94 | Very high trust |
| Diamond | 95-100 | Maximum trust |

## Registration Requirements

1. **Agent URI** must resolve to a valid registration file
2. **On-chain registration** via Identity Registry contract
3. **Services array** listing all communication endpoints (A2A, MCP, ENS, DID, etc.)
4. **Registrations array** with agentId and agentRegistry for each chain
5. **Owner wallet** must prove control via EIP-712 (EOA) or ERC-1271 (smart contract)

## Deployment Addresses

- **Base (8453)**: Identity Registry deployed
- **Ethereum (1)**: Identity Registry deployed
- **Monad (143)**: Identity Registry deployed


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
| `scripts/validate.py` | 8004 script | Run with python3 |
| `scripts/main.py` | 8004 script | Run with python3 |

## Key References

- **ERC-8004 Official**: [references/erc-8004-official.md](references/erc-8004-official.md)
- **Chains**: [references/chains.md](references/chains.md)
- **SDK Usage**: [references/sdk-usage.md](references/sdk-usage.md)
- **Identity Registry**: [references/identity-registry.md](references/identity-registry.md)
- **Protocol**: [references/protocol.md](references/protocol.md)
- **Reputation Registry**: [references/reputation-registry.md](references/reputation-registry.md)
- **Trust Model**: [references/trust-model.md](references/trust-model.md)
- **Python Recipes**: [references/python-recipes.md](references/python-recipes.md)
- **Agent Schema**: [references/agent-schema.md](references/agent-schema.md)
- **Integration**: [references/integration.md](references/integration.md)
- **Validation Registry**: [references/validation-registry.md](references/validation-registry.md)
## Usage

Use this skill to:
- Register agents on ERC-8004
- Query agent identity and services
- Submit feedback or validation signals
- Check trust scores and reputation
- Discover agents across chains