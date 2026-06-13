---
name: sessions
description: "Session lifecycle management for multi-turn agent conversations. Handles session creation, persistence, context loading, and resumption across agent workspaces."
license: MIT
metadata:
  category: infrastructure
  tags:
    - sessions
    - persistence
    - context
version: 0.0.3
---

# Sessions

Session lifecycle management for multi-turn agent conversations. Handles session creation, persistence, context loading, and resumption across agent workspaces.

## When to Use

- Starting a new multi-turn conversation with an agent
- Resuming a previous session from history
- Managing context windows across long interactions
- Persisting conversation state between agent restarts

## Core Functions

### Session Management
- Create new sessions with unique identifiers
- Load session history and context
- Save session state after each interaction
- Resume sessions from any point in history

### Context Handling
- Track conversation context across turns
- Manage context window limits
- Summarize older context when windows fill
- Preserve key facts and decisions across sessions

### Persistence
- Store sessions as JSON files
- Index sessions by agent, topic, and timestamp
- Search across session history
- Archive completed sessions

## Provider Compatibility

| Provider | Compatibility | Notes |
|----------|---------------|-------|
| Claude (Anthropic) | Full | MCP servers, tool use |
| OpenAI / ChatGPT | Full | Function calling, Actions |
| Mistral / Le Chat | Full | Tool calling, script execution |
| Gemini (Google) | Full | Extensions, Vertex AI |
| Hermes (Nous) | Full | Tool-use fine-tuned |
| Any LLM + tools | Full | Scripts are plain Python, provider-independent |


## Workflow

### Step 1: Installation

```bash
# Install dependencies if needed
```

### Step 2: Configuration

```bash
# Configure the skill
```

### Step 3: Usage

```bash
# Use the skill
python3 scripts/main.py
```

### Step 4: Validation

```bash
# Validate the skill
python3 scripts/validate.py
```


## Free-First Strategy

| Tier | Cost | Stack |
|------|------|-------|
| **Tier 0** | $0/mo | Python 3.8+ (all scripts use stdlib only) |
| **Tier 1** | $0-5/mo | + CI/CD for automated validation |
| **Tier 2** | $5-20/mo | + Hosted skill registry for team distribution |

The entire core toolchain is permanently $0.


## Enforced Output Statistics

Every script produces structured output on completion:

```json
{
  "operation": "script_name",
  "timestamp": "ISO8601",
  "status": "success | failed",
  "skill_name": "the-skill-name",
  "details": {},
  "cost": {"tier": 0, "amount_usd": 0.0, "service": "local"}
}
```


## Error Handling

| Error | Response |
|-------|----------|
| Invalid input | Validate and report with guidance |
| Missing dependency | Auto-install or report requirement |
| Network failure | Retry with exponential backoff |
| Permission denied | Report and suggest alternatives |
| Resource not found | Report with available options |


## Enhancement Hooks

| Skill | Enhancement | When to Add |
|-------|-------------|-------------|
| `skill-creator` | Basic skill creation | When creating simple skills |
| `skill-creator-pro` | Enterprise upgrade | When upgrading to enterprise |
| `html-report` | Visual validation dashboard | When auditing many skills |
| `xlsx` | Export validation results | When tracking skill quality metrics |


## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/validate.py` | sessions script | Run with python3 |
| `scripts/main.py` | sessions script | Run with python3 |

## Key References

- **Overview**: [references/overview.md](references/overview.md)
## Key Commands

```bash
# List recent sessions
ls -lt $XDG_DATA_HOME/opencode/sessions/ 2>/dev/null || ls -lt ~/.local/share/opencode/sessions/

# Search sessions by keyword
grep -rl "keyword" $XDG_DATA_HOME/opencode/sessions/ 2>/dev/null

# View a specific session
cat $XDG_DATA_HOME/opencode/sessions/session-id.json 2>/dev/null
```
