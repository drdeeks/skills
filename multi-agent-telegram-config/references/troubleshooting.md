# Multi-Agent Telegram Troubleshooting

## Common Issues

### Polling Conflicts
**Error**: `Telegram polling conflict`
**Cause**: Multiple agents using same bot token
**Fix**: Use separate bot tokens per agent

### Messages Not Received
**Error**: No incoming messages
**Causes**:
- `TELEGRAM_ALLOWED_USERS` not set or wrong
- `HERMES_MANAGED=true` preventing .env loading
- Bot not added to group/channel
**Fixes**:
- Verify allowed users match your Telegram ID
- Set `HERMES_MANAGED=false` for non-Hermes agents
- Add bot to group with admin rights

### Configuration Not Applied
**Error**: Config changes not reflected
**Causes**:
- Config file not mounted correctly
- Docker container not restarted
- Environment variables not interpolated
**Fixes**:
- Check volume mounts in docker-compose
- Run `docker compose down && docker compose up -d --build`
- Use `${VAR}` syntax in docker-compose.yml

### Profile Segregation Failed
**Error**: Hermes receiving other agents' messages
**Cause**: Shared bot token or misconfigured allowed users
**Fix**: 
- Ensure unique bot tokens per agent
- Strict `TELEGRAM_ALLOWED_USERS` per agent
- Verify `telegram.enabled: false` in Hermes config.yaml

## Debugging Commands
```bash
# Check agent logs
docker compose logs -f agent-1

# Verify environment
docker compose exec agent-1 env | grep TELEGRAM

# Test bot token
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe"

# Check config
docker compose exec agent-1 cat /app/config.yaml

# Restart single agent
docker compose restart agent-1
```

## Validation Checklist
- [ ] Each agent has unique bot token
- [ ] `TELEGRAM_ALLOWED_USERS` set per agent
- [ ] Hermes has `telegram.enabled: false`
- [ ] Non-Hermes agents have `HERMES_MANAGED=false`
- [ ] Docker Compose includes all env vars
- [ ] Containers restarted after config changes
- [ ] Logs show correct enabled/disabled status
