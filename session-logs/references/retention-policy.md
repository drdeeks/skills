# Session Log Retention Policy

## Default Retention
- **Active sessions**: Kept indefinitely until session ends
- **Completed sessions**: 30 days
- **Failed sessions**: 90 days (for debugging)
- **Archived sessions**: 1 year (compressed)

## Cleanup Commands
```bash
# Clean old logs
find ~/.opencode/sessions -name "*.jsonl" -mtime +30 -delete

# Archive old logs
find ~/.opencode/sessions -name "*.jsonl" -mtime +7 -exec gzip {} \;
```

## Compliance
- GDPR: Right to erasure supported via `opencode session delete`
- SOC2: Audit logs retained per policy
