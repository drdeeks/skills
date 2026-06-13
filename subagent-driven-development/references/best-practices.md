# Subagent Best Practices

## Task Decomposition
- Break work into independent units
- Minimize shared state
- Define clear success criteria

## Resource Management
- Limit concurrent subagents (3-5)
- Monitor token usage
- Clean up on completion

## Error Handling
- Subagent failures don't crash parent
- Retry with different approach
- Escalate to human if needed

## When to Use
- Large refactoring tasks
- Multi-file changes
- Research + implementation
- Parallel testing

## When Not to Use
- Simple, linear tasks
- Highly dependent steps
- Real-time collaboration needed
