# B2B Partnership Playbook

Detailed strategies for acquiring B2B partners (DAOs, payroll platforms, freelance platforms, exchanges). Load when executing B2B campaigns or nurturing partnership leads.

## Table of Contents

1. [Partnership Value Propositions](#partnership-value-propositions)
2. [DAO Integration Playbook](#dao-integration-playbook)
3. [Payroll Platform Playbook](#payroll-platform-playbook)
4. [Freelance Platform Playbook](#freelance-platform-playbook)
5. [Exchange Partnership Playbook](#exchange-partnership-playbook)
6. [Partnership Funnel Stages](#partnership-funnel-stages)

---

## Partnership Value Propositions

### For DAOs

"Eliminate contributor payout friction. Your global contributors get paid via email and choose crypto wallet or gift card — no exchange, no bank, no KYC. 3 lines of API code. You focus on governance, we handle the last mile."

**ROI argument:** If a DAO pays 500 contributors/quarter at $500 avg, that's $250K/quarter flowing through the system. At 1% fee (with 0.5% revenue share to the DAO), the DAO earns $1,250/quarter while reducing payout support overhead.

### For payroll platforms

"Add instant gift card payouts to your platform. Your contractors in 100+ countries convert crypto earnings to Amazon, Walmart, or Visa gift cards in 30 seconds. We handle compliance, fraud, and settlement. You differentiate on payout flexibility."

**ROI argument:** Reduces contractor churn (payout friction is #2 reason contractors leave platforms). Estimated 5-15% contractor retention improvement.

### For freelance platforms

"Expand your addressable contributor pool by removing the crypto barrier. Non-crypto-native talent can now participate — they receive email, click link, get gift card. No wallet setup required."

**ROI argument:** Expands talent pool by 30-50% (non-crypto-native freelancers who currently avoid Web3 gigs).

### For exchanges

"Offer your users a no-KYC gift card offramp. Users send crypto to any email, recipient gets gift card. Regulatory lighter than fiat offramp. New revenue stream at 1% fee."

---

## DAO Integration Playbook

### Target identification

Run `market_scanner.py partnerships --type dao` to list targets ranked by treasury size and contributor count.

**Priority scoring:**
- Treasury size >$100M: +30 points
- Contributors >200: +20 points
- Active governance forum: +15 points
- Existing payout pain (evidenced by forum discussions): +25 points
- Deployed on chains we support (Celo, Base, Monad): +10 points

### Engagement sequence

1. **Week 1-2: Research** — Read the DAO's governance forum. Find discussions about contributor compensation, payout friction, or treasury management. Understand their current payout process.

2. **Week 3: Engage** — Comment thoughtfully on 3-5 governance discussions. Add value. Do NOT pitch yet. Build reputation.

3. **Week 4: Soft introduce** — In a relevant compensation discussion, mention "there are new tools for email-based payouts with gift card options" without hard pitching.

4. **Week 5: Formal proposal** — Post a governance proposal using `outreach_engine.py generate --template dao_proposal`. Include: problem statement, solution, technical integration plan, cost analysis, pilot proposal.

5. **Week 6-8: Nurture** — Respond to all questions. Offer a live demo. Provide technical documentation. Be available.

6. **Week 9-10: Pilot** — If approved, run 10-50 test transactions with real contributors. Collect feedback.

7. **Week 11+: Scale** — Present pilot results. Push for full integration vote.

### Key DAO contacts to engage

| DAO | Forum | Key roles to engage |
|-----|-------|---------------------|
| Uniswap | governance.uniswap.org | Treasury committee members, active delegates |
| Arbitrum | forum.arbitrum.foundation | Grants program leads, delegate council |
| Optimism | gov.optimism.io | RetroPGF reviewers, foundation team |
| Gitcoin | gov.gitcoin.co | Grants operations, workstream leads |
| Coordinape | Discord | Core team, active circle admins |

---

## Payroll Platform Playbook

### Target identification

Run `market_scanner.py partnerships --type payroll` to list targets.

### Engagement sequence

1. **Research phase:** Understand target's current crypto payout options. Read their docs, blog, and support forums.
2. **LinkedIn connect:** Connect with Head of Partnerships, VP Product, or CTO.
3. **Content engagement:** Like/comment on their LinkedIn posts for 2 weeks.
4. **Cold outreach:** Send personalized email using `outreach_engine.py generate --template b2b_payroll`.
5. **Follow-up cadence:** Day 0 → Day 3 → Day 7 → Day 14 → Day 30.
6. **Demo:** If response received, schedule 15-min API walkthrough.
7. **Technical trial:** Offer sandbox environment for their engineering team.
8. **Contract:** Revenue share agreement (1% fee, 50/50 split).

---

## Freelance Platform Playbook

### Engagement sequence

1. **Join their Discord/community** — Engage as a contributor first.
2. **Identify payout pain** — Find discussions about payout friction, exchange issues.
3. **Soft pitch in context** — "Have you considered gift card offramps? There's an API for this."
4. **Direct outreach** — Contact platform team via email/Discord DM.
5. **Demo** — Show the claim flow: email → click → gift card in 30 seconds.
6. **Integration** — Provide API docs, SDK, and sandbox.

---

## Exchange Partnership Playbook

### Value prop for exchanges

Exchanges are looking for differentiated fiat offramps. Gift cards via email = novel, regulatory-lighter alternative.

### Engagement strategy

1. **Apply to partnership programs** — Most major exchanges have formal partnership applications.
2. **Attend their ecosystem events** — Coinbase Developer Days, Binance Build events.
3. **Build on their chain** — If exchange has an L2 (Base for Coinbase), deploy there first.
4. **Cold email to BD team** — Use `outreach_engine.py generate --template b2b_payroll` adapted for exchanges.

---

## Partnership Funnel Stages

| Stage | Definition | Next action | Timeout |
|-------|-----------|-------------|---------|
| Identified | Target discovered and researched | Initiate engagement | — |
| Engaged | Initial contact made, in conversation | Schedule demo/call | 2 weeks |
| Demo'd | Technical walkthrough completed | Send follow-up + integration docs | 1 week |
| Piloting | Running test transactions | Collect feedback, iterate | 4 weeks |
| Negotiating | Terms discussion, contract review | Close deal | 2 weeks |
| Signed | Partnership agreement executed | Begin full integration | — |
| Live | Integration deployed, transactions flowing | Monitor + expand | Ongoing |

Track all B2B leads through these stages in `pipeline/b2b_pipeline.jsonl`.
