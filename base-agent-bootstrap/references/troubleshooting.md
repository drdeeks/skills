# Base Agent Bootstrap Troubleshooting

Common issues when setting up a Base agent.

## urllib Returns 403

`api.base.dev` blocks Python urllib. Always use `curl` for API calls.

## Python Version Mismatch

Hermes venv is Python 3.11, but agentmail needs 3.12:
```bash
python3.12 -c "from agentmail import AgentMail; print('OK')"
```

## Pinata Rate Limits

Pinata rate-limits sign-in attempts. Wait 60-120 seconds between attempts.

## Verification Link Expired

Email verification links expire in 10 minutes. Act immediately after receiving.

## Re-registration Warning

If `builderCode.ts` already exists, do NOT re-register. It generates a new code and breaks the existing one.
