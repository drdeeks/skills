---
name: running-a-base-node
description: Runs a Base node for production environments. Covers hardware requirements,
license: MIT
version: 0.0.3
---
# Running a Base Node

For production apps requiring reliable, unlimited RPC access.

## Security

- **Restrict RPC access** — bind to `127.0.0.1` or a private interface, never expose RPC ports (`8545`/`8546`) to the public internet without authentication
- **Firewall rules** — only open ports 9222 (Discovery v5) and 30303 (P2P) to the public; block all other inbound traffic
- **Run as a non-root user** with minimal filesystem permissions
- **Use TLS termination** (reverse proxy with nginx/caddy) if exposing the RPC endpoint to remote clients
- **Monitor for unauthorized access** — log and alert on unexpected RPC calls or connection spikes

## Hardware Requirements

- **CPU**: 8-Core minimum
- **RAM**: 16 GB minimum
- **Storage**: NVMe SSD, formula: `(2 × chain_size) + snapshot_size + 20% buffer`

## Networking

**Required Ports:**
- **Port 9222**: Critical for Reth Discovery v5
- **Port 30303**: P2P Discovery & RLPx

If these ports are blocked, the node will have difficulty finding peers and syncing.

## Client Selection

Use **Reth** for Base nodes. Geth Archive Nodes are no longer supported.

Reth provides:
- Better performance for high-throughput L2
- Built-in archive node support

## Syncing

- Initial sync takes **days**
- Consumes significant RPC quota if using external providers
- Use snapshots to accelerate (check Base docs for URLs)


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
| `scripts/main.py` | running-a-base-node script | Run with python3 |

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

## Sync Status

**Incomplete sync indicator**: `Error: nonce has already been used` when deploying.

Verify sync:
- Compare latest block with explorer
- Check peer connections
- Monitor logs for progress
