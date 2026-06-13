# Migration Troubleshooting

## Common Issues

### Missing Skills
**Problem**: Source tool has no Hermes equivalent
**Solution**: 
- Check skill registry
- Create custom skill
- Use generic exec skill

### Prompt Conversion Fails
**Problem**: Complex prompts don't translate
**Solution**:
- Simplify prompt structure
- Split into multiple skills
- Use subagent-driven-development

### Memory Structure Mismatch
**Problem**: Source memory format differs
**Solution**:
- Manual review of memory files
- Map to HOT/WARM/COLD tiers
- Preserve critical context

### MCP Server Config
**Problem**: Server configs not compatible
**Solution**:
- Use native MCP client config
- Convert to config.yaml format
- Test each server individually

## Validation Checklist
- [ ] SOUL.md created and valid
- [ ] Skills installed and working
- [ ] Memory tiers populated
- [ ] MCP servers connected
- [ ] Test task completes

## Rollback Procedure
1. Backup current Hermes config
2. Run migration
3. If failed: restore backup
4. Report issue with logs
