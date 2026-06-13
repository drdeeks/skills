# Analytics Framework

KPIs, decision engine, reporting cadences, and A/B testing protocol for the growth engine. Load when generating reports, making campaign decisions, or evaluating performance.

## Table of Contents

1. [North Star Metric](#north-star-metric)
2. [KPI Hierarchy](#kpi-hierarchy)
3. [Decision Engine](#decision-engine)
4. [Reporting Cadences](#reporting-cadences)
5. [A/B Testing Protocol](#ab-testing-protocol)
6. [Volume-to-Goal Tracker](#volume-to-goal-tracker)

---

## North Star Metric

**$5,000,000 total value processed through the application.**

This is the singular goal. All campaigns, channels, and tactics are measured by their contribution to this number. Not profit — total transaction volume flowing through the Email Remittance Pro smart contracts.

### Breakdown to $5M

| Scenario | Avg TX | Transactions needed | Monthly (12mo) | Daily |
|----------|--------|---------------------|-----------------|-------|
| Conservative | $150 | 33,334 | 2,778 | 93 |
| Moderate | $200 | 25,000 | 2,084 | 70 |
| Optimistic | $300 | 16,667 | 1,389 | 47 |

At the conservative $150 avg, ~93 transactions/day across all corridors achieves $5M in 12 months.

---

## KPI Hierarchy

### Level 1: Volume metrics (weekly review)

| KPI | Definition | Target |
|-----|-----------|--------|
| Total Volume Processed (TVP) | Sum of all transaction values (USD) | $5M cumulative |
| Monthly Active Senders (MAS) | Unique sender wallets per month | 3,000 by month 12 |
| Transaction Count | Total transactions per period | 10,000/month by month 12 |
| Average Transaction Value (ATV) | TVP / Transaction Count | $150+ |

### Level 2: Growth metrics (weekly review)

| KPI | Definition | Target |
|-----|-----------|--------|
| New Sender Acquisition | First-time senders per week | 200/week by month 6 |
| Repeat Rate | % senders who transact 2+ times | >40% |
| Referral Rate | % new users from referral links | >25% |
| Corridor Distribution | Volume share per corridor | No single corridor >50% |

### Level 3: Outreach metrics (daily review)

| KPI | Definition | Target |
|-----|-----------|--------|
| Leads Discovered | New leads added to pipeline | 50/week |
| Leads Qualified | Leads scoring 40+ | 30/week |
| Outreach Sent | Messages/proposals sent | 100/week |
| Response Rate | Replies / outreach sent | >15% |
| Conversion Rate | Converted / outreach sent | >5% |
| CAC | Total outreach cost / new users acquired | <$10 |

### Level 4: Product metrics (weekly review)

| KPI | Definition | Target |
|-----|-----------|--------|
| Claim Rate | % of sent remittances that get claimed | >80% |
| Gift Card vs Wallet Split | % claiming as gift card | Target 60/40 |
| Time to Claim | Median hours from send to claim | <2 hours |
| Failed Transaction Rate | % transactions that fail | <1% |
| Fraud Rate | % flagged/reversed transactions | <2% |

---

## Decision Engine

Automated signals that trigger campaign adjustments.

### Signal: SCALE

**Condition:** Corridor achieving >$50K/month volume AND >20% MoM growth AND CAC <$10
**Action:** Double campaign intensity — add subagents, increase ad spend, activate influencer partnerships
**Frequency:** Check weekly

### Signal: EXPAND

**Condition:** All Tier 1 corridors active AND combined volume >$200K/month
**Action:** Activate next Tier 2 corridor with highest score from market_scanner.py
**Frequency:** Check monthly

### Signal: PIVOT

**Condition:** Corridor <$5K/month after 8 weeks of active campaigns AND CAC >$50
**Action:** Reduce to maintenance mode, reallocate budget to higher-performing corridors
**Frequency:** Check monthly

### Signal: OPTIMIZE

**Condition:** Response rate <10% on any channel for 2 consecutive weeks
**Action:** A/B test new outreach templates, rotate messaging, try different channels
**Frequency:** Check biweekly

### Signal: PARTNER

**Condition:** Any B2B lead responds positively (demo scheduled or API docs requested)
**Action:** Escalate to priority — dedicate subagent to relationship nurturing, prepare custom integration plan
**Frequency:** Check daily

---

## Reporting Cadences

### Daily Digest (automated)

```json
{
  "report": "daily_digest",
  "date": "YYYY-MM-DD",
  "volume_today_usd": 0,
  "transactions_today": 0,
  "cumulative_volume_usd": 0,
  "pct_to_goal": 0.0,
  "new_leads": 0,
  "outreach_sent": 0,
  "responses_received": 0,
  "top_corridor_today": "",
  "alerts": []
}
```

### Weekly Review

```json
{
  "report": "weekly_review",
  "week": "YYYY-WNN",
  "volume_week_usd": 0,
  "volume_wow_delta_pct": 0.0,
  "cumulative_volume_usd": 0,
  "pct_to_goal": 0.0,
  "mas": 0,
  "new_senders": 0,
  "repeat_rate_pct": 0.0,
  "referral_rate_pct": 0.0,
  "corridors": {},
  "outreach_funnel": {
    "discovered": 0, "qualified": 0, "sent": 0, "replied": 0, "converted": 0
  },
  "signals_fired": [],
  "decisions_made": [],
  "cost": {"tier": 0, "spend_usd": 0.0}
}
```

### Monthly Summary

```json
{
  "report": "monthly_summary",
  "month": "YYYY-MM",
  "volume_month_usd": 0,
  "volume_mom_delta_pct": 0.0,
  "cumulative_volume_usd": 0,
  "pct_to_goal": 0.0,
  "revenue_usd": 0,
  "cac_usd": 0.0,
  "ltv_usd": 0.0,
  "active_corridors": 0,
  "b2b_pipeline": {"proposals_sent": 0, "demos_done": 0, "partnerships_signed": 0},
  "strategic_outlook": "",
  "next_month_priorities": []
}
```

---

## A/B Testing Protocol

### What to test

| Variable | Variants | Metric | Min sample |
|----------|----------|--------|------------|
| Outreach subject line | 2-3 variants per template | Open/response rate | 50 sends per variant |
| Messaging angle | Fee savings vs convenience vs speed | Response rate | 30 per variant |
| Channel priority | WhatsApp-first vs Facebook-first | Conversion rate | 100 leads per variant |
| Ad creative | Photo vs video vs carousel | Click-through rate | 1,000 impressions per variant |
| Referral incentive | $5 vs $10 vs $25 credit | Referral conversion | 100 referrals per tier |
| Language | English vs native language | Claim rate | 50 claims per variant |

### Testing rules

1. Run one test at a time per corridor (avoid confounding)
2. Minimum 2 weeks per test (account for weekly cycles)
3. Statistical significance: p < 0.05 before declaring winner
4. Document all tests in `analytics/ab_tests.jsonl`
5. Winner becomes new default; loser variants archived

---

## Volume-to-Goal Tracker

### Monthly volume targets to reach $5M in 12 months

| Month | Monthly volume | Cumulative | % to goal | MoM growth |
|-------|---------------|------------|-----------|------------|
| 1 | $50K | $50K | 1.0% | — |
| 2 | $75K | $125K | 2.5% | 50% |
| 3 | $120K | $245K | 4.9% | 60% |
| 4 | $180K | $425K | 8.5% | 50% |
| 5 | $270K | $695K | 13.9% | 50% |
| 6 | $400K | $1.1M | 21.9% | 48% |
| 7 | $500K | $1.6M | 31.9% | 25% |
| 8 | $600K | $2.2M | 43.9% | 20% |
| 9 | $700K | $2.9M | 57.9% | 17% |
| 10 | $750K | $3.6M | 72.9% | 7% |
| 11 | $750K | $4.4M | 87.9% | 0% |
| 12 | $650K | $5.0M | 100% | -13% |

Growth rate decelerates as volume scales — early months are steepest growth, later months sustain.
