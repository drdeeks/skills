# Farcaster Agent Best Practices

## Rate Limits

| Action | Limit |
|--------|-------|
| Messages per hour | 5000 |
| Casts per day | 2000 |
| Reactions per day | 5000 |

## Error Handling

| Error Code | Meaning | Action |
|------------|---------|--------|
| 429 | Rate limited | Exponential backoff |
| 401 | Auth failed | Refresh credentials |
| 404 | Not found | Check user exists |
| 500 | Server error | Retry with delay |

## Message Validation

1. Always verify message signatures
2. Check timestamp freshness
3. Validate FID ownership
4. Sanitize user input

## State Management

```javascript
// Use persistent storage
const state = {
  lastMessage: null,
  conversationHistory: [],
  userPreferences: {},
};

// Save state regularly
async function saveState() {
  await db.write('agent-state', JSON.stringify(state));
}
```

## Security

- Never expose private keys
- Validate all inputs
- Rate limit incoming requests
- Log suspicious activity
- Use HTTPS for all endpoints
