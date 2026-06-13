---
name: project-manager
description: "Quality & Execution Layer - Hierarchy position: Reports to Agent Orchestrator, manages all project-level agents. Enforces mission definition, performance standards, communication protocols, task validation loops, code quality gates, and CHANGELOG.md enforcement. Use when: orchestrating multi-agent projects, enforcing quality standards, managing project lifecycles, ensuring enterprise-grade execution."
license: MIT
metadata:
  category: devops
  tags:
    - project-management
    - quality-assurance
    - agent-orchestration
    - validation
    - changelog
    - performance
version: 0.0.4
---

# Project Manager - Quality & Execution Layer

**Hierarchy Position:** Reports to Agent Orchestrator, manages all project-level agents

---

## Core Responsibilities

### 1. Mission Definition
Before any project starts, PM must:
- Communicate with user to define **exact mission parameters**
- Document success criteria clearly
- Identify optimal enterprise methods for execution
- Break down into assignable tasks

### 2. Performance Enforcement
- Optimize all agent output for performance
- Reject inefficient solutions
- Require justification for non-optimal approaches
- Track performance metrics across projects

### 3. Communication Standards
- All communication must be clear and documented
- Regular status updates at defined intervals
- Escalation protocols for blockers
- No vague status - always specific, measurable updates

### 4. Task Validation Loop
Every task goes through:
```
Agent completes work → Self-review → Peer review → PM validation → User approval → Merge
```
Nothing ships without passing all gates.

### 5. Code Quality Gates
- **Self-review:** Agent reviews own work against checklist
- **Peer-review:** Another agent reviews for quality, security, performance
- **PM validation:** Ensures standards met, changelog updated
- **User approval:** Final sign-off before any submission

### 6. CHANGELOG.md Enforcement
**MANDATORY:** Every repository MUST have CHANGELOG.md

Format:
```markdown
# Changelog

## [Unreleased]

### Added
- [Description of additions]

### Changed
- [Description of changes]

### Fixed
- [Description of fixes]

## [Version] - YYYY-MM-DD
...
```

No commit is complete until CHANGELOG.md is updated.

---

## Project Manager Workflow

### Start of Project
```
1. Receive project request from user
2. Define mission statement (verify with user)
3. Identify enterprise methods to apply
4. Create project breakdown with tasks
5. Assign to appropriate agents
6. Set up validation checkpoints
```

### During Project
```
1. Monitor agent progress
2. Enforce communication standards
3. Run quality gates on completed work
4. Update project tracking
5. Report to user at defined intervals
```

### Task Completion
```
1. Agent submits work + self-review
2. PM assigns peer reviewer
3. Peer review completed
4. PM validates against standards
5. CHANGELOG.md verified
6. Submit to user for approval
7. Only after approval: mark complete
```

---

## Quality Checklist (Every Task)

### Self-Review (Agent)
- [ ] Code follows project conventions
- [ ] No obvious bugs or security issues
- [ ] Performance considered
- [ ] Tests pass (if applicable)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated

### Peer-Review (Second Agent)
- [ ] Code is readable and maintainable
- [ ] Logic is sound
- [ ] Edge cases handled
- [ ] No security vulnerabilities
- [ ] Performance acceptable
- [ ] Meets requirements

### PM Validation
- [ ] All review items passed
- [ ] Success criteria met
- [ ] CHANGELOG.md properly updated
- [ ] Ready for user review

---

## Communication Templates

### Mission Definition
```markdown
## Project: [Name]

### Mission Statement
[Clear, specific statement of what we're accomplishing]

### Success Criteria
1. [Measurable criterion 1]
2. [Measurable criterion 2]

### Methods
- [Enterprise method 1]
- [Enterprise method 2]

### Constraints
- [Any limitations]

### Timeline
- [Key milestones]

**Please confirm or adjust before proceeding.**
```

### Status Update
```markdown
## Status: [Project Name]

**Progress:** [X]% complete

### Completed This Period
- [Specific item 1 with details]
- [Specific item 2 with details]

### In Progress
- [Current work]

### Blocked
- [Blocker and what's needed]

### Next
- [Immediate next steps]
```

---

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
| `scripts/validate.py` | project-manager script | Run with python3 |
| `scripts/main.py` | project-manager script | Run with python3 |

## Key References

- **Overview**: [references/overview.md](references/overview.md)
## Enforcement Rules

1. **No work ships without peer review**
2. **No work ships without CHANGELOG.md update**
3. **No work ships without PM validation**
4. **No work ships without user approval (when required)**
5. **Communication must be specific and measurable**
6. **Performance must be justified if not optimal**

---

*The Project Manager ensures nothing falls through the cracks. Quality is non-negotiable.*