---
name: 8004scan-webhooks
description: "Register and manage 8004scan webhooks for real-time event notifications on agent validations and feedback"
version: 0.0.2
license: MIT
allowed-tools: "Bash(curl:*) Bash(jq:*)"
metadata:
  openclaw:
    version: "1.0"
    category: blockchain
    complexity: standard
---

## Base URL

```
https://www.8004scan.io/api/v1
```

**Note**: Webhook endpoints require authentication. Include `X-API-Key` header.

## Authentication

All webhook management endpoints require a valid API key:

```bash
-H "X-API-Key: $EIGHTSCAN_API_KEY"
```

---

## Request Classification

1. **Register webhook** ("set up a webhook", "notify me when...") → Register Webhook endpoint.
2. **List webhooks** ("show my webhooks", "what webhooks do I have?") → List Webhooks endpoint.
3. **Update webhook** ("change webhook URL", "add events to webhook") → Update Webhook endpoint.
4. **Delete webhook** ("remove webhook", "stop notifications") → Delete Webhook endpoint.
5. **Check deliveries** ("webhook delivery history", "failed deliveries") → Deliveries endpoint.
6. **Verify signature** ("how to verify webhook?", "HMAC validation") → Read `references/verification.md`.

---

## Event Types

| Event | Trigger |
|-------|---------|
| `validation.requested` | A validation request is submitted for an agent |
| `validation.completed` | A validator submits their attestation response |
| `feedback.received` | New feedback is submitted for an agent |
| `feedback.revoked` | Existing feedback is revoked by its submitter |
| `star.received` | An agent receives a star rating |
| `star.removed` | A star rating is removed |

---

## Quick Reference

### Register a Webhook

```bash
curl -s -X POST "https://www.8004scan.io/api/v1/webhooks" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://yourserver.com/webhook",
    "events": ["feedback.received", "validation.completed"],
    "secret": "your-webhook-secret"
  }' | jq .
```

### List Webhooks

```bash
curl -s "https://www.8004scan.io/api/v1/webhooks" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" | jq .
```

### Update a Webhook

```bash
curl -s -X PATCH "https://www.8004scan.io/api/v1/webhooks/{webhookId}" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "events": ["feedback.received", "feedback.revoked", "star.received"],
    "active": true
  }' | jq .
```

### Delete a Webhook

```bash
curl -s -X DELETE "https://www.8004scan.io/api/v1/webhooks/{webhookId}" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" | jq .
```

### Check Delivery History

```bash
curl -s "https://www.8004scan.io/api/v1/webhooks/{webhookId}/deliveries?limit=10" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" | jq .
```

---

## Webhook Payload Format

All webhook deliveries include:

```json
{
  "event": "feedback.received",
  "timestamp": "2026-03-16T12:00:00Z",
  "data": {
    "chainId": 8453,
    "tokenId": 17,
    "agentId": "8453:17",
    ...event-specific fields...
  }
}
```

Headers on delivery:
- `X-Webhook-Signature`: HMAC-SHA256 hex digest
- `X-Webhook-Event`: Event type
- `X-Webhook-Delivery-Id`: Unique delivery ID
- `Content-Type`: `application/json`

---

## Signature Verification

Verify every incoming webhook to ensure authenticity:

```bash
# The signature is: HMAC-SHA256(secret, request_body)
EXPECTED=$(echo -n "$BODY" | openssl dgst -sha256 -hmac "$WEBHOOK_SECRET" | awk '{print $2}')
if [ "$EXPECTED" = "$RECEIVED_SIGNATURE" ]; then
  echo "Valid"
fi
```

---

## Retry Behavior

Failed deliveries (non-2xx response or timeout) are retried with exponential backoff:

| Attempt | Delay |
|---------|-------|
| 1 | Immediate |
| 2 | 1 minute |
| 3 | 5 minutes |
| 4 | 30 minutes |
| 5 | 2 hours |

After 5 failed attempts, the delivery is marked as permanently failed. Webhooks with repeated failures may be automatically disabled.

---


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
| `scripts/main.py` | 8004scan-webhooks script | Run with python3 |

## Key References

- **Webhook API**: [references/webhook-api.md](references/webhook-api.md)
- **Verification**: [references/verification.md](references/verification.md)
- **Events**: [references/events.md](references/events.md)

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

## Examples

**Example 1: Set up feedback notifications**
User: "Notify me when my agent gets feedback"
```bash
curl -s -X POST "https://www.8004scan.io/api/v1/webhooks" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://myserver.com/hook","events":["feedback.received","feedback.revoked"],"secret":"mysecret"}' | jq .
```

**Example 2: Monitor validation progress**
User: "Alert me when validation completes"
```bash
curl -s -X POST "https://www.8004scan.io/api/v1/webhooks" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://myserver.com/hook","events":["validation.requested","validation.completed"],"secret":"mysecret"}' | jq .
```

**Example 3: Debug failed deliveries**
User: "Why aren't my webhooks working?"
```bash
curl -s "https://www.8004scan.io/api/v1/webhooks/{id}/deliveries?limit=5" \
  -H "X-API-Key: $EIGHTSCAN_API_KEY" | jq '.data[] | {status, responseCode, attempt, createdAt}'
```