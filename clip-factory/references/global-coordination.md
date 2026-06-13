# Global Coordination & Niche Collision Prevention
## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Global Registry Schema](#global-registry-schema)
- [Coordination Protocol](#coordination-protocol)
- [Stale Agent Pruning](#stale-agent-pruning)
- [Coordination Log](#coordination-log)
- [Niche Availability Query](#niche-availability-query)
- [Integration with Decision Engine](#integration-with-decision-engine)
- [Scaling the Max-Per-Niche Limit](#scaling-the-max-per-niche-limit)


## Overview

When multiple clip-factory agents run independently (up to 25+ instances), they MUST coordinate to prevent niche over-saturation. The global registry on MuleRun Drive acts as a distributed coordination layer — every agent checks in before claiming a niche, and no more than 2 agents may operate in the same niche simultaneously.

## Architecture

```
MuleRun Drive (shared cloud storage)
└── /clip-factory/
    ├── global-registry.json     ← Niche claims, agent heartbeats, locks
    ├── niche-catalog.json       ← Discovered niches (proactive scouting)
    └── coordination-log.jsonl   ← Append-only audit trail
```

All agents read/write to the same Drive path. MuleRun Drive persists across sessions and is accessible to any agent with Drive access.

## Global Registry Schema

`/clip-factory/global-registry.json`:
```json
{
  "version": 1,
  "last_updated": "ISO8601",
  "max_agents_per_niche": 2,
  "agents": {
    "agent-a1b2": {
      "instance_id": "a1b2",
      "registered_at": "ISO8601",
      "last_heartbeat": "ISO8601",
      "niches": ["podcasts", "finance"],
      "accounts_count": 4,
      "status": "active"
    },
    "agent-c3d4": {
      "instance_id": "c3d4",
      "registered_at": "ISO8601",
      "last_heartbeat": "ISO8601",
      "niches": ["streamers"],
      "accounts_count": 2,
      "status": "active"
    }
  },
  "niche_claims": {
    "podcasts": {
      "claimed_by": ["agent-a1b2"],
      "max_slots": 2,
      "available_slots": 1
    },
    "streamers": {
      "claimed_by": ["agent-c3d4"],
      "max_slots": 2,
      "available_slots": 1
    },
    "finance": {
      "claimed_by": ["agent-a1b2"],
      "max_slots": 2,
      "available_slots": 1
    },
    "reddit": {
      "claimed_by": [],
      "max_slots": 2,
      "available_slots": 2
    }
  }
}
```

## Coordination Protocol

### 1. Agent Registration (on first setup)

Every clip-factory instance MUST register before claiming any niche:

```
1. Generate a unique instance_id (8-char UUID prefix)
2. Download /clip-factory/global-registry.json from Drive
3. If file doesn't exist → create it with empty agents/niche_claims
4. Add self to agents map with status="registering"
5. Upload updated registry back to Drive
6. Append registration event to coordination-log.jsonl
```

### 2. Niche Claim (before activating a niche)

Before an agent activates a niche, it MUST check and claim a slot:

```
1. Download /clip-factory/global-registry.json (fresh copy)
2. Prune stale agents: any agent with last_heartbeat > 2 hours ago → remove from claims
3. Check niche_claims[niche].claimed_by → count active claimants
4. IF count >= max_agents_per_niche (default 2):
   → DENY: niche is full, pick a different niche
   → Log denial to coordination-log.jsonl
   → Return list of available niches to the agent
5. IF count < max_agents_per_niche:
   → Add self to claimed_by list
   → Decrement available_slots
   → Update last_updated timestamp
   → Upload registry back to Drive
   → Append claim event to coordination-log.jsonl
   → PROCEED with niche activation
```

### 3. Heartbeat (every cron health check — hourly)

Agents send heartbeats to prove they're still alive:

```
1. Download global-registry.json
2. Update self: last_heartbeat = now
3. Prune any agent with last_heartbeat > 2 hours → release their niche claims
4. Upload registry
```

### 4. Niche Release (when pivoting, killing, or shutting down)

When an agent stops working a niche:

```
1. Download global-registry.json
2. Remove self from niche_claims[niche].claimed_by
3. Increment available_slots
4. Upload registry
5. Log release event
```

### 5. Collision Resolution

If two agents try to claim the last slot simultaneously (race condition):

```
1. After uploading claim, immediately re-download registry
2. Check if niche now has > max_agents_per_niche claimants
3. If over-subscribed:
   a. Compare registration timestamps — newest agent yields
   b. Remove self from claim
   c. Upload corrected registry
   d. Select next best available niche
```

## Stale Agent Pruning

An agent is considered stale if `last_heartbeat` is older than 2 hours. Stale agents are automatically pruned by any agent that downloads the registry:

- Remove stale agent from all `niche_claims[*].claimed_by` arrays
- Recalculate `available_slots` for affected niches
- Set stale agent status to `"expired"`
- Log pruning event

This ensures that crashed or abandoned agents don't permanently block niche slots.

## Coordination Log

`/clip-factory/coordination-log.jsonl` — append-only audit trail:

```json
{"timestamp": "ISO8601", "agent": "a1b2", "event": "register", "details": {}}
{"timestamp": "ISO8601", "agent": "a1b2", "event": "claim_niche", "niche": "podcasts", "slot": "1/2"}
{"timestamp": "ISO8601", "agent": "c3d4", "event": "claim_denied", "niche": "podcasts", "reason": "2/2 slots full"}
{"timestamp": "ISO8601", "agent": "a1b2", "event": "release_niche", "niche": "podcasts", "reason": "pivot"}
{"timestamp": "ISO8601", "agent": "a1b2", "event": "heartbeat"}
{"timestamp": "ISO8601", "agent": "e5f6", "event": "pruned_stale", "stale_agent": "x7y8", "released_niches": ["streamers"]}
```

Agents upload log entries by downloading the current log, appending, and re-uploading. For high-volume coordination, the orchestrator can batch log entries.

## Niche Availability Query

Before selecting a niche (during setup or pivot), query the registry for available niches:

```python
def get_available_niches(registry):
    available = []
    for niche, info in registry["niche_claims"].items():
        slots = info.get("available_slots", info["max_slots"] - len(info["claimed_by"]))
        if slots > 0:
            available.append({
                "niche": niche,
                "available_slots": slots,
                "current_agents": len(info["claimed_by"])
            })
    return sorted(available, key=lambda n: n["available_slots"], reverse=True)
```

This is the first thing checked during the decision engine's PIVOT workflow — never pivot into a full niche.

## Integration with Decision Engine

The SCALE/PIVOT/KILL signals are now registry-aware:

| Signal | Registry Action |
|---|---|
| **SCALE** | Before adding accounts in the same niche, verify slots. If full, scale by adding a second niche instead. |
| **PIVOT** | Query available niches. Only pivot into niches with available_slots > 0. Rank by composite score × availability. |
| **KILL** | Release the niche claim. Freed slot becomes available to other agents immediately. |
| **MAINTAIN** | Send heartbeat only. No registry changes. |

## Scaling the Max-Per-Niche Limit

The `max_agents_per_niche` defaults to 2 but can be adjusted:

- For broad niches (podcasts, educational) with deep content supply → increase to 3
- For narrow niches (single creator) → keep at 1-2
- Override per-niche: set `max_slots` individually in niche_claims

The limit prevents view cannibalization — when too many clippers post the same moments from the same creator, views split and RPM drops for everyone.
