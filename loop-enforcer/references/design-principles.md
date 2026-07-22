# Design Principles

## 1. Additive Only

The chain enforces that work is additive. No step may delete, overwrite, or destroy work from a previous step. If a step needs to modify something a previous step created, it must be done through append or augmentation, not replacement.

## 2. Verification Before Progression

No step completes without verification. Even without a validator script, the act of running `verify` creates an explicit confirmation gate. This prevents "fire and forget" where an agent writes a file and moves on without checking.

## 3. Atomic State

State writes use atomic file replacement (write to tmp, then rename). This prevents corruption if the process crashes mid-write. The state file is always either fully old or fully new, never half-written.

## 4. Full Audit Trail

Every state change is logged with a timestamp. The log is append-only. This provides a complete history of what happened, when, and in what order.

## 5. Agent-Agnostic

The chain doesn't care which agent is working. It's a file-based coordination mechanism. Any process that can read/write files and run shell commands can participate.

## 6. Fail-Safe Defaults

- Step 0 is always immediately active (no chicken-and-egg problem)
- If no validator is set, verification auto-passes (with a warning)
- Locked steps return clear error messages, not silent failures
- State is JSON (human-readable, debuggable)

## Chain Enforcer Patterns That Work

| Pattern | Use Case |
|---|---|
| Sequential build | src/config → src/db → src/api → src/routes |
| TDD pairs | src/utils.js → tests/utils.test.js → src/db.js → tests/db.test.js |
| Blueprint phases | phase1.md → phase2.md → phase3.md (with phase validators) |
| Additive enforcement | Validator checks git diff for deletions on completed steps |

## Files That Embody These Principles

- `scripts/validate.py` — unified validator with all checks composable
- `scripts/chain.py` — enforcement engine with atomic state + audit log
- `references/agent-integration.md` — agent MUST check before write
- `references/lessons/` — the operational incidents that produced each principle above
