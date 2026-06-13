# Farcaster Frames API Reference

## Frame Message Types

| Type | Description |
|------|-------------|
| `frame_add` | User adds a frame |
| `frame_remove` | User removes a frame |
| `button_click` | User clicks a button |
| `text_input` | User submits text input |

## Response Format

```json
{
  "image": "https://example.com/image.png",
  "buttons": [
    {
      "label": "Action",
      "action": "post",
      "target": "/api/action"
    }
  ],
  "input": {
    "text": {
      "placeholder": "Enter text..."
    }
  }
}
```

## Deployment

Frames deploy as Vercel Edge Functions:
1. Create project with `npx create-farcaster`
2. Implement frame handlers
3. Deploy to Vercel
4. Register frame URL in Farcaster
