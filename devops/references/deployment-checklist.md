# DevOps Deployment Checklist

## Pre-Deployment

- [ ] All validation scripts pass
- [ ] No hardcoded paths in skill files
- [ ] SKILL.md has valid frontmatter
- [ ] Required references present
- [ ] Scripts have proper shebangs

## Deployment

- [ ] Deploy to staging environment first
- [ ] Run integration tests
- [ ] Verify skill loads correctly
- [ ] Test core functionality

## Post-Deployment

- [ ] Monitor for errors
- [ ] Verify skill appears in registry
- [ ] Update documentation if needed
- [ ] Notify team of deployment

## Rollback Plan

1. Identify failed component
2. Revert to previous version
3. Verify rollback success
4. Document root cause
