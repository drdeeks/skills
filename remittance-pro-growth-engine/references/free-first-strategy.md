# Free-First Strategy

Cost tiers, free alternatives, and upgrade decision criteria. Load when planning budget or evaluating paid tool upgrades.

## Table of Contents

1. [Cost Tier Ladder](#cost-tier-ladder)
2. [Component Cost Map](#component-cost-map)
3. [Upgrade Decision Matrix](#upgrade-decision-matrix)

---

## Cost Tier Ladder

### Tier 0: $0/month — Validate the approach

| Component | Free option |
|-----------|-------------|
| Outreach messaging | Manual DMs via personal accounts |
| Community engagement | Organic posting in FB groups, Telegram, WhatsApp |
| Content creation | Agent-generated graphics, copy, and video scripts |
| Email outreach | Personal email + free SMTP (Gmail, Outlook) |
| SEO content | Self-published blog on GitHub Pages or Hashnode |
| Lead tracking | JSONL files via pipeline.py |
| Analytics | run_stats.jsonl + agent-generated reports |
| Social media management | Direct platform posting |
| Landing page | GitHub Pages, Vercel free tier |

### Tier 1: $0-50/month — First paid tools

| Component | Paid option | Cost | When to upgrade |
|-----------|-------------|------|-----------------|
| Email outreach | Resend API | $0-20/mo | >3,000 emails/month |
| Social scheduling | Buffer free → paid | $15/mo | >3 platforms, >10 posts/day |
| Ad spend | Facebook/Instagram ads | $5-20/day | Response rate >15% proven |
| Domain + landing | Custom domain | $12/year | Brand credibility needed |

### Tier 2: $50-200/month — Growth mode

| Component | Paid option | Cost | When to upgrade |
|-----------|-------------|------|-----------------|
| Ad spend | Multi-platform ads | $100-150/mo | CAC <$10 proven |
| Influencer partnerships | Micro-influencer fees | $50-100/mo | Volume >$100K/month |
| Email marketing | Resend Pro or Mailgun | $25/mo | >10K emails/month |
| CRM | HubSpot free → starter | $50/mo | >500 active leads |
| Analytics | Mixpanel free tier | $0-25/mo | Need funnel analytics |

### Tier 3: $200+/month — Scale mode (justified by revenue)

| Component | Paid option | Cost | When to upgrade |
|-----------|-------------|------|-----------------|
| Ad spend | Professional campaigns | $500+/mo | Revenue covers 3x ad spend |
| Influencer partnerships | Established creators | $200+/mo | Proven ROI per influencer |
| Conference attendance | Event tickets + travel | Variable | B2B pipeline needs acceleration |
| PR/Media | Press outreach service | $200/mo | Ready for mainstream coverage |

---

## Component Cost Map

| Component | Role | Free option | Paid option | Paid cost |
|-----------|------|-------------|-------------|-----------|
| Lead discovery | Find communities/partners | Web search, manual browsing | Firecrawl search | $0 (MCP) |
| Outreach templates | Generate messages | outreach_engine.py | — | $0 |
| Email delivery | Send outreach emails | Personal email | Resend API | $20/mo |
| Social posting | Publish content | Direct platform posting | Buffer/Hootsuite | $15/mo |
| Ad campaigns | Paid acquisition | — | FB/Instagram/TikTok Ads | Variable |
| Content creation | Graphics, copy, video | Agent-generated | Canva Pro | $13/mo |
| SEO | Organic search traffic | Agent-written content | Ahrefs/SEMrush | $99/mo |
| Landing page | Convert visitors | GitHub Pages | Vercel Pro | $20/mo |
| CRM | Manage relationships | pipeline.py JSONL | HubSpot | $50/mo |
| Analytics | Track performance | run_stats.jsonl | Mixpanel | $25/mo |
| Video editing | Create demo videos | FFmpeg + agent | — | $0 |
| Translation | Multi-language content | Agent translation | DeepL Pro | $25/mo |

---

## Upgrade Decision Matrix

| Trigger | Current tier | Upgrade to | Justification |
|---------|-------------|------------|---------------|
| >100 outreach emails/week | Tier 0 | Tier 1 | Gmail daily limits, need tracking |
| Response rate >15% on ads | Tier 1 | Tier 2 | Proven ROI, scale the channel |
| >500 leads in pipeline | Tier 1 | Tier 2 | JSONL management gets unwieldy |
| Monthly volume >$100K | Tier 2 | Tier 3 | Revenue justifies professional tools |
| Revenue >$1,500/month (1.5% of $100K) | Tier 2 | Tier 3 | Self-sustaining growth budget |
| B2B partner requests professional materials | Any | Tier 2+ | Credibility requires investment |

### Cost tracking in output

Every report must include:

```json
{
  "cost": {
    "tier": 0,
    "monthly_spend_usd": 0.00,
    "breakdown": {
      "ads": 0, "tools": 0, "influencers": 0, "events": 0
    },
    "revenue_this_period": 0,
    "roi": null
  }
}
```
