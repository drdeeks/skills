# Builder Code Testing

Test cases for builder code integration.

## Test 1: Builder Code in Transaction

```javascript
const tx = {
  to: "0x123...",
  data: "0xabc123" + BUILDER_CODE_HEX.slice(2)
};
assert(verifyBuilderCode(tx.data)); // Pass
```

## Test 2: Agent Inheritance

```javascript
const agent = createSubAgent("TestAgent");
assert(agent.builderCode === BUILDER_CODE); // Pass
```

## Test 3: Configuration Loading

```javascript
const config = getBuilderCodeConfig();
assert(config.builderCode === "bc_26ulyc23"); // Pass
assert(config.hardwired === true); // Pass
```
