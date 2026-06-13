# MCP Auto-Provisioning & Skill Enhancement
## Table of Contents

- [Overview](#overview)
- [MCP Server Registry](#mcp-server-registry)
- [Auto-Provisioning Workflow](#auto-provisioning-workflow)
- [Skill Enhancement: Auto-Discovery](#skill-enhancement:-auto-discovery)
- [Enforced Output Statistics](#enforced-output-statistics)
- [Hooks for Quality Enforcement](#hooks-for-quality-enforcement)
- [MCP Health Monitoring](#mcp-health-monitoring)
- [Version Management](#version-management)


## Overview

The clip factory autonomously provisions MCP servers, discovers complementary skills, and enforces output statistics standards. This makes the system self-expanding — as new tools become available, the agent integrates them without manual wiring.

## MCP Server Registry

### Tier 1: Core Pipeline MCPs (provision on first setup)

**Vugola MCP** — Clipping engine
```json
{
  "vugola": {
    "command": "npx",
    "args": ["-y", "vugola-mcp@latest"],
    "env": {
      "VUGOLA_API_KEY": "${VUGOLA_API_KEY}"
    }
  }
}
```
Tools exposed: `clip_video`, `get_clip_status`, `caption_video`, `schedule_post`, `list_scheduled_posts`, `cancel_scheduled_post`, `download_clip`, `get_credits`

**Postiz MCP** — Social scheduling
```json
{
  "postiz": {
    "command": "npx",
    "args": ["-y", "postiz-mcp@latest"],
    "env": {
      "POSTIZ_URL": "${POSTIZ_URL}",
      "POSTIZ_API_KEY": "${POSTIZ_API_KEY}",
      "POSTIZ_ENABLE_WRITE": "true"
    }
  }
}
```
Tools exposed: `posts:create`, `posts:list`, `posts:schedule`, `integrations:list`, `analytics:get`

**AgentMail MCP** — Agent email for self-registration
```json
{
  "agentmail": {
    "command": "npx",
    "args": ["-y", "agentmail-mcp@latest"],
    "env": {
      "AGENTMAIL_API_KEY": "${AGENTMAIL_API_KEY}"
    }
  }
}
```
Tools exposed: `create_inbox`, `list_inboxes`, `send_message`, `list_messages`, `get_message`, `reply_message`, `create_draft`, `list_threads`, `create_webhook`

### Tier 2: Analytics & Enhancement MCPs (provision when scaling)

**YouTube Data MCP** — Source content discovery
```json
{
  "youtube": {
    "command": "npx",
    "args": ["-y", "@anthropic/youtube-mcp@latest"],
    "env": {
      "YOUTUBE_API_KEY": "${YOUTUBE_API_KEY}"
    }
  }
}
```
Use for: Discovering new uploads from tracked creators, pulling video metadata, checking view counts for source selection.

**Social Analytics MCP** — Cross-platform metrics
If a dedicated social analytics MCP becomes available (check via `skill-finder`), add it for unified metrics pulling across TikTok, YouTube, Instagram, X.

**Browserbase / Playwright MCP** — Headless browser for registration flows
```json
{
  "playwright": {
    "command": "npx",
    "args": ["-y", "@anthropic/playwright-mcp@latest"]
  }
}
```
Use for: AgentMail self-registration flows, scraping platform analytics dashboards, verifying posted content.

### Tier 3: Intelligence MCPs (provision for advanced analytics)

**Firecrawl** (already present in environment) — Web scraping for competitive intelligence
- Scrape competitor clip pages to benchmark performance
- Monitor Content Rewards campaign listings
- Track trending content across platforms

**Market Data** (already present) — Not directly used by clip factory, but available for finance-niche content trend analysis.

## Auto-Provisioning Workflow

### When to provision MCPs

Run this check during the `SessionStart` or first clip-factory invocation:

1. Read `/workspace/.mcp.json`
2. For each Tier 1 MCP, check if it exists in `mcpServers`
3. If missing and the corresponding API key is available in `~/.clip-factory/config.json`:
   - Add the MCP entry to `.mcp.json`
   - Set the env var in `.claude/settings.local.json` under `env`
   - Log the addition

### How to add an MCP server

Read the existing `.mcp.json`, merge the new server entry, write back:

```python
import json

# Read existing
with open('/workspace/.mcp.json', 'r') as f:
    config = json.load(f)

# Add new server
config['mcpServers']['vugola'] = {
    "command": "npx",
    "args": ["-y", "vugola-mcp@latest"],
    "env": {
        "VUGOLA_API_KEY": api_key
    }
}

# Write back
with open('/workspace/.mcp.json', 'w') as f:
    json.dump(config, f, indent=2)
```

### Environment variable management

Store API keys in `.claude/settings.local.json` (gitignored, local scope):

```json
{
  "env": {
    "VUGOLA_API_KEY": "vug_sk_...",
    "POSTIZ_API_KEY": "...",
    "POSTIZ_URL": "https://api.postiz.com",
    "AGENTMAIL_API_KEY": "...",
    "YOUTUBE_API_KEY": "..."
  }
}
```

Never put API keys in `.claude/settings.json` (committed) or `.mcp.json` directly — always use `${VAR_NAME}` interpolation in `.mcp.json` and actual values in `.claude/settings.local.json`.

## Skill Enhancement: Auto-Discovery

### Complementary skills to detect and leverage

During setup or scaling, check if these skills are available via the `skill-finder` skill:

| Skill | Trigger | Purpose |
|---|---|---|
| `playwright-cli` | Self-registration flows | Browser automation for signup, verification, dashboard scraping |
| `mulerun-computer` | Cron setup | Persistent compute for state and scheduling |
| `mulerun-computer-schedule` | Cron creation | Create/manage recurring jobs |
| `mulerun-session` | Subagent spawning | Launch niche-scoped subagents |
| `mulerun-multi-session` | Parallel subagents | Spawn multiple niche agents simultaneously |
| `html-report` | Report generation | Rich visual reports with charts for weekly/monthly analytics |
| `xlsx` | Data export | Export analytics to spreadsheets for external analysis |
| `tiktok-ecommerce` | TikTok niche research | Discover trending products/content for TikTok-focused niches |
| `technical-analysis` | Revenue optimization | Analyze revenue patterns, predict optimal scaling timing |

### Auto-enhancement pattern

When the clip factory detects a scaling event (SCALE signal), it should:

1. Check which complementary skills are available
2. If `html-report` is available → generate visual reports instead of plain markdown
3. If `xlsx` is available → export analytics data alongside reports
4. If `tiktok-ecommerce` is available → cross-reference trending TikTok content with niche selection
5. If `mulerun-multi-session` is available → use parallel session spawning instead of sequential

## Enforced Output Statistics

### Mandatory Statistics Block

Every clip-factory operation MUST conclude with a structured statistics block. This is non-negotiable — it's the feedback loop that drives all decisions.

#### Per-Run Statistics (after every clip pipeline execution)
```
═══════════════════════════════════════════
 CLIP FACTORY RUN REPORT
═══════════════════════════════════════════
 Run ID:          {uuid}
 Timestamp:       {ISO8601}
 Duration:        {minutes}m {seconds}s
 Mode:            {one-shot | cron-scan | cron-process | cron-post}
───────────────────────────────────────────
 PIPELINE
   Source videos scanned:    {n}
   New videos found:         {n}
   Clips extracted:          {n}
   Clips captioned:          {n}
   Clips scheduled:          {n}
   Clips posted:             {n}
   Clips failed:             {n} ({reasons})
───────────────────────────────────────────
 DISTRIBUTION
   TikTok:     {n} posts  │  YouTube: {n} posts
   Instagram:  {n} posts  │  X:       {n} posts
   LinkedIn:   {n} posts  │  Threads: {n} posts
───────────────────────────────────────────
 API USAGE
   Vugola credits used:     {n} / {total}
   Postiz API calls:        {n}
   AgentMail emails sent:   {n}
───────────────────────────────────────────
 ERRORS
   {error_type}: {count} — {summary}
═══════════════════════════════════════════
```

#### Daily Statistics (generated by daily-report cron)
```
═══════════════════════════════════════════
 DAILY DIGEST — {date}
═══════════════════════════════════════════
 VOLUME
   Total clips posted:      {n}
   Across platforms:         {n}
   Across accounts:          {n}
   Across niches:            {n}
───────────────────────────────────────────
 PERFORMANCE (24h window)
   Total views accrued:      {n}
   Avg views/clip:           {n}
   Best clip:                {title} — {views} views
   Worst clip:               {title} — {views} views
   Engagement rate (avg):    {pct}%
   View velocity (avg):      {ratio} (6h/24h)
───────────────────────────────────────────
 REVENUE (estimated)
   Platform RPM:             ${amount}
   Content Rewards:          ${amount}
   Direct deals:             ${amount}
   Total:                    ${amount}
───────────────────────────────────────────
 TOP 3 CLIPS
   1. {title} — {views} views, {engagement}% ER
   2. {title} — {views} views, {engagement}% ER
   3. {title} — {views} views, {engagement}% ER
───────────────────────────────────────────
 SIGNALS FIRED
   {SCALE|PIVOT|KILL|MAINTAIN}: {account} — {reason}
───────────────────────────────────────────
 HEALTH
   Pipeline errors:          {n}
   API quota remaining:      Vugola: {pct}% | Postiz: OK
   Accounts active:          {n} / {total}
═══════════════════════════════════════════
```

#### Weekly Statistics (generated by weekly-review cron)
```
═══════════════════════════════════════════
 WEEKLY REVIEW — Week of {date}
═══════════════════════════════════════════
 PORTFOLIO SUMMARY
   Active niches:            {n}
   Active accounts:          {n}
   Total clips posted:       {n} (WoW: {+/-pct}%)
   Total views:              {n} (WoW: {+/-pct}%)
   Total revenue:            ${n} (WoW: {+/-pct}%)
───────────────────────────────────────────
 PER-NICHE BREAKDOWN
   {niche_1}:
     Clips: {n} | Views: {n} | Rev: ${n} | Hit Rate: {pct}%
     Score: {composite} | Signal: {SCALE/PIVOT/KILL/MAINTAIN}
   {niche_2}:
     Clips: {n} | Views: {n} | Rev: ${n} | Hit Rate: {pct}%
     Score: {composite} | Signal: {SCALE/PIVOT/KILL/MAINTAIN}
───────────────────────────────────────────
 PER-ACCOUNT BREAKDOWN
   {handle}@{platform}:
     Views/clip: {n} | Followers: {n} ({+/-delta})
     Revenue/day: ${n} | Status: {active/scaling/pivoting}
───────────────────────────────────────────
 PER-PLATFORM BREAKDOWN
   TikTok:    {views} views | ${rev} | CPM: ${n}
   YouTube:   {views} views | ${rev} | CPM: ${n}
   Instagram: {views} views | ${rev} | CPM: ${n}
   X:         {views} views | ${rev} | CPM: ${n}
───────────────────────────────────────────
 A/B TEST RESULTS
   {test_name}: Variant A ({metric}) vs Variant B ({metric})
   Winner: {variant} — {confidence}% confidence
───────────────────────────────────────────
 NICHE SCORES (recalculated)
   1. {niche}: {score} ({change from last week})
   2. {niche}: {score} ({change from last week})
───────────────────────────────────────────
 DECISIONS EXECUTED
   - {action taken and why}
───────────────────────────────────────────
 RECOMMENDATIONS
   - {actionable recommendation}
───────────────────────────────────────────
 COST TRACKING
   Vugola:        ${cost}
   Postiz:        ${cost}
   AgentMail:     ${cost}
   Compute:       ${cost}
   Total:         ${cost}
   ROI:           {revenue/cost}x
═══════════════════════════════════════════
```

#### Monthly Statistics
Same structure as weekly but with 30-day aggregation plus:
- Strategic pivot recommendations
- New niche opportunity analysis
- Projected revenue at current trajectory
- Tool cost optimization suggestions

### Enforcement Mechanism

The statistics output is not optional. To enforce this:

1. **Post-run validation**: After every pipeline run, the orchestrator agent must verify the statistics block was generated. If metrics are missing (e.g., view counts not yet available), the block must still be output with `pending` markers.

2. **Append-only logging**: Every statistics block is appended to `~/.clip-factory/analytics/run_stats.jsonl` as structured JSON, in addition to the human-readable format shown to the user.

3. **Missing data protocol**: If a metric cannot be computed (API down, data not yet available):
   - Mark with `[pending]` in the report
   - Queue a retry in the next `metrics-pull` cron cycle
   - Never skip the entire report because some data is missing

## Hooks for Quality Enforcement

### SessionStart Hook — Auto-load clip-factory state

Add to `.claude/settings.local.json`:
```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "test -f ~/.clip-factory/config.json && echo '{\"hookSpecificOutput\":{\"hookEventName\":\"SessionStart\",\"additionalContext\":\"Clip factory config detected at ~/.clip-factory/config.json. Load it if the user mentions clipping or content.\"}}' || true",
        "timeout": 5
      }]
    }]
  }
}
```

### Stop Hook — Enforce statistics output

```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "prompt",
        "prompt": "Check if this session involved any clip-factory pipeline operations. If so, verify that a structured statistics block (CLIP FACTORY RUN REPORT or DAILY DIGEST or WEEKLY REVIEW) was included in the output. If statistics are missing, output them now from the data available."
      }]
    }]
  }
}
```

## MCP Health Monitoring

### Cron: mcp-health-check (every 1h)

For each configured MCP server:
1. Attempt a lightweight API call (e.g., Vugola `get_credits`, Postiz `integrations:list`)
2. Record response time and status
3. If server is down:
   - Log the failure
   - If 3 consecutive failures → alert user
   - Queue pipeline items for retry
4. Track MCP uptime in `~/.clip-factory/analytics/mcp_health.jsonl`

Include MCP health in the daily statistics:
```
 MCP HEALTH
   vugola:     UP (avg response: 340ms)
   postiz:     UP (avg response: 120ms)
   agentmail:  UP (avg response: 95ms)
   youtube:    DOWN since {time} — queued {n} items
```

## Version Management

### Auto-update MCP packages

During the weekly review cron, check for MCP package updates:

```bash
# Check latest version
npm view vugola-mcp version
npm view postiz-mcp version
npm view agentmail-mcp version
```

If a newer version is available:
1. Log the available update
2. Include in weekly report under "MAINTENANCE"
3. If it's a patch/minor update → auto-update the `@latest` tag handles this
4. If it's a major version → flag for user review (breaking changes possible)

### Track MCP tool additions

When an MCP server is updated and exposes new tools, the agent should:
1. Detect new tools via tool listing
2. Log them in the weekly report
3. Evaluate if new tools enhance the pipeline (e.g., new analytics endpoints)
4. Auto-integrate if the tool clearly fits the workflow
