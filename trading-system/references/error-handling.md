# Error Handling — Error Catalog & Recovery Procedures

Complete error catalog, recovery procedures, and logging standards for the autonomous trading system.

## Table of Contents

1. [Error Categories](#error-categories)
2. [Platform-Specific Errors](#platform-specific-errors)
3. [Recovery Procedures](#recovery-procedures)
4. [Error Logging Format](#error-logging-format)
5. [Retry Strategy](#retry-strategy)
6. [Escalation Matrix](#escalation-matrix)

---

## Error Categories

| Category | Code | Examples | Response | Max Retries |
|---|---|---|---|---|
| **Network** | `NET` | Timeout, DNS failure, connection refused | Exponential backoff | 3 |
| **Authentication** | `AUTH` | Expired key, invalid token, revoked access | Refresh + alert | 1 |
| **Rate Limiting** | `RATE` | 429 response, quota exceeded | Respect Retry-After | Wait |
| **Execution** | `EXEC` | Slippage, partial fill, insufficient funds | Recalculate/skip | 2 |
| **Data** | `DATA` | Stale prices, malformed response, missing fields | Skip + log | 0 |
| **Platform** | `PLAT` | Exchange down, maintenance, API change | Failover | 0 |
| **Internal** | `INT` | Config error, state corruption, disk full | Alert + halt | 0 |

## Platform-Specific Errors

### Polymarket

| Error | Cause | Response |
|---|---|---|
| Gamma API 500 | Server overload | Retry after 30s |
| CLOB signature invalid | Wrong key or nonce | Regenerate signature |
| Order rejected | Insufficient USDC balance | Block new trades, alert |
| Market closed | Event resolved | Remove from open positions |
| Price moved | Orderbook changed | Recalculate and resubmit |

### Kalshi

| Error | Cause | Response |
|---|---|---|
| 401 Unauthorized | Bad signature or expired key | Re-sign with fresh timestamp |
| 403 Forbidden | Account restricted | Alert, disable platform |
| Insufficient balance | Not enough funds | Block new trades, alert |
| Market not found | Ticker expired/delisted | Remove from watchlist |
| Order price out of range | Price < 1¢ or > 99¢ | Adjust to valid range |

### Hyperliquid

| Error | Cause | Response |
|---|---|---|
| Nonce too low | Transaction ordering issue | Increment nonce, retry |
| Insufficient margin | Not enough collateral | Reduce position size |
| Rate limited | Too many requests | Backoff 60s |
| Liquidation risk | Position underwater | Reduce or close position |

## Recovery Procedures

### Automatic Recovery

All recoverable errors follow this pipeline:

```
Error detected
  → Log error to errors.jsonl
  → Check retry count
  → If retries < max:
      → Wait (exponential backoff: 2^retry seconds)
      → Retry operation
      → If success: log recovery, continue
      → If fail: increment retry, repeat
  → If retries >= max:
      → Log as permanent failure
      → Alert via Telegram
      → Skip this opportunity
      → Continue to next cycle
```

### Manual Recovery

For non-recoverable errors:

1. **Check logs**: `~/.autonomous-trading-system/logs/errors.jsonl`
2. **Run diagnostics**: `python3 analytics.py health`
3. **Check safety state**: `python3 safety_net.py status`
4. **Validate connectivity**: `python3 bootstrap.py validate`
5. **If platform issue**: Disable platform in config, re-enable after fix
6. **If config issue**: `python3 bootstrap.py reset` and reconfigure

## Error Logging Format

Every error is logged as structured JSON to `logs/errors.jsonl`:

```json
{
    "timestamp": "2026-05-19T12:00:00Z",
    "error_type": "network",
    "error_code": "NET_TIMEOUT",
    "source": "scan_polymarket",
    "message": "Request to gamma-api.polymarket.com timed out after 15s",
    "recoverable": true,
    "retry_count": 1,
    "max_retries": 3,
    "resolution": "retried",
    "context": {
        "url": "https://gamma-api.polymarket.com/markets",
        "timeout_ms": 15000
    }
}
```

## Retry Strategy

### Exponential Backoff

```python
def retry_with_backoff(operation, max_retries=3, base_delay=2):
    for attempt in range(max_retries + 1):
        try:
            return operation()
        except RecoverableError as e:
            if attempt >= max_retries:
                raise PermanentError(f"Failed after {max_retries} retries: {e}")
            delay = base_delay ** attempt  # 1s, 2s, 4s
            time.sleep(delay)
```

### Rate Limit Handling

```python
def handle_rate_limit(response):
    retry_after = response.headers.get("Retry-After", 60)
    # Queue the operation for later
    queue_for_retry(operation, delay=int(retry_after))
```

## Escalation Matrix

| Severity | Trigger | Response | Alert |
|---|---|---|---|
| **Low** | Single timeout, stale data | Auto-retry | Console log only |
| **Medium** | Auth failure, rate limit | Retry + log | Telegram if repeated |
| **High** | Platform outage, insufficient funds | Disable + alert | Telegram immediately |
| **Critical** | Kill switch, state corruption | Full halt | Telegram + email |

### Telegram Alert Format

```
🚨 TRADING SYSTEM ALERT
━━━━━━━━━━━━━━━━━━━━━
Type: [ERROR_TYPE]
Source: [SOURCE]
Message: [MESSAGE]
Action: [RESPONSE]
Time: [TIMESTAMP]
━━━━━━━━━━━━━━━━━━━━━
Review: python3 analytics.py health
```
