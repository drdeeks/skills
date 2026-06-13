# OpenClaw Hermes Docker - Architecture

## Container Architecture

Each container runs two components:
1. **OpenClaw Gateway** (Node.js) — receives Telegram messages, routes to agent
2. **Hermes Brain MCP** (Python) — agent loop, memory, skills, auto-learning as MCP tools

Key insight: OpenClaw has its own Node.js agent runtime AND supports `mcp.servers` config. The hermes brain is exposed as an MCP tool provider via a new FastMCP server, not by replacing OpenClaw's runtime.

## Bind Mounts (NOT Volumes)

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

**Critical:** The agent home at `${OPENCLAW_DIR:-~/.openclaw}/agents/<name>/` is the SINGLE SOURCE OF TRUTH. Edit files on host → changes appear instantly in the container. No sync, no copy.
