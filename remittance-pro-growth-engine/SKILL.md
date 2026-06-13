---
name: remittance-pro-growth-engine
description: "Autonomous client acquisition and growth engine for Email Remittance Pro — a crypto-to-email remittance service with gift card offramps. Deploys subagents across 10+ campaigns spanning B2C corridors (US→Mexico, UAE→India, US→Philippines, Saudi→Pakistan, UK→Nigeria) and B2B partnerships (DAOs, payroll platforms, freelance platforms, exchanges). Handles lead discovery, pipeline management, multi-channel outreach (Facebook, WhatsApp, Telegram, TikTok, email, governance forums, LinkedIn, Discord), content creation, influencer sourcing, SEO, referral loops, credential bootstrapping, and campaign analytics. Free-first cost strategy with $0 startup. Provider-agnostic — works with any LLM agent runtime. Goal: $5M total value processed through the application. Use when: client acquisition, growth campaigns, outreach, lead generation, market scanning, corridor expansion, partnership development, or any task related to growing Email Remittance Pro's transaction volume."
version: 0.0.5
---

# Remittance Pro Growth Engine

Autonomous multi-agent growth system for Email Remittance Pro. Targets $5M total value processed by orchestrating subagents across B2C remittance corridors and B2B platform partnerships.

**Product:** Email Remittance Pro — send crypto to any email, recipient claims as crypto wallet or gift card. 1.5% flat fee, instant settlement, email-only identity layer.

## Provider Compatibility

| Provider | Compatibility | Notes |
|---|---|---|
| MuleRun | Full | Native session/compute/drive for subagent dispatch |
| Claude (Anthropic) | Full | Tool use chains for multi-step workflows |
| OpenAI / ChatGPT | Full | Function calling, Assistants API for subagents |
| Mistral / Vibe | Full | Tool calling, script execution |
| Gemini (Google) | Full | Extensions, Vertex AI |
| Any LLM + tools | Full | Scripts are pure Python, provider-independent |

**Provider-specific subagent dispatch:**
- MuleRun: `mulerun-session` for parallel campaign agents
- OpenAI: Assistants API threads per campaign
- Generic: Run scripts directly in sequential mode

## Free-First Strategy

| Tier | Monthly cost | What you get |
|---|---|---|
| Tier 0 | $0 | All scripts, organic outreach, manual DMs, JSONL analytics |
| Tier 1 | $0-50 | Email API (Resend), social scheduling (Buffer), small ad budget |
| Tier 2 | $50-200 | Multi-platform ads, micro-influencer deals, CRM |
| Tier 3 | $200+ | Professional campaigns, conferences, PR — justified by revenue |

Start at Tier 0. Upgrade only when quantitative criteria met. See [references/free-first-strategy.md](references/free-first-strategy.md).

## Core Stack

| Component | Role | Cost | Free alternative |
|---|---|---|---|
| `orchestrator.py` | Campaign dispatch + decision engine | $0 | — |
| `pipeline.py` | Lead qualification + funnel management | $0 | — |
| `market_scanner.py` | Corridor analysis + opportunity ranking | $0 | — |
| `outreach_engine.py` | Template generation + outreach tracking | $0 | — |
| Firecrawl MCP | Web search for lead/community discovery | $0 (MCP) | Manual search |
| Playwright | Platform self-registration + scraping | $0 | Manual signup |
| Resend API | Email delivery at scale | $0-20/mo | Personal email |

## Workflow: Campaign Launch

### Step 1: Scan markets

```bash
python3 scripts/market_scanner.py corridors
python3 scripts/market_scanner.py partnerships --type dao
python3 scripts/market_scanner.py opportunities --top 10
```

Select corridors and B2B targets. Prioritize by score.

### Step 2: Dispatch campaigns

```bash
python3 scripts/orchestrator.py dispatch --campaign corridor_us_mexico
python3 scripts/orchestrator.py dispatch --campaign b2b_dao_outreach
python3 scripts/orchestrator.py dispatch --campaign all  # Launch all campaigns
```

Each campaign defines subagent roles. Dispatch subagents as parallel tasks:

| Subagent role | Responsibility |
|---|---|
| `community_infiltrator` | Join and authentically engage target communities |
| `content_creator` | Generate corridor-specific content (graphics, videos, copy) |
| `outreach_sender` | Send personalized outreach via appropriate channels |
| `influencer_scout` | Find and pitch micro-influencers (5K-50K followers) |
| `ad_manager` | Deploy and optimize paid ad campaigns |
| `proposal_writer` | Draft governance proposals for DAO integration |
| `relationship_builder` | Nurture B2B contacts through consistent engagement |
| `demo_coordinator` | Prepare and deliver live product walkthroughs |
| `seo_researcher` | Find high-volume, low-competition keywords per corridor |
| `partnership_scout` | Connect with bloggers, podcasters, media contacts |
| `campaign_designer` | Design referral programs and viral mechanics |

### Step 3: Build lead pipeline

```bash
python3 scripts/pipeline.py ingest --source leads.json
python3 scripts/pipeline.py qualify --min-score 40
python3 scripts/pipeline.py process --stage outreach --batch 20
python3 scripts/pipeline.py status
```

Pipeline stages: `discovered → qualified → outreach_pending → outreach_sent → responded → converted`

### Step 4: Execute outreach

```bash
python3 scripts/outreach_engine.py templates
python3 scripts/outreach_engine.py generate --template expat_community --corridor "US→Mexico" --language es
python3 scripts/outreach_engine.py generate --template dao_proposal --target "Uniswap DAO"
python3 scripts/outreach_engine.py track --lead "Uniswap DAO" --status replied
```

Templates available: `dao_proposal`, `expat_community`, `expat_community_es`, `b2b_payroll`, `influencer_pitch`, `freelance_platform`, `seo_article`

### Step 5: Monitor + decide

```bash
python3 scripts/orchestrator.py report --period weekly
python3 scripts/orchestrator.py decide
python3 scripts/orchestrator.py health
```

Decision engine fires signals: `SCALE` (increase intensity), `EXPAND` (add corridors), `PIVOT` (reallocate), `OPTIMIZE` (A/B test), `PARTNER` (escalate B2B lead).

## Workflow: Subagent Creative Thinking

Subagents are not limited to templates. For each campaign, agents should:

1. **Research the audience** — Read community posts, understand pain points, learn the language and tone
2. **Create original angles** — Fee savings is one angle; also try: speed, convenience for elderly, privacy, gift card variety, crypto optionality, "no bank needed"
3. **Test unconventional channels** — Churches, labor camp welfare officers, professional association newsletters, diaspora podcasts, university international student offices
4. **Build authentic relationships** — Spend 2 weeks engaging before pitching. Community leaders respond to peers, not salespeople
5. **Leverage cultural moments** — Diwali, Eid, Mother's Day, Independence Day — remittance demand spikes during these periods
6. **Create shareable content** — "I saved $X vs Western Union" testimonial format spreads organically
7. **Cross-pollinate corridors** — Success stories from one corridor can be adapted to others

See [references/audience-discovery.md](references/audience-discovery.md) for unconventional audience angles (students, digital nomads, NGOs, gaming, emergency response).

## Workflow: Credential Bootstrap

Before outreach, register on target platforms. See [references/credential-bootstrap.md](references/credential-bootstrap.md) for full protocol.

Quick reference: Facebook → WhatsApp → Telegram → Twitter → Instagram → LinkedIn → TikTok → Discord → YouTube → Reddit

**Account warming is mandatory** — 7-14 days of authentic engagement before any promotional activity. Cold accounts get flagged.

## Scripts

| Script | Purpose |
|---|---|
| `scripts/orchestrator.py` | Multi-campaign dispatch, polling, reporting, decision engine, health checks |
| `scripts/pipeline.py` | Lead ingestion, scoring, qualification, stage management, CSV export |
| `scripts/market_scanner.py` | Corridor ranking, audience discovery, B2B target scanning, competitor analysis |
| `scripts/outreach_engine.py` | Template-based message generation, personalization, outreach tracking, funnel reporting |

All scripts support `--help` and `--dry-run` flags.

## Enforced Output Statistics

Every operation concludes with structured JSON output:

```json
{
  "operation": "campaign_dispatch | lead_qualify | outreach_send | report",
  "timestamp": "ISO8601",
  "status": "success | partial | failed",
  "inputs": {"count": 0, "source": ""},
  "outputs": {"count": 0, "type": ""},
  "errors": [],
  "metrics": {},
  "cost": {"tier": 0, "amount_usd": 0.0, "service": ""}
}
```

Append to `analytics/run_stats.jsonl`. Reports: per-operation, daily digest, weekly review, monthly summary.

## Error Handling

| Error | Response |
|---|---|
| Platform ban | Switch to backup account, appeal, reduce frequency |
| Rate limiting | Respect cooldown, queue items, resume at 50% rate |
| Content rejection | Revise content, remove flagged terms, resubmit |
| API failure | Retry 3x with backoff, fallback to manual |
| Budget exceeded | Pause campaigns, review spend |

Full error catalog: [references/error-handling.md](references/error-handling.md)

## Enhancement Hooks

| Skill | Enhancement | When to add |
|---|---|---|
| `playwright-cli` | Browser automation for self-registration and scraping | Platform account setup |
| `html-report` | Visual analytics dashboards | When generating weekly/monthly reports |
| `xlsx` | Spreadsheet export for lead data | When sharing data externally |
| `mulerouter-skills` | Generate outreach graphics and demo videos | Content creation campaigns |
| `mulerun-session` | Parallel subagent spawning | Running multiple campaigns simultaneously |
| `mulerun-computer-schedule` | Cron jobs for daily/weekly automated reports | Scheduled campaign monitoring |
| `firecrawl` | Web search for community discovery | Lead discovery sweeps |
| `skill-finder` | Discover new capabilities | When SCALE or EXPAND signal fires |

## Key References

- **Corridor strategies, gift card mapping, launch checklists**: [references/corridor-playbook.md](references/corridor-playbook.md) — read when planning or executing corridor campaigns
- **Channel-specific outreach tactics and selection matrix**: [references/outreach-channels.md](references/outreach-channels.md) — read when choosing or optimizing outreach channels
- **KPIs, decision engine signals, A/B testing, volume targets**: [references/analytics-framework.md](references/analytics-framework.md) — read when generating reports or making campaign decisions
- **Cost tiers, free alternatives, upgrade criteria**: [references/free-first-strategy.md](references/free-first-strategy.md) — read when evaluating budget or paid tool upgrades
- **Error catalog and recovery procedures**: [references/error-handling.md](references/error-handling.md) — read when troubleshooting failures
- **Audience profiling, market signals, unconventional angles**: [references/audience-discovery.md](references/audience-discovery.md) — read when discovering new audiences or expanding to new corridors
- **Platform self-registration and account warming**: [references/credential-bootstrap.md](references/credential-bootstrap.md) — read when setting up new platform accounts
- **DAO, payroll, freelance, exchange partnership strategies**: [references/b2b-partnerships.md](references/b2b-partnerships.md) — read when executing B2B campaigns
