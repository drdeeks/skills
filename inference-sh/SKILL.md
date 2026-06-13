---
name: inference-sh
description: "Run 150+ AI applications via inference.sh. Image generation, video creation, LLMs, search, 3D, and more through a single API key and unified interface."
license: MIT
metadata:
version: 0.0.4
---
# inference.sh

Run 150+ AI applications in the cloud via the [inference.sh](https://inference.sh) platform.

**One API key for everything** — access image generation, video creation, LLMs, search, 3D, and more through a single account. No need to manage separate API keys for each provider.

## Available Skills

- **cli**: Use the inference.sh CLI (`infsh`) via the terminal tool


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
| `scripts/main.py` | inference-sh script | Run with python3 |

## Key References

- **Overview**: [references/overview.md](references/overview.md)
- **API Catalog**: [references/api-catalog.md](references/api-catalog.md)
- **CLI Usage**: [references/cli-usage.md](references/cli-usage.md)

## Sources

- **inference.sh**: https://inference.sh/ - Unified AI API platform
- **inference.sh Docs**: https://docs.inference.sh/ - API documentation

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

## What's Included

- **Image Generation**: FLUX, Reve, Seedream, Grok Imagine, Gemini
- **Video Generation**: Veo, Wan, Seedance, OmniHuman, HunyuanVideo
- **LLMs**: Claude, Gemini, Kimi, GLM-4 (via OpenRouter)
- **Search**: Tavily, Exa
- **3D**: Rodin
- **Social**: Twitter/X automation
- **Audio**: TTS, voice cloning
