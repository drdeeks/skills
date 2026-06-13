# Issue Taxonomy for Dogfooding

## Issue Categories

### Critical
- Security vulnerabilities
- Data loss risks
- Complete functionality failures

### High
- Major feature broken
- Performance degradation
- Incorrect results

### Medium
- Minor feature issues
- Poor error messages
- Missing documentation

### Low
- Cosmetic issues
- Nice-to-have improvements
- Typos

## Classification Guide

| Symptom | Category | Priority |
|---------|----------|----------|
| Crash | Critical | P0 |
| Wrong output | High | P1 |
| Slow response | Medium | P2 |
| Typo in docs | Low | P3 |

## Resolution Process

1. Reproduce the issue
2. Identify root cause
3. Implement fix
4. Test fix
5. Update documentation
6. Release
