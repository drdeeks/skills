---
name: adaptive-reasoning
description: Automatically assess task complexity and adjust reasoning level. Triggers on every user message to evaluate whether extended thinking (reasoning mode) would improve response quality. Use this as a pre-processing step before answering complex questions.
version: 0.0.5
---

# Adaptive Reasoning

Self-assess complexity before responding. Adjust reasoning level dynamically.

## Quick Assessment (run mentally on every request)

Score the request 0-10 on these dimensions:

| Signal | Weight | Examples |
|--------|--------|----------|
| **Multi-step logic** | +3 | Planning, proofs, debugging chains |
| **Ambiguity** | +2 | Nuanced questions, trade-offs, "it depends" |
| **Code architecture** | +2 | System design, refactoring, security review |
| **Math/formal reasoning** | +2 | Calculations, algorithms, logic puzzles |
| **Novel problem** | +1 | No clear pattern, requires creativity |
| **High stakes** | +1 | Production changes, irreversible actions |

**Subtract:**
- Routine/repetitive task: -2
- Clear single answer: -2
- Simple lookup/fetch: -3

## Decision Thresholds

| Score | Action |
|-------|--------|
| ≤2 | Stay fast. No reasoning needed. |
| 3-5 | Standard response. Light internal deliberation. |
| 6-7 | Consider `/reasoning on` or pause to think explicitly. |
| ≥8 | **Activate extended thinking.** Complex problem warrants it. |

## Activation (Automatic)

**Do not ask. Just activate.**

| Score | Action |
|-------|--------|
| ≤5 | Respond normally. No change. |
| 6-7 | Enable reasoning silently. Add 🧠 at end of response. |
| ≥8 | Enable reasoning. Add 🧠🔥 at end of response. |

### Visual Indicator

Always append the reasoning icon at the **very end** of your response:

- **Score 6-7:** `🧠` (thinking mode active)
- **Score ≥8:** `🧠🔥` (deep thinking mode)
- **Score ≤5:** No icon (fast mode)

### How to Activate

Use `session_status` tool or `/reasoning on` command internally before responding:

```
/reasoning on
```

Or via tool:
```json
{"action": "session_status", "reasoning": "on"}
```

After completing a complex task, optionally disable to save tokens on follow-ups:
```
/reasoning off
```

## Examples

**Low complexity (score: 1)**
> "What time is it in Tokyo?"
→ Simple lookup. Answer immediately. No icon.

**Medium complexity (score: 4)**
> "Refactor this function to be more readable"
→ Standard response with brief explanation. No icon.

**High complexity (score: 7)**
> "Design a caching strategy for this API with these constraints..."
→ Enable reasoning. Thoughtful response ends with: 🧠

**Very high complexity (score: 9)**
> "Debug why this distributed system has race conditions under load"
→ Enable extended thinking. Deep analysis ends with: 🧠🔥

## Integration

This skill runs as mental preprocessing. No external tools needed.

For explicit control:
- `/reasoning on` — Enable extended thinking
- `/reasoning off` — Disable (faster responses)
- `/status` — Check current reasoning state

## When NOT to Escalate

- User explicitly wants quick answer ("just tell me", "quick", "tldr")
- Time-sensitive requests where speed matters more than depth
- Conversational/social messages (banter, greetings)
- Already in reasoning mode for this session
- User previously disabled reasoning in this conversation


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
| `scripts/validate.py` | adaptive-reasoning script | Run with python3 |
| `scripts/main.py` | adaptive-reasoning script | Run with python3 |

## Key References

- **Overview**: [references/overview.md](references/overview.md)
## Auto-Downgrade

After completing a complex task (score ≥6), if the next message is simple (score ≤3):
- Silently disable reasoning to save tokens
- Resume normal fast responses
