---
name: openclaw-hermes-docker
description: Deploy OpenClaw multi-agent fleet in Docker containers with Hermes agent
license: MIT
version: 0.0.5
---
# OpenClaw + Hermes Brain Docker Deployment

Deploy each OpenClaw agent in its own Docker container. Agent workspace lives
on the host at `${OPENCLAW_DIR:-~/.openclaw}/agents/<name>/` and is bind-mounted directly into
the container. No Docker volumes, no duplication.

## Architecture

Each container runs two components:
1. **OpenClaw Gateway** (Node.js) — receives Telegram messages, routes to agent
2. **Hermes Brain MCP** (Python) — agent loop, memory, skills, auto-learning as MCP tools

Key insight: OpenClaw has its own Node.js agent runtime AND supports `mcp.servers` config.
The hermes brain is exposed as an MCP tool provider via a new FastMCP server, not by
replacing OpenClaw's runtime.

```
HOST                                    CONTAINER (oc-titan)
─────────────────────────────────       ─────────────────────────────
${OPENCLAW_DIR:-~/.openclaw}/agents/titan/        ──►    /data/agents/titan/
  ├── SOUL.md                            ├── SOUL.md         (same file)
  ├── MEMORY.md                          ├── MEMORY.md
  ├── memory/                            ├── memory/
  ├── sessions/                          ├── sessions/
  ├── skills/                            ├── skills/
  ├── config.yaml                        ├── config.yaml
  ├── .env                               ├── .env
  └── agent.json                         └── agent.json

${OPENCLAW_DIR:-~/.openclaw}/openclaw.json        ──►    /data/openclaw.json (read-only)

${OPENCLAW_DIR:-~/.openclaw}/agents/.scripts/
  agent-toolkit/agent_brain_mcp.py ──►  /app/agent_brain_mcp.py (read-only)
```

**Critical:** The agent home at `${OPENCLAW_DIR:-~/.openclaw}/agents/<name>/` is the SINGLE SOURCE OF
TRUTH. Edit files on host → changes appear instantly in the container. No sync, no copy.

## Files

- `${OPENCLAW_DIR:-~/.openclaw}/agents/.scripts/agent-toolkit/agent_brain_mcp.py` — FastMCP server (lives in toolkit, bind-mounted)
- `${OPENCLAW_DIR:-~/.openclaw}/agents/.scripts/agent-toolkit/agent-bootstrap.sh` — generates all Docker files
- `${OPENCLAW_DIR:-~/.openclaw}/docker/Dockerfile` — python:3.11-slim + Node.js + hermes-agent
- `${OPENCLAW_DIR:-~/.openclaw}/docker/entrypoint.sh` — per-agent MCP config injection
- `${OPENCLAW_DIR:-~/.openclaw}/docker/docker-compose.yml` — bind-mounts agent homes from host

## Quick Start

```bash
# 1. Create agents (workspace goes to ${OPENCLAW_DIR:-~/.openclaw}/agents/<name>/)
cd ${OPENCLAW_DIR:-~/.openclaw}/agents/.scripts/agent-toolkit
./agent-bootstrap.sh --openclaw init titan
./agent-bootstrap.sh configure titan

# 2. Generate openclaw.json entries + Docker files
./agent-bootstrap.sh config
./agent-bootstrap.sh docker

# 3. Build and launch
cd ${OPENCLAW_DIR:-~/.openclaw}/docker
docker compose up -d --build
```

## MCP Brain Tools

agent_brain_mcp.py (at `${OPENCLAW_DIR:-~/.openclaw}/agents/.scripts/agent-toolkit/agent_brain_mcp.py`)
exposes these tools to OpenClaw via `mcp.servers` config injection:

| Tool | Description |
|------|-------------|
| `agent_chat` | Run hermes agent loop with tool calling |
| `agent_memory_get` / `agent_memory_set` | Persistent memory across sessions |
| `agent_skills_list` | Available skills inventory |
| `agent_insights` | Usage/cost analytics |
| `agent_sessions` | Recent session listing |
| `agent_identity` | SOUL.md, USER.md, config |

## docker-compose.yml Pattern

Each agent gets 3 bind mounts — NO Docker volumes:

```yaml
services:
  titan:
    build: .
    container_name: oc-titan
    restart: unless-stopped
    volumes:
      - ${OPENCLAW_DIR:-~/.openclaw}/agents/titan:/data/agents/titan                # agent home
      - ${OPENCLAW_DIR:-~/.openclaw}/openclaw.json:/data/openclaw.json:ro           # shared config
      - ${OPENCLAW_DIR:-~/.openclaw}/agents/.scripts/agent-toolkit/agent_brain_mcp.py:/app/agent_brain_mcp.py:ro  # brain
    environment:
      - OPENCLAW_ROOT=/data
      - HERMES_HOME=/data/agents/titan
      - AGENT_ID=titan
      - TELEGRAM_BOT_TOKEN=<token>
```

No `volumes:` section needed. No named volumes. Host directory IS the workspace.

## Dockerfile Pattern

```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y curl git jq \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs && rm -rf /var/lib/apt/lists/*
RUN npm install -g openclaw
COPY hermes-agent/ /app/hermes-agent/
WORKDIR /app/hermes-agent
RUN pip install --no-cache-dir -e ".[mcp]" && pip install --no-cache-dir pyyaml
# agent_brain_mcp.py is bind-mounted, not baked in
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
```

## Entrypoint Pattern

1. Set HERMES_HOME, PYTHONPATH
2. Create missing directories (only if absent — never overwrite host files)
3. Write identity stubs ONLY if completely missing
4. Generate per-agent openclaw.json from shared config
5. Inject `mcp.servers.hermes-brain` entry pointing to agent_brain_mcp.py
6. Start `openclaw gateway run`

## Config Injection

The entrypoint injects MCP config into per-agent openclaw.json at container start:

```json
{
  "mcp": {
    "servers": {
      "hermes-brain": {
        "command": "python3",
        "args": ["/app/agent_brain_mcp.py"],
        "env": {
          "AGENT_ID": "titan",
          "HERMES_HOME": "/data/agents/titan"
        }
      }
    }
  }
}
```

## Backup

Agent workspace is on the host. Back up by copying the directory:

```bash
# Single agent
cp -r ${OPENCLAW_DIR:-~/.openclaw}/agents/titan/ ./titan-backup/

# All agents
for agent in allman aton avery guard main mort titan tom; do
    cp -r ${OPENCLAW_DIR:-~/.openclaw}/agents/$agent/ ./backup-$agent/
done
```

No `docker cp` needed. No volume export. Just copy files.

## Testing

```bash
cd ${OPENCLAW_DIR:-~/.openclaw}/docker
./tests/run_tests.sh           # Unit + infra + bootstrap
./tests/run_tests.sh --all     # Include smoke tests
./tests/run_tests.sh --smoke   # Live container tests only
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
| `scripts/main.py` | openclaw-hermes-docker script | Run with python3 |

## Key References

- **Overview**: [references/overview.md](references/overview.md)
- **Architecture**: [references/architecture.md](references/architecture.md)
- **Pitfalls**: [references/pitfalls.md](references/pitfalls.md)

## Sources

- Docker Documentation: https://docs.docker.com
- OpenClaw GitHub: https://github.com/openclaw/openclaw
- FastMCP Documentation: https://github.com/jlowin/fastmcp
- Hermes Agent: https://github.com/nousresearch/hermes-agent

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

## Pitfalls

- **Bind mounts, NOT volumes** — the old pattern used Docker volumes (`titan-data:/data`); that created copies. Current pattern: `${OPENCLAW_DIR:-~/.openclaw}/agents/<name>:/data/agents/<name>` directly. No `volumes:` section in docker-compose.yml at all.
- **agent_brain_mcp.py lives in toolkit** — at `${OPENCLAW_DIR:-~/.openclaw}/agents/.scripts/agent-toolkit/agent_brain_mcp.py`, bind-mounted read-only into containers. Not baked into image. Not copied to build context.
- **Entrypoint never overwrites host files** — it only writes stubs if files are completely missing. Edit on host, restart container.
- **hermes-agent source must be in build context** — run `./agent-bootstrap.sh docker` to copy it into `${OPENCLAW_DIR:-~/.openclaw}/docker/hermes-agent/`
- **mcp package required** — install hermes-agent with `[mcp]` extra
- **OpenClaw is Node.js** — base image needs both Python AND Node.js. Use `python:3.11-slim` as base, then install Node.js separately.
- **Config regenerates on container start** — always edit the HOST `${OPENCLAW_DIR:-~/.openclaw}/openclaw.json`, then restart the container
- **openclaw.json can have broken braces** — the `gateway.tailscale` section sometimes gets a duplicate closing brace. Validate with `python3 -m json.tool` before generating Docker. Look for extra `}\n}` around line 363.
- **Entrypoint uses quoted heredoc** — `python3 << 'PYEOF'` (not `python3 << PYEOF`) to prevent variable expansion in the embedded Python script
- **Dockerfile does NOT COPY agent_brain_mcp.py** — it's bind-mounted at runtime. If you see `COPY agent_brain_mcp.py` in the Dockerfile, it's from the old pattern.
- **bootstrap `cmd_docker` verifies brain exists** — it no longer copies agent_brain_mcp.py to the build dir. Instead it checks `${OPENCLAW_DIR:-~/.openclaw}/agents/.scripts/agent-toolkit/agent_brain_mcp.py` exists and warns if missing.
- **Test suite at `${OPENCLAW_DIR:-~/.openclaw}/docker/tests/`** — run `./tests/run_tests.sh` for unit+infra, `--all` for smoke tests. Requires `pytest` and `pyyaml` installed.
- **No top-level `volumes:` in compose** — the old pattern had `volumes: { titan-data: {} }`. New pattern: pure bind mounts, zero Docker volumes.
