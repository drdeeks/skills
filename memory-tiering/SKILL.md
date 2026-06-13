---
name: memory-tiering
description: Automated multi-tiered memory management (HOT, WARM, COLD). Use this skill to organize, prune, and archive context during memory operations or compactions.
version: 0.0.4
---

# Memory Tiering Skill 🧠⚖️

This skill implements a dynamic, three-tiered memory architecture to optimize context usage and retrieval efficiency.

## The Three Tiers

1.  **🔥 HOT (memory/hot/HOT_MEMORY.md)**:
    *   **Focus**: Current session context, active tasks, temporary credentials, immediate goals.
    *   **Management**: Updated frequently. Pruned aggressively once tasks are completed.
2.  **🌡️ WARM (memory/warm/WARM_MEMORY.md)**:
    *   **Focus**: User preferences (Hui's style, timezone), core system inventory, stable configurations, recurring interests.
    *   **Management**: Updated when preferences change or new stable tools are added.
3.  **❄️ COLD (MEMORY.md)**:
    *   **Focus**: Long-term archive, historical decisions, project milestones, distilled lessons.
    *   **Management**: Updated during archival phases. Detail is replaced by summaries.

## Workflow: `Organize-Memory`

Whenever a memory reorganization is triggered (manual or post-compaction), follow these steps:

### Step 1: Ingest & Audit
- Read all three tiers and recent daily logs (`memory/YYYY-MM-DD.md`).
- Identify "Dead Context" (completed tasks, resolved bugs).

### Step 2: Tier Redistribution
- **Move to HOT**: Anything requiring immediate attention in the next 2-3 turns.
- **Move to WARM**: New facts about the user or system that are permanent.
- **Move to COLD**: Completed high-level project summaries.

### Step 3: Pruning & Summarization
- Remove granular details from COLD.
- Ensure credentials in HOT point to their root files rather than storing raw secrets (if possible).

### Step 4: Verification
- Ensure no critical information was lost during the move.
- Verify that `HOT` is now small enough for efficient context use.


## Provider Compatibility

| Provider | Compatibility | Notes |
|----------|---------------|-------|
| Claude (Anthropic) | Full | MCP servers, tool use |
| OpenAI / ChatGPT | Full | Function calling, Actions |
| Mistral / Le Chat | Full | Tool calling, script execution |
| Gemini (Google) | Full | Extensions, Vertex AI |
| Hermes (Nous) | Full | Tool-use fine-tuned |
| GitHub Copilot | Partial | Code generation; use external runner for scripts |
| Any LLM + tools | Full | Scripts are plain Python, provider-independent |


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
| `scripts/validate.py` | memory-tiering script | Run with python3 |
| `scripts/main.py` | memory-tiering script | Run with python3 |

## Key References

- **Overview**: [references/overview.md](references/overview.md)
- **Architecture**: [references/architecture.md](references/architecture.md)
- **Workflows**: [references/workflows.md](references/workflows.md)

## Sources

- **File-based storage**: Local filesystem (memory/ directory)
- **Git**: Version control for memory history
## Usage Trigger
- Trigger manually with: "Run memory tiering" or "整理记忆层级".
- Trigger automatically after any `/compact` command.
