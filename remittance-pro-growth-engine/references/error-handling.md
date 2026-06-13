# Error Handling & Recovery

Error catalog and recovery procedures for the growth engine. Load when troubleshooting campaign failures or building resilience.

## Table of Contents

1. [Error Categories](#error-categories)
2. [Recovery Procedures](#recovery-procedures)
3. [Escalation Rules](#escalation-rules)

---

## Error Categories

| Category | Examples | Response | Max retries |
|----------|----------|----------|-------------|
| **Platform ban** | Account suspended, shadow-banned, group removal | Switch to backup account, reduce posting frequency, appeal | 1 appeal |
| **Rate limiting** | Too many DMs, post frequency limits, API 429s | Respect cooldown, queue for next window, rotate accounts | 3 |
| **Content rejection** | Ad disapproved, post removed by admin, spam filter | Revise content, remove flagged terms, resubmit | 2 |
| **Lead invalid** | Email bounced, fake profile, dead community | Mark as rejected in pipeline, move on | 0 |
| **API failure** | Firecrawl down, email API timeout, gift card API error | Retry with backoff, fallback to manual process | 3 |
| **Outreach failure** | Message not delivered, blocked by recipient | Log and skip, try alternative channel | 1 |
| **Data corruption** | Malformed JSONL, missing fields, duplicate records | Validate + repair, deduplicate, rebuild from source | Auto |
| **Budget exceeded** | Ad spend over limit, unexpected charges | Pause campaigns, review spend, adjust daily limits | 0 |
| **Compliance** | Regulatory warning, cease-and-desist, GDPR request | Immediate pause, legal review, comply within 72h | 0 |

---

## Recovery Procedures

### Platform ban recovery

1. Immediately stop all activity on banned account
2. Do NOT create new account on same device/IP — platform fingerprinting detects this
3. Wait 24-48 hours before any action
4. If appeal possible, submit within 24h with professional, compliant explanation
5. Switch outreach to alternative channels while appeal pending
6. If permanent ban, use alternative account from different device/IP after 1 week cooldown
7. Reduce future posting frequency by 50% to avoid repeat

### Rate limit recovery

1. Stop all API calls / posting immediately
2. Check Retry-After header or platform-specific cooldown docs
3. Queue pending items in `pipeline/outreach_pending.jsonl` with `retry_after` timestamp
4. Resume at 50% of previous rate after cooldown expires
5. Gradually increase rate over 3 days if no further limits

### Data corruption recovery

1. Identify corrupted file via error logs
2. Backup corrupted file: `cp file.jsonl file.jsonl.corrupt.TIMESTAMP`
3. Filter valid JSON lines: `python3 -c "import json; [print(l.strip()) for l in open('file.jsonl') if json.loads(l.strip())]" > file_clean.jsonl`
4. Deduplicate by key field (name, lead, run_id)
5. Replace original with cleaned file
6. Log recovery in `analytics/error_log.jsonl`

---

## Escalation Rules

| Severity | Condition | Action | Response time |
|----------|-----------|--------|---------------|
| **Critical** | All outreach channels blocked, legal notice, data breach | Pause all campaigns, notify human operator | Immediate |
| **High** | Primary corridor campaign failing, B2B partner issue, budget overrun | Investigate root cause, implement fix, notify human | <4 hours |
| **Medium** | Single channel rate-limited, ad disapproved, moderate data issue | Auto-recover, log, include in daily digest | <24 hours |
| **Low** | Minor data inconsistency, single lead invalid, cosmetic content issue | Auto-fix, log for weekly review | Next reporting cycle |

### Error logging format

```json
{
  "timestamp": "ISO8601",
  "error_type": "platform_ban | rate_limit | content_rejection | lead_invalid | api_failure | outreach_failure | data_corruption | budget_exceeded | compliance",
  "severity": "critical | high | medium | low",
  "operation": "operation_name",
  "campaign": "campaign_name",
  "message": "Human-readable description",
  "recoverable": true,
  "retry_count": 0,
  "resolution": "retried | queued | fallback | escalated | failed_permanent",
  "details": {}
}
```
