# Twitter API v2 Reference

## Authentication
- **Bearer Token**: Read-only access (tweet lookup, search, timelines)
- **OAuth 2.0**: Write access (post, like, retweet, follow)
- **App-only**: Rate limited, no user context

## Key Endpoints

### Tweets
```
GET /2/tweets/:id                    # Single tweet
GET /2/tweets                        # Multiple tweets (ids param)
GET /2/tweets/search/recent          # Recent search
GET /2/tweets/search/all             # Full archive (elevated)
POST /2/tweets                       # Create tweet
DELETE /2/tweets/:id                 # Delete tweet
```

### Users
```
GET /2/users/:id                     # Single user
GET /2/users/by/username/:username   # User by handle
GET /2/users/:id/tweets              # User tweets
GET /2/users/:id/following           # Following list
GET /2/users/:id/followers           # Followers list
POST /2/users/:id/following          # Follow user
DELETE /2/users/:source_id/following/:target_id  # Unfollow
```

### Engagement
```
POST /2/users/:id/likes              # Like tweet
DELETE /2/users/:id/likes/:tweet_id  # Unlike tweet
POST /2/users/:id/retweets           # Retweet
DELETE /2/users/:id/retweets/:tweet_id  # Unretweet
POST /2/users/:id/bookmarks          # Bookmark
DELETE /2/users/:id/bookmarks/:tweet_id  # Remove bookmark
```

### Lists
```
GET /2/lists                         # Owned lists
GET /2/lists/:id                     # List details
GET /2/lists/:id/tweets              # List timeline
POST /2/lists                        # Create list
DELETE /2/lists/:id                  # Delete list
POST /2/lists/:id/members            # Add member
DELETE /2/lists/:id/members/:user_id # Remove member
```

## Rate Limits (15-min windows)
| Endpoint | Limit |
|----------|-------|
| Tweet lookup | 900 |
| Recent search | 450 |
| User lookup | 900 |
| User tweets | 900 |
| Follow/Unfollow | 50 |
| Like/Unlike | 50 |
| Tweet create | 300 |
| List ops | 300 |

## Response Format
```json
{
  "data": {...},
  "includes": {...},
  "meta": {...},
  "errors": [...]
}
```

## Pagination
- `next_token` in meta for next page
- `max_results` param (10-100)
- `--all` flag fetches all pages
