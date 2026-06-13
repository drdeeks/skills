# Credential Handling

## Secure Credential Patterns

### Environment Variables
```bash
export API_KEY="${SECRET_API_KEY}"
export DB_PASSWORD="${SECRET_DB_PASSWORD}"
```

### File-Based (Restricted Permissions)
```bash
chmod 600 ~/.config/credentials
source ~/.config/credentials
```

### 1Password Integration
```bash
op read "op://vault/item/field" --account myaccount
```

## Anti-Patterns to Avoid
- Committing credentials to git
- Storing in plain text files
- Sharing via chat/email
- Using default/weak passwords

## Validation
Always validate credentials before use:
```python
def validate_credentials(creds: dict) -> bool:
    required = ['api_key', 'endpoint']
    return all(k in creds and creds[k] for k in required)
```
