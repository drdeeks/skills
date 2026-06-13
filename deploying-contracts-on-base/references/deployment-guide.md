# Contract Deployment Guide for Base

## Prerequisites

1. Ethereum wallet with ETH
2. Development framework (Foundry or Hardhat)
3. Base network configured

## Deployment Steps

### Foundry

```bash
# Install Foundry
curl -L https://foundry.paradigm.xyz | bash

# Initialize project
forge init my-project
cd my-project

# Deploy to Base
forge script script/Deploy.s.sol \
  --rpc-url https://mainnet.base.org \
  --private-key $PRIVATE_KEY \
  --broadcast
```

### Hardhat

```bash
# Install Hardhat
npm init -y
npm install hardhat @nomicfoundation/hardhat-toolbox

# Deploy
npx hardhat run scripts/deploy.js --network base
```

## Verification

Verify contract on BaseScan:
```bash
# Foundry
forge verify-contract <address> <contract> \
  --chain-id 8453 \
  --etherscan-api-key $ETHERSCAN_KEY

# Hardhat
npx hardhat verify --network base <address> <constructor-args>
```

## Gas Optimization

- Use Solidity 0.8.x with optimizer enabled
- Batch operations when possible
- Use events instead of storage for non-critical data
