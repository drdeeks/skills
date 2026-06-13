---
description: Fix systemd service WorkingDirectory issues when services fail to start
  due to path problems
name: fix-systemd-workingdirectory
version: 0.0.5
---

# Fix Systemd Service WorkingDirectory Issues

## When to Use This Skill
When a systemd service fails with errors like:
- "Changing to the requested working directory failed: No such file or directory"
- "Failed to change to working directory"
- Service fails to start due to path issues

## Steps to Fix

### 1. Check Service Status and Logs
```bash
systemctl status <service-name>
journalctl -u <service-name> -n 20
```

Look for errors indicating working directory problems.

### 2. Examine the Service File
```bash
cat /etc/systemd/system/<service-name>.service
```

Check the `WorkingDirectory` directive in the `[Service]` section.

### 3. Verify Actual Directory Exists
```bash
ls -la /path/from/WorkingDirectory
```

If the directory doesn't exist, you have two options:
- Create the missing directory
- Update WorkingDirectory to point to an existing directory

### 4. Find Correct Directory Location
Search for the service's actual files:
```bash
find /home -type d -name "*<service-name>*" 2>/dev/null | head -10
ls -la ${HOME}/ | grep -E "\\.(gateway|hermes)"
```

### 5. Update the Service File
```bash
sudo sed -i 's|OldWorkingDirectory|NewWorkingDirectory|' /etc/systemd/system/<service-name>.service
```

Example:
```bash
sudo sed -i 's|WorkingDirectory=${HOME}/hermes-agent/workspaces/agent-allman|WorkingDirectory=${HOME}/.agent-allman.gateway|' /etc/systemd/system/agent-allman-gateway.service
```

### 6. Reload Systemd and Restart Service
```bash
sudo systemctl daemon-reload
sudo systemctl start <service-name>
```

### 7. Verify Service is Running
```bash
systemctl status <service-name>
```

## Verification
- Service should show "Active: active (running)"
- No more working directory errors in logs
- Service maintains active state over time

## Common Causes
- Service configuration references old directory structure
- Directory was moved or renamed after service creation
- Template services deployed to incorrect paths
- Gateway or agent directory restructuring


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
| `scripts/validate.py` | fix-systemd-workingdirectory script | Run with python3 |
| `scripts/main.py` | fix-systemd-workingdirectory script | Run with python3 |

## Key References

- **Overview**: [references/overview.md](references/overview.md)
## Prevention
- When deploying services, verify WorkingDirectory points to existing path
- Use environment variables or dynamic paths when possible
- Document directory structure assumptions in service descriptions