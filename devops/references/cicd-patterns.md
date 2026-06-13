# CI/CD Patterns for DevOps Skills

## GitHub Actions Workflow

```yaml
name: Validate Skills
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: python scripts/validate.py
```

## Pipeline Stages

1. **Lint** — Check code quality
2. **Test** — Run validation scripts
3. **Build** — Package skill artifacts
4. **Deploy** — Distribute to target environments

## Deployment Strategies

| Strategy | Use Case |
|----------|----------|
| Rolling update | Zero-downtime deployments |
| Blue-green | Quick rollback capability |
| Canary | Gradual rollout with monitoring |
| Feature flags | Toggle skills without redeployment |
