---
name: clip-factory
description: 'Autonomous content clipping factory — multi-agent system that clips
  long-form video into short-form content, captions it, and posts across social platforms
  at scale. Provider-agnostic: works with any LLM backend (OpenAI, Claude, Mistral,
  Gemini, Hermes, Copilot, or any agent with tool use). Free-first: starts with $0/mo
  tools (yt-dlp, whisperX, FFmpeg, self-hosted Postiz) and escalates only when revenue
  justifies cost. Use for: clip pipelines, clip farms, short-form automation, content
  rewards, cron-based content workflows, multi-niche account management with analytics-driven
  scale/pivot/kill decisions. Triggers: clip, clipping, clipper, short-form, reels,
  shorts, content factory, content farm, Vugola, Postiz, content rewards, repurpose
  video.'
license: MIT
version: 0.0.5
---
# Clip Factory

Autonomous multi-agent content clipping system. Clips long-form video into captioned shorts, posts across all platforms, tracks performance, and self-optimizes through analytics-driven scale/pivot/kill decisions.

## Provider Compatibility

This skill is **provider-agnostic** — it works with any LLM or agent runtime that can read markdown instructions and execute shell commands or API calls. No provider-specific features are required.

| Provider | Compatibility | Notes |
|---|---|---|
| **MuleRun** | Full | Native support for sessions, compute, drive, scheduling |
| **Claude (Anthropic)** | Full | Tool use, MCP servers, computer use all supported |
| **OpenAI / ChatGPT** | Full | Function calling maps to tool use; use Actions for MCPs |
| **Mistral / Mistral Vibe** | Full | Tool calling supported; scripts run independently of model |
| **Gemini (Google)** | Full | Function calling + extensions; Vertex AI for compute |
| **Hermes (Nous Research)** | Full | Tool-use fine-tuned; runs all scripts natively |
| **GitHub Copilot** | Partial | Best for code generation; use external scheduler for crons |
| **OpenClaw** | Full | Agent framework compatible; map tools to actions |
| **Any LLM with tool use** | Full | Scripts are plain Python — any agent can execute them |

**Provider-specific adapters**: The only MuleRun-specific features are `mulerun-session` (subagent spawning), `mulerun-computer` (persistent compute), and `mulerun-drive` (shared storage). For other providers:
- **Subagent spawning** → Use the provider's native multi-agent or threading API, or run `orchestrator.py` directly
- **Persistent compute** → Any VPS, Docker container, or cloud VM with cron
- **Shared storage** → Any cloud storage (S3, GCS, Azure Blob) or shared filesystem — update `niche_registry.py` drive functions

## Free-First Pipeline Strategy

**Always exhaust free options before committing to paid services.** Read [references/free-first-strategy.md](references/free-first-strategy.md) for the full alternatives table and upgrade decision matrix.

### Cost Tiers

| Tier | Cost | Stack | When to Use |
|---|---|---|---|
| **Tier 0** | $0/mo | yt-dlp + whisperX + FFmpeg + Postiz self-hosted | Starting out, validating niche |
| **Tier 1** | $0-15/mo | One paid service (e.g., Vugola) + free everything else | Revenue >$30/day, volume >10 clips/day |
| **Tier 2** | $15-40/mo | Full paid stack | Validated niches generating consistent revenue |
| **Tier 3** | $40+/mo | Premium APIs, multiple accounts | Scale mode with proven ROI |

**Escalation rule**: Never upgrade tiers until current tier revenue covers next tier cost with 2x margin.

### Free Pipeline (Tier 0)

```
yt-dlp (download) → whisperX (transcribe) → energy_scorer.py (find moments)
→ FFmpeg (cut + caption) → Postiz self-hosted (schedule) → Platform APIs (post)
→ Local JSONL (analytics) → decision_engine (optimize)
```

The `config.json` supports pluggable backends:
```json
{
  "clip_backend": "local",
  "caption_backend": "whisperx",
  "post_backend": "postiz-selfhost"
}
```

## Core Stack

| Component | Role | Cost | Free Alternative |
|---|---|---|---|
| **Vugola** (vugolaai.com) | AI clip extraction + captions | $14-21/mo | yt-dlp + whisperX + FFmpeg ($0) |
| **Postiz** (postiz.com) | Multi-platform posting | Free (self-host) or paid | Self-host via Docker ($0) |
| **AgentMail** (agentmail.to) | Agent email inboxes | Free-$20/mo | Free tier sufficient for setup |
| **Orchestrator Agent** | Pipeline brain, spawns subagents | - | Any LLM with tool use |
| **Persistent Compute** | Cron jobs and state | - | Any VPS or cloud VM |

## Workflow: First-Time Setup

### 1. Gather Requirements

Ask the user for:
- **Niche selection** — See [references/niche-playbook.md](references/niche-playbook.md) for tiers and scoring
- **AgentMail API key** — From console.agentmail.to (or ask user to create one). This is the only key the user *must* provide. The agent can self-register for everything else.
- **Vugola API key** — If user already has one, use it. Otherwise, the agent self-registers via AgentMail (see below).
- **Postiz API key** — If user already has one, use it. Otherwise, self-register.
- **Target platforms** — Which of: TikTok, YouTube Shorts, Instagram Reels, X, LinkedIn, Threads
- **Connected social accounts** — Which accounts are already linked in Postiz
- **Posting cadence** — Default: 3-5 clips/day per platform
- **Timezone** — For scheduling posts at optimal times
- **Source creators** — Which creators/channels to clip from

### 1b. Self-Registration (AgentMail Bootstrap)

If the user does not have API keys for Vugola, Postiz, or monetization platforms, the agent bootstraps them autonomously. See [references/self-registration.md](references/self-registration.md) for the full workflow.

**Summary**: For each service needing an account:
1. Create a dedicated AgentMail inbox (e.g., `clipfactory-vugola@agentmail.to`)
2. Use Playwright to navigate the service's signup page
3. Register with the AgentMail email address
4. Poll the AgentMail inbox for verification email (10s intervals, 5min timeout)
5. Extract OTP or verification link from the email body
6. Complete verification via Playwright
7. Navigate to the API key dashboard and extract the key
8. Store the key in `~/.clip-factory/config.json`

This enables fully autonomous bootstrapping — the only prerequisite from the user is the AgentMail API key (or their own email if they prefer manual setup).

**Services the agent can self-register for**: Vugola, Postiz, Whop (Content Rewards), Clipping.net, Vyro.

**Ongoing monitoring**: A `service-mail-check` cron (every 12h) monitors all AgentMail inboxes for billing alerts, API key rotations, new campaign opportunities, and account warnings.

### 1c. Auto-Provision MCP Servers

After obtaining API keys (manually or via self-registration), auto-wire MCP servers into the environment. See [references/mcp-provisioning.md](references/mcp-provisioning.md) for the full registry and provisioning workflow.

**Tier 1 (provision immediately)**: Vugola MCP, Postiz MCP, AgentMail MCP
**Tier 2 (provision when scaling)**: YouTube Data MCP, Playwright MCP
**Tier 3 (provision for advanced analytics)**: Firecrawl (already available), social analytics MCPs

Provisioning steps:
1. Read `/workspace/.mcp.json` — merge new MCP server entries (never replace existing)
2. Store API keys in `.claude/settings.local.json` under `env` using `${VAR_NAME}` interpolation
3. Reference env vars in `.mcp.json` via `${VAR_NAME}` syntax — never hardcode keys
4. After adding MCPs, run `skill-finder` to discover complementary skills that enhance the pipeline

### 1d. Discover & Leverage Complementary Skills

Use `skill-finder` to check for and leverage these enhancement skills:
- `playwright-cli` → browser automation for self-registration and dashboard scraping
- `html-report` → rich visual analytics reports with charts (use instead of plain markdown when available)
- `xlsx` → export analytics data to spreadsheets for external analysis
- `tiktok-ecommerce` → trending content discovery for TikTok-focused niches
- `mulerun-multi-session` → parallel subagent spawning (faster than sequential)

When a SCALE signal fires, re-check for new skills that could enhance the expanded operation.

### 2. Initialize State on Compute Instance

Use `mulerun-computer` skill to set up the persistent state directory:

```bash
mkdir -p ~/.clip-factory/{analytics,reports/{daily,weekly,monthly},logs}
```

Create `~/.clip-factory/config.json`:
```json
{
  "agentmail_api_key": "...",
  "agentmail_inboxes": {
    "services": "clipfactory-services@agentmail.to",
    "ops": "clipfactory-ops@agentmail.to"
  },
  "vugola_api_key": "vug_sk_...",
  "postiz_api_key": "...",
  "timezone": "America/Chicago",
  "niches": [
    {
      "name": "podcasts",
      "creators": ["Lex Fridman", "Joe Rogan"],
      "accounts": [
        {"handle": "@clippage1", "platform": "tiktok"},
        {"handle": "@clippage1", "platform": "youtube"}
      ],
      "clips_per_day": 5,
      "status": "active"
    }
  ],
  "posting_schedule": {
    "slots_cdt": ["09:00", "12:00", "15:00", "18:00", "21:00"]
  }
}
```

### 3. Set Up Cron Jobs

Use `mulerun-computer-schedule` skill to create the recurring jobs. See [references/scaling-guide.md](references/scaling-guide.md) for the full cron table.

Essential crons:
- **clip-scan** (every 4h): Discover new source videos from tracked creators
- **clip-process** (every 2h): Send queued videos to Vugola, poll for completion
- **clip-post** (every 30min): Dispatch ready clips to Postiz for scheduled posting
- **metrics-pull** (every 6h): Pull view/engagement data from platforms
- **daily-report** (11 PM): Generate analytics summary
- **weekly-review** (Sunday 10 PM): Run decision engine (scale/pivot/kill)
- **niche-discovery** (Sunday 8 PM): Proactive niche discovery scan — scrape trending content, score and validate new niches, update shared catalog
- **service-mail-check** (every 12h): Monitor AgentMail inboxes for billing alerts, key rotations, new campaigns
- **mcp-health-check** (every 1h): Verify all MCP servers are responding, log uptime/latency

Each cron job triggers a MuleRun session that loads this skill and executes the specific workflow.

To deploy all cron jobs at once, upload and run `scripts/setup_crons.py` on the compute instance:
```bash
python3 scripts/setup_crons.py              # Deploy scripts + create all crons
python3 scripts/setup_crons.py --dry-run    # Preview without creating
python3 scripts/setup_crons.py --status     # Show current cron status
```

### 4. Wire the Pipeline

The clip pipeline for each cron cycle:

```
Source Discovery → Vugola Clip → Caption → Postiz Schedule → Post → Metrics
```

**Source Discovery**: Scrape or API-check the tracked creator's channel for new uploads since last scan. Log new videos to `~/.clip-factory/queue.jsonl`.

**Vugola Clip**: For each queued video:
1. Call Vugola `clip_video` with the source URL
2. Poll `get_clip_status` until complete
3. Download clips via `download_clip`
4. Log clip metadata to `~/.clip-factory/analytics/clips.jsonl`

**Postiz Schedule**: For each clip:
1. Call Postiz `posts:create` with the clip file, caption, and scheduled time
2. Distribute across platforms according to the posting schedule
3. Spread posts across time slots to avoid platform rate limits

## Workflow: Multi-Agent Orchestration

### Spawning Niche Subagents

When the user has multiple niches or the SCALE signal fires, use `mulerun-session` or `mulerun-multi-session` to spawn subagents:

```
Orchestrator prompt for subagent:
"You are a niche clipping agent for [NICHE]. Your scope:
- Creators: [LIST]
- Accounts: [LIST]
- Platforms: [LIST]
- Cadence: [N] clips/day

Execute the clip pipeline:
1. Check for new source content from your creators
2. Send to Vugola for clipping
3. Schedule via Postiz at the designated time slots
4. Log all clip records to the shared analytics store

Report back: clips_processed, clips_posted, any errors."
```

Each subagent operates independently within its niche scope. The orchestrator aggregates results.

### Scaling Up

To add a new niche subagent:
1. Update `config.json` with the new niche entry
2. Spawn a new subagent scoped to that niche
3. The existing cron schedule automatically picks up the new niche

To add accounts within a niche:
1. Connect the new social account in Postiz
2. Add the account to the niche's account list in `config.json`
3. The subagent automatically distributes clips across all accounts

## Workflow: Analytics-Driven Decisions

Read [references/analytics-framework.md](references/analytics-framework.md) for the full KPI definitions, decision engine rules, and A/B testing protocol.

### Decision Engine Summary

Run on the weekly cron. For each account, evaluate:

| Signal | Condition | Action |
|---|---|---|
| **SCALE** | Avg views >5K, hit rate >20%, revenue >$30/day | Add accounts, increase frequency, expand platforms |
| **PIVOT** | Avg views <1K for 7d, or hit rate <5% for 14d | Shift niche/hook/creator based on winning patterns |
| **KILL** | <500 avg views after 30d + 2 failed pivots | Archive account, reallocate slot |
| **MAINTAIN** | No triggers fired | Continue, log, wait |

### Generating Reports

**Daily**: Total clips posted, views accrued (24h), top 3 clips, signals fired, revenue estimate.

**Weekly**: WoW growth by account, revenue by niche/platform, niche score recalculation, recommendations.

**Monthly**: Total revenue, ROI vs tool costs, portfolio health, strategic outlook.

Format reports as structured markdown. Store in `~/.clip-factory/reports/`. Optionally send via Telegram/Discord.

## Workflow: Async Pipeline Execution

### Scripts

Three scripts handle the deterministic pipeline infrastructure. Upload them to the compute instance during setup:

| Script | Purpose |
|---|---|
| `scripts/orchestrator.py` | Spawns parallel niche subagents, polls for completion, aggregates results, runs decision engine, generates reports |
| `scripts/pipeline.py` | Queue management, parallel Vugola processing, Postiz scheduling, retry logic |
| `scripts/setup_crons.py` | One-command deployment of all cron jobs to the compute instance |
| `scripts/niche_registry.py` | Global registry interaction — register, claim/release niches, heartbeat, catalog management |

### Async Subagent Dispatch Pattern

The orchestrator spawns one MuleRun session per active niche using `--wait=false` for fully async execution:

```
Orchestrator dispatches:
  session run --name clip-podcasts-a1b2 --wait=false → session_id_1
  session run --name clip-streamers-a1b2 --wait=false → session_id_2
  session run --name clip-finance-a1b2 --wait=false → session_id_3
  (all fire simultaneously — no sequential waiting)

Orchestrator polls:
  session get session_id_1 → running | completed
  session get session_id_2 → running | completed
  session get session_id_3 → completed (with JSON result)
  
  Poll every 30s until all complete or timeout (30 min)

Orchestrator aggregates:
  Merge clip records from all subagents → clips.jsonl
  Sum pipeline totals → run stats
  Generate run report → mandatory statistics block
```

Use `scripts/orchestrator.py dispatch` to execute this pattern, then `poll --run-id <id>` to monitor, then `report --run-id <id>` to generate statistics.

### Parallel Processing Standards

- **Concurrency limit**: Max 5 simultaneous Vugola clip jobs (respect API rate limits). Configurable via `pipeline.py process --max-concurrent 5`.
- **Timeout per job**: 30 minutes max for a single clip extraction. Jobs exceeding this are moved to retry queue.
- **Retry policy**: Failed items retry up to 3 times with exponential backoff (4h between retry cycles via cron). After 3 failures → permanent failure log.
- **Queue isolation**: Separate JSONL files for each pipeline stage (queue → processing → clips → retry → permanent_failures). No state collision between concurrent runs.
- **Stale detection**: The health cron moves any item stuck in "processing" for >2 hours back to retry queue.

### Throughput Targets

| Phase | Metric | Target |
|---|---|---|
| Scan | Creators checked per cycle | All active creators (unlimited) |
| Process | Videos through Vugola per cycle | 5-10 (limited by API) |
| Post | Clips scheduled per cycle | Up to 60 (all platforms × accounts) |
| Metrics | Clips updated per cycle | All clips from last 7 days |
| Full cycle | End-to-end latency | <25 minutes per niche |

### Pipeline Recovery

If the pipeline fails mid-run:
1. `pipeline.py status` — shows queue sizes and pipeline health
2. `pipeline.py retry` — requeues failed items
3. `orchestrator.py health` — checks MCP connectivity
4. Cron jobs auto-recover on next cycle — pending items are never lost

## Workflow: One-Shot Clip Run

For users who want to run a single clip job (not the full cron system):

1. Accept: source video URL + target platforms + posting times
2. Call Vugola `clip_video` → poll → download
3. Call Postiz `posts:create` for each clip × platform × time slot
4. Report: number of clips created, scheduled post times, preview links

Example user message:
> "Clip the latest Lex Fridman episode, pull the 5 best moments, schedule to TikTok and YouTube Shorts at 9am, 12pm, 6pm CDT for the next 3 days"

## Enforced Output Statistics

**Every clip-factory operation MUST conclude with a structured statistics block.** This is the feedback loop that drives all autonomous decisions. See [references/mcp-provisioning.md](references/mcp-provisioning.md) for the full template formats.

### Per-Run Report (after every pipeline execution)
Must include: pipeline counts (scanned/found/extracted/captioned/scheduled/posted/failed), distribution by platform, API usage (Vugola credits, Postiz calls, AgentMail emails), and errors.

### Daily Digest (11 PM cron)
Must include: volume totals, 24h performance (views, avg views/clip, best/worst clip, engagement rate, view velocity), estimated revenue by source, top 3 clips with links, signals fired, and pipeline health status including MCP uptime.

### Weekly Review (Sunday 10 PM cron)
Must include: portfolio summary with WoW deltas, per-niche breakdown with composite scores and signals, per-account breakdown with status, per-platform CPM comparison, A/B test results with confidence levels, recalculated niche scores, decisions executed, actionable recommendations, and full cost tracking with ROI calculation.

### Monthly Report (1st of month)
Same as weekly plus: 30-day revenue projection, strategic pivot recommendations, new niche opportunities, tool cost optimization suggestions.

### Enforcement rules:
- Statistics output is **non-negotiable** — if metrics are unavailable, output with `[pending]` markers
- Every statistics block is appended as structured JSON to `~/.clip-factory/analytics/run_stats.jsonl`
- If `html-report` skill is available, generate rich visual reports with charts alongside the text block
- If `xlsx` skill is available, export weekly/monthly data to spreadsheets

## Workflow: Global Coordination (Multi-Agent Niche Collision Prevention)

When multiple clip-factory agents run independently (up to 25+), they coordinate via a shared registry on MuleRun Drive to prevent niche over-saturation. **No more than 2 agents may operate in the same niche simultaneously.**

Read [references/global-coordination.md](references/global-coordination.md) for the full protocol and schema.

### Coordination Protocol Summary

1. **Register** — On first setup, generate a unique instance ID, add self to the global registry on Drive
2. **Claim** — Before activating a niche, check `niche_claims` for available slots. If full, pick a different niche
3. **Heartbeat** — Every health check cron, update `last_heartbeat`. Prune agents with heartbeat >2h as stale
4. **Release** — When pivoting or killing a niche, release the claim so other agents can use it
5. **Collision Resolution** — If two agents claim the last slot simultaneously, the newest agent yields

### Registry-Aware Decision Engine

| Signal | Registry Action |
|---|---|
| **SCALE** | Verify niche slots before adding accounts. If full, scale into a second niche instead |
| **PIVOT** | Query available niches. Only pivot into niches with `available_slots > 0` |
| **KILL** | Release the niche claim immediately. Freed slot becomes available to other agents |
| **MAINTAIN** | Send heartbeat only |

Use `scripts/niche_registry.py` to interact with the global registry:
```bash
python3 niche_registry.py register          # Register this agent instance
python3 niche_registry.py claim podcasts    # Claim a niche slot
python3 niche_registry.py release podcasts  # Release a niche claim
python3 niche_registry.py heartbeat         # Send heartbeat + prune stale agents
python3 niche_registry.py available         # List niches with open slots
python3 niche_registry.py status            # Full registry dump
```

## Workflow: Proactive Niche Discovery

The clip factory continuously scouts, analyzes, and discovers new niche opportunities — making the niche catalog a living, expanding database that feeds the decision engine with an unbounded set of possibilities.

Read [references/niche-discovery.md](references/niche-discovery.md) for the full discovery sources, catalog schema, taxonomy, and validation cadence.

### Discovery Sources

1. **Platform Trend Scraping** — TikTok, YouTube, Instagram, X, Reddit trending content
2. **Creator Economy Intelligence** — Content Rewards campaigns, Social Blade growth, brand spend signals
3. **Cultural & News Trend Mining** — News cycle topics, seasonal events, viral moments
4. **Competitive Intelligence** — Top clipper page analysis, Content Rewards leaderboards

### Weekly Discovery Cron (Sunday 8 PM — before weekly review)

```
SCRAPE → EXTRACT → SCORE → VALIDATE → REGISTER → RECOMMEND
```

Each discovered niche is scored using the composite formula, validated against minimum thresholds, deduplicated against the existing catalog, and stored in the shared `/clip-factory/niche-catalog.json` on MuleRun Drive.

### Niche Catalog Interaction

```bash
python3 niche_registry.py catalog                    # List all discovered niches by score
python3 niche_registry.py discover-add '<niche_json>' # Add a new niche to the catalog
```

### Continuous Passive Discovery

During normal operations, capture signals automatically:
- Clip goes viral (>100K views) in an uncataloged niche → add it
- New creator appears in engagement data → investigate and catalog
- Content Rewards email announces new campaign → check for new niche
- PIVOT signal fires → trigger immediate discovery scan for fresh options


## Enhancement Hooks

| Skill | Enhancement | When to Add |
|-------|-------------|-------------|
| `skill-creator` | Basic skill creation | When creating simple skills |
| `skill-creator-pro` | Enterprise upgrade | When upgrading to enterprise |
| `html-report` | Visual validation dashboard | When auditing many skills |
| `xlsx` | Export validation results | When tracking skill quality metrics |

## Key References

- **Niche selection, monetization platforms, posting schedules**: [references/niche-playbook.md](references/niche-playbook.md)
- **KPIs, decision engine, A/B testing, reporting**: [references/analytics-framework.md](references/analytics-framework.md)
- **Multi-agent architecture, cron setup, scaling phases, state management, error handling**: [references/scaling-guide.md](references/scaling-guide.md)
- **AgentMail self-registration, verification parsing, inbox management, credential bootstrapping**: [references/self-registration.md](references/self-registration.md)
- **MCP auto-provisioning, skill enhancement, enforced statistics templates, hooks, health monitoring**: [references/mcp-provisioning.md](references/mcp-provisioning.md)
- **Global coordination, niche collision prevention, shared registry protocol**: [references/global-coordination.md](references/global-coordination.md)
- **Proactive niche discovery, catalog schema, taxonomy, validation cadence**: [references/niche-discovery.md](references/niche-discovery.md)
- **Free-first pipeline strategy, cost tiers, free tool alternatives, upgrade decision matrix**: [references/free-first-strategy.md](references/free-first-strategy.md)

## Sources

- **Docker Documentation**: https://docs.docker.com
- **Azure Documentation**: https://learn.microsoft.com/azure/
- **yt-dlp Documentation**: https://github.com/yt-dlp/yt-dlp
- **FFmpeg Documentation**: https://ffmpeg.org/documentation.html

