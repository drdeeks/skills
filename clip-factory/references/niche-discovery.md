# Proactive Niche Discovery & Expansion
## Table of Contents

- [Overview](#overview)
- [Discovery Sources](#discovery-sources)
- [Niche Catalog Schema](#niche-catalog-schema)
- [Discovery Workflow](#discovery-workflow)
- [Niche Taxonomy](#niche-taxonomy)
- [Cross-Agent Niche Distribution](#cross-agent-niche-distribution)
- [Validation Cadence](#validation-cadence)
- [Expansion Triggers](#expansion-triggers)


## Overview

The clip factory doesn't just operate in pre-selected niches — it continuously scouts, analyzes, and discovers new niche opportunities. This makes the niche catalog a living, expanding database that feeds the decision engine with an unbounded set of possibilities.

## Discovery Sources

### 1. Platform Trend Scraping

**TikTok Trending** (via Firecrawl or tiktok-ecommerce skill):
- Scrape TikTok Discover/For You trending topics weekly
- Identify creators gaining rapid follower growth (>10K/week)
- Track hashtag velocity — rising hashtags signal emerging niches
- Cross-reference with Content Rewards campaigns for monetization potential

**YouTube Trending** (via YouTube MCP or Firecrawl):
- Monitor YouTube Trending page across categories
- Track Shorts with >1M views in <24h — identify the source creator/niche
- Scrape YouTube Creator on the Rise badges
- Monitor new podcast launches (channels with interview format, >10K subs gained in first month)

**Instagram Explore** (via Firecrawl):
- Scrape Explore page for emerging Reels categories
- Track which content types are getting Reels Bonus attention
- Identify brand accounts investing heavily in short-form (signals ad spend flowing into that niche)

**X/Twitter Trending** (via Firecrawl):
- Monitor trending topics and viral threads
- Identify creators whose clips are going viral organically
- Track Spaces hosts with growing audiences (potential clip targets)

**Reddit Trending** (via Firecrawl):
- Monitor r/popular and fast-growing subreddits
- Track subreddits with >100K growth/month — signals a new content vertical
- Identify story-driven subreddits ripe for clip-style content (r/BestOf, r/AmITheAsshole, etc.)

### 2. Creator Economy Intelligence

**Content Rewards Platforms**:
- Scrape Whop Content Rewards for new campaigns weekly
- Monitor Clipping.net for new creator listings
- Check Vyro marketplace for new creator programs
- Track CPM changes — rising CPMs signal growing demand in that niche

**Creator Analytics** (via social scraping):
- Monitor Social Blade or similar for fastest-growing creators across platforms
- Identify creators who just started streaming/podcasting (early mover advantage)
- Track creator collab networks — when a big creator collabs with a smaller one, the smaller creator's content becomes clippable

**Brand Spend Signals**:
- Track which brands are running influencer campaigns (signals money flowing into that niche)
- Monitor sponsorship announcements from creators
- Cross-reference with programmatic ad CPMs by content category

### 3. Cultural & News Trend Mining

**News Cycle**:
- Scrape major news aggregators for trending topics
- When a topic trends (e.g., AI regulation, crypto bull run, sports event), check if there are creators producing long-form content about it
- Time-sensitive: these niches have a 1-4 week window before they saturate

**Seasonal/Event Calendar**:
- Sports seasons (NFL, NBA, UFC — clipper demand spikes during events)
- Award shows, product launches, elections
- Gaming releases (new game = new streamer content = new clip opportunities)
- Holiday content cycles

**Cultural Moments**:
- Viral moments, controversies, debates
- Meme cycles (identify meme formats early, clip source content)
- Cross-platform spillover (TikTok trend → YouTube reaction videos → clip the reactions)

### 4. Competitive Intelligence

**Clipper Page Analysis**:
- Use Firecrawl to scrape the top 50 clip pages on each platform
- Identify which niches they're serving
- Track their view counts and posting frequency
- Find niches with high views but few clippers (opportunity gap)
- Find niches where clippers are abandoning (declining niche or over-saturated)

**Content Rewards Leaderboards**:
- Scrape Whop leaderboards for top-earning clippers
- Identify which niches dominate the earnings
- Track new entrants vs established clippers

## Niche Catalog Schema

All discovered niches are stored in `/clip-factory/niche-catalog.json` on MuleRun Drive (shared across all agents):

```json
{
  "version": 1,
  "last_updated": "ISO8601",
  "niches": [
    {
      "id": "uuid",
      "name": "AI Tech Podcasts",
      "category": "podcast",
      "subcategory": "technology",
      "discovered_at": "ISO8601",
      "discovered_by": "agent-a1b2",
      "discovery_source": "youtube_trending",
      "status": "validated",
      "creators": [
        {
          "name": "Lex Fridman",
          "platform": "youtube",
          "channel_url": "https://...",
          "subscribers": 4200000,
          "upload_frequency": "weekly",
          "avg_video_length_min": 180,
          "estimated_clip_yield": 8
        }
      ],
      "scoring": {
        "view_velocity": 4.2,
        "rpm_ceiling": 3.5,
        "content_supply": 4.0,
        "competition_density": 2.8,
        "monetization_diversity": 3.5,
        "evergreen_score": 4.5,
        "composite_score": 3.82
      },
      "monetization": {
        "content_rewards_campaigns": ["campaign_id_1"],
        "estimated_cpm": 2.50,
        "platform_rpms": {
          "tiktok": 1.20,
          "youtube": 3.00,
          "instagram": 0.80
        }
      },
      "competitive_landscape": {
        "active_clippers_estimated": 45,
        "top_clipper_avg_views": 50000,
        "entry_difficulty": "moderate"
      },
      "tags": ["tech", "AI", "interview", "long-form", "evergreen"],
      "last_validated": "ISO8601",
      "validation_notes": "Strong content supply, moderate competition, high evergreen score"
    }
  ]
}
```

## Discovery Workflow

### Cron: niche-discovery (weekly, Sunday 8 PM — before weekly review)

```
1. SCRAPE — Hit all discovery sources:
   a. TikTok trending → extract emerging creators/topics
   b. YouTube trending Shorts → identify viral source creators
   c. Content Rewards platforms → new campaigns + CPM changes
   d. Reddit trending subreddits → new content verticals
   e. Competitive clipper pages → opportunity gaps

2. EXTRACT — For each potential niche found:
   a. Identify 3-5 creators in the niche
   b. Estimate content supply (uploads/week)
   c. Check Content Rewards for matching campaigns
   d. Estimate competition density (how many clippers already active)

3. SCORE — Calculate composite niche score:
   view_velocity * 0.25 + rpm_ceiling * 0.20 + content_supply * 0.15 
   + (6 - competition_density) * 0.15 + monetization_diversity * 0.15 
   + evergreen_score * 0.10

4. VALIDATE — Filter out low-quality discoveries:
   - Composite score < 2.5 → discard
   - Content supply < 2 videos/week → discard
   - No monetization path identified → flag as "experimental"
   - Already in catalog with same creators → update existing entry

5. REGISTER — Add validated niches to the shared catalog:
   a. Download /clip-factory/niche-catalog.json from Drive
   b. Merge new discoveries (deduplicate by creator overlap >60%)
   c. Upload updated catalog
   d. Log discoveries in coordination-log.jsonl

6. RECOMMEND — Feed into weekly review:
   a. Sort all catalog niches by composite score
   b. Cross-reference with global-registry.json for availability
   c. Present top 5 available niches as expansion candidates
```

### Continuous Discovery (passive, during regular operations)

During normal pipeline operations, the agent should passively capture signals:

- When a clip unexpectedly goes viral (>100K views) in a niche not in the catalog → add the niche
- When metrics pull reveals a new creator appearing in engagement data → investigate and catalog
- When Content Rewards emails (via AgentMail) announce new campaigns → check if it's a new niche
- When a PIVOT signal fires → trigger an immediate niche discovery scan for fresh options

## Niche Taxonomy

Organize discovered niches into a hierarchical taxonomy for deduplication and comparison:

```
Content Type
├── Streaming
│   ├── Gaming (FPS, MOBA, Battle Royale, RPG, Survival)
│   ├── IRL (Travel, Cooking, Fitness, Daily Life)
│   ├── Just Chatting (Drama, Debate, Comedy, React)
│   └── Music (DJ, Production, Covers, Freestyle)
├── Podcast
│   ├── Interview (Tech, Business, Science, Culture, Politics)
│   ├── Commentary (News, Sports, Entertainment, True Crime)
│   ├── Educational (Health, Finance, History, Psychology)
│   └── Comedy (Improv, Panel, Roast, Storytelling)
├── Finance & Business
│   ├── Crypto (Trading, DeFi, NFTs, Market Analysis)
│   ├── Investing (Stocks, Real Estate, Passive Income)
│   ├── Entrepreneurship (Startups, E-commerce, Agency)
│   └── Personal Finance (Budgeting, Debt, FIRE)
├── Fitness & Health
│   ├── Bodybuilding (Training, Nutrition, Competitions)
│   ├── Combat Sports (MMA, Boxing, Wrestling)
│   ├── Wellness (Meditation, Biohacking, Mental Health)
│   └── Sports Commentary (NFL, NBA, Soccer, F1)
├── Education & How-To
│   ├── Tech Tutorials (Coding, AI, Cybersecurity)
│   ├── Creative Skills (Design, Video Editing, Music Production)
│   ├── Language Learning
│   └── Academic (Science, Math, Philosophy)
├── Entertainment
│   ├── Reaction Content (Movies, Music, Internet Culture)
│   ├── Commentary (YouTube Drama, Pop Culture, Celebrity)
│   ├── Storytelling (Reddit Stories, Scary Stories, Lore)
│   └── Comedy (Sketches, Stand-up, Prank)
├── Lifestyle
│   ├── Fashion & Beauty
│   ├── Travel & Adventure
│   ├── Food & Cooking
│   └── Relationships & Dating
└── Emerging / Uncategorized
    └── (Auto-categorize after 7 days of data)
```

When a new niche is discovered, place it in the taxonomy. This prevents:
- Duplicate niches (two entries for "podcast/interview/tech" and "tech podcasts")
- Over-indexing on a single branch (if 8 agents all pick streaming subcategories)
- Missing opportunities in underserved branches

## Cross-Agent Niche Distribution

Combined with the global registry (see global-coordination.md), the niche catalog enables intelligent distribution:

```
Catalog has 50 niches scored and validated
Global registry shows 10 agents active
Max 2 agents per niche

Step 1: Sort all niches by composite_score (descending)
Step 2: For each agent needing a niche:
  a. Filter to niches with available_slots > 0
  b. Filter out niches in the same taxonomy branch if agent already has one
     (prefer diversity: don't give one agent "podcast/interview/tech" AND "podcast/interview/business")
  c. Select highest-scoring remaining niche
  d. Claim slot in global registry

Result: 10 agents × 2-3 niches each = 20-30 niche slots filled
         across diverse taxonomy branches, with no niche having >2 agents
         and the catalog continuously expanding with new discoveries
```

## Validation Cadence

Discovered niches degrade over time. Re-validate monthly:

| Age | Action |
|---|---|
| 0-7 days | "New" — monitor closely, don't commit heavy resources |
| 7-30 days | "Validated" — if metrics confirm scoring, promote to active |
| 30-90 days | "Established" — full confidence, eligible for SCALE |
| 90+ days | "Re-validate" — rescore, check if competition has changed |
| No clips in 60 days | "Stale" — remove from active recommendations |

## Expansion Triggers

The system proactively expands the niche catalog when:

1. **Agent count grows**: More agents → need more niche diversity → trigger extra discovery scans
2. **Multiple agents queued for same niche**: Demand signal → scout adjacent niches in same taxonomy branch
3. **PIVOT signals fire frequently**: Current catalog is exhausted → expand to entirely new taxonomy branches
4. **Cultural event detected**: Breaking news, product launch, sports season → time-limited niche injection
5. **Revenue plateau**: Overall revenue flat despite volume increases → need fresh niches with higher CPMs
