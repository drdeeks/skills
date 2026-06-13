# Analytics Framework
## Table of Contents

- [Overview](#overview)
- [Data Model](#data-model)
- [Key Performance Indicators (KPIs)](#key-performance-indicators-kpis)
- [Decision Engine](#decision-engine)
- [Reporting Cadence](#reporting-cadence)
- [A/B Testing Framework](#a/b-testing-framework)


## Overview

The analytics engine is the decision-making core of the clip factory. It tracks performance across every dimension (niche, platform, account, posting time, hook style, creator) and produces actionable signals: scale, pivot, or kill.

## Data Model

### Clip Record
```json
{
  "clip_id": "uuid",
  "source_video": "url or title",
  "niche": "streamer|podcast|finance|reddit|educational",
  "creator": "creator name",
  "account": "posting account handle",
  "platform": "tiktok|youtube|instagram|x|linkedin",
  "posted_at": "ISO8601",
  "hook_style": "controversy|question|shock|insight|cliffhanger",
  "duration_seconds": 45,
  "caption_style": "word-by-word|sentence|none",
  "metrics": {
    "views_1h": 0,
    "views_6h": 0,
    "views_24h": 0,
    "views_48h": 0,
    "views_7d": 0,
    "likes": 0,
    "comments": 0,
    "shares": 0,
    "saves": 0,
    "watch_time_avg_pct": 0,
    "follower_delta": 0
  },
  "revenue": {
    "platform_rpm": 0.0,
    "content_rewards": 0.0,
    "direct_deal": 0.0,
    "total": 0.0
  }
}
```

### Account Record
```json
{
  "account_id": "uuid",
  "handle": "@handle",
  "platform": "tiktok",
  "niche": "streamer",
  "created_at": "ISO8601",
  "followers": 0,
  "total_views_30d": 0,
  "total_revenue_30d": 0.0,
  "clips_posted_30d": 0,
  "avg_views_per_clip": 0,
  "status": "active|scaling|pivoting|paused|killed"
}
```

## Key Performance Indicators (KPIs)

### Per-Clip KPIs
| KPI | Formula | Signal |
|---|---|---|
| View Velocity | views_6h / views_24h | >0.6 = viral trajectory |
| Engagement Rate | (likes + comments + shares) / views | >5% = high engagement |
| Save Rate | saves / views | >2% = highly valuable content |
| Watch Completion | watch_time_avg_pct | >70% = strong hook + content |
| Revenue Per Clip | total_revenue / 1 | Track over time |

### Per-Account KPIs
| KPI | Formula | Signal |
|---|---|---|
| Views/Clip (7d avg) | total_views_7d / clips_posted_7d | Trending up = scale |
| Revenue/Day | total_revenue_7d / 7 | Target: >$30/day/account |
| Follower Growth Rate | follower_delta_7d / followers | >2%/week = healthy |
| Post Frequency | clips_posted_7d / 7 | Target: 3-5/day |
| Platform CPM | (revenue / views) * 1000 | Compare across platforms |

### Per-Niche KPIs
| KPI | Formula | Signal |
|---|---|---|
| Niche CPM | total_niche_revenue / (total_niche_views / 1000) | Compare across niches |
| Saturation Index | active_clippers_estimate / content_supply | >5 = oversaturated |
| Content Freshness | hours since source content published | <24h for streamer, weeks OK for podcast |
| Hit Rate | clips_with_10k+_views / total_clips | >20% = good niche fit |

## Decision Engine

### Signal: SCALE
Trigger when ALL of:
- Account avg views/clip > 5,000 (7-day rolling)
- Hit rate > 20%
- Revenue/day > $30 per account
- Follower growth > 1%/week

Actions:
1. Increase posting frequency to max (5/day on that platform)
2. Spawn a new account in the same niche with a different angle
3. Expand to additional platforms
4. Increase Vugola clip extraction count per source video

### Signal: PIVOT
Trigger when ANY of:
- Account avg views/clip < 1,000 for 7 consecutive days
- Hit rate < 5% over 14 days
- Revenue/day < $5 per account for 7 days
- Follower growth negative for 7 days

Actions:
1. Analyze top 10 performing clips across ALL accounts — identify what niche/hook/creator/platform combo is working
2. Shift this account to the winning pattern
3. If no winning pattern exists across any account, select a new niche from the playbook using the composite score formula
4. Reset the 30-day evaluation clock

### Signal: KILL
Trigger when ALL of:
- Account has been active > 30 days
- Avg views/clip < 500 (30-day)
- Revenue total < $20 over 30 days
- Two pivot attempts have already been made

Actions:
1. Stop posting on this account
2. Archive analytics data
3. Reallocate the posting slot to a new account in a different niche

### Signal: MAINTAIN
When none of the above triggers fire:
- Continue current posting cadence
- Run weekly niche score recalculation
- Log metrics and wait for signals

## Reporting Cadence

### Daily Report (auto-generated)
- Total clips posted (by niche, platform, account)
- Total views accrued (24h window)
- Top 3 performing clips with links
- Any SCALE/PIVOT/KILL signals fired
- Revenue estimate

### Weekly Report (auto-generated)
- Week-over-week view growth by account
- Revenue by niche and platform
- Niche composite score recalculation
- Recommendations: scale/pivot/kill per account
- Content supply status (are source creators still producing?)

### Monthly Report (auto-generated)
- Total revenue breakdown
- ROI calculation (revenue vs tool costs: Vugola, hosting, API)
- Account portfolio health: how many active, scaling, pivoting, killed
- Strategic recommendations for next month
- New niche opportunities identified

## A/B Testing Framework

### What to test:
1. **Hook styles** — Run 2 hook variants of the same clip moment. Measure view velocity at 6h.
2. **Caption styles** — Word-by-word vs sentence vs none. Measure watch completion.
3. **Posting times** — Same clip, different time slots. Measure views_24h.
4. **Clip duration** — 30s vs 45s vs 60s of same moment. Measure engagement rate.
5. **Platform priority** — Post to TikTok first vs YouTube first. Measure cross-platform lift.

### Test protocol:
- Run each test for minimum 10 clips (5 per variant)
- Use only clips from the same creator/niche to control variables
- Log variant tag in clip record
- Auto-evaluate after 48h and adopt the winner
- Never test more than 1 variable at a time per account
