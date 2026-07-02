# Phase Definition Template

Use this template for each implementation phase in the blueprint.

---

### PHASE-N: <Phase Title> (Week X) — <Focus>
> **Rollback Tag:** `[PHASE-N-v1]`
> **Prerequisites:** PHASE-(N-1) complete, <feature flags>
> **Feature Flags:** FEAT_*, FEAT_*

- [ ] **PHASE-N.1** <Task description> → <script.py>
- [ ] **PHASE-N.2** <Task description> → <script.sh>
- [ ] **PHASE-N.3** <Task description> → <script.py>
- [ ] **PHASE-N.4** <Task description>
- [ ] **PHASE-N.5** Validation gate: <command> → <expected output>

---

**Exit Criteria:** `<verifiable outcome>`

**Rollback Procedure:** `Disable FEAT_* → revert <script> → <recovery command>`

---

## Example: PHASE-7

### PHASE-7: Safety, Logging & Database Foundation (Week 4) — Core Infrastructure
> **Rollback Tag:** `[PHASE-7-v1]`
> **Prerequisites:** PHASE-6 complete, FEAT_SAFETY_LIB, FEAT_LOGGING_SYSTEM, FEAT_DATABASE
> **Feature Flags:** FEAT_SAFETY_LIB, FEAT_LOGGING_SYSTEM, FEAT_DATABASE

- [ ] **PHASE-7.1** Implement safety library (`/scripts/safety.sh`): `safe_command`, `safe_command_with_retry`, atomic file ops, lock manager, port allocator, rollback stack
- [ ] **PHASE-7.2** Implement logging system (`/scripts/logging.sh`): `log`, `log_json`, `audit_log`, `record_agent_action`, `spin`, `progress_bar`, `dry_run_log`
- [ ] **PHASE-7.3** Implement database module (`/scripts/database.sh`): SQLite/JSON backend, agent/crew/message schemas, registry sync, migration runner
- [ ] **PHASE-7.4** Validation gate: Run health checks → safety commands execute with timeout/retry → logs written as JSONL → database initializes with schema

---

**Exit Criteria:** `hemlock safety-check` → all checks pass → `hemlock log tail` shows JSON logs → `hemlock db status` shows schema

**Rollback Procedure:** Disable FEAT_SAFETY_LIB/FEAT_LOGGING_SYSTEM/FEAT_DATABASE → revert safety.sh/logging.sh/database.sh