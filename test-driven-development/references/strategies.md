# TDD Strategies

## Test Types
- **Unit**: Single function/class, isolated
- **Integration**: Multiple components together
- **E2E**: Full user workflows

## Test Organization
```
tests/
├── unit/
├── integration/
├── e2e/
└── fixtures/
```

## Mocking
- Mock external dependencies
- Don't mock what you own
- Verify interactions, not implementation

## Coverage Goals
- Unit: > 90%
- Integration: > 70%
- E2E: Critical paths only

## Anti-Patterns
- Testing implementation details
- Flaky tests
- Slow test suite
- No test maintenance
