# ClawHub Publishing Guide

Guide for publishing skills to ClawHub.

## Prerequisites

1. Create account at clawhub.com
2. Authenticate: `clawhub login`
3. Verify: `clawhub whoami`

## Publish Command

```bash
clawhub publish ./my-skill \
  --slug my-skill \
  --name "My Skill" \
  --version 1.2.0 \
  --changelog "Fixes + docs"
```

## Versioning

Follow semantic versioning:
- Major: Breaking changes
- Minor: New features
- Patch: Bug fixes
