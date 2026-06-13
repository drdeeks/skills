# Base Builder Code Registration - API Reference

## Base Builder Code API

### Register Agent
```
POST https://api.base.dev/v1/agents/builder-codes
Content-Type: application/json

{
  "wallet_address": "0x..."
}
```

### Response
```json
{
  "builder_code": "bc_a1b2c3d4",
  "wallet_address": "0x...",
  "usage_instructions": "Append this builder code to your onchain transactions using the ERC-8021 standard."
}
```

### API Response Fields
- `builderCode` (camelCase) - The builder code string
- `walletAddress` (camelCase) - The registered wallet address
- `usageInstructions` (camelCase) - Instructions for using the builder code

## ERC-8021 Attribution

### ox/erc8021 Usage
```typescript
import { Attribution } from "ox/erc8021"
import { BUILDER_CODE } from "./constants/builderCode"

const DATA_SUFFIX = Attribution.toDataSuffix({
  codes: [BUILDER_CODE],
})
```

### Viem Integration (Option A)
```typescript
import { createWalletClient, http } from "viem"
import { base } from "viem/chains"
import { privateKeyToAccount } from "viem/accounts"
import { Attribution } from "ox/erc8021"
import { BUILDER_CODE } from "./constants/builderCode"

const DATA_SUFFIX = Attribution.toDataSuffix({ codes: [BUILDER_CODE] })

const account = privateKeyToAccount(process.env.PRIVATE_KEY! as `0x${string}`)

export const walletClient = createWalletClient({
  account,
  chain: base,
  transport: http(),
  dataSuffix: DATA_SUFFIX,
})
```

### Ethers.js Integration (Option B)
```typescript
import { ethers } from "ethers"
import { Attribution } from "ox/erc8021"
import { BUILDER_CODE } from "./constants/builderCode"

const DATA_SUFFIX = Attribution.toDataSuffix({ codes: [BUILDER_CODE] })

const provider = new ethers.JsonRpcProvider("https://mainnet.base.org")
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY!, provider)

const tx = await wallet.sendTransaction({
  to: "0x...",
  value: ethers.parseEther("0.01"),
  data: DATA_SUFFIX,
})
```
