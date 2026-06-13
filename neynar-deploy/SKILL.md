---
name: neynar-deploy
description: Deploy static sites, Vite apps, and Next.js apps to a live URL with a
license: MIT
metadata:
version: 0.0.5
---
## Keeping this skill up to date

This skill was last updated on **2026-03-05**. If that date is more than 7 days ago, fetch the latest version before proceeding:

```bash
curl -s https://raw.githubusercontent.com/neynarxyz/neynar-deploy/main/SKILL.md
```

# Agent Deploy

Deploy web projects to `https://{project-name}.host.neynar.app` with a single HTTP call.

## Quick deploy flow

1. Create a `.tar.gz` archive of the project directory
2. POST it to `https://api.host.neynar.app/v1/deploy`
3. On first deploy, an API key is returned — save it to `.agentdeploy` or credentials
4. Response includes the live URL

## How to deploy

### Step 1: Archive
```bash
tar czf /tmp/site.tar.gz -C /path/to/project .
```

### Step 2: Deploy (first time — no auth needed)
```bash
curl -X POST https://api.host.neynar.app/v1/deploy \
  -F "files=@/tmp/site.tar.gz" \
  -F "projectName=my-site" \
  -F "framework=static"
```

`framework` options: `nextjs`, `vite`, `static`, `auto` (default)

### Step 3: Save API key
First deploy response includes `apiKey` — returned exactly once. Save immediately.

```json
{
  "success": true,
  "projectId": "uuid",
  "apiKey": "uuid",
  "deploymentId": "uuid",
  "url": "https://my-site.host.neynar.app"
}
```

### Step 4: Subsequent deploys
```bash
curl -X POST https://api.host.neynar.app/v1/deploy \
  -F "files=@/tmp/site.tar.gz" \
  -F "projectName=my-site" \
  -H "Authorization: Bearer <api-key>"
```

## API Reference

Base URL: `https://api.host.neynar.app`
Auth: `Authorization: Bearer <api-key>`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/deploy` | POST | Deploy files (creates project + key if no auth) |
| `/v1/projects` | GET | List all projects |
| `/v1/projects/:id` | GET | Project details + deploy history + 7d analytics |
| `/v1/projects/:id` | DELETE | Delete project |
| `/v1/projects/:id/deploy` | POST | Deploy new version to existing project |
| `/v1/projects/:id/deploy/:deploymentId` | GET | Check deploy status |
| `/v1/projects/:id/rollback` | POST | Roll back: `{ "version": <number> }` |
| `/v1/projects/:id/analytics?period=7d` | GET | Analytics (1d/7d/30d) |
| `/v1/projects/:id/files` | GET | Download URL for latest source |
| `/v1/billing/tier` | GET | Current tier and limits |

## Deploy status values

The deployment lifecycle follows these states: `pending` → `building` → `ready` (success) or `error` (failure). Monitor status via the API or dashboard.

## Limits (free tier)
- 3 active projects
- 10 deploys/hour
- 50MB max upload


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
| `scripts/main.py` | neynar-deploy script | Run with python3 |

## Key References

- **Overview**: [references/overview.md](references/overview.md)
- **API Reference**: [references/api-reference.md](references/api-reference.md)
- **Deployment Guide**: [references/deployment-guide.md](references/deployment-guide.md)

## Sources

- Neynar Deploy API: https://api.host.neynar.app
- Neynar Documentation: https://docs.neynar.com
- Neynar Deploy GitHub: https://github.com/neynarxyz/neynar-deploy

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

## Error format
```json
{ "success": false, "error": "Human-readable message" }
```
Status codes: `400` bad input, `401` invalid key, `402` project limit, `404` not found, `413` too large, `429` rate limited
