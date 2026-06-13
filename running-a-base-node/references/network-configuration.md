# Network Configuration for Base Node

## Required Ports
- **Port 9222**: Discovery v5 (UDP/TCP) - Critical for peer discovery
- **Port 30303**: P2P Discovery & RLPx (UDP/TCP) - Ethereum P2P protocol

## Firewall Rules
```bash
# Allow P2P ports
ufw allow 9222/tcp
ufw allow 9222/udp
ufw allow 30303/tcp
ufw allow 30303/udp

# Block RPC ports from public
ufw deny 8545
ufw deny 8546
```

## Reverse Proxy (Optional)
If exposing RPC endpoint:
- Use nginx or Caddy with TLS termination
- Restrict to authenticated clients only
- Rate limit requests
