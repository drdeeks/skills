---
name: tool-enforcement
description: "Enforces workspace structure and tool availability for agents. Ensures all required tools are present and properly configured. Provider-agnostic: works with any LLM backend."
license: MIT
metadata:
  openclaw:
    tags:
      - enforcement
      - tools
      - workspace
      - structure
    category: devops
    priority: medium
  hermes:
    tags:
      - enforcement
      - tools
      - workspace
    category: automation
    related_skills:
      - agent-memory
      - backup-protocol
  providers:
    - openai
    - claude
    - mistral
    - gemini
    - hermes
    - copilot
    - any
version: 0.0.3
---

# Tool Enforcement

## Overview

Ensures agent workspace has all required tools and proper structure:
- Validates tools/ directory exists
- Checks required tools are present
- Enforces tool permissions
- Validates tool functionality

## Workspace Detection

Scripts detect workspace automatically by scanning (in order):
1. Environment variables: `AGENT_HOME`, `AGENT_WORKSPACE`, `WORKSPACE`
2. Common paths: `/opt/${PACKAGE_NAME}/`, `/data/agents/`, `~/agents/`, etc.
3. Walk up from script location looking for `SOUL.md`, `agent.json`, `MEMORY.md`
4. First argument if provided

## When to Use This Skill

- After agent initialization — validate all tools are present
- When tools are missing or corrupted
- When enforcing workspace structure rules
- When checking for dangerous chmod patterns

## Prerequisites

- Bash shell
- Agent workspace directory

## Workflow

### Step 1: Validate Tools

```bash
bash scripts/validate.sh
```

### Step 2: Fix Missing Tools

```bash
bash scripts/validate.sh --fix
```

### Step 3: Check Permissions

```bash
bash scripts/validate.sh --check-permissions
```

## Required Tools

Every agent must have:
- `enforce.sh` — Workspace structure enforcement
- `secret.sh` — Encrypted secret management
- `memory-log.sh` — Memory logging
- `memory-promote.sh` — Memory promotion
- `jsonfmt.py` — JSON formatting and validation
- `TOOLS-GUIDE.md` — Tool usage documentation
- `inject-context.sh` — Session context injection

## Scripts

| Script | Purpose | Path |
|--------|---------|------|
| validate.sh | Tool validation | scripts/validate.sh |
| validate.sh | Fix missing tools | scripts/validate.sh --fix |
| validate.sh | Check permissions | scripts/validate.sh --check-permissions |
| safe-write.sh | Safe file writing | scripts/safe-write.sh |
| safe-write.sh | Check if file is critical | scripts/safe-write.sh --check-only |

## Safety Practices

- NEVER overwrite critical files (credentials, config, identity, memory, tools)
- Store overrides in `.override/TIMESTAMP/` with `EXPLANATION.md`
- Immediately notify user/manager of any override
- Never use chmod 700/600 (except .secret-key)
- Always use 755 for directories, 644 for files
- See [safety-practices.md](references/safety-practices.md) for details
- See [critical-file-protection.md](references/critical-file-protection.md) for override protocol

## Free-First Strategy

| Tier | Cost | Stack | Escalation Criteria |
|---|---|---|---|
| **Tier 0** | $0/mo | Bash + basic tools | Default — covers all individual use |
| **Tier 1** | $0-5/mo | + CI/CD automated validation | When validating 10+ workspaces automatically |
| **Tier 2** | $5-20/mo | + Hosted validation service | When distributing across a team or org |

## Enforced Output Statistics

After each validation, report:
- Number of tools validated
- Number of missing tools found
- Number of permission issues
- Workspace structure compliance percentage

## Error Handling

- **Missing tools**: Run with `--fix` to restore missing tools
- **Permission denied**: Check file permissions with `--check-permissions`
- **Wrong workspace**: Set `AGENT_HOME` or pass workspace path

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Missing tools | Tools not initialized | Run with `--fix` |
| Permission denied | Wrong chmod | Check permissions |
| Wrong workspace | Agent not set | Set AGENT_HOME |

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
| `scripts/validate.py` | tool-enforcement script | Run with python3 |
## Key References

- [safety-practices.md](references/safety-practices.md)
- [critical-file-protection.md](references/critical-file-protection.md)
- [workspace-structure.md](references/workspace-structure.md)
- [tool-guidelines.md](references/tool-guidelines.md)
- [tool-permissions.md](references/tool-permissions.md)
- [TOOLS-GUIDE.md](TOOLS-GUIDE.md)
