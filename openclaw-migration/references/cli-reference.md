# OpenClaw Migration - CLI Reference

## Commands

```bash
# Full interactive migration
hermes claw migrate

# Preview what would be migrated
hermes claw migrate --dry-run

# Migrate without secrets
hermes claw migrate --preset user-data

# Overwrite existing conflicts
hermes claw migrate --overwrite

# Custom source path
hermes claw migrate --source /custom/path/.openclaw
```

## Python Script Usage

```bash
# Dry run with full discovery
python3 ${HERMES_DIR:-~/.hermes}/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py

# Dry run with user-data preset
python3 ${HERMES_DIR:-~/.hermes}/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py --preset user-data

# Execute user-data migration
python3 ${HERMES_DIR:-~/.hermes}/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py --execute --preset user-data --skill-conflict skip

# Execute full compatible migration
python3 ${HERMES_DIR:-~/.hermes}/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py --execute --preset full --migrate-secrets --skill-conflict skip

# Execute with workspace instructions
python3 ${HERMES_DIR:-~/.hermes}/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py --execute --preset user-data --skill-conflict rename --workspace-target "/absolute/workspace/path"
```
