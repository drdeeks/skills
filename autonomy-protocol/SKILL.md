---
name: autonomy-protocol
description: "The autonomy protocol — a spectrum from deterministic to emergent. Use when deciding whether to write a script, call a tool, load a skill, spawn a subagent, or handle something in main agent context. Provider-agnostic: works with any LLM backend."
license: MIT
metadata:
  openclaw:
    tags:
      - autonomy
      - delegation
      - scripts
      - subagents
      - planning
    category: productivity
    priority: high
  hermes:
    tags:
      - automation
      - planning
      - architecture
    category: automation
    related_skills:
      - tool-enforcement
      - enterprise-blueprint
  providers:
    - openai
    - claude
    - mistral
    - gemini
    - hermes
    - copilot
    - any
version: 0.0.5
---

# The Autonomy Protocol

The spectrum from deterministic to emergent. Push everything as far LEFT as it can go.

## When to Use This Skill

- When deciding how to handle a task
- When evaluating whether to script, tool, or delegate
- When planning complex workflows
- When optimizing for cost and consistency

## Prerequisites

- None — this is a decision-making framework

## Workflow

### Step 1: Assess the Task

Determine if the task is:
- Repetitive → Script
- External API → Tool
- Complex workflow → Skill
- Parallel exploration → Subagent
- One-off judgment → Main agent

### Step 2: Apply the Spectrum

```
BUILD ←————————————————————————————————————————————→ THINK
  scripts    tools    skills    subagents    main agent
```

### Step 3: Document Decision

Record why you chose a specific layer for future reference.

## The Spectrum

| Layer | What | Who controls it | Cost | Consistency |
|-------|------|-----------------|------|-------------|
| 1. Scripts | Code you write | You | Zero tokens | Perfect |
| 2. Tools | Capabilities you call | Someone else | Zero tokens | Perfect |
| 3. Skills | Methodologies you follow | You follow guidance | Some tokens | High |
| 4. Subagents | Fresh context, full SOUL | Delegated | Expensive | High |
| 5. Main agent | Coordinate and decide | You | Most expensive | Variable |

## Decision Matrix

| Scenario | Best Choice | Why |
|----------|-------------|-----|
| Repetitive task | Script | Zero cost, perfect consistency |
| External API call | Tool | Already built, tested |
| Complex workflow | Skill | Guidance + flexibility |
| Parallel exploration | Subagents | Independent contexts |
| One-off judgment | Main agent | Human-level reasoning |

## Safety Practices

- Never overwrite critical files — use override protocol
- Always consider if a task could kill the agent's configuration
- When in doubt, use a lower layer (script/tool) before escalating
- Document all decisions for audit trail
- See [safety-practices.md](references/safety-practices.md) for details
- See [critical-file-protection.md](references/critical-file-protection.md) for override protocol

## Scripts

| Script | Purpose | Path |
|--------|---------|------|
| autonomy.sh | Decision helper | scripts/autonomy.sh |
| validate-decision.sh | Validate decision | scripts/validate-decision.sh |

## Free-First Strategy

| Tier | Cost | Stack | Escalation Criteria |
|---|---|---|---|
| **Tier 0** | $0/mo | Bash + decision matrix | Default — covers all individual use |
| **Tier 1** | $0-5/mo | + CI/CD automated validation | When validating 10+ decisions automatically |
| **Tier 2** | $5-20/mo | + Hosted decision service | When distributing across a team or org |

## Enforced Output Statistics

After each decision, report:
- Task assessed
- Layer selected
- Reason for selection

## Error Handling

- **Over-engineering**: Don't use subagents for simple tasks
- **Under-utilizing tools**: Don't rewrite what's already available
- **Ignoring cost**: Consider token usage for large tasks

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Over-engineering | Using subagents for simple tasks | Use scripts/tools instead |
| Under-utilizing | Rewriting existing tools | Check available tools first |
| High cost | Ignoring token usage | Consider cost implications |

## Provider Compatibility

| Provider | Compatibility | Notes |
|---|---|---|
| Claude (Anthropic) | Full | Tool use, MCP servers |
| OpenAI / ChatGPT | Full | Function calling, assistants |
| Mistral / Vibe | Full | Tool calling, script execution |
| Gemini (Google) | Full | Extensions, Vertex AI |
| Hermes (Nous) | Full | Tool-use fine-tuned |
| GitHub Copilot | Partial | Code generation; use external runner for scripts |
| Any LLM + tools | Full | All scripts are plain Python, provider-independent |


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
| `scripts/validate.py` | autonomy-protocol script | Run with python3 |
## Key References

- [spectrum.md](references/spectrum.md)
- [examples.md](references/examples.md)
- [axioms.md](references/axioms.md)
