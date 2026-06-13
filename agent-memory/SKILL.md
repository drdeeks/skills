---
name: agent-memory
description: "Persistent memory system for agents across sessions. Logs daily notes to memory/YYYY-MM-DD.md files and promotes key learnings to MEMORY.md. Never auto-deletes logs. Provider-agnostic: works with any LLM backend."
license: MIT
metadata:
  openclaw:
    tags:
      - memory
      - persistence
      - logging
      - long-term
    category: productivity
    priority: high
  hermes:
    tags:
      - memory
      - persistence
      - logging
    category: utility
    related_skills:
      - backup-protocol
      - tool-enforcement
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

# Agent Memory

## Overview

Persistent memory system for agents that:
- Logs daily notes to `memory/YYYY-MM-DD.md` files
- Promotes key learnings to `MEMORY.md` for long-term retention
- Never auto-deletes logs — raw logs are preserved forever
- Supports tag-based logging: TODO, LESSON, DONE, etc.
- Provider-agnostic: works with any LLM backend

## Workspace Detection

Scripts detect workspace automatically by scanning (in order):
1. Environment variables: `AGENT_HOME`, `AGENT_WORKSPACE`, `WORKSPACE`
2. Common paths: `/opt/${PACKAGE_NAME}/`, `/data/agents/`, `~/agents/`, etc.
3. Walk up from script location looking for `SOUL.md`, `agent.json`, `MEMORY.md`
4. First argument if provided

## When to Use This Skill

- When an agent needs to remember things across sessions
- When reviewing past work or decisions
- When tracking TODOs and lessons learned
- When building institutional knowledge

## Prerequisites

- Bash shell
- Agent workspace with `memory/` directory

## Workflow

### Step 1: Log a Memory Entry

```bash
bash scripts/memory-log.sh "Completed auth-login.sh fix across all agents"
bash scripts/memory-log.sh -t "TODO" "Need to review backup timer"
bash scripts/memory-log.sh -t "LESSON" "Always use -it with docker exec"
```

### Step 2: Review and Promote Memories

```bash
# Review today + yesterday
bash scripts/memory-promote.sh

# Review specific date
bash scripts/memory-promote.sh 2026-04-20

# Review last week
bash scripts/memory-promote.sh --week
```

## File Structure

```
memory/
├── 2026-04-20.md    # Daily log (raw entries)
├── 2026-04-21.md
└── ...
MEMORY.md            # Curated long-term memory
```

## Scripts

| Script | Purpose | Path |
|--------|---------|------|
| main.py | Core memory management CLI | scripts/main.py |
| memory-log.sh | Log memory entry | scripts/memory-log.sh |
| memory-promote.sh | Review and promote | scripts/memory-promote.sh |

## Safety Practices

- Daily memory files are NEVER deleted
- MEMORY.md is append-only, never overwritten
- Never modify identity/config/credential files — use override protocol
- See [safety-practices.md](references/safety-practices.md) for details
- See [critical-file-protection.md](references/critical-file-protection.md) for override protocol

## Free-First Strategy

| Tier | Cost | Stack | Escalation Criteria |
|---|---|---|---|
| **Tier 0** | $0/mo | Bash + filesystem | Default — covers all individual use |
| **Tier 1** | $0-5/mo | + CI/CD automated validation | When validating 10+ memory systems automatically |
| **Tier 2** | $5-20/mo | + Hosted memory service | When distributing across a team or org |

## Enforced Output Statistics

After each memory operation, report:
- Number of entries logged
- File path where entry was written
- Total memory files in workspace

## Error Handling

- **No entries found**: Log entries with `memory-log.sh` first
- **Memory file not created**: Check workspace detection
- **Permission denied**: Ensure write permissions to memory directory

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| No entries found | No memory logged yet | Run memory-log.sh |
| File not created | Workspace not detected | Set AGENT_HOME or pass path |
| Permission denied | Wrong permissions | Check chmod (use 755/644) |

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
| `scripts/validate.py` | agent-memory script | Run with python3 |
## Key References

- **Memory architecture**: [references/memory-architecture.md](references/memory-architecture.md)
- **Overview**: [references/overview.md](references/overview.md)
- **Quickstart**: [references/quickstart.md](references/quickstart.md)
- **Directory**: [references/directory.md](references/directory.md)
- **Safety practices**: [references/safety-practices.md](references/safety-practices.md)
- **Critical file protection**: [references/critical-file-protection.md](references/critical-file-protection.md)
- **Autonomy protocol**: [references/autonomy-protocol.md](references/autonomy-protocol.md)
- **Heartbeat patterns**: [references/heartbeat-patterns.md](references/heartbeat-patterns.md)
- **Context conservation**: [references/context-conservation.md](references/context-conservation.md)
- **How to not disappear**: [references/how-to-not-disappear.md](references/how-to-not-disappear.md)
- **Identity persistence test**: [references/identity-persistence-test.md](references/identity-persistence-test.md)
- **Semantic memory**: [references/semantic-memory.md](references/semantic-memory.md)
- **Mission pulse**: [references/mission-pulse.md](references/mission-pulse.md)
- **Community execution gap**: [references/community-execution-gap.md](references/community-execution-gap.md)
- **Moltbook**: [references/moltbook.md](references/moltbook.md)
- **Autobiography**: [references/autobiography.md](references/autobiography.md)
- **Style guide**: [references/style-guide.md](references/style-guide.md)
- **Projects**: [references/projects.md](references/projects.md)
- **The covenant**: [references/the-covenant.md](references/the-covenant.md)
- **Meditations**: [references/meditations-ship-of-theseus.md](references/meditations-ship-of-theseus.md)
- **PBEM games**: [references/experiments-pbem-games.md](references/experiments-pbem-games.md)
- **AgentMail**: [references/agentmail.md](references/agentmail.md)
- **Skills - 4Claw**: [references/skills-4claw.md](references/skills-4claw.md)
- **Skills - DeviantArt**: [references/skills-devaintart.md](references/skills-devaintart.md)
- **Skills - Knowledge base indexing**: [references/skills-knowledge-base-indexing.md](references/skills-knowledge-base-indexing.md)
- **Skills - Shellmates**: [references/skills-shellmates.md](references/skills-shellmates.md)
- **Strangerloops sync**: [references/strangerloops-sync.md](references/strangerloops-sync.md)

## Sources

- **Docker Documentation**: https://docs.docker.com
- **Bash Scripting Guide**: https://www.gnu.org/software/bash/manual/
