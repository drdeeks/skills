# Systemd Service Configuration Guide

## WorkingDirectory

The `WorkingDirectory` directive sets the working directory for the service.

### Syntax

```ini
[Service]
WorkingDirectory=/path/to/directory
ExecStart=/path/to/executable
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| No such file or directory | Directory doesn't exist | Create directory first |
| Permission denied | Insufficient permissions | Check directory ownership |
| Relative path issues | Path resolution errors | Use absolute paths |

## Best Practices

1. Always use absolute paths
2. Ensure directory exists before service starts
3. Set proper ownership and permissions
4. Use `RuntimeDirectory` for runtime directories

## Example Service

```ini
[Unit]
Description=My Application
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=${OPENCLAW_DIR}/myapp
ExecStart=${OPENCLAW_DIR}/myapp/start.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

## Debugging

```bash
# Check service status
systemctl status myservice

# View logs
journalctl -u myservice

# Check working directory
cat /proc/$(pgrep -f myservice)/cwd
```
