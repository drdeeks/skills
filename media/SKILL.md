---
name: media
description: Media creation and management skills — gif search, heartmula audio, songsee music discovery, and YouTube content creation tools.
version: 0.0.5
---

# Media Skills

Container skill providing media-related sub-skills for content creation, audio processing, and video management.

## Sub-Skills

| Skill | Purpose |
|-------|---------|
| **gif-search** | Search and discover GIFs from various sources |
| **heartmula** | Audio processing and music creation tools |
| **songsee** | Music discovery and playlist management |
| **youtube-content** | YouTube content creation, transcript extraction, and video processing |


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
| `scripts/main.py` | media script | Run with python3 |

## Key References

- **Overview**: [references/overview.md](references/overview.md)
## Usage

Load the specific sub-skill based on your media task:

- **GIF creation/search**: Load `media/gif-search`
- **Audio/music work**: Load `media/heartmula`
- **Music discovery**: Load `media/songsee`
- **YouTube content**: Load `media/youtube-content`
