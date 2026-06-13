# Free-First Pipeline Strategy
## Table of Contents

- [Philosophy](#philosophy)
- [Cost Tier Escalation](#cost-tier-escalation)
- [Free Alternatives by Component](#free-alternatives-by-component)
- [Free-First Pipeline (Tier 0)](#free-first-pipeline-tier-0)
- [Provider-Specific Free Tiers](#provider-specific-free-tiers)
- [Cost Tracking](#cost-tracking)
- [Upgrade Decision Matrix](#upgrade-decision-matrix)


## Philosophy

Always exhaust free and open-source options before committing to paid services. The pipeline is designed in cost tiers — start at Tier 0 (zero cost) and only escalate when free options create a genuine bottleneck or the revenue justifies the spend.

## Cost Tier Escalation

```
Tier 0: $0/mo — Free tools only, manual where needed
Tier 1: $0-15/mo — One paid service (typically Vugola or equivalent)
Tier 2: $15-40/mo — Full paid stack for validated, revenue-generating niches
Tier 3: $40+/mo — Scale mode with premium APIs, multiple accounts
```

**Rule**: Never escalate tiers until the current tier's revenue covers the next tier's cost with 2x margin.

## Free Alternatives by Component

### Video Clipping (replaces Vugola at $14-21/mo)

| Tool | Cost | Method | Trade-offs |
|---|---|---|---|
| **FFmpeg + scene detection** | Free | `ffmpeg -i input.mp4 -filter:v "select='gt(scene,0.3)'"` splits on scene changes | No AI moment detection, requires manual curation |
| **yt-dlp + FFmpeg** | Free | Download source → split into segments by timestamp | Manual timestamp identification |
| **Whisper + FFmpeg** | Free | Transcribe → find high-energy segments by keyword density → cut | CPU-intensive, but highly effective |
| **Auto-Editor** | Free | `auto-editor input.mp4 --margin 0.5s` removes silence, keeps high-energy | Good for podcasts, less effective for visual content |
| **PySceneDetect** | Free | Python library for automated scene boundary detection | Clip boundaries only, no "best moment" intelligence |
| **Opus Clip free tier** | Free (10 clips/mo) | AI-powered, similar to Vugola | Very limited volume |
| **Clipper (open-source)** | Free | GitHub: various open-source clip extractors | Quality varies, requires evaluation |

**Recommended free stack**: `yt-dlp` (download) → `whisper.cpp` (transcribe) → keyword/energy scoring (Python script) → `FFmpeg` (cut + encode)

### Captioning (replaces Vugola captions)

| Tool | Cost | Method |
|---|---|---|
| **Whisper / whisper.cpp** | Free | OpenAI's open-source speech-to-text, runs locally |
| **whisperX** | Free | Whisper with word-level timestamps + speaker diarization |
| **FFmpeg drawtext** | Free | Burn subtitles from SRT/ASS onto video |
| **ass-subtitle styling** | Free | Advanced SubStation Alpha for animated captions |

**Recommended free stack**: `whisperX` (transcribe with timestamps) → generate `.ass` subtitle file with styling → `FFmpeg` burn-in

### Social Media Posting (replaces Postiz paid)

| Tool | Cost | Method |
|---|---|---|
| **Postiz self-hosted** | Free | Docker self-host on any VPS or compute instance |
| **Platform native APIs** | Free | TikTok Content Posting API, YouTube Data API, Instagram Graph API (requires Meta app review) |
| **Buffer free tier** | Free | 3 channels, 10 scheduled posts/channel |
| **Typefully free tier** | Free | X/Twitter scheduling, limited posts |
| **Direct upload scripts** | Free | Python scripts using platform SDKs/APIs |

**Recommended free approach**: Self-host Postiz via Docker on the compute instance. Zero cost, full feature set.

### Email / Identity (replaces AgentMail paid tier)

| Tool | Cost | Method |
|---|---|---|
| **AgentMail free tier** | Free | Limited inboxes, sufficient for bootstrapping |
| **Temp mail APIs** | Free | Guerrilla Mail, 10MinuteMail — for one-time verifications only |
| **Self-hosted email** | Free | Docker mailserver on compute instance (complex setup) |
| **Gmail + App Passwords** | Free | Use existing Google account with app-specific passwords |

**Recommended**: AgentMail free tier for initial setup, upgrade only if inbox volume exceeds free limits.

### Analytics & Metrics

| Tool | Cost | Method |
|---|---|---|
| **Platform native analytics** | Free | TikTok Analytics API, YouTube Analytics API, Instagram Insights |
| **Firecrawl scraping** | Free tier | Scrape public view counts from profile pages |
| **Local JSONL analytics** | Free | All analytics stored locally in structured JSONL files |
| **Social Blade (public)** | Free | Scrape public creator statistics |

All analytics in this skill are already free — JSONL-based local storage with no external dependencies.

### Content Discovery

| Tool | Cost | Method |
|---|---|---|
| **YouTube RSS feeds** | Free | `https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID` |
| **yt-dlp --flat-playlist** | Free | List channel uploads without downloading |
| **Firecrawl free tier** | Free | Scrape creator pages for new uploads |
| **Reddit JSON API** | Free | Append `.json` to any Reddit URL |
| **Platform public APIs** | Free | YouTube Data API (10K quota/day free), TikTok Research API |

### Video Download

| Tool | Cost | Method |
|---|---|---|
| **yt-dlp** | Free | Download from YouTube, Twitch VODs, and 1000+ sites |
| **gallery-dl** | Free | Download from Instagram, Twitter/X media |
| **Twitch CLI** | Free | Download Twitch VODs and clips |

## Free-First Pipeline (Tier 0)

```
yt-dlp (download) → whisperX (transcribe) → energy_scorer.py (find moments)
→ FFmpeg (cut + caption) → Postiz self-hosted (schedule) → Platform APIs (post)
→ Local JSONL (analytics) → decision_engine.py (optimize)
```

Total cost: **$0/mo** (excluding compute instance)

### When to Upgrade from Tier 0

Escalate to Tier 1 (paid clipping) when ALL of these are true:
- Volume exceeds 10 clips/day (manual curation becomes bottleneck)
- Revenue from clips exceeds $30/day (ROI justifies spend)
- Free clip quality consistently underperforms paid alternatives (measured by view velocity)

### Scripts for Free Pipeline

The `scripts/pipeline.py` already supports pluggable backends. To use the free stack:

```python
# In config.json, set:
{
  "clip_backend": "local",  # "vugola" or "local"
  "caption_backend": "whisperx",  # "vugola" or "whisperx"
  "post_backend": "postiz-selfhost",  # "postiz-cloud" or "postiz-selfhost" or "direct-api"
}
```

When `clip_backend` is `"local"`, the pipeline uses:
1. `yt-dlp` to download the source video
2. `whisperX` to generate a timestamped transcript
3. Keyword density + silence detection to score segments
4. `FFmpeg` to cut top-scoring segments into clips
5. `FFmpeg drawtext` to burn styled captions

## Provider-Specific Free Tiers

Some services offer free tiers that should be exhausted before upgrading:

| Service | Free Tier | When to Upgrade |
|---|---|---|
| YouTube Data API | 10,000 units/day | >50 creator scans/day |
| TikTok Content Posting API | Unlimited (with app approval) | N/A — always free |
| Firecrawl | 500 credits/mo | >500 scrapes/month |
| AgentMail | Limited inboxes | >5 service registrations |
| Opus Clip | 10 clips/month | >10 clips/month |
| Buffer | 30 posts/month across 3 channels | >30 posts/month |

## Cost Tracking

Every weekly report MUST include a cost section:

```
═══ COST TRACKING ═══
Tool Costs:
  Vugola:     $0.00 (using local FFmpeg stack)
  Postiz:     $0.00 (self-hosted)
  AgentMail:  $0.00 (free tier)
  Compute:    $X.XX (MuleRun Computer)
  ─────────────────
  Total:      $X.XX/mo

Revenue:      $XX.XX/mo
ROI:          XX.Xx
Tier:         0 (free-first)
Upgrade recommendation: [HOLD | EVALUATE | UPGRADE to Tier 1]
```

## Upgrade Decision Matrix

| Metric | Hold at Free | Evaluate Upgrade | Upgrade |
|---|---|---|---|
| Clips/day | <10 | 10-20 | >20 |
| Revenue/day | <$15 | $15-30 | >$30 |
| Clip quality (view velocity vs paid) | >0.8x | 0.5-0.8x | <0.5x |
| Manual curation time | <30min/day | 30-60min/day | >60min/day |
| Failed clips (quality issues) | <10% | 10-20% | >20% |
