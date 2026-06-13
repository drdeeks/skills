# Code Quality Standards

## Linting & Formatting
- ESLint/Prettier (JavaScript/TypeScript)
- Ruff/Black (Python)
- golangci-lint (Go)
- Run on every commit (pre-commit hooks)

## Code Review Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No hardcoded secrets
- [ ] Error handling present
- [ ] Performance considered
- [ ] Security reviewed

## Metrics
- Cyclomatic complexity < 10
- Test coverage > 80%
- No critical vulnerabilities
- Build passes in CI

## Technical Debt
- Track in issue tracker
- Allocate 20% sprint capacity
- Prioritize by impact
- Refactor incrementally
