# Base Network Testing Guide

## Testnet Configuration

| Property | Value |
|----------|-------|
| Network | Base Sepolia |
| Chain ID | 84532 |
| RPC | https://sepolia.base.org |
| Faucet | https://www.alchemy.com/faucets/base-sepolia |

## Testing Best Practices

1. **Always test on testnet first**
2. **Use deterministic deployments**
3. **Mock external dependencies**
4. **Test edge cases and failures**
5. **Verify gas costs**

## Common Test Patterns

### Unit Tests
```solidity
function testTransfer() public {
    // Arrange
    uint256 amount = 1 ether;
    
    // Act
    token.transfer(recipient, amount);
    
    // Assert
    assertEq(token.balanceOf(recipient), amount);
}
```

### Integration Tests
```javascript
describe("Token", function() {
  it("Should transfer tokens", async function() {
    const [owner, addr1] = await ethers.getSigners();
    const Token = await ethers.getContractFactory("Token");
    const token = await Token.deploy();
    
    await token.transfer(addr1.address, 100);
    expect(await token.balanceOf(addr1.address)).to.equal(100);
  });
});
```

## Gas Optimization Tips

- Use `calldata` instead of `memory` for read-only parameters
- Cache storage variables in memory
- Use events for non-critical data
- Batch operations when possible
