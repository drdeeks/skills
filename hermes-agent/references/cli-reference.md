# Hermes Agent CLI Reference

## Basic Commands

### Chat
```bash
# Interactive chat
hermes

# Single query
hermes chat -q "What is the capital of France?"

# With specific model
hermes chat -m gpt-4 -q "Explain quantum computing"

# Continue last conversation
hermes chat --continue
```

### Setup
```bash
# Run setup wizard
hermes setup

# Configure API keys
hermes setup --api-keys

# Configure model provider
hermes setup --provider

# Configure gateway
hermes setup --gateway
```

### Model Management
```bash
# List available models
hermes model --list

# Change model
hermes model gpt-4

# Change provider
hermes model --provider openrouter

# Check current model
hermes model --current
```

## System Commands

### Health Check
```bash
# Check system health
hermes doctor

# Check specific component
hermes doctor --component memory

# Check all components
hermes doctor --all
```

### Status
```bash
# Show current status
hermes status

# Show detailed status
hermes status --verbose

# Show memory usage
hermes status --memory
```

## Configuration

### View Config
```bash
# Show current config
hermes config

# Show specific config
hermes config --section memory

# Show all configs
hermes config --all
```

### Set Config
```bash
# Set configuration value
hermes config set memory.backend honcho

# Set multiple values
hermes config set memory.backend honcho memory.max_tokens 4000

# Reset to defaults
hermes config reset
```

## Memory Commands

### Memory Management
```bash
# Show memory status
hermes memory status

# Clear memory
hermes memory clear

# Export memory
hermes memory export --format json

# Import memory
hermes memory import --file memory.json
```

### Memory Search
```bash
# Search memory
hermes memory search "quantum computing"

# Search with filters
hermes memory search --type preference "dark mode"

# Search recent memories
hermes memory search --recent 7d
```

## Skill Commands

### Skill Management
```bash
# List installed skills
hermes skill list

# Install skill
hermes skill install /path/to/skill

# Uninstall skill
hermes skill uninstall skill-name

# Update skill
hermes skill update skill-name
```

### Skill Creation
```bash
# Create new skill
hermes skill create --name my-skill

# Create from template
hermes skill create --template basic

# Validate skill
hermes skill validate /path/to/skill
```

## Gateway Commands

### Gateway Management
```bash
# Start gateway
hermes gateway start

# Stop gateway
hermes gateway stop

# Restart gateway
hermes gateway restart

# Check gateway status
hermes gateway status
```

### Platform Configuration
```bash
# Configure Telegram
hermes gateway config telegram

# Configure Discord
hermes gateway config discord

# Configure Slack
hermes gateway config slack
```

## Advanced Commands

### Profile Management
```bash
# List profiles
hermes profile list

# Create profile
hermes profile create work

# Switch profile
hermes profile use work

# Delete profile
hermes profile delete work
```

### Plugin Management
```bash
# List plugins
hermes plugin list

# Install plugin
hermes plugin install plugin-name

# Uninstall plugin
hermes plugin uninstall plugin-name

# Enable plugin
hermes plugin enable plugin-name
```

### Cron Jobs
```bash
# List cron jobs
hermes cron list

# Add cron job
hermes cron add "0 9 * * *" "daily-report"

# Remove cron job
hermes cron remove job-id

# Run cron job now
hermes cron run job-id
```

## Debugging

### Logs
```bash
# Show recent logs
hermes logs

# Show logs for specific component
hermes logs --component memory

# Follow logs
hermes logs --follow

# Show error logs
hermes logs --level error
```

### Diagnostics
```bash
# Run diagnostics
hermes diagnostics

# Export diagnostics
hermes diagnostics --export

# Check system requirements
hermes diagnostics --check-requirements
```

## Best Practices

1. **Use setup wizard** - Configure properly before first use
2. **Check health regularly** - Run `hermes doctor` periodically
3. **Keep updated** - Use `hermes update` to get latest features
4. **Backup memory** - Export memory regularly
5. **Use profiles** - Separate work and personal configurations