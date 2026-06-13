# Neynar Deploy - Deployment Guide

## Quick Deploy Flow

1. Create a `.tar.gz` archive of the project directory
2. POST it to `https://api.host.neynar.app/v1/deploy`
3. On first deploy, an API key is returned — save it to `.agentdeploy` or credentials
4. Response includes the live URL

## Step 1: Archive
```bash
tar czf /tmp/site.tar.gz -C /path/to/project .
```

## Step 2: Deploy (first time — no auth needed)
```bash
curl -X POST https://api.host.neynar.app/v1/deploy \
  -F "files=@/tmp/site.tar.gz" \
  -F "projectName=my-site" \
  -F "framework=static"
```

Framework options: `nextjs`, `vite`, `static`, `auto` (default)

## Step 3: Save API Key
First deploy response includes `apiKey` — returned exactly once. Save immediately.

```json
{
  "success": true,
  "projectId": "uuid",
  "apiKey": "uuid",
  "deploymentId": "uuid",
  "url": "https://my-site.host.neynar.app"
}
```

## Step 4: Subsequent Deploys
```bash
curl -X POST https://api.host.neynar.app/v1/deploy \
  -F "files=@/tmp/site.tar.gz" \
  -F "projectName=my-site" \
  -H "Authorization: Bearer <api-key>"
```
