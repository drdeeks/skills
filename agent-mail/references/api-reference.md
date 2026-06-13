# AgentMail API Reference

Complete API reference for the AgentMail service.

## Core Endpoints

### Inboxes
- `POST /inboxes` - Create a new inbox
- `GET /inboxes` - List all inboxes
- `GET /inboxes/{id}` - Get inbox details
- `DELETE /inboxes/{id}` - Delete an inbox

### Messages
- `GET /inboxes/{id}/messages` - List messages in inbox
- `GET /inboxes/{id}/messages/{msg_id}` - Get full message content
- `DELETE /inboxes/{id}/messages/{msg_id}` - Delete a message

## Authentication

All API calls require the `Authorization: Bearer <api_key>` header.

## Rate Limits

- Free tier: 100 requests/hour
- Pro tier: 1000 requests/hour
- Enterprise: Custom limits
