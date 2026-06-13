---
name: productivity
description: Productivity and workspace integration skills — Google Workspace, Linear, Notion, PDF processing, OCR, and PowerPoint creation.
version: 0.0.4
---

# Productivity Skills

Container skill providing productivity-related sub-skills for workspace integration, document processing, and project management.

## Sub-Skills

| Skill | Purpose |
|-------|---------|
| **google-workspace** | Gmail, Calendar, Drive integration via Google API |
| **linear** | Linear project management and issue tracking |
| **nano-pdf** | PDF creation, editing, and manipulation |
| **notion** | Notion workspace integration and page management |
| **ocr-and-documents** | Optical character recognition and document extraction |
| **powerpoint** | PowerPoint presentation creation and editing |


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
| `scripts/main.py` | productivity script | Run with python3 |

## Key References

- **Overview**: [references/overview.md](references/overview.md)
## Usage

Load the specific sub-skill based on your productivity task:

- **Email/calendar**: Load `productivity/google-workspace`
- **Project management**: Load `productivity/linear`
- **PDF work**: Load `productivity/nano-pdf`
- **Notion pages**: Load `productivity/notion`
- **Document extraction**: Load `productivity/ocr-and-documents`
- **Presentations**: Load `productivity/powerpoint`
