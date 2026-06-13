# Credential Bootstrap & Self-Registration

How the agent autonomously creates and manages accounts on outreach platforms. Load when setting up new channels or onboarding to new platforms.

## Table of Contents

1. [Self-Registration Protocol](#self-registration-protocol)
2. [Platform Account Matrix](#platform-account-matrix)
3. [Credential Management](#credential-management)
4. [Account Warming](#account-warming)

---

## Self-Registration Protocol

### General procedure

1. Navigate to platform signup page (use `playwright-cli` skill or manual browser)
2. Create account with professional identity:
   - Name: "Email Remittance Pro" or "[Corridor] Remittance Advisor"
   - Email: Use dedicated outreach email (e.g., outreach@emailremittancepro.com)
   - Bio: Clear, professional description of service
3. Complete email verification
4. Set up profile with professional photo/logo and service description
5. Store credentials securely in `state/credentials.json` (encrypted)
6. Begin account warming period before any outreach (see Account Warming)

### Rules

- **One primary + one backup account per platform** — never more
- **Never misrepresent identity** — always identify as Email Remittance Pro
- **Follow all platform Terms of Service** — no fake accounts, no impersonation
- **Disclose commercial intent** — when required by platform rules
- **Separate personal and business** — use dedicated business accounts only

---

## Platform Account Matrix

| Platform | Account type | Registration URL | Warming period | Daily limits |
|----------|-------------|-----------------|----------------|--------------|
| Facebook | Business Page | business.facebook.com | 1 week | 20 group joins/day, 50 DMs/day |
| Instagram | Business | instagram.com/accounts/signup | 1 week | 30 follows/day, 20 DMs/day |
| Twitter/X | Standard | twitter.com/i/flow/signup | 3 days | 50 tweets/day, 500 DMs/day |
| Telegram | Standard | telegram.org | 1 day | 20 groups/day, 50 DMs/day |
| LinkedIn | Business | linkedin.com/signup | 1 week | 20 connections/day, 25 InMails/mo |
| Discord | Standard | discord.com/register | 1 day | 10 servers/day |
| Reddit | Standard | reddit.com/register | 2 weeks | 5 posts/day, 10 comments/day |
| TikTok | Business | tiktok.com/signup | 3 days | 3 videos/day |
| YouTube | Brand | youtube.com | 1 day | 1 video/day |
| Viber | Standard | viber.com | 1 day | Unlimited groups |

### Required platform accounts (priority order)

1. **Facebook** — Largest expat community platform
2. **WhatsApp Business** — Highest conversion channel for B2C
3. **Telegram** — Worker communities in Gulf states
4. **Twitter/X** — B2B/crypto community engagement
5. **Instagram** — Visual storytelling for B2C
6. **LinkedIn** — B2B partnership outreach
7. **TikTok** — Viral content potential
8. **Discord** — DAO/crypto community engagement
9. **YouTube** — Demo and tutorial hosting
10. **Reddit** — Long-form community engagement

---

## Credential Management

### Storage format

```json
{
  "platform": "facebook",
  "account_type": "primary",
  "username": "",
  "email": "",
  "created_at": "ISO8601",
  "warming_complete": false,
  "warming_complete_at": null,
  "status": "active | warming | suspended | banned",
  "daily_actions_today": 0,
  "daily_limit": 50,
  "last_action_at": null,
  "notes": ""
}
```

### Security rules

- Never store passwords in plaintext — use environment variables or encrypted config
- Rotate credentials if any compromise suspected
- Use 2FA on all accounts where available
- Keep backup email for account recovery
- Document all accounts in `state/credentials.json` (metadata only, no passwords)

---

## Account Warming

Before any outreach activity, accounts must be "warmed" to avoid platform flags.

### Warming schedule

| Day | Activity | Purpose |
|-----|----------|---------|
| 1 | Complete profile (photo, bio, links) | Establish legitimacy |
| 2-3 | Follow/join 5 relevant accounts/groups | Show organic interest |
| 4-5 | Like/react to 10 posts per day | Build engagement history |
| 6-7 | Comment on 5 posts per day (genuine, relevant) | Demonstrate authentic participation |
| 8-10 | Share 2 value-add posts (no promotion) | Establish content pattern |
| 11-14 | Start organic engagement with target communities | Test platform response |
| 15+ | Begin outreach at 25% of daily limits, gradually increase | Ramp up safely |

### Warming rules

- Never skip warming — cold accounts get flagged immediately
- Increase activity by max 25% per week
- If any warning/restriction received, reduce activity by 50% for 1 week
- Monitor account health indicators (reach, engagement, restrictions)
- Keep engagement authentic — never use bots or automation that violates ToS
