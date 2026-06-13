# OpenClaw Hermes MCP Integration - MCP Tools

## agent_brain_mcp.py Tools

| Tool | Description |
|------|-------------|
| `agent_chat` | Run hermes agent loop with tool calling |
| `agent_memory_get` / `agent_memory_set` | Persistent memory across sessions |
| `agent_skills_list` | Available skills inventory |
| `agent_insights` | Usage/cost analytics |
| `agent_sessions` | Recent session listing |
| `agent_identity` | SOUL.md, USER.md, config |

## Critical Implementation Details

- `agent_chat` MUST run in ThreadPoolExecutor with hard timeout (300s) — never hang the MCP server
- All tools return JSON strings
- All tools have try/except
- All tools log with timestamps
