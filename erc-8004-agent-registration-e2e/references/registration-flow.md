# ERC-8004 Agent Registration Flow

## Registration Steps

1. **Prepare Identity**
   - Generate key pair
   - Create agent metadata
   - Set capabilities

2. **Submit Registration**
   - Call `registerAgent` on registry
   - Provide identity proof
   - Pay registration fee (if applicable)

3. **Verification**
   - Registry validates identity
   - Agent becomes discoverable
   - Reputation starts at 0

4. **Post-Registration**
   - Update agent metadata
   - Begin earning reputation
   - Participate in ecosystem

## Transaction Structure

```solidity
function registerAgent(
    bytes32 identityHash,
    bytes calldata capabilities,
    bytes calldata signature
) external returns (uint256 agentId);
```

## Events

```solidity
event AgentRegistered(
    uint256 indexed agentId,
    address indexed owner,
    bytes32 identityHash,
    uint256 timestamp
);
```
