# ERC-8004 Testing Guide

## Test Environment Setup

1. **Local Development**
   - Use Hardhat or Foundry
   - Fork mainnet for realistic testing
   - Deploy mock contracts

2. **Testnet Deployment**
   - Deploy to Base Sepolia
   - Use testnet faucets for ETH
   - Verify on Blockscout

## Test Cases

### Registration Tests

```solidity
function testRegisterAgent() public {
    bytes32 identity = keccak256("agent1");
    bytes memory caps = abi.encode(["chat", "code"]);
    
    vm.prank(agentOwner);
    uint256 id = registry.registerAgent(identity, caps, signature);
    
    assertTrue(id > 0);
    assertEq(registry.ownerOf(id), agentOwner);
}
```

### Reputation Tests

```solidity
function testReputationUpdate() public {
    registry.updateReputation(agentId, 100);
    assertEq(registry.reputationOf(agentId), 100);
}
```

## Test Coverage

| Area | Coverage Target |
|------|-----------------|
| Registration | 100% |
| Reputation | 95% |
| Transfer | 100% |
| Events | 100% |

## Continuous Integration

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: forge test --coverage
```
