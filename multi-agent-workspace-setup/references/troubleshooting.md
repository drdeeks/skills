# Multi-Agent Workspace Setup - Troubleshooting

## Agent Not Starting

1. Check service: `systemctl status [agent-id]-bot.service`
2. Check logs: `journalctl -u [agent-id]-bot.service -f`
3. Verify bot token in environment
4. Check workspace permissions

## Registry Issues

1. Validate JSON: `python3 -m json.tool agents.json`
2. Check workspace paths exist
3. Verify service names match

## Template Problems

1. Ensure all placeholders replaced
2. Check file permissions
3. Validate JSON files
