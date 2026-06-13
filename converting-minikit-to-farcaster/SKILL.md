---
name: converting-minikit-to-farcaster
description: Converts Mini Apps from MiniKit (OnchainKit) to native Farcaster SDK. Use when migrating from @coinbase/onchainkit/minikit, converting MiniKit hooks, removing MiniKitProvider, or when user mentions MiniKit, OnchainKit, or Farcaster SDK migration.
version: 0.0.5
---

# MiniKit to Farcaster SDK

## Breaking Changes (SDK v0.2.0+)

1. `sdk.context` is a **Promise** — must await
2. `sdk.isInMiniApp()` accepts **no parameters**
3. `sdk.actions.setPrimaryButton()` has no onClick callback

Check version: `npm list @farcaster/miniapp-sdk`

## Quick Reference

| MiniKit | Farcaster SDK | Notes |
|---------|---------------|-------|
| `useMiniKit().setFrameReady()` | `await sdk.actions.ready()` | |
| `useMiniKit().context` | `await sdk.context` | **Async** |
| `useMiniKit().isSDKLoaded` | `await sdk.isInMiniApp()` | No params |
| `useClose()` | `await sdk.actions.close()` | |
| `useOpenUrl(url)` | `await sdk.actions.openUrl(url)` | |
| `useViewProfile(fid)` | `await sdk.actions.viewProfile({ fid })` | |
| `useViewCast(hash)` | `await sdk.actions.viewCast({ hash })` | |
| `useComposeCast()` | `await sdk.actions.composeCast({ text, embeds })` | |
| `useAddFrame()` | `await sdk.actions.addMiniApp()` | |
| `usePrimaryButton(opts, cb)` | `await sdk.actions.setPrimaryButton(opts)` | No callback |
| `useAuthenticate()` | `sdk.quickAuth.getToken()` | See [AUTH.md](AUTH.md) |

## Context Access Pattern

```typescript
// WRONG
const fid = sdk.context?.user?.fid;

// CORRECT
const context = await sdk.context;
const fid = context?.user?.fid;
```

In React components, use state:

```typescript
const [context, setContext] = useState(null);

useEffect(() => {
  const load = async () => {
    const ctx = await sdk.context;
    setContext(ctx);
  };
  load();
}, []);
```

## Conversion Workflow

1. Verify Node.js >= 22.11.0
2. Update dependencies — see [DEPENDENCIES.md](DEPENDENCIES.md)
3. Replace imports: `@coinbase/onchainkit/minikit` → `@farcaster/miniapp-sdk`
4. Convert hooks using reference above
5. Add FrameProvider — see [PROVIDER.md](PROVIDER.md)
6. Update manifest: `frame` → `miniapp` — see [MANIFEST.md](MANIFEST.md)

## Common Errors

**"Property 'user' does not exist on type 'Promise<MiniAppContext>'"**
→ Await `sdk.context` before accessing properties

**"Expected 0 arguments, but got 1"**
→ Remove parameters from `sdk.isInMiniApp()`

**Context is null in components**
→ Ensure FrameProvider is in your provider chain


## Workflow

### Step 1: Installation

```bash
# Install dependencies if needed
```

### Step 2: Configuration

```bash
# Configure the skill
```

### Step 3: Usage

```bash
# Use the skill
python3 scripts/main.py
```

### Step 4: Validation

```bash
# Validate the skill
python3 scripts/validate.py
```


## Provider Compatibility

| Provider | Compatibility | Notes |
|----------|---------------|-------|
| Claude (Anthropic) | Full | MCP servers, tool use |
| OpenAI / ChatGPT | Full | Function calling, Actions |
| Mistral / Le Chat | Full | Tool calling, script execution |
| Gemini (Google) | Full | Extensions, Vertex AI |
| Hermes (Nous) | Full | Tool-use fine-tuned |
| GitHub Copilot | Partial | Code generation; use external runner for scripts |
| Any LLM + tools | Full | Scripts are plain Python, provider-independent |


## Free-First Strategy

| Tier | Cost | Stack |
|------|------|-------|
| **Tier 0** | $0/mo | Python 3.8+ (all scripts use stdlib only) |
| **Tier 1** | $0-5/mo | + CI/CD for automated validation |
| **Tier 2** | $5-20/mo | + Hosted skill registry for team distribution |

The entire core toolchain is permanently $0.


## Enforced Output Statistics

Every script produces structured output on completion:

```json
{
  "operation": "script_name",
  "timestamp": "ISO8601",
  "status": "success | failed",
  "skill_name": "the-skill-name",
  "details": {},
  "cost": {"tier": 0, "amount_usd": 0.0, "service": "local"}
}
```


## Error Handling

| Error | Response |
|-------|----------|
| Invalid input | Validate and report with guidance |
| Missing dependency | Auto-install or report requirement |
| Network failure | Retry with exponential backoff |
| Permission denied | Report and suggest alternatives |
| Resource not found | Report with available options |


## Enhancement Hooks

| Skill | Enhancement | When to Add |
|-------|-------------|-------------|
| `skill-creator` | Basic skill creation | When creating simple skills |
| `skill-creator-pro` | Enterprise upgrade | When upgrading to enterprise |
| `html-report` | Visual validation dashboard | When auditing many skills |
| `xlsx` | Export validation results | When tracking skill quality metrics |


## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/validate.py` | converting-minikit-to-farcaster script | Run with python3 |
| `scripts/main.py` | converting-minikit-to-farcaster script | Run with python3 |

## Key References

- **Overview**: [references/overview.md](references/overview.md)
## References

- [MAPPING.md](MAPPING.md) — Complete hook-by-hook conversion reference
- [EXAMPLES.md](EXAMPLES.md) — Before/after code examples
- [PROVIDER.md](PROVIDER.md) — Provider setup with FrameProvider
- [PITFALLS.md](PITFALLS.md) — Common errors and solutions
- [DEPENDENCIES.md](DEPENDENCIES.md) — Package updates
- [AUTH.md](AUTH.md) — Quick Auth migration
- [MANIFEST.md](MANIFEST.md) — farcaster.json changes
