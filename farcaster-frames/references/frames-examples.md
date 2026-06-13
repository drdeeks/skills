# Farcaster Frames Examples

## Simple Button Frame

```typescript
import { Button } from '@farcaster/frame';

export default function Frame() {
  return (
    <Frame>
      <Image src="/og.png" />
      <Button action="post" target="/api/click">
        Click Me
      </Button>
    </Frame>
  );
}
```

## Input Frame

```typescript
<Frame>
  <Image src="/og.png" />
  <Input text={{ placeholder: "Enter your message..." }} />
  <Button action="post" target="/api/submit">
    Submit
  </Button>
</Frame>
```

## State Management

```typescript
// Server-side state
const state = {
  count: 0,
  lastAction: null,
};

// Update on button click
app.post('/api/click', (req, res) => {
  state.count++;
  res.json({
    image: `/api/og?count=${state.count}`,
    buttons: [{ label: `Count: ${state.count}`, action: 'post' }],
  });
});
```
