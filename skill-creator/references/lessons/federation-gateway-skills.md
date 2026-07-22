---
title: Coordination-gateway skill scaffolding — server stability and scope boundaries
category: scaffolding
failure: While building the autonomous-federation skill, a persistent server was launched under `timeout`, which killed it (exit 124), and the federation server's role was initially conflated with the individual project implementations it coordinates
root_cause: timeout is meant for finite commands, not long-running servers; and a coordination gateway (join/discovery/routing) is architecturally distinct from the things it coordinates
resolution: Ran the server directly in the background instead of under timeout, added a mandatory fast-returning /health endpoint, and treated the federation server strictly as a gateway — each coordinated project keeps its own agent logic
prevention: Persistent servers scaffolded by a skill must never be wrapped in timeout; must expose a fast /health endpoint; port conflicts (EADDRINUSE) should be treated as routine (kill by port/process name before restart, not treated as a fatal error)
date: 2026-07-04
verified: true
---

Session: building the autonomous-federation skill for hackathon-2026 workspace
consolidation.

**Scope boundary:** the federation server is a coordination gateway (MCP join endpoint,
project discovery, shared memory bus, work-assignment routing, WebSocket hub) — it does
NOT replace individual project implementations. Each coordinated track still needs its
own agent logic; the federation skill only lets agents find and join them. Spawning
sub-agents to actually implement coordinated projects is separate delegation work, not
part of the federation skill itself.

**Scaffolding checklist for this class of skill:** template `server.js` needs health,
discovery, join, work-assignment, status, stats, and WebSocket/memory endpoints;
`package.json` needs its runtime dependencies (`express`, `ws`); include identity/memory
templates; scaffold script should create the memory directory structure the server
expects (`memory/{daily,entities,templates}`).

**Memory architecture integration:** a layered memory bus (knowledge graph + daily notes
+ long-term + identity) must be seeded with the relevant entities, searchable, indexed
for semantic recall, and loadable on startup — not bolted on after the fact.
