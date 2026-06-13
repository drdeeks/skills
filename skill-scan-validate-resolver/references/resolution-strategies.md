# Resolution Strategies

## Auto-Fix Capabilities
- Frontmatter validation and correction
- Hardcoded path replacement
- Missing directory creation
- Placeholder file generation

## Manual Resolution Required
- Missing external service documentation
- Complex logic errors
- Architecture decisions
- Security review items

## Priority Levels
1. **Critical**: Blocks validation (missing scripts/references)
2. **High**: Quality issues (TODO/FIXME, hardcoded paths)
3. **Medium**: Best practice violations
4. **Low**: Style/formatting issues

## Resolution Workflow
1. Run validator with `--full` flag
2. Review JSON output for details
3. Apply auto-fixes where available
4. Manually resolve remaining issues
5. Re-validate until passing
