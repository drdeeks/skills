# Memory Tiering Architecture

## Three-Tier Design

### HOT Tier (memory/hot/HOT_MEMORY.md)
- **Purpose**: Immediate context, active tasks
- **Size Target**: < 2000 tokens
- **Update Frequency**: Every interaction
- **Content**: Current goals, active credentials, temporary state

### WARM Tier (memory/warm/WARM_MEMORY.md)
- **Purpose**: Stable preferences, configurations
- **Size Target**: < 5000 tokens
- **Update Frequency**: When preferences change
- **Content**: User preferences, system inventory, recurring patterns

### COLD Tier (MEMORY.md)
- **Purpose**: Long-term archive
- **Size Target**: Unlimited (summarized)
- **Update Frequency**: During archival
- **Content**: Project history, lessons learned, decisions

## Data Flow
```
Daily Logs → HOT (active) → WARM (stable) → COLD (archived)
                ↓              ↓              ↓
           Prune daily    Update rarely   Summarize
```

## Implementation
- File-based storage in `memory/` directory
- Markdown format for readability
- Git-tracked for history
- Automated via scripts
