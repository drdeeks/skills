---
description: Generate complete, functional config files with real example values —
  never placeholder stubs or TODO comments.
name: generate-complete-configs
---

# Generate Complete Configs

When generating config files (.env, config.yaml, JSON, etc.) for users, ALWAYS produce fully functional output with real example values. Never output stubs, TODOs, or empty placeholders.

## Rules

1. **No TODO comments** — replace with actual values or clear commented examples
2. **No empty placeholders** — `PASTE_HERE`, `YOUR_KEY_HERE`, `TODO` are unacceptable
3. **Provide real alternatives** — if a value is unknown, show 3-5 real examples with model names, URLs, and format
4. **Inline documentation** — every section has comments explaining what it does and how to fill it in
5. **Uncomment-one pattern** — for provider selection, show all options commented with "uncomment ONE" instruction
6. **Self-documenting** — user should understand what to do without external docs

## Example: Bad vs Good

**BAD (.env stub):**
```bash
# Agent: titan
# TODO: Add your provider keys
# TELEGRAM_BOT_TOKEN=
```

**GOOD (.env with real examples):**
```bash
# Agent: titan
# REQUIRED: Uncomment ONE provider below and add your bot token
#
# Telegram
# Get token from @BotFather. Format: 123456789:ABCdefGHI...
# TELEGRAM_BOT_TOKEN=<your-bot-token>
TELEGRAM_ALLOWED_USERS=6537959619
TELEGRAM_HOME_CHANNEL=6537959619
#
# --- Nous Portal (free tier) ---
# NOUS_API_KEY=<your-key>
# Model: xiaomi/mimo-v2-pro
#
# --- OpenRouter (200+ models) ---
# OPENROUTER_API_KEY=<your-key>
# Model: any model on openrouter.ai
```

## When to Apply

- Script output generation (bash scripts writing config files)
- CLI tools that scaffold new projects
- Agent bootstrap, docker-compose, service configs
- Any file the user needs to customize after generation

## Why

Users HATE seeing `TODO` and `PASTE_HERE`. It means the tool did half the work and left them guessing. A complete config with real examples and inline docs is immediately useful — the user knows exactly what to change and how.