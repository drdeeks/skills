# Neynar Deploy API Reference

## Base URL
`https://api.host.neynar.app`

## Authentication
`Authorization: Bearer <api-key>`

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/deploy` | POST | Deploy files (creates project + key if no auth) |
| `/v1/projects` | GET | List all projects |
| `/v1/projects/:id` | GET | Project details + deploy history + 7d analytics |
| `/v1/projects/:id` | DELETE | Delete project |
| `/v1/projects/:id/deploy` | POST | Deploy new version to existing project |
| `/v1/projects/:id/deploy/:deploymentId` | GET | Check deploy status |
| `/v1/projects/:id/rollback` | POST | Roll back: `{ "version": <number> }` |
| `/v1/projects/:id/analytics?period=7d` | GET | Analytics (1d/7d/30d) |
| `/v1/projects/:id/files` | GET | Download URL for latest source |
| `/v1/billing/tier` | GET | Current tier and limits |

## Deploy Status Values
`pending` → `building` → `ready` (success) or `error` (failure)

## Free Tier Limits
- 3 active projects
- 10 deploys/hour
- 50MB max upload
