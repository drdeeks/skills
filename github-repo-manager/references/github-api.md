# GitHub API Reference

## Authentication

The GitHub Repository Manager uses token-based authentication for all API requests.

### Required Permissions

For full functionality, the GitHub token needs the following scopes:
- `repo` - Full control of private repositories
- `public_repo` - Access to public repositories (subset of `repo`)
- `delete_repo` - Delete repositories (if deletion features are added)

### Token Format

```
Authorization: token ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Rate Limits

### Limits by Authentication Type

| Authentication | Requests per Hour | Notes |
|----------------|-------------------|-------|
| Unauthenticated | 60 | Per IP address |
| Authenticated | 5,000 | Per token |

### Rate Limit Headers

All API responses include:
- `X-RateLimit-Limit`: Request limit for the endpoint
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Time at which rate limit resets (UTC epoch seconds)
- `Retry-After`: Seconds to wait before retrying (when limit exceeded)

### Handling Rate Limits

The manager implements exponential backoff:
1. Initial delay: 1 second
2. Max retries: 5
3. Backoff multiplier: 2x
4. Max delay: 60 seconds

When `X-RateLimit-Remaining` < 10, the manager preemptively waits.

## API Endpoints Used

### Repository Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /user/repos` | GET | List user's repositories |
| `GET /orgs/{org}/repos` | GET | List organization repositories |
| `GET /repos/{owner}/{repo}` | GET | Get repository details |
| `PATCH /repos/{owner}/{repo}` | PATCH | Update repository information |
| `GET /repos/{owner}/{repo}/contents/{path}` | GET | Get file contents |
| `PUT /repos/{owner}/{repo}/contents/{path}` | PUT | Create/update file |
| `GET /repos/{owner}/{repo}/license` | GET | Get repository license |

### Repository Information Fields

When updating a repository via `PATCH /repos/{owner}/{repo}`, the following fields can be modified:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Repository name |
| `description` | string | Repository description |
| `homepage` | string | URL for repository homepage |
| `private` | boolean | Repository visibility |
| `has_issues` | boolean | Enable issues |
| `has_projects` | boolean | Enable projects |
| `has_wiki` | boolean | Enable wiki |
| `is_template` | boolean | Make repository a template |

### Topics Management

Repository topics are managed via a separate endpoint:
- `PUT /repos/{owner}/{repo}/topics` - Replace all topics
- Requires media type: `application/vnd.github.mercy-preview+json`

### License Information

The license endpoint returns:
- `license.key` - SPDX license identifier (e.g., "mit", "apache-2.0", "gpl-3.0")
- `license.name` - Human-readable license name
- `license.spdx_id` - SPDX identifier
- `license.url` - URL to license text
- `license.node_id` - Internal GitHub identifier

## Error Handling

### Common HTTP Status Codes

| Code | Description | Handling |
|------|-------------|----------|
| 200 | OK | Success |
| 201 | Created | Resource created |
| 204 | No Content | Successful deletion/update |
| 304 | Not Modified | Conditional request, resource unchanged |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions or rate limit |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource already exists (for creation) |
| 422 | Unprocessable Entity | Validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | GitHub service error |
| 502 | Bad Gateway | Invalid response from upstream |
| 503 | Service Unavailable | GitHub service unavailable |
| 504 | Gateway Timeout | Upstream server timeout |

### Retry Logic

The manager automatically retries on:
- 408 Request Timeout
- 429 Too Many Requests
- 500 Internal Server Error
- 502 Bad Gateway
- 503 Service Unavailable
- 504 Gateway Timeout

### Network Errors

Handles:
- Connection timeouts
- DNS resolution failures
- SSL/TLS errors
- Network unreachable

## Data Formats

### Request/Response Body

All API communication uses JSON encoding:
- Request bodies: `application/json`
- Response bodies: `application/json`
- Character encoding: UTF-8

### File Contents

When uploading/downloading repository contents:
- Content is Base64 encoded in API requests/responses
- Manager handles encoding/decoding automatically
- Supports both text and binary files

## Examples

### Get Repository License
```http
GET /repos/octocat/Hello-World/license
Accept: application/vnd.github.v3+json
Authorization: token ghp_...

Response:
{
  "license": {
    "key": "mit",
    "name": "MIT License",
    "spdx_id": "MIT",
    "url": "https://api.github.com/licenses/mit",
    "node_id": "MDc6TGljZW5zZW1pdA=="
  }
}
```

### Update Repository Description
```http
PATCH /repos/octocat/Hello-World
Authorization: token ghp_...

{
  "description": "This is your first repository",
  "homepage": "https://github.com",
  "private": false,
  "has_issues": true,
  "has_projects": true,
  "has_wiki": true
}
```

### Create File
```http
PUT /repos/octocat/Hello-World/contents/README.md
Authorization: token ghp_...

{
  "message": "Add README",
  "content": "IyBCb29rZWQgd2l0aCBHZWl0SGViIEFQSSAK",
  "branch": "main"
}
```
Where content is base64 for "# Created with GitHub API"

## Best Practices

1. **Always check rate limits** before making bulk operations
2. **Implement exponential backoff** for failed requests
3. **Use conditional requests** when possible (ETag, Last-Modified)
4. **Handle pagination** for list endpoints (max 100 items per page)
5. **Validate inputs** before sending to API
6. **Log all API interactions** for debugging
7. **Respect user intent** - don't make unexpected changes
8. **Provide dry-run capability** for previewing changes
9. **Maintain audit trail** of all modifications
10. **Handle partial failures** gracefully in bulk operations

## References

- [GitHub REST API v3 Documentation](https://docs.github.com/en/rest)
- [GitHub API Rate Limiting](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting)
- [Repository Licensing API](https://docs.github.com/en/rest/reference/repos#licenses)
- [Repository Update API](https://docs.github.com/en/rest/reference/repos#update-a-repository)