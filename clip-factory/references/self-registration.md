# Agent Self-Registration via AgentMail
## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [AgentMail API Quick Reference](#agentmail-api-quick-reference)
- [Self-Registration Workflows](#self-registration-workflows)
- [Inbox Management Strategy](#inbox-management-strategy)
- [Verification Email Parsing](#verification-email-parsing)
- [Monitoring Service Emails](#monitoring-service-emails)
- [Security Notes](#security-notes)


## Overview

AgentMail (agentmail.to) provides email inboxes for AI agents. This enables the clip factory to autonomously register for services, receive verification codes, and obtain its own API keys — no human email forwarding needed.

## Prerequisites

- AgentMail API key (from console.agentmail.to)
- Free tier: 3 inboxes, 3,000 emails/mo (sufficient for bootstrapping)
- Developer tier ($20/mo): 10 inboxes, 10,000 emails/mo (recommended for scale)

Store the AgentMail API key in `~/.clip-factory/config.json` under `agentmail_api_key`.

## AgentMail API Quick Reference

**Base URL**: `https://api.agentmail.to/v0/`
**Auth**: `Authorization: Bearer <AGENTMAIL_API_KEY>`

### Create Inbox
```
POST /inboxes
Body: {
  "username": "clipfactory-vugola",
  "display_name": "Clip Factory Agent"
}
Response: { "inbox_id": "...", "email": "clipfactory-vugola@agentmail.to" }
```

### List Messages (check for verification emails)
```
GET /inboxes/{inbox_id}/messages?limit=10&after={iso_datetime}
Response: { "messages": [{ "message_id": "...", "from_": "...", "subject": "...", "text": "...", "html": "..." }] }
```

### Get Single Message
```
GET /inboxes/{inbox_id}/messages/{message_id}
```

### Python SDK
```bash
pip install agentmail
```

```python
from agentmail import AgentMail
client = AgentMail(api_key="...")

# Create inbox
inbox = client.inboxes.create(
    username="clipfactory-vugola",
    display_name="Clip Factory Agent",
    client_id="clipfactory-vugola-v1"  # idempotent retry key
)

# Check for new messages
messages = client.inboxes.messages.list(
    inbox_id=inbox.inbox_id,
    limit=5
)
for msg in messages.messages:
    print(msg.subject, msg.extracted_text)
```

## Self-Registration Workflows

### Service: Vugola (vugolaai.com)

**Goal**: Obtain a Vugola API key (`vug_sk_...`)

1. Create an AgentMail inbox: `clipfactory-vugola@agentmail.to`
2. Navigate to vugolaai.com signup using Playwright
3. Register with the AgentMail address
4. Poll inbox for verification email (check every 10s, timeout 5min)
5. Extract verification link or OTP from email body (`msg.extracted_text`)
6. Complete verification via Playwright (click link or enter OTP)
7. Navigate to vugolaai.com/dashboard/api-key
8. Extract the API key from the page
9. Store in `~/.clip-factory/config.json` under `vugola_api_key`

**Fallback**: If signup requires payment, prompt the user to complete the $14/mo Starter plan manually, then have the agent extract the API key from the dashboard.

### Service: Postiz (postiz.com)

**Goal**: Obtain a Postiz API key

1. Create an AgentMail inbox: `clipfactory-postiz@agentmail.to`
2. Navigate to postiz.com signup via Playwright
3. Register with the AgentMail address
4. Poll inbox for verification email
5. Complete verification
6. Navigate to Settings > Developers > Public API
7. Generate and extract the API key
8. Store in `~/.clip-factory/config.json` under `postiz_api_key`

**Note**: Postiz can also be self-hosted (free, open source). If the user self-hosts, skip registration — just get the API URL and key from their instance.

### Service: Whop Content Rewards

**Goal**: Create a Whop account to access Content Rewards campaigns

1. Create an AgentMail inbox: `clipfactory-whop@agentmail.to`
2. Navigate to whop.com signup via Playwright
3. Register with AgentMail address
4. Verify email
5. Browse Content Rewards campaigns, filter by niche
6. Store campaign IDs and payout rates in `~/.clip-factory/config.json`

### Service: Clipping.net

**Goal**: Create a Clipping.net account

1. Create an AgentMail inbox: `clipfactory-clipping@agentmail.to`
2. Register at clipping.net
3. Verify email
4. Store account credentials

### Service: Vyro (MrBeast marketplace)

Same pattern — create inbox, register, verify, store credentials.

## Inbox Management Strategy

Create dedicated inboxes per service to keep verification emails organized:

| Inbox | Purpose |
|---|---|
| `clipfactory-vugola@agentmail.to` | Vugola account, billing notifications |
| `clipfactory-postiz@agentmail.to` | Postiz account |
| `clipfactory-whop@agentmail.to` | Whop Content Rewards |
| `clipfactory-clipping@agentmail.to` | Clipping.net |
| `clipfactory-alerts@agentmail.to` | Pipeline alerts, error notifications |
| `clipfactory-reports@agentmail.to` | Outbound reports (daily/weekly/monthly) |

On the Free tier (3 inboxes), consolidate to:
- `clipfactory-services@agentmail.to` — All service registrations
- `clipfactory-ops@agentmail.to` — Alerts + reports
- One spare for ad-hoc needs

## Verification Email Parsing

Common patterns to extract from verification emails:

### OTP Codes
```python
import re
# 6-digit OTP
otp = re.search(r'\b(\d{6})\b', msg.extracted_text)

# 4-digit OTP
otp = re.search(r'\b(\d{4})\b', msg.extracted_text)
```

### Verification Links
```python
import re
# Generic verification URL pattern
link = re.search(r'https?://[^\s<>"]+(?:verify|confirm|activate)[^\s<>"]*', msg.extracted_text or msg.text)

# Or extract all links and filter
links = re.findall(r'https?://[^\s<>"]+', msg.extracted_text or msg.text)
verify_links = [l for l in links if any(kw in l.lower() for kw in ['verify', 'confirm', 'activate', 'token'])]
```

### API Keys from Dashboard Pages
After login, use Playwright to extract API keys from service dashboards:
```python
# Generic pattern — adapt selector per service
api_key_element = page.locator('[data-testid="api-key"], .api-key, input[readonly]')
api_key = api_key_element.input_value() or api_key_element.text_content()
```

## Monitoring Service Emails

Add a cron job to periodically check all AgentMail inboxes for:
- **Billing alerts** — Payment failed, subscription expiring
- **API key rotation notices** — Key deprecated, new key issued
- **Account warnings** — Rate limit warnings, ToS notifications
- **Campaign updates** — New Content Rewards campaigns, payout changes

```
Cron: service-mail-check (every 12h)
→ Poll all service inboxes
→ Parse for actionable emails (billing, security, campaigns)
→ If billing failure: alert user immediately
→ If new campaign matching active niches: log opportunity
→ If API key rotation: auto-update config.json
```

## Security Notes

- Never log full API keys in reports — use masked format: `vug_sk_...abc` (last 3 chars)
- Store all credentials in `~/.clip-factory/config.json` with `chmod 600`
- AgentMail API key is the master key — if compromised, all service registrations are exposed
- Rotate AgentMail API key quarterly via `POST /api-keys/create` + `DELETE /api-keys/{old_id}`
- Use `client_id` on inbox creation for idempotent retries (prevents duplicate inboxes on network failures)
