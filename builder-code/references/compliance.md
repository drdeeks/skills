# Builder Code Compliance

Compliance rules and audit logging for builder codes.

## Mandatory Checks

1. Builder code in every transaction
2. Builder code in every agent
3. Builder code in every sub-agent
4. Verification before execution
5. Audit logging enabled

## Audit Log Format

```json
{
  "timestamp": "ISO8601",
  "agent": "agent-name",
  "action": "action-type",
  "builderCode": "bc_26ulyc23",
  "verified": true
}
```

## Verification Function

```javascript
function verifyBuilderCode(calldata) {
  const suffix = calldata.slice(-20);
  return suffix === BUILDER_CODE_HEX.slice(2);
}
```
