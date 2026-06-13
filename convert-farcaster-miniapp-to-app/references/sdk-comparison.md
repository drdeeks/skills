# Farcaster SDK Comparison

## Packages Overview

| Package | Purpose |
|---------|---------|
| @farcaster/frame | Frame development |
| @farcaster/auth-client | Authentication |
| @farcaster/hub-client | Hub interaction |
| @farcaster/mini-app | Legacy mini app (deprecated) |

## Migration Paths

| From | To | Complexity |
|------|----|------------|
| mini-app SDK | frame + auth-client | Medium |
| Raw HTTP | hub-client | Low |
| Custom auth | auth-client | Low |

## Breaking Changes

- Frame message format updated
- Authentication flow changed
- State management API differs
- Event handling restructured
