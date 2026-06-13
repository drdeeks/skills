# Autonomous Crew Troubleshooting

Common issues and solutions for the multi-agent system.

## Bot Conflicts

```bash
sudo systemctl stop telegram-bot.service
sudo pkill -f bot_enhanced.py
sleep 5
sudo systemctl start telegram-bot.service
```

## Missing Dependencies

```bash
sudo apt install python3-psutil
source ~/venv/bin/activate
pip install psutil requests
```

## Permission Errors

```bash
chmod 700 ~/workspace/.secrets
chmod 600 ~/workspace/.secrets/*.secret
```

## Builder Code Issues

- Ensure builder code is in agent.json at creation time
- Do not re-register existing codes
