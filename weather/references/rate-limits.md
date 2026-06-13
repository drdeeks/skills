# Rate Limits

## wttr.in
- **Limit**: ~1000 requests/day per IP
- **Burst**: ~60 requests/minute
- **Response**: 429 Too Many Requests
- **Best Practice**: Cache responses, use 5+ min intervals

## Open-Meteo
- **Limit**: 10,000 requests/day (free tier)
- **Burst**: 60 requests/minute
- **Response**: 429 with Retry-After header
- **Best Practice**: Respect Retry-After, cache 10+ min

## Handling Rate Limits
```bash
# Check headers
curl -I "wttr.in/London"

# Exponential backoff
for i in {1..5}; do
  response=$(curl -s -w "%{http_code}" "wttr.in/London?format=3")
  code=${response: -3}
  if [ "$code" = "200" ]; then
    echo "${response%???}"
    break
  elif [ "$code" = "429" ]; then
    sleep $((2**i))
  else
    echo "Error: $code"
    break
  fi
done
```

## Monitoring
- Log all requests with timestamps
- Track 429 responses
- Alert if > 10% requests return 429
