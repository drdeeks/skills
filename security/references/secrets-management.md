# Secrets Management

## Overview
Guidelines and best practices for managing secrets in agent infrastructure and deployment pipelines.

## Tools
- **1Password CLI**: Secure secrets storage and retrieval
- **HashiCorp Vault**: Enterprise secrets management
- **AWS Secrets Manager**: Cloud-native secrets management
- **GitHub Actions Secrets**: CI/CD pipeline secrets

## Best Practices
1. Never hardcode secrets in code or configuration files
2. Use environment variables for runtime secrets
3. Rotate secrets regularly
4. Audit secret access logs
5. Use least-privilege access principles

## Rotation Schedule
- API keys: Every 90 days
- Database passwords: Every 180 days
- SSH keys: Every 365 days
- TLS certificates: Before expiration (monitor 30 days prior)
