# OpenClaw Hermes Docker - Pitfalls

## Common Pitfalls

1. **Bind mounts, NOT volumes** — the old pattern used Docker volumes (`titan-data:/data`); that created copies. Current pattern: `${OPENCLAW_DIR:-~/.openclaw}/agents/<name>:/data/agents/<name>` directly. No `volumes:` section in docker-compose.yml at all.

2. **agent_brain_mcp.py lives in toolkit** — at `${OPENCLAW_DIR:-~/.openclaw}/agents/.scripts/agent-toolkit/agent_brain_mcp.py`, bind-mounted read-only into containers. Not baked into image. Not copied to build context.

3. **Entrypoint never overwrites host files** — it only writes stubs if files are completely missing. Edit on host, restart container.

4. **hermes-agent source must be in build context** — run `./agent-bootstrap.sh docker` to copy it into `${OPENCLAW_DIR:-~/.openclaw}/docker/hermes-agent/`

5. **mcp package required** — install hermes-agent with `[mcp]` extra

6. **OpenClaw is Node.js** — base image needs both Python AND Node.js. Use `python:3.11-slim` as base, then install Node.js separately.

7. **Config regenerates on container start** — always edit the HOST `${OPENCLAW_DIR:-~/.openclaw}/openclaw.json`, then restart the container

8. **openclaw.json can have broken braces** — the `gateway.tailscale` section sometimes gets a duplicate closing brace. Validate with `python3 -m json.tool` before generating Docker. Look for extra `}\n}` around line 363.

9. **Entrypoint uses quoted heredoc** — `python3 << 'PYEOF'` (not `python3 << PYEOF`) to prevent variable expansion in the embedded Python script

10. **Dockerfile does NOT COPY agent_brain_mcp.py** — it's bind-mounted at runtime. If you see `COPY agent_brain_mcp.py` in the Dockerfile, it's from the old pattern.

11. **bootstrap `cmd_docker` verifies brain exists** — it no longer copies agent_brain_mcp.py to the build dir. Instead it checks `${OPENCLAW_DIR:-~/.openclaw}/agents/.scripts/agent-toolkit/agent_brain_mcp.py` exists and warns if missing.

12. **Test suite at `${OPENCLAW_DIR:-~/.openclaw}/docker/tests/`** — run `./tests/run_tests.sh` for unit+infra, `--all` for smoke tests. Requires `pytest` and `pyyaml` installed.

13. **No top-level `volumes:` in compose** — the old pattern had `volumes: { titan-data: {} }`. New pattern: pure bind mounts, zero Docker volumes.
