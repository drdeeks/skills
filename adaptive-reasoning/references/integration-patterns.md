# Integration Patterns for Adaptive Reasoning

How to integrate adaptive reasoning with other skills and tools.

## Session Integration

- Use `session_status` tool to toggle reasoning mode
- Track reasoning state across conversation turns
- Auto-downgrade after complex tasks complete

## Companion Skills

| Skill | Integration |
|-------|-------------|
| `skill-creator` | Apply reasoning to skill design decisions |
| `skill-creator-pro` | Enterprise-grade reasoning for complex skills |
| `html-report` | Visual reasoning analysis dashboards |

## Performance Considerations

- Reasoning mode increases token usage by 2-5x
- Auto-downgrade saves tokens on follow-up simple queries
- Session-level caching of reasoning state
