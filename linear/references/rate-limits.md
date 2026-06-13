# Linear API Rate Limits

## Limits
- **Requests**: 5,000/hour per API key
- **Complexity**: 3,000,000 points/hour
- **Page size**: Default 50, max 250

## Headers
```
X-RateLimit-Requests-Limit: 5000
X-RateLimit-Requests-Remaining: 4999
X-RateLimit-Requests-Reset: 1699999999
X-RateLimit-Complexity-Limit: 3000000
X-RateLimit-Complexity-Remaining: 2999999
```

## Best Practices
1. Always use `first: N` to limit results
2. Monitor `X-RateLimit-Requests-Remaining`
3. Use cursor pagination for large datasets
4. Cache team/workflow state queries
5. Batch related queries when possible

## Complexity Costs
- Simple queries (viewer, teams): ~100 points
- Issues list (20): ~500 points
- Issue search: ~1000 points
- Mutations: ~200 points

## Handling 429
```bash
# Check rate limit headers
curl -I -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { id } }"}'

# Wait for reset if limited
reset_time=$(curl -s -I ... | grep -i "x-ratelimit-requests-reset" | cut -d' ' -f2)
sleep $((reset_time - $(date +%s) + 5))
```

## Elevated Limits
- Contact Linear support for higher limits
- Enterprise plans have increased quotas
