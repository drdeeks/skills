# Subagent Patterns

## Parallel Execution
- Split independent tasks across subagents
- Each subagent handles a complete subtask
- Aggregate results in parent agent

## Specialization
- Assign domain-specific subagents
- Code review subagent
- Testing subagent
- Documentation subagent

## Communication
- Parent defines clear objectives
- Subagents report progress
- Results passed via structured output

## Coordination
- Use shared context for state
- Avoid circular dependencies
- Define clear interfaces
