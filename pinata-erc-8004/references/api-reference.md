# Pinata ERC-8004 - API Reference

## Pinata API Domains

### Authenticated (carry PINATA_JWT)
- `uploads.pinata.cloud` — File uploads only
- `api.pinata.cloud` — File management, groups, listing

### Unauthenticated (public reads)
- `{PINATA_GATEWAY_URL}` — User's configured Pinata gateway (from env var)

### Blockchain RPC
- `mainnet.base.org`
- `sepolia.base.org`
- Value of `RPC_URL` environment variable

## Pinata Operations

### Upload File
```
POST https://uploads.pinata.cloud/v3/files
Authorization: Bearer {PINATA_JWT}
Body: multipart/form-data (file, network, group_id)
```

### List Files
```
GET https://api.pinata.cloud/v3/files/{network}
Authorization: Bearer {PINATA_JWT}
Query: cid, mimeType, limit, pageToken
```

### Delete File
```
DELETE https://api.pinata.cloud/v3/files/{network}/{file_id}
Authorization: Bearer {PINATA_JWT}
```

### Retrieve from IPFS
```
GET https://{PINATA_GATEWAY_URL}/ipfs/{cid}
```

## ERC-8004 Contract Methods

### Read Operations (Free)
- `ownerOf(tokenId)` → address
- `tokenURI(tokenId)` → string URI
- `balanceOf(address)` → uint256 count

### Write Operations (Require Gas)
- `register()` → transaction hash (extract tokenId from logs)
- `setAgentURI(tokenId, uri)` → transaction hash
- `transferFrom(from, to, tokenId)` → transaction hash

## Official Registry Addresses

### Mainnet (All Chains)
`0x8004A169FB4a3325136EB29fA0ceB6D2e539a432`

### Testnet (All Chains)
`0x8004A818BFB912233c491871b3d84c89A494BD9e`
