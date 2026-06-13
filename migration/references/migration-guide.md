# Migration Guide

## Supported Source Systems

### Claude Code
- Settings export
- Custom commands
- MCP server configs

### OpenAI Assistants
- Instructions
- Tools configuration
- File references

### Custom Agent Systems
- Configuration files
- Prompt templates
- Tool definitions

## Migration Process

### Phase 1: Export
```bash
# Export from source system
# Save as JSON/YAML
```

### Phase 2: Transform
```bash
# Map fields to Hermes format
# Convert prompts
# Transform tool definitions
```

### Phase 3: Import
```bash
# Apply to Hermes config
# Verify functionality
# Test key workflows
```

## Field Mapping

| Source | Hermes | Notes |
|--------|--------|-------|
| system_prompt | SOUL.md | Core identity |
| tools | skills/ | Skill-based |
| memory | memory/ | Tiered storage |
| mcp_servers | config.yaml | Native MCP |

## Validation
- [ ] All prompts converted
- [ ] Tools mapped to skills
- [ ] Memory structure created
- [ ] MCP servers configured
- [ ] Test run successful
