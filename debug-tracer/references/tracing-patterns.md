# Debug Tracing Patterns

## Log Levels

| Level | Use Case |
|-------|----------|
| DEBUG | Detailed diagnostic information |
| INFO | General operational messages |
| WARN | Unexpected but recoverable issues |
| ERROR | Failures that need attention |

## Tracing Techniques

### 1. Entry/Exit Logging
```python
def process_data(data):
    logger.debug(f"Entering process_data with {len(data)} items")
    result = transform(data)
    logger.debug(f"Exiting process_data with {len(result)} items")
    return result
```

### 2. Performance Tracing
```python
import time
start = time.time()
result = expensive_operation()
elapsed = time.time() - start
logger.info(f"Operation took {elapsed:.3f}s")
```

### 3. State Snapshots
```python
logger.debug(f"State before: {state}")
# ... operation ...
logger.debug(f"State after: {state}")
```

## Tools

| Tool | Purpose |
|------|---------|
| Python logging | Built-in logging framework |
| structlog | Structured logging |
| Sentry | Error tracking |
| Datadog | APM and monitoring |
