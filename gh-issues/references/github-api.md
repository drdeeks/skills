# GitHub API Reference

## Authentication

### Token Authentication
```bash
curl -H "Authorization: Bearer $GH_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/user
```

### Token Scopes
- `repo` - Full repository access
- `public_repo` - Public repositories only
- `admin:repo_hook` - Webhook management

## Issues API

### List Issues
```bash
GET /repos/{owner}/{repo}/issues
```

**Parameters:**
- `state` - open, closed, all (default: open)
- `labels` - Comma-separated label names
- `milestone` - Milestone number
- `assignee` - User login
- `per_page` - Results per page (max 100)
- `page` - Page number

### Create Issue
```bash
POST /repos/{owner}/{repo}/issues
```

**Body:**
```json
{
  "title": "Issue title",
  "body": "Issue description",
  "labels": ["bug", "enhancement"],
  "assignees": ["username"]
}
```

### Update Issue
```bash
PATCH /repos/{owner}/{repo}/issues/{issue_number}
```

## Pull Requests API

### List Pull Requests
```bash
GET /repos/{owner}/{repo}/pulls
```

**Parameters:**
- `state` - open, closed, all
- `head` - Filter by head branch
- `base` - Filter by base branch
- `sort` - created, updated, popularity, long-running

### Create Pull Request
```bash
POST /repos/{owner}/{repo}/pulls
```

**Body:**
```json
{
  "title": "PR title",
  "head": "feature-branch",
  "base": "main",
  "body": "PR description"
}
```

### Get PR Reviews
```bash
GET /repos/{owner}/{repo}/pulls/{pull_number}/reviews
```

### Create PR Review
```bash
POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews
```

## Rate Limits

### Core API
- **Authenticated:** 5000 requests/hour
- **Unauthenticated:** 60 requests/hour

### Search API
- **Authenticated:** 30 requests/minute
- **Unauthenticated:** 10 requests/minute

### Check Rate Limit
```bash
GET /rate_limit
```

## Error Handling

### Common Status Codes
- `200` - Success
- `201` - Created
- `304` - Not Modified
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Unprocessable Entity
- `403` - Rate Limit Exceeded

### Error Response Format
```json
{
  "message": "Validation Failed",
  "errors": [
    {
      "resource": "Issue",
      "field": "title",
      "code": "missing_field"
    }
  ]
}
```

## Best Practices

1. **Use conditional requests** - Include `If-None-Match` headers
2. **Respect rate limits** - Monitor `X-RateLimit-*` headers
3. **Handle pagination** - Use `Link` header for multiple pages
4. **Use webhooks** - For real-time updates instead of polling