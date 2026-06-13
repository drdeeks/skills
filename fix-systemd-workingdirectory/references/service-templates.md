# Systemd Service Templates

## Basic Service Template

```ini
[Unit]
Description=My Application
After=network.target

[Service]
Type=simple
User=${USER}
WorkingDirectory=${OPENCLAW_DIR}/myapp
ExecStart=${OPENCLAW_DIR}/myapp/start.sh
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## Service with Environment File

```ini
[Unit]
Description=My Application
After=network.target

[Service]
Type=simple
User=${USER}
WorkingDirectory=${OPENCLAW_DIR}/myapp
EnvironmentFile=${OPENCLAW_DIR}/myapp/.env
ExecStart=${OPENCLAW_DIR}/myapp/start.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

## Service with Resource Limits

```ini
[Unit]
Description=My Application
After=network.target

[Service]
Type=simple
User=${USER}
WorkingDirectory=${OPENCLAW_DIR}/myapp
ExecStart=${OPENCLAW_DIR}/myapp/start.sh
MemoryMax=512M
CPUQuota=50%
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
```

## Template Variables

| Variable | Description |
|----------|-------------|
| `${USER}` | Service user |
| `${OPENCLAW_DIR}` | OpenClaw installation directory |
| `${HOME}` | User home directory |
