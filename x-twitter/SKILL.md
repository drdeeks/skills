---
name: x-twitter
description: Interact with Twitter/X — read tweets, search, post, like, retweet, and
license: MIT
metadata:
version: 0.0.3
---
# twitter-openclaw 🐦‍⬛

Interact with Twitter/X posts, timelines, and users from OpenClaw.

## Authentication

Requires a Twitter API Bearer Token set as `TWITTER_BEARER_TOKEN`.

Optionally set `TWITTER_API_KEY` and `TWITTER_API_SECRET` for write operations (post, like, retweet).

Run `twclaw auth-check` to verify credentials.

## Commands

### Reading

```bash
twclaw read <tweet-url-or-id>          # Read a single tweet with full metadata
twclaw thread <tweet-url-or-id>        # Read full conversation thread
twclaw replies <tweet-url-or-id> -n 20 # List replies to a tweet
twclaw user <@handle>                  # Show user profile info
twclaw user-tweets <@handle> -n 20     # User's recent tweets
```

### Timelines

```bash
twclaw home -n 20                      # Home timeline
twclaw mentions -n 10                  # Your mentions
twclaw likes <@handle> -n 10           # User's liked tweets
```

### Search

```bash
twclaw search "query" -n 10            # Search tweets
twclaw search "from:elonmusk AI" -n 5  # Search with operators
twclaw search "#trending" --recent     # Recent tweets only
twclaw search "query" --popular        # Popular tweets only
```

### Trending

```bash
twclaw trending                        # Trending topics worldwide
twclaw trending --woeid 23424977       # Trending in specific location
```

### Posting

```bash
twclaw tweet "hello world"                          # Post a tweet
twclaw reply <tweet-url-or-id> "great thread!"      # Reply to a tweet
twclaw quote <tweet-url-or-id> "interesting take"   # Quote tweet
twclaw tweet "look at this" --media image.png        # Tweet with media
```

### Engagement

```bash
twclaw like <tweet-url-or-id>          # Like a tweet
twclaw unlike <tweet-url-or-id>        # Unlike a tweet
twclaw retweet <tweet-url-or-id>       # Retweet
twclaw unretweet <tweet-url-or-id>     # Undo retweet
twclaw bookmark <tweet-url-or-id>      # Bookmark a tweet
twclaw unbookmark <tweet-url-or-id>    # Remove bookmark
```

### Following

```bash
twclaw follow <@handle>                # Follow user
twclaw unfollow <@handle>              # Unfollow user
twclaw followers <@handle> -n 20       # List followers
twclaw following <@handle> -n 20       # List following
```

### Lists

```bash
twclaw lists                           # Your lists
twclaw list-timeline <list-id> -n 20   # Tweets from a list
twclaw list-add <list-id> <@handle>    # Add user to list
twclaw list-remove <list-id> <@handle> # Remove user from list
```

## Output Options

```bash
--json          # JSON output
--plain         # Plain text, no formatting
--no-color      # Disable ANSI colors
-n <count>      # Number of results (default: 10)
--cursor <val>  # Pagination cursor for next page
--all           # Fetch all pages (use with caution)
```

## Guidelines for OpenClaw

- When reading tweets, always show: author, handle, text, timestamp, engagement counts.
- For threads, present tweets in chronological order.
- When searching, summarize results concisely with key metrics.
- Before posting/liking/retweeting, confirm the action with the user.
- Rate limits apply — space out bulk operations.
- Use `--json` when you need to process output programmatically.


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
| `scripts/main.py` | x-twitter script | Run with python3 |

## Key References

- **Overview**: [references/overview.md](references/overview.md)
- **API Reference**: [references/api-reference.md](references/api-reference.md)
- **Rate Limits**: [references/rate-limits.md](references/rate-limits.md)

## Sources

- **Twitter API v2**: https://developer.twitter.com/en/docs/twitter-api - Official Twitter API documentation

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

## Troubleshooting

### 401 Unauthorized
Check that `TWITTER_BEARER_TOKEN` is set and valid.

### 429 Rate Limited
Wait and retry. Twitter API has strict rate limits per 15-minute window.

---

**TL;DR**: Read, search, post, and engage on Twitter/X. Always confirm before write actions.
