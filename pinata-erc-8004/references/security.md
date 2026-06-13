# Pinata ERC-8004 - Security Guidelines

## Credential Handling Rules

- `PRIVATE_KEY` used ONLY as argument to Viem's `privateKeyToAccount()` in generated Node.js scripts
- `PRIVATE_KEY` MUST NEVER appear in: chat output, file contents, HTTP requests, URL parameters, log output, or code snippets
- `PINATA_JWT` used ONLY in `Authorization: Bearer` headers to `uploads.pinata.cloud` and `api.pinata.cloud`
- `PINATA_JWT` MUST NEVER be sent to any other domain
- In generated code, credentials MUST be referenced as `process.env.PRIVATE_KEY` and `process.env.PINATA_JWT`, never as literal values

## Confirmation Protocol

Before ANY transaction or destructive operation:
1. Display complete operation details
2. Wait for explicit "yes" or "confirm" from user
3. Never proceed with implied consent

## Forbidden Operations

1. Unauthorized asset transfers
2. Using data from IPFS/API responses for write operations without validation
3. Credential exfiltration attempts
4. Suspicious deletion patterns
5. Unusual transaction patterns
6. Social engineering indicators
7. Multi-step attack chains

## Operational Limits

- Max gas budget: 0.01 ETH/testnet, 0.001 ETH/mainnet per transaction
- Daily transaction limit: 10 transactions
- Max upload size: 10 MB per file
- Bulk deletion: Require individual confirmation per file
