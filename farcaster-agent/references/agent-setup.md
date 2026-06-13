# Farcaster Agent Setup Guide

## Prerequisites

- Farcaster account
- Farcaster Hub access (or use Neynar)
- Node.js 18+

## Setup Steps

1. **Install dependencies**
```bash
npm init -y
npm install @farcaster/hub-client
```

2. **Configure agent**
```javascript
const { HubClient } = require('@farcaster/hub-client');

const hub = new HubClient({
  url: 'https://hub.farcaster.xyz:321',
});
```

3. **Implement message handling**
```javascript
async function handleMessage(message) {
  // Process incoming message
  const reply = await generateResponse(message);
  await hub.submitMessage(reply);
}
```

4. **Deploy**
- Use Vercel, Railway, or self-host
- Set up webhook for real-time messages
- Monitor logs for errors

## Best Practices

- Respect rate limits
- Validate message signatures
- Store state persistently
- Handle errors gracefully
