---
name: debug-tracer
description: Systematic upstream/downstream issue tracing for any failure — HTTP errors, load failures, CORS, network, auth, signing, UI state, backend validation. Use when debugging any "load failed", silent error, unexpected response, broken flow, or integration issue. Forces full-path diagnosis before attempting any fix. Prevents blind patching.
version: 0.0.5
---

# Debug Tracer

**One rule: trace before you fix. Never patch without confirmed root cause.**

---

## The Protocol

### Step 1 — Capture the exact failure

Before touching any code, get the exact error:
- HTTP status code (200/400/401/403/404/422/500/502/CORS)
- Browser console output (network tab + console errors)
- Backend logs if accessible
- Exact request payload that triggered it

If you don't have the exact error, **get it first**. Ask the user, check logs, run a curl.

### Step 2 — Identify the failure layer

Map the request path end-to-end:

```
User action
  → Browser/UI state (React/JS)
    → Fetch/XHR call
      → CORS preflight (OPTIONS)
        → Backend receipt
          → Middleware (auth, validation)
            → Business logic
              → External service (DB, blockchain, email)
                → Response
                  → UI rendering
```

Identify **which layer** the failure occurs at. One of:

| Layer | Signals |
|-------|---------|
| UI state | Wrong value passed, stale ref, React state timing |
| Network | `fetch failed`, `ERR_NETWORK`, timeout |
| CORS | Missing `access-control-allow-origin` on OPTIONS response |
| Auth | 401, 403, invalid token/signature |
| Validation | 400, 422, schema mismatch |
| Backend logic | 500, wrong business rule |
| External service | Blockchain revert, email bounce, 3rd party 4xx/5xx |

### Step 3 — Reproduce the exact failure with a minimal test

Test **that single layer** in isolation:

```bash
# Test CORS preflight
curl -sI -X OPTIONS <url> \
  -H "Origin: <frontend-origin>" \
  -H "Access-Control-Request-Method: POST" \
  | grep -i "access-control"

# Test backend directly (bypass browser/CORS)
curl -s -X POST <url> \
  -H "Content-Type: application/json" \
  -d '<exact-payload>' | jq .

# Test signature verification
node -e "const {ethers}=require('ethers'); console.log(ethers.verifyMessage('<msg>','<sig>'))"
```

If the isolated test **passes**, the problem is upstream (browser/CORS/network).
If it **fails**, the problem is in that layer or downstream.

### Step 4 — Binary search the path

Split the path in half. Test the midpoint. Narrow from there. Never assume.

```
Failure at UI → check state values before fetch
Failure at network → check CORS preflight response headers
Failure at backend receipt → check what payload arrived (add logging)
Failure at validation → check exact field names and types
Failure at external → check service-specific error codes
```

### Step 5 — Fix the confirmed root cause once

Only after Step 3/4 confirms the exact failure layer:
- Make the minimal change that fixes that specific layer
- Do not make additional "defensive" changes to unrelated layers
- Test again with the same isolated test from Step 3

### Step 6 — Verify end-to-end

Run the full flow once after the fix to confirm the patch resolved the root cause and didn't break anything else.

---

## Common Failure Patterns

### "Load failed" / fetch error in browser
**Always check CORS first.** Run:
```bash
curl -sI -X OPTIONS <backend-url>/<endpoint> \
  -H "Origin: <frontend-url>" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  | grep -i "access-control-allow-origin"
```
If empty → CORS is the problem. Fix: add `ALLOWED_ORIGINS` env var on backend.

### "Invalid signature" / wallet verification failure
Test the exact message + signature before touching UI code:
```bash
node -e "const {ethers}=require('ethers'); console.log(ethers.verifyMessage('<message>','<signature>').toLowerCase() === '<address>'.toLowerCase())"
```

### Stale state / wrong value sent
Add a `console.log(payload)` before the fetch. Confirm the value being sent is what you expect. Don't guess — log it.

### "Works on desktop, fails on mobile"
- Check CORS preflight (mobile browsers always send it, desktop sometimes caches it)
- Check wallet provider differences (injected vs WalletConnect)
- Check network timing (mobile is slower, promises may resolve differently)

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
| `scripts/validate.py` | debug-tracer script | Run with python3 |
| `scripts/main.py` | debug-tracer script | Run with python3 |

## Key References

- **Overview**: [references/overview.md](references/overview.md)
## What NOT to Do

- Do not change unrelated code while fixing a confirmed issue
- Do not add "defensive" changes without evidence they're needed
- Do not make the same fix in multiple places without understanding why
- Do not guess at root causes — verify them
- Do not move to the next layer without eliminating the current one
