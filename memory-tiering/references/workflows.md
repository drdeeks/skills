# Memory Tiering Workflows

## Organize-Memory Workflow

### Trigger Conditions
- Manual: "Run memory tiering" or "整理记忆层级"
- Automatic: After `/compact` command
- Scheduled: Weekly via cron

### Step 1: Ingest & Audit
```bash
# Read all tiers
cat memory/hot/HOT_MEMORY.md
cat memory/warm/WARM_MEMORY.md
cat MEMORY.md

# Read recent daily logs
ls -t memory/*.md | head -7
```

### Step 2: Tier Redistribution
- HOT: Next 2-3 turns immediate needs
- WARM: Permanent user/system facts
- COLD: Completed project summaries

### Step 3: Pruning & Summarization
- Remove completed tasks from HOT
- Replace COLD details with summaries
- Ensure credentials reference root files

### Step 4: Verification
- Check critical info preserved
- Verify HOT size < 2000 tokens
- Confirm no broken references

## Automation Script
```python
# scripts/main.py
def organize_memory():
    # Implementation
    pass

if __name__ == "__main__":
    organize_memory()
```

## Integration
- Called from agent initialization
- Runs before context loading
- Updates tier files in place
