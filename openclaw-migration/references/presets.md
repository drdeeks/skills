# OpenClaw Migration - Migration Presets

## user-data Preset
Includes:
- `soul` - SOUL.md import
- `workspace-agents` - Workspace agents file
- `memory` - MEMORY.md and USER.md transformation
- `user-profile` - User profile settings
- `messaging-settings` - Telegram/Messaging config
- `command-allowlist` - Command approval patterns
- `skills` - Skill directory migration
- `tts-assets` - TTS asset files
- `archive` - Non-secret docs archival

## full Preset
Includes everything in `user-data` plus:
- `secret-settings` - Allowlisted secrets (TELEGRAM_BOT_TOKEN)

## Category-Level Flags
Advanced users can use `--include` / `--exclude` for specific categories:
```bash
# Only migrate memory and skills
python3 scripts/openclaw_to_hermes.py --execute --include memory,skills

# Migrate everything except secrets
python3 scripts/openclaw_to_hermes.py --execute --exclude secret-settings
```
