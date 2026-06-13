# Audience Discovery & Global Market Investigation

Methods for proactively discovering new audiences, untapped corridors, and partnership opportunities. Load when the decision engine fires EXPAND or when manually seeking new markets.

## Table of Contents

1. [Discovery Methods](#discovery-methods)
2. [Audience Profiling Framework](#audience-profiling-framework)
3. [Global Market Signals](#global-market-signals)
4. [Unconventional Audience Angles](#unconventional-audience-angles)

---

## Discovery Methods

### Method 1: Corridor volume scanning

Run `market_scanner.py corridors` to rank all corridors by score. Cross-reference with:
- World Bank bilateral remittance matrix (updated annually)
- KNOMAD remittance data
- Central bank reports from destination countries

Look for corridors where: high volume + high incumbent fees + low competition + good gift card infrastructure.

### Method 2: Community platform mining

For each potential corridor, systematically discover communities:

1. **Facebook:** Search "[nationality] in [country]", "[nationality] abroad", "[nationality] expats"
2. **Telegram:** Search expat keywords in Telegram search, join and evaluate activity level
3. **Reddit:** Search r/[country]expats, r/remittance, r/personalfinance[country]
4. **WhatsApp:** Ask existing community members to invite to relevant groups (organic discovery)
5. **Discord:** Search crypto/DAO servers for "payout", "compensation", "bounty" channels
6. **Forums:** Search expatforum.com, internations.org for active communities

**Qualification criteria for communities:**
- >500 members (viable reach)
- Active posting (>5 posts/day)
- Remittance-related discussions exist
- Admin is contactable

### Method 3: B2B target scanning

Use web search to find:
- "crypto payroll platform" — identify payroll companies accepting crypto
- "DAO contributor compensation" — find DAOs discussing payout friction
- "global freelance platform crypto" — find platforms needing offramps
- "[company] partnership page" — verify partnership program exists

### Method 4: Competitor user analysis

Monitor competitors' communities and reviews:
- Western Union / MoneyGram app store reviews (1-2 star reviews reveal pain points)
- Wise community forum complaints
- Remitly subreddit discussions
- Twitter complaints about remittance fees

These users are warm leads — they're already looking for alternatives.

### Method 5: News and trend monitoring

Track events that create remittance demand spikes:
- Natural disasters in recipient countries (urgent family support)
- Currency crises (Argentina, Nigeria, Lebanon — demand for stable value)
- Policy changes (new regulations, remittance taxes, capital controls)
- Seasonal patterns (holidays, back-to-school, harvest season)
- New gift card retailer launches in target countries

---

## Audience Profiling Framework

For each discovered audience segment, build a profile:

```json
{
  "segment_name": "",
  "corridor": "",
  "size_estimate": 0,
  "avg_monthly_remittance_usd": 0,
  "frequency": "weekly | biweekly | monthly | quarterly",
  "current_provider": "",
  "current_fee_pct": 0.0,
  "pain_points": [],
  "digital_literacy": "low | medium | high",
  "preferred_channels": [],
  "preferred_languages": [],
  "gift_card_preference": [],
  "crypto_familiarity": "none | basic | intermediate | advanced",
  "decision_maker": "sender | recipient | both",
  "best_outreach_time": "",
  "cultural_considerations": "",
  "estimated_cac_usd": 0.0,
  "estimated_ltv_usd": 0.0
}
```

---

## Global Market Signals

### High-opportunity indicators

| Signal | Why it matters | How to detect |
|--------|---------------|---------------|
| High incumbent fees (>5%) | Largest fee savings = strongest value prop | World Bank remittance prices database |
| Low digital competition | Less noise, easier to acquire users | Search for digital remittance in corridor |
| Gift card infrastructure | Gift card offramp actually works | Check Tango/Reloadly catalog for country |
| High smartphone penetration | Recipients can claim digitally | ITU/GSMA mobile data |
| Young sender demographics | More open to crypto/digital solutions | Census data for diaspora populations |
| Crypto-friendly regulations | Fewer compliance barriers | Regulatory landscape analysis |
| Currency instability | Creates demand for value preservation | FX volatility data |
| Large diaspora concentration | Dense audience for targeted outreach | Migration statistics |

### Seasonal demand patterns

| Period | Corridors affected | Reason |
|--------|-------------------|--------|
| December-January | All | Holiday remittances, New Year gifts |
| March-April | India, Pakistan | Ramadan/Eid + Hindu festivals |
| May | Philippines, Mexico | Mother's Day (massive in these cultures) |
| June-August | Latin America | Back-to-school season |
| October-November | India | Diwali, Dussehra |
| Year-round (25th-1st) | All blue-collar corridors | Salary day → immediate remittance |

---

## Unconventional Audience Angles

Beyond traditional migrant worker corridors:

### 1. International students
- Parents send tuition + living expenses
- High transaction values ($500-2000)
- Tech-savvy, low friction to adopt
- Channels: University international student offices, student FB groups

### 2. Digital nomads
- Receive payments from multiple countries
- Need flexible offramps in various locations
- Channels: Nomad List, r/digitalnomad, DN community Slacks

### 3. Cross-border e-commerce sellers
- Receive payments from international customers
- Need fast conversion to local spending value
- Channels: Amazon seller forums, Shopify communities

### 4. NGOs and aid organizations
- Distribute micro-grants and aid payments globally
- Gift card option = instant verifiable value delivery
- Channels: Direct outreach to program officers, UN agency contacts

### 5. Gaming and creator economy
- International gamers paying each other, creators receiving tips
- Small transactions but high frequency
- Channels: Twitch, YouTube, gaming Discord servers

### 6. Family support for elderly
- Explicitly target the "mother in the village" use case
- Gift card = no bank needed, no crypto knowledge
- Channels: Through the sender (children/grandchildren)

### 7. Emergency/disaster response
- Instant value delivery when banking infrastructure is down
- Gift cards provide immediate purchasing power
- Channels: Diaspora crisis response groups, Red Cross partnerships
