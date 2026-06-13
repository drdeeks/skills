# MiniKit to Farcaster API Mapping

## Function Mapping

| MiniKit Function | Farcaster Equivalent |
|------------------|---------------------|
| `minikit.auth()` | `farcasterAuth.signIn()` |
| `minikit.send()` | `farcasterHub.submitMessage()` |
| `minikit.getUser()` | `farcasterAuth.getUser()` |
| `minikit.frame()` | `frame.send()` |

## Event Mapping

| MiniKit Event | Farcaster Event |
|---------------|-----------------|
| `minikit:ready` | `frame:ready` |
| `minikit:auth` | `auth:success` |
| `minikit:action` | `frame:action` |

## Configuration Changes

```javascript
// Before (MiniKit)
const config = { appId: 'xxx', scopes: ['read'] };

// After (Farcaster)
const config = { 
  clientId: 'xxx',
  scopes: ['farcaster']
};
```
