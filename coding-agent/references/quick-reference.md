# Coding Agent Reference

Quick reference for coding agent delegation.

## Agent Selection Guide

| Task | Recommended Agent | Mode |
|------|------------------|------|
| Feature building | Codex or Claude Code | Interactive/Print |
| PR review | Claude Code | Print (`-p`) |
| Refactoring | Claude Code | Print (`-p`) |
| Quick fix | Just edit directly | N/A |

## PTY Requirements

- Codex: Yes (`pty: true`)
- Claude Code: No (use `--print`)
- Pi: Yes (`pty: true`)
- OpenCode: Yes (`pty: true`)
