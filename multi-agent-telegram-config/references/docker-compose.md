# Docker Compose Configuration

## Base Template
```yaml
version: '3.8'

services:
  hermes:
    build: ./hermes
    environment:
      - HERMES_MANAGED=true
      - TELEGRAM_ENABLED=false
    env_file:
      - ./hermes/.env
    volumes:
      - ./hermes/config.yaml:/app/config.yaml
    restart: unless-stopped

  agent-1:
    build: ./agent-1
    environment:
      - HERMES_MANAGED=false
      - TELEGRAM_ENABLED=true
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN_1}
      - TELEGRAM_ALLOWED_USERS=${TELEGRAM_ALLOWED_USERS_1}
    env_file:
      - ./agent-1/.env
    volumes:
      - ./agent-1/config.yaml:/app/config.yaml
    restart: unless-stopped

  agent-2:
    build: ./agent-2
    environment:
      - HERMES_MANAGED=false
      - TELEGRAM_ENABLED=true
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN_2}
      - TELEGRAM_ALLOWED_USERS=${TELEGRAM_ALLOWED_USERS_2}
    env_file:
      - ./agent-2/.env
    volumes:
      - ./agent-2/config.yaml:/app/config.yaml
    restart: unless-stopped
```

## Environment Variables
```bash
# .env file (root)
TELEGRAM_BOT_TOKEN_1=bot_token_for_agent_1
TELEGRAM_ALLOWED_USERS_1=123456789,987654321
TELEGRAM_BOT_TOKEN_2=bot_token_for_agent_2
TELEGRAM_ALLOWED_USERS_2=123456789,987654321
```

## Network Configuration
```yaml
networks:
  agent-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

services:
  hermes:
    networks:
      - agent-network
  agent-1:
    networks:
      - agent-network
  agent-2:
    networks:
      - agent-network
```

## Health Checks
```yaml
services:
  agent-1:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```
