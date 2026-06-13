# Session Configuration

## Config File
Location: `${HOME}/.opencode/sessions/config.yaml`

## Options
```yaml
auto_save: true
save_interval: 300  # seconds
max_history: 1000
compression: gzip
encryption: false
```

## Environment Variables
- `OPENCODE_SESSION_DIR`: Custom session directory
- `OPENCODE_AUTO_SAVE`: Enable/disable auto-save
- `OPENCODE_MAX_HISTORY`: Maximum history entries
