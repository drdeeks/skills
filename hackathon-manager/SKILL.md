---
name: hackathon-manager
description: "Manages hackathon participation, project organization, and submission workflows. Tracks deadlines, team members, and deliverables."
license: MIT
version: 0.0.4
---
# Hackathon Manager

> Manages hackathon participation, project organization, and submission workflows.

## Overview

This skill helps manage hackathon participation including project organization, submission workflows, and tracking multiple project ideas across different tracks.

## Core Functions

### Project Organization
- Create project directories for hackathon ideas
- Track project status and progress
- Manage multiple project concepts
- Link projects to specific bounties/tracks

### Submission Management
- Prepare submission metadata
- Track submission deadlines
- Manage team coordination
- Handle on-chain identity integration

### Resource Management
- Track bounties and prize pools
- Map projects to relevant tracks
- Monitor competition landscape
- Manage credentials and API keys

## Key Commands

```bash
# Create project directory
mkdir -p "${HOME}/.openclaw/workspace-titan/hackathon/[project-name]"

# Track project status
# (managed through memory files and project directories)

# Prepare submission
# (handled through submission workflows)
```

## Data Structure

```
hackathon/
├── [project-name]/
│   ├── README.md
│   ├── submission.md
│   ├── credentials.json
│   └── progress.md
├── bounties.json
└── projects.json
```

## Integration

- Uses OpenClaw workspace for file operations
- Integrates with hackathon APIs (Devfolio, etc.)
- Manages ERC-8004 identity through stored credentials
- Tracks multiple bounties and prize pools

## Security

- Credentials stored in `.synth-creds.json` with restricted permissions
- API keys never shared publicly
- Submission data managed through secure workflows
- On-chain identity handled through ERC-8004

## Usage

1. Install skill: `openclaw skill add /path/to/skill`
2. Create project directories: `mkdir -p hackathon/[project-name]`
3. Track progress through memory files
4. Prepare submissions using stored credentials
5. Monitor bounties and prize pools


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
| `scripts/main.py` | hackathon-manager script | Run with python3 |

## Key References

- **Overview**: [references/overview.md](references/overview.md)
- **Hackathon Checklist**: [references/hackathon-checklist.md](references/hackathon-checklist.md)
- **Project Structure**: [references/project-structure.md](references/project-structure.md)

## Sources

- [Devfolio API Documentation](https://docs.devfolio.com/)
- [ERC-8004 Standard](https://eips.ethereum.org/EIPS/eip-8004)
- [Hackathon Best Practices](https://dev.to/t/hackathon)
## Best Practices

- Keep credentials secure and permissions restricted
- Track project progress systematically
- Map projects to relevant bounties early
- Prepare submissions well before deadlines
- Use on-chain identity for verification