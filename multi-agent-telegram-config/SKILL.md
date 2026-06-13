---
name: multi-agent-telegram-config
description: |
  Steps to enable/disable Telegram per agent in a multi-agent Hermes setup, ensuring profile segregation and correct gateway configuration.
version: 0.0.4
---

triggers:
  - Enable Telegram for all agents except Hermes
  - Disable Telegram for Hermes
  - Fix Telegram conflicts in multi-agent Hermes
  - Ensure .env is respected in Hermes agents
  - Profile segregation for Hermes agents

steps:
  1. Disable Telegram in Hermes:
     - Set `telegram.enabled: false` in `hermes/config.yaml`.
     - Remove `TELEGRAM_BOT_TOKEN` from Hermes' `.env` if present.

  2. Enable Telegram in All Other Agents:
     - Set `telegram.enabled: true` in each agent's `config.yaml`.
     - Add `TELEGRAM_BOT_TOKEN` and `TELEGRAM_ALLOWED_USERS` to the agent's `.env` file.

  3. Ensure `HERMES_MANAGED=false`:
     - Set `HERMES_MANAGED=false` in the agent's `config.yaml` and Docker Compose environment.
     - This ensures the agent respects `.env` files.

  4. Patch Docker Compose:
     - Add `TELEGRAM_BOT_TOKEN` and `TELEGRAM_ALLOWED_USERS` to all agents except Hermes in `docker-compose.yml`.

  5. Restart All Agents:
     - Run `docker compose down && docker compose up -d --build` to apply changes.

  6. Verify:
     - Check logs for each agent to confirm Telegram is enabled/disabled as expected.

pitfalls:
  - Do not enable Telegram in multiple agents unless you want multiple gateways.
  - Ensure `.env` files are not protected if you need to edit them.
  - If configs are corrupted, reconstruct them from backups or rewrite them.

verification:
  - Check agent logs for "Telegram: enabled" or "Telegram: not set".
  - Confirm no "Telegram polling conflict" errors in logs.

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
| `scripts/main.py` | multi-agent-telegram-config script | Run with python3 |


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

## Key References

- **Overview**: [references/overview.md](references/overview.md)
- **Docker Compose**: [references/docker-compose.md](references/docker-compose.md)
- **Troubleshooting**: [references/troubleshooting.md](references/troubleshooting.md)

## Sources

- **Telegram Bot API**: https://core.telegram.org/bots/api - Official Telegram Bot API documentation