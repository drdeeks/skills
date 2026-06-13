---
name: backup-protocol
description: "Multi-destination backup system with crew/agent selection, three-tier exclusion, encryption, compression, and automatic scheduling. Supports local, SSH, git, and cloud destinations. Provider-agnostic: works with any LLM backend."
license: MIT
metadata:
  openclaw:
    tags:
      - backup
      - recovery
      - automation
      - scheduling
      - crew
      - agent
    category: devops
    priority: high
  hermes:
    tags:
      - backup
      - recovery
      - automation
    category: automation
    related_skills:
      - agent-memory
      - tool-enforcement
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

# Backup Protocol

## Overview

Multi-destination backup system derived from `backup-interactive.sh`. Supports:
- **Crew and agent selection** — backup specific crews/agents or all
- **Three backup modes** — plan-history, docker-full, combo
- **Five destination types** — local, external, SSH, git, cloud
- **Three-tier exclusion** — always, bloat, docker
- **Encryption** — AES-256-CBC with PBKDF2 for sensitive files
- **Compression** — optional tar.gz output
- **Automatic scheduling** — cron-based timer setup
- **Integrity verification** — manifest and checksum validation

## Workspace Detection

Scripts detect workspace automatically by scanning (in order):
1. Environment variables: `AGENT_HOME`, `AGENT_WORKSPACE`, `WORKSPACE`
2. Common paths: `/opt/${PACKAGE_NAME}/`, `/data/agents/`, `~/agents/`, etc.
3. Walk up from script location looking for `SOUL.md`, `agent.json`, `MEMORY.md`
4. First argument if provided

## When to Use This Skill

- After major changes — backup before risky operations
- Regular scheduled backups — daily or weekly
- Before migrations — backup everything
- After critical fixes — backup the working state
- When deploying agents to new environments

## Workflow

### Step 1: Initialize Backup Configuration

```bash
bash scripts/backup-interactive.sh init
```

Follow the interactive prompts to configure destination, mode, encryption, and scheduling.

### Step 2: Execute Backup

```bash
# Backup specific crew
bash scripts/backup-interactive.sh --crews alpha,beta

# Backup all agents (full)
bash scripts/backup-interactive.sh --all-agents --agent full

# Backup everything (combo)
bash scripts/backup-interactive.sh --combo all-full
```

### Step 3: Verify Backup Integrity

```bash
bash scripts/backup-interactive.sh validate
```

### Step 4: Schedule Automatic Backups

```bash
bash scripts/backup-interactive.sh --setup-timer --timer 6
```

## Prerequisites

- Bash shell
- rsync (required for file copying)
- OpenSSL (for encryption)
- Git (optional, for git destination)
- SSH (optional, for SSH destination)

## Commands

| Command | Purpose |
|---------|---------|
| `init` | Interactive setup wizard |
| `backup` | Execute a backup (default) |
| `restore` | Restore from backup |
| `status` | Show current config and last backup |
| `list` | List available backups |
| `validate` | Verify backup integrity |
| `test` | Run comprehensive test suite |

## Backup Modes

### Plan History
Metadata and config only — small, suitable for Git.
Excludes: `*.tar`, `*.gz`, `*.zip`, `*.img`, `*.iso`, `.docker/`

### Docker Full
Complete Docker files and images.

### Combo (Default)
Both plan-history + docker-full combined.

## Destination Types

| Type | Command | Use Case |
|------|---------|----------|
| `local` | Default | Local filesystem |
| `external` | `--type external` | External drive |
| `ssh` | `--type ssh --dest ssh://user@host:/path` | Remote SSH |
| `git` | `--type git --dest https://github.com/user/repo` | Git repository |
| `cloud` | `--type cloud --dest s3://bucket/path` | Cloud storage (S3/GCS) |

## Three-Tier Exclusion System

### Tier 1: Always Excluded
```
.git/, __pycache__/, *.pyc, .DS_Store, *.bak, *.tmp, *.swp, Thumbs.db, desktop.ini
```

### Tier 2: Bloat Excluded (unless --no-exclude-bloat)
```
node_modules/, .npm/, .yarn/, vendor/, bower_components/, dist/, build/,
.parcel-cache/, .next/, .nuxt/, coverage/, *.log, logs/, *.lock
```
Note: Only excluded if a lockfile exists in the source directory.

### Tier 3: Docker Excluded
```
checkpoints/, cache/, tmp/, .docker/
```

### User-Specified
```bash
bash scripts/backup-interactive.sh --exclude "pattern1" --exclude "pattern2"
```

## CLI Options

### Selection
- `--crews crew1,crew2` — Specific crews
- `--agents agent1,agent2` — Specific agents
- `--all-crews` — All crews
- `--all-agents` — All agents
- `--combo <mode>` — Preset combo (crews-configs, crews-full, crews-workspaces, all-full)

### Backup Options
- `--mode <mode>` — plan-history, docker-full, combo
- `--crew <level>` — configs (default), full, workspaces
- `--agent <level>` — configs (default), full
- `--full` — Include sessions and workflows
- `--include-skills` — Include skills directory
- `--include-git` — Include .git directory
- `--include-hidden` — Include hidden files (default: yes)
- `--exclude-hidden` — Exclude hidden files

### Destination Options
- `--type <type>` — local, external, ssh, git, cloud
- `--dest <path>` — Destination path/URL
- `--compress` — Compress to tar.gz
- `--encrypt` — Encrypt sensitive files

### Scheduling
- `--setup-timer` — Enable automatic backups
- `--timer <hours>` — Interval in hours (default: 6)

### Output
- `--dry-run` — Preview without writing
- `--quiet` — Suppress output
- `--json` — Machine-readable output

## Usage

### Interactive Setup

```bash
bash scripts/backup-interactive.sh init
```

Presents prompts for:
1. Backup destination
2. Backup type (local/external/ssh/git/cloud)
3. Backup mode (plan-history/docker-full/combo)
4. Hidden file inclusion
5. Git inclusion
6. node_modules exclusion
7. Bloat exclusion
8. Automatic timer
9. Encryption
10. Compression

### Backup Specific Crew

```bash
bash scripts/backup-interactive.sh --crews alpha,beta
```

### Backup All Agents (Full)

```bash
bash scripts/backup-interactive.sh --all-agents --agent full
```

### Backup Everything (Combo)

```bash
bash scripts/backup-interactive.sh --combo all-full
```

### Backup to Git

```bash
bash scripts/backup-interactive.sh --type git --dest https://github.com/user/repo
```

### Backup to SSH

```bash
bash scripts/backup-interactive.sh --type ssh --dest ssh://user@host:/backups
```

### Backup to Cloud

```bash
bash scripts/backup-interactive.sh --type cloud --dest s3://my-bucket/backups
```

### Setup Automatic Backups

```bash
bash scripts/backup-interactive.sh --setup-timer --timer 6
```

### Validate Backup

```bash
bash scripts/backup-interactive.sh validate
```

### Run Tests

```bash
bash scripts/backup-interactive.sh test
```

## Backup Output Structure

```
backup-YYYYMMDD-HHMMSS/
├── BACKUP_MANIFEST.txt
├── crews/
│   └── <crew-name>/...
├── agents/
│   └── <agent-name>/...
├── docker/
│   ├── images/*.tar
│   └── volumes/*.tar.gz
├── config/...
├── plugins/...
├── sessions/...        # full mode only
├── workflows/...       # full mode only
└── skills/...          # --include-skills only
```

## Scripts

| Script | Purpose | Path |
|--------|---------|------|
| backup-interactive.sh | Main backup system | scripts/backup-interactive.sh |
| backup.sh | Simple backup wrapper | scripts/backup.sh |

## Safety Practices

- Destination validated before backup
- Encryption key backed up with rotation (keeps last 10)
- Backup manifest records all settings
- Integrity verification after backup
- Never overwrite critical files — use override protocol
- See [safety-practices.md](references/safety-practices.md) for details
- See [critical-file-protection.md](references/critical-file-protection.md) for override protocol

## Free-First Strategy

| Tier | Cost | Stack | Escalation Criteria |
|---|---|---|---|
| **Tier 0** | $0/mo | Bash + rsync + openssl | Default — covers all individual use |
| **Tier 1** | $0-5/mo | + CI/CD automated validation | When validating 10+ backups automatically |
| **Tier 2** | $5-20/mo | + Hosted backup registry | When distributing across a team or org |

## Enforced Output Statistics

After each backup, report:
- Total files backed up
- Total size of backup
- Number of sensitive files encrypted
- Last backup timestamp
- Backup mode used

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| No encryption key | First-time setup needed | Run `init` |
| Permission denied | Wrong file permissions | Check chmod |
| Disk space | Insufficient storage | Free up space |
| SSH connection failed | Network or auth issue | Check SSH config |
| Git push failed | Remote not configured | Check git remote |
| rsync not found | Missing dependency | Install rsync |

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
| `scripts/validate.py` | backup-protocol script | Run with python3 |
## Key References

- [safety-practices.md](references/safety-practices.md)
- [critical-file-protection.md](references/critical-file-protection.md)
- [backup-restore.md](references/backup-restore.md)
- [error-handling.md](references/error-handling.md)
- [free-first-strategy.md](references/free-first-strategy.md)

## Sources

- **Docker Documentation**: https://docs.docker.com
- **OpenSSL Documentation**: https://www.openssl.org/docs/
- **rsync Manual**: https://man7.org/linux/man-pages/man1/rsync.1.html
