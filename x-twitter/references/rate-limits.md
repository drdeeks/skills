# Twitter API Rate Limits

## Standard Limits (15-minute windows)

### Read Operations
- Tweet lookup (by ID): 900 requests
- Recent search: 450 requests
- Full archive search: 300 requests (elevated)
- User lookup: 900 requests
- User tweets: 900 requests
- User followers/following: 15 requests
- Lists: 300 requests

### Write Operations
- Create tweet: 300 requests
- Like/Unlike: 50 requests
- Retweet/Unretweet: 50 requests
- Follow/Unfollow: 50 requests
- Bookmark: 50 requests
- List management: 300 requests

## Handling Rate Limits

### Headers
```
x-rate-limit-limit: 450
x-rate-limit-remaining: 449
x-rate-limit-reset: 1699999999
```

### Best Practices
1. Check `x-rate-limit-remaining` before requests
2. Sleep until `x-rate-limit-reset` if 0 remaining
3. Use exponential backoff on 429
4. Cache responses when possible
5. Batch operations (multi-tweet lookup)

### Retry Logic
```python
import time
import requests

def request_with_retry(url, headers, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            reset = int(response.headers.get('x-rate-limit-reset', 0))
            wait = max(reset - time.time(), 60)
            time.sleep(wait)
        else:
            response.raise_for_status()
    raise Exception("Max retries exceeded")
```

## Elevated Access
- Apply at developer.twitter.com
- Full archive search
- Higher rate limits
- Requires review
