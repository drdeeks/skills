# OpenClaw Hermes MCP Integration - Security Hardening

## agent_brain_mcp.py Security Features

- `_validate_filename()` — blocks path traversal (`../`), absolute paths, unsafe chars
- `_safe_read_text()` — 5MB max per file read, `errors="replace"` for encoding safety
- `_safe_write_text()` — atomic writes via temp file + rename, permission error handling
- `_clamp()` — all integer inputs clamped to sane ranges
- SIGTERM/SIGINT handlers — graceful shutdown instead of abrupt exit
- Every tool returns JSON (never raises to caller), all exceptions caught and logged
- Startup diagnostics log agent_id, model, API key presence, issues list
