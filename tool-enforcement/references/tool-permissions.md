# Tool Permissions Reference

## File Permission Rules

### Standard Permissions

| Type | Permission | Use Case |
|------|------------|----------|
| Directory | 755 (rwxr-xr-x) | All directories |
| File | 644 (rw-r--r--) | All regular files |
| Executable | 755 (rwxr-xr-x) | Scripts (.sh, .py) |

### Exception: Secret Keys

| File | Permission | Reason |
|------|------------|--------|
| `.secrets/.secret-key` | 600 (rw-------) | Encryption key protection |

## Forbidden Permissions

| Permission | Why Forbidden |
|------------|----------------|
| `chmod 700` | Locks out user, has caused catastrophic data loss |
| `chmod 600` | Locks out user on non-secret files |
| `chmod 000` | Completely inaccessible |

## Fixing Permission Issues

```bash
# Find and fix chmod 700 violations
find . -type d -perm 700 -exec chmod 755 {} \;

# Find and fix chmod 600 violations (except .secrets/)
find . -type f -perm 600 ! -path "*/.secrets/*" -exec chmod 644 {} \;
```

## Secret File Handling

- Never store plaintext secrets
- Always use `secret.sh` for encrypted storage
- Never log secret values
- Never commit secrets to version control
