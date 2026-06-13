# Hermes Agent Troubleshooting Guide

## Common Issues

### Installation Problems

#### Permission Denied
```bash
# Problem: Permission denied during installation
# Solution: Use sudo or fix permissions
sudo curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# Or fix permissions
chmod +x ~/.local/bin/hermes
```

#### Command Not Found
```bash
# Problem: hermes command not found
# Solution: Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Or add to .bashrc/.zshrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

### Configuration Issues

#### API Key Not Found
```bash
# Problem: API key not recognized
# Solution: Set API key properly
hermes setup --api-keys

# Or set directly
hermes config set api.openai "sk-your-api-key"

# Or use environment variable
export OPENAI_API_KEY="sk-your-api-key"
```

#### Model Not Available
```bash
# Problem: Model not found
# Solution: Check available models
hermes model --list

# Or check provider
hermes model --provider openrouter
```

### Memory Issues

#### Memory Not Persisting
```bash
# Problem: Memory cleared between sessions
# Solution: Check memory backend
hermes config get memory.backend

# Set persistent backend
hermes config set memory.backend honcho

# Check memory status
hermes memory status
```

#### Memory Search Not Working
```bash
# Problem: Memory search returns no results
# Solution: Rebuild memory index
hermes memory rebuild-index

# Or check memory contents
hermes memory list --limit 10
```

### Gateway Issues

#### Gateway Won't Start
```bash
# Problem: Gateway fails to start
# Solution: Check logs
hermes logs --component gateway

# Check port availability
netstat -tulpn | grep :8080

# Restart gateway
hermes gateway restart
```

#### Platform Connection Failed
```bash
# Problem: Can't connect to Telegram/Discord/etc.
# Solution: Check platform configuration
hermes gateway config telegram

# Verify credentials
hermes config get platforms.telegram.token

# Test connection
hermes gateway test telegram
```

### Performance Issues

#### Slow Response Times
```bash
# Problem: Agent responds slowly
# Solution: Check system resources
hermes status --verbose

# Optimize memory usage
hermes config set memory.max_tokens 2000

# Use faster model
hermes model gpt-4-mini
```

#### High Memory Usage
```bash
# Problem: Agent uses too much memory
# Solution: Clear memory cache
hermes memory clear --cache

# Reduce memory limits
hermes config set memory.max_size 1000

# Use compressed memory
hermes config set memory.compression true
```

### Skill Issues

#### Skill Not Loading
```bash
# Problem: Skill doesn't appear in list
# Solution: Check skill installation
hermes skill list

# Reinstall skill
hermes skill uninstall skill-name
hermes skill install /path/to/skill

# Validate skill
hermes skill validate /path/to/skill
```

#### Skill Errors
```bash
# Problem: Skill throws errors
# Solution: Check skill logs
hermes logs --component skill-skill-name

# Update skill
hermes skill update skill-name

# Reinstall skill
hermes skill reinstall skill-name
```

## Debugging Commands

### System Diagnostics
```bash
# Run full diagnostics
hermes diagnostics

# Check specific component
hermes diagnostics --component memory

# Export diagnostic report
hermes diagnostics --export --file diagnostics.json
```

### Log Analysis
```bash
# Show recent logs
hermes logs --lines 100

# Show error logs only
hermes logs --level error

# Follow logs in real-time
hermes logs --follow

# Search logs
hermes logs --grep "error"
```

### Configuration Validation
```bash
# Validate configuration
hermes config validate

# Check for conflicts
hermes config check-conflicts

# Reset to defaults
hermes config reset
```

## Getting Help

### Official Resources
- **Documentation**: https://hermes-agent.nousresearch.com/docs/
- **GitHub**: https://github.com/NousResearch/hermes-agent
- **Discord**: Community support available

### Community Support
- **Issues**: Report bugs on GitHub
- **Discussions**: Ask questions in GitHub Discussions
- **Discord**: Real-time community support

### Professional Support
- **Enterprise**: Contact Nous Research for enterprise support
- **Consulting**: Available for custom implementations

## Best Practices

1. **Keep logs** - Save logs for debugging
2. **Document issues** - Record error messages and steps to reproduce
3. **Update regularly** - Use latest stable version
4. **Backup configuration** - Export config before major changes
5. **Test changes** - Test in development environment first