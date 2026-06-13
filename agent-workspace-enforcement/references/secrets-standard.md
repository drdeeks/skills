# Secrets Standard

## Storage Location
- All secrets go in `.secrets/` directory
- Never store secrets in config files, environment variables, or code

## Encryption
- Use age encryption for sensitive files
- Encryption key stored in `.secrets/.secret-key`
- Key permissions: chmod 600 (only exception to 755/644 rule)

## Files to Encrypt
- API keys
- Tokens
- Passwords
- Private keys
- Credentials

## Never
- Commit secrets to git
- Log secrets
- Display secrets in plain text
- Share secrets between agents
