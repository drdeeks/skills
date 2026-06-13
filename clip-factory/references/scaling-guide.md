# Scaling & Multi-Agent Architecture
## Table of Contents

- [Multi-Agent Design](#multi-agent-design)
- [Cron Architecture](#cron-architecture)
- [Scaling Playbook](#scaling-playbook)
- [Pivot Protocol](#pivot-protocol)
- [State Management](#state-management)
- [Error Handling & Resilience](#error-handling-&-resilience)


## Multi-Agent Design

The clip factory operates as a hierarchy of specialized subagents, each scoped to a content focus area. The orchestrator (parent agent) manages the portfolio and delegates execution.

### Agent Hierarchy

```
┌─────────────────────────────────────┐
│         ORCHESTRATOR AGENT          │
│  Portfolio management, analytics,   │
│  scale/pivot/kill decisions, cron   │
└──────────┬──────────────────────────┘
           │
    ┌──────┴──────────────────────────────────┐
    │              │              │            │
┌───▼───┐    ┌────▼────┐   ┌────▼────┐  ┌────▼────┐
│Niche  │    │Niche    │   │Niche    │  │Niche    │
│Agent  │    │Agent    │   │Agent    │  │Agent    │
│Streams│    │Podcasts │   │Finance  │  │Reddit   │
└───┬───┘    └────┬────┘   └────┬────┘  └────┬────┘
    │             │             │             │
  Accounts    Accounts      Accounts      Accounts
  Platforms   Platforms     Platforms     Platforms
```

### Orchestrator Agent Responsibilities
- Maintain global config: API keys, posting schedule, niche assignments
- Spawn/despawn niche subagents based on SCALE/PIVOT/KILL signals
- Aggregate analytics across all subagents
- Generate daily/weekly/monthly reports
- Manage cron schedule
- Handle user commands (add niche, pause account, force pivot, etc.)

### Niche Subagent Responsibilities
- Own 1-N accounts within a single niche
- Execute the clip pipeline: source discovery → Vugola clip → Postiz post
- Track per-clip and per-account metrics
- Report metrics up to orchestrator
- Execute A/B tests assigned by orchestrator
- Handle platform-specific posting rules

## Cron Architecture

### Cron Jobs (managed via MuleRun Computer Schedule)

| Job | Schedule | Description |
|---|---|---|
| `clip-scan` | Every 4 hours | Scan for new source content from tracked creators |
| `clip-process` | Every 2 hours | Process queued source videos through Vugola |
| `clip-post` | Every 30 min | Check posting schedule and dispatch to Postiz |
| `metrics-pull` | Every 6 hours | Pull view/engagement metrics from all platforms |
| `daily-report` | Daily 11 PM | Generate daily analytics report |
| `weekly-review` | Sunday 10 PM | Run weekly analytics, recalculate niche scores, fire signals |
| `monthly-review` | 1st of month | Full monthly report + strategic recommendations |
| `health-check` | Every 1 hour | Verify API keys, account status, posting pipeline health |

### Cron Setup Pattern
Each cron job triggers a MuleRun session that:
1. Loads the clip-factory skill
2. Reads the persistent state (config, analytics DB)
3. Executes the job-specific workflow
4. Writes updated state
5. Sends notifications if action needed (Telegram/Discord/email)

## Scaling Playbook

### Phase 1: Single Niche Launch (Week 1-2)
- 1 niche, 1 account per platform, 3 platforms
- 3 clips/day = ~9 posts/day total
- Goal: Validate niche viability
- Subagents: 1 niche agent

### Phase 2: Validate & Double Down (Week 3-4)
- Winning platform identified → increase to 5 clips/day there
- Add account #2 (same niche, different angle)
- 2 accounts × 5 clips × 3 platforms = ~30 posts/day
- Subagents: 1 niche agent, 2 account scopes

### Phase 3: Multi-Niche Expansion (Month 2)
- Add 2nd niche based on niche composite score
- 2 niches × 2 accounts × 5 clips × 4 platforms = ~80 posts/day
- Subagents: 2 niche agents

### Phase 4: Full Scale (Month 3+)
- 3-4 active niches
- 3 accounts per niche × 5 clips × 4 platforms = 180-240 posts/day
- Automated SCALE/PIVOT/KILL managing the portfolio
- Subagents: 3-4 niche agents, fully autonomous

## Pivot Protocol

When the analytics engine fires a PIVOT signal:

1. **Freeze** — Stop posting on the flagged account (pause cron for that account)
2. **Diagnose** — Pull the last 14 days of clip data for the account:
   - Which clips got views? What hooks/creators/durations?
   - Compare against winning accounts in other niches
   - Check if the niche itself is declining (cross-reference with other clippers' public metrics)
3. **Decide** —
   - If the niche is dying → move to highest-scoring available niche
   - If the niche is fine but the account is underperforming → change hook style, posting times, or creator selection
   - If no niche is performing → pause scaling, reduce to 1 experimental account per niche, enter test mode
4. **Execute** — Update the niche agent's config, reset the evaluation window, resume posting
5. **Monitor** — 7-day evaluation window before next decision

## State Management

All persistent state is stored in a JSON file on the compute instance:

```
~/.clip-factory/
├── config.json          # API keys, niche assignments, account list
├── state.json           # Current status of all agents/accounts
├── analytics/
│   ├── clips.jsonl      # Append-only clip records
│   ├── accounts.json    # Account-level aggregated metrics
│   └── niches.json      # Niche-level scores and history
├── reports/
│   ├── daily/           # Daily report archives
│   ├── weekly/          # Weekly report archives
│   └── monthly/         # Monthly report archives
└── logs/
    └── pipeline.log     # Operational logs
```

## Error Handling & Resilience

| Failure | Response |
|---|---|
| Vugola API down | Queue source video, retry in 30 min, alert after 3 failures |
| Postiz API down | Hold clips in local queue, retry posting on next cron cycle |
| Platform rate limit | Back off posting for that platform, redistribute to others |
| API key expired | Alert user immediately, pause all posting for that service |
| Account banned/shadowbanned | Fire KILL signal, alert user, spin up replacement account |
| Clip processing fails | Log error, skip clip, continue pipeline with next clip |
| Metrics pull fails | Use last known metrics, retry next cycle |
