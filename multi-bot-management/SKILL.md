---
name: multi-bot-management
description: Run multiple Telegram bots on the same server without conflicts. Covers token management, separate state/log files, systemd services, and troubleshooting.
version: 0.0.1
---

# Multi-Bot Management

Run multiple Telegram bots on the same server without conflicts.

## Environment Variables

| Variable | Purpose | Used In |
|----------|---------|---------|
| `$TELEGRAM_BOT_DIR` | Bot directory root | All bot files |
| `$HOME` | User home directory | Default working dir |

## Quick Setup

### Step 1: Create Bot File
```bash
# Copy template
cp $TELEGRAM_BOT_DIR/bot_enhanced.py $TELEGRAM_BOT_DIR/newbot_enhanced.py

# Update token
sed -i 's/TOKEN="old_token"/TOKEN="new_token"/' $TELEGRAM_BOT_DIR/newbot_enhanced.py

# Update state file
sed -i 's|STATE_FILE = ".*"|STATE_FILE = "'$TELEGRAM_BOT_DIR'/newbot_state.json"|' $TELEGRAM_BOT_DIR/newbot_enhanced.py

# Update log file
sed -i 's|LOG_FILE = ".*"|LOG_FILE = "'$TELEGRAM_BOT_DIR'/logs/newbot.log"|' $TELEGRAM_BOT_DIR/newbot_enhanced.py
```

### Step 2: Create Service File
```bash
tee /etc/systemd/system/telegram-newbot.service > /dev/null << EOF
[Unit]
Description=Telegram Bot (NewBot)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 $TELEGRAM_BOT_DIR/newbot_enhanced.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1
WorkingDirectory=$TELEGRAM_BOT_DIR

[Install]
WantedBy=multi-user.target
EOF
```

### Step 3: Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-newbot.service
sudo systemctl start telegram-newbot.service
```

### Step 4: Verify
```bash
# Check status
sudo systemctl status telegram-newbot.service

# Check logs
tail -f $TELEGRAM_BOT_DIR/logs/newbot.log

# Test bot token
python3 -c "
import requests
TOKEN = 'your_new_token'
r = requests.get(f'https://api.telegram.org/bot{TOKEN}/getMe', timeout=5)
print(r.json())
"
```

## Per-Bot Configuration

Each bot needs:
1. **Unique token** (from @BotFather)
2. **Unique STATE_FILE** path
3. **Unique LOG_FILE** path
4. **Separate systemd service**


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
| `scripts/main.py` | multi-bot-management script | Run with python3 |

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

## Troubleshooting

### Bot not responding
```bash
# Check service status
sudo systemctl status telegram-bot.service

# Check logs
tail -50 $TELEGRAM_BOT_DIR/logs/bot.log

# Restart
sudo systemctl restart telegram-bot.service
```

### Token issues
```bash
# Verify token
python3 -c "
import requests
TOKEN = 'your_token'
r = requests.get(f'https://api.telegram.org/bot{TOKEN}/getMe')
print(r.json())
"
```

### State file conflicts
Ensure each bot has a unique state file path to avoid data corruption.