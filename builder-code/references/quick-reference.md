# Builder Code Reference

Quick reference for builder code integration.

## Builder Code: bc_26ulyc23

- Owner: Dr Deeks
- Hardwired into all agents
- Enforced on every transaction

## ERC-8021 Attribution

Append to transaction calldata:
```
0x62635f3236756c79633233
```

## Verification

Check last 16 bytes of calldata for builder code hex.

## Compliance

- Every transaction must include builder code
- Every agent must inherit builder code
- Verification required before execution
