---
description: Patterns for making bash scripts resilient under set -euo pipefail, particularly
  batch loops, backup operations, and multi-agent config generation.
metadata:
  hermes:
    related_skills:
    - systematic-debugging
    - multi-agent-manager
    tags:
    - bash
    - scripting
    - error-handling
    - multi-agent
    - openclaw
name: bash-set-e-resilience
---

# Bash set -euo Pipefail Resilience

## The Problem

`set -euo pipefail` makes bash strict — any command returning non-zero kills the script. This is good for catching errors but breaks batch operations where one failure shouldn't stop the rest.

## Pattern 1: Loop body extraction

**Problem:** `set -e` kills the `for` loop on first agent failure.

```bash
# BAD — set -e kills loop on first failure
for agent in "${agents[@]}"; do
    backup_file "$agent" /tmp/backup     # if cp fails, loop dies
    generate_config "$agent"             # never reached
done
```

**Fix:** Extract body to a function, wrap with `||`:

```bash
# GOOD — each agent isolated
_process_agent() {
    local agent="$1"
    backup_file "$agent" /tmp/backup
    generate_config "$agent"
    return 0
}

for agent in "${agents[@]}"; do
    _process_agent "$agent" || { warn "Failed: ${agent}, continuing..."; continue; }
done
```

The function call returns non-zero on failure, `||` catches it, `continue` moves to next agent.

## Pattern 2: Resilient backup operations

**Problem:** `cp -a` fails on permission/disk, `set -e` kills script.

```bash
# BAD
run cp -a "$src/." "$dest/" 2>/dev/null    # if cp fails, script exits

# GOOD — if-then with warning, no exit
if run cp -a "$src/." "$dest/" 2>/dev/null; then
    log "Backed up"
else
    warn "Backup failed (continuing)"
fi
```

Also apply to `rsync`, `mv`, `mkdir -p` in backup paths.

## Pattern 3: Safe prompt under set -e

**Problem:** `prompt_yn` returns 1 on "no", `set -e` exits.

```bash
# BAD
prompt_yn "Proceed?" "n"     # user says "n", returns 1, script exits

# GOOD — || short-circuit
prompt_yn "Proceed?" "n" || { info "Aborted."; return 0; }

# BETTER — safe wrapper that checks --yes flag
safe_prompt_yn() {
    if [ "$NO_CONFIRM" = true ]; then return 0; fi
    prompt_yn "$@"
}
safe_prompt_yn "Proceed?" "n" || { info "Aborted."; return 0; }
```

## Pattern 4: Heredoc file writes with dry-run

**Problem:** Heredoc writes happen even in dry-run mode.

```bash
# BAD — heredoc always writes
{ cat << EOF
config content
EOF
} > "$file"

# GOOD — guard with if
if [ "$DRY_RUN" = false ]; then
    { cat << EOF
config content
EOF
    } > "$file"
else
    echo "[dry-run] Would write $file"
fi
```

## Pattern 5: Incomplete config detection

**Problem:** Checking `[ -f "$file" ] && [ -s "$file" ]` only checks existence + non-empty. Stub files with `# TODO` pass this check.

```bash
# BAD — passes on stub files
if [ ! -f "$file" ] || [ ! -s "$file" ]; then
    generate_config
fi

# GOOD — check for required content
has_model=false
if [ -f "$file" ]; then
    grep -q "^model:" "$file" 2>/dev/null && has_model=true
fi

if [ ! -f "$file" ] || [ ! -s "$file" ] || [ "$has_model" = false ]; then
    generate_config
fi
```

## OpenClaw Multi-Agent Config Format

Correct format from docs.openclaw.ai:

```json5
{
  "agents": {
    "defaults": {
      "workspace": "${OPENCLAW_WORKSPACE}"
    },
    "list": [
      { "id": "titan" },
      { "id": "avery", "skills": ["creative"] },  // overrides defaults
      { "id": "allman" }  // inherits defaults
    ]
  },
  "channels": {
    "telegram": {
      "accounts": {
        "titan": { "botToken": "...", "dmPolicy": "pairing" },
        "avery": { "botToken": "...", "dmPolicy": "pairing" }
      }
    }
  },
  "bindings": [
    { "agentId": "titan", "match": { "channel": "telegram", "accountId": "titan" } }
  ]
}
```

Key fields:
- `agents.list[].id` — NOT `agentId` or `name`
- `agents.list[].skills` — replaces defaults, doesn't merge
- `channels.telegram.accounts.<id>.botToken` — per-account tokens
- `bindings[].match.accountId` — routes account to agent
- No `agentDir` or `workspace` per agent — all share `agents.defaults.workspace`

## Pattern 6: Arithmetic increment with set -e

**Problem:** `(( VAR++ ))` returns exit code 1 when the variable is 0 (post-increment returns the original value, and `(( 0 ))` is falsy in bash). With `set -e`, this kills the script.

```bash
# BAD — kills script when OK_COUNT is 0
OK_COUNT=0
(( OK_COUNT++ ))    # returns 1 (the pre-increment value), set -e exits

# BAD — same issue with pre-increment from 0
(( ++OK_COUNT ))    # actually works, but confusing

# GOOD — arithmetic assignment, always returns 0
OK_COUNT=$((OK_COUNT + 1))

# ALSO OK — || true suppresses the exit
(( OK_COUNT++ )) || true
```

**Where this hides:** Counter variables in loops, especially `OK_COUNT`, `ERRORS`, `copied`, `total` — anywhere you start at 0 and increment.

## Pattern 7: Grep patterns with special characters

**Problem:** `***` is NOT "match anything" in regex. It means "zero or more literal asterisks." In unquoted bash, it's also a file glob that expands to filenames containing asterisks.

```bash
# BROKEN — *** is "zero or more asterisks" in regex
grep -cE "^TELEGRAM_BOT_TOKEN=*** "$ENV_FILE"

# BROKEN — *** expands as file glob (unquoted)
grep -cE "^KEY=*** " $FILE

# FIXED — .+ for non-empty value, .* for any value
grep -cE '^TELEGRAM_BOT_TOKEN=.+' "$ENV_FILE"
grep -cE '^KEY=.*' "$FILE"
```

**Rule:** Use single quotes for grep regex patterns to prevent both shell expansion and confusion. Use `.+` for "non-empty" and `.*` for "any value (including empty)."

## Pattern 8: set +e / set -e toggle for command capture

**Problem:** You need to capture a command's exit code AND output, but `set -e` kills the script if the command fails.

```bash
# BAD — if check_services.sh exits 1, the whole heartbeat dies
OUTPUT=$(bash check_services.sh 2>&1)

# GOOD — toggle set -e around the capture
set +e
OUTPUT=$(bash check_services.sh 2>&1)
EXIT_CODE=$?
set -e
echo "$OUTPUT"
# Now you can inspect EXIT_CODE without dying
```

## Pattern 9: Unquoted variables in [ test expressions

**Problem:** `[ $var -gt 0 ]` fails with "too many arguments" when `$var` is empty or contains spaces. Bash splits the value into multiple words.

```bash
# BROKEN — if $has_token is empty or has spaces, [ gets wrong arg count
has_token=$(grep -cE '^TOKEN=.+' "$FILE" || echo 0)
[ $has_token -gt 0 ]    # works if has_token="0", fails if somehow empty

# BROKEN — even worse with piped output that might have trailing whitespace
errors=$(some_command | wc -l)
[ $errors -gt 0 ]    # "too many arguments" if wc output has spaces

# FIXED — always quote variable in test expressions
[ "$has_token" -gt 0 ]
[ "$errors" -gt 0 ]
```

**Rule:** Always quote variables inside `[ ... ]` test brackets. No exceptions.

## Pattern 10: Hex-level verification for debugging

**Problem:** Terminal rendering can display characters differently than their actual bytes. `.+` may render as `***` in some fonts/terminals, making grep pattern debugging unreliable.

```bash
# Terminal shows: BOT_TOKEN=*** "$ENV_FILE"
# Actual bytes:   BOT_TOKEN=.+ "$ENV_FILE"    (0x2e 0x2b)

# WRONG — trusting terminal display
grep -n '\*\*\*' script.sh    # finds nothing (file has .+ not ***)
sed -n '958p' script.sh       # shows *** (terminal rendering lies)

# RIGHT — check raw bytes
python3 -c "
with open('script.sh', 'rb') as f:
    lines = f.readlines()
line = lines[957]
idx = line.find(b'BOT_TOKEN')
chunk = line[idx:idx+20]
print('Hex:', ' '.join(f'{b:02x}' for b in chunk))
print('ASCII:', ''.join(chr(b) if 32<=b<127 else f'0x{b:02x}' for b in chunk))
"
# Hex:   42 4f 54 5f 54 4f 4b 45 4e 3d 2e 2b 27
# ASCII: B  O  T  _  T  O  K  E  N  =  .  +  '
# Proof: bytes 0x2e 0x2b = .+ (correct), NOT ***
```

**When to use hex verification:**
- Grep `pattern` returns no matches but `sed`/`head` shows the pattern
- `patch` tool shows different content than `cat`/`sed`
- File bytes might contain Unicode lookalikes (e.g., fullwidth asterisks)
- Debugging regex patterns that don't match when they should

## Pattern 9: Unquoted variables in [ test expressions

**Problem:** `[ $var -gt 0 ]` fails with "too many arguments" when `$var` is empty or contains spaces. Bash splits the value into multiple words.

```bash
# BROKEN — if $has_token is empty or has spaces, [ gets wrong arg count
has_token=$(grep -cE '^TOKEN=.+' "$FILE" || echo 0)
[ $has_token -gt 0 ]    # works if has_token="0", fails if somehow empty

# BROKEN — even worse with piped output that might have trailing whitespace
errors=$(some_command | wc -l)
[ $errors -gt 0 ]    # "too many arguments" if wc output has spaces

# FIXED — always quote variable in test expressions
[ "$has_token" -gt 0 ]
[ "$errors" -gt 0 ]
```

**Rule:** Always quote variables inside `[ ... ]` test brackets. No exceptions.

## Pattern 10: Hex-level verification for debugging

**Problem:** Terminal rendering can display characters differently than their actual bytes. `.+` may render as `***` in some fonts/terminals, making grep pattern debugging unreliable.

```bash
# Terminal shows: BOT_TOKEN=*** "$ENV_FILE"
# Actual bytes:   BOT_TOKEN=.+ "$ENV_FILE"    (0x2e 0x2b)

# WRONG — trusting terminal display
grep -n '\*\*\*' script.sh    # finds nothing (file has .+ not ***)
sed -n '958p' script.sh       # shows *** (terminal rendering lies)

# RIGHT — check raw bytes
python3 -c "
with open('script.sh', 'rb') as f:
    lines = f.readlines()
line = lines[957]
idx = line.find(b'BOT_TOKEN')
chunk = line[idx:idx+20]
print('Hex:', ' '.join(f'{b:02x}' for b in chunk))
print('ASCII:', ''.join(chr(b) if 32<=b<127 else f'0x{b:02x}' for b in chunk))
"
# Hex:   42 4f 54 5f 54 4f 4b 45 4e 3d 2e 2b 27
# ASCII: B  O  T  _  T  O  K  E  N  =  .  +  '
# Proof: bytes 0x2e 0x2b = .+ (correct), NOT ***
```

**When to use hex verification:**
- Grep `pattern` returns no matches but `sed`/`head` shows the pattern
- `patch` tool shows different content than `cat`/`sed`
- File bytes might contain Unicode lookalikes (e.g., fullwidth asterisks)
- Debugging regex patterns that don't match when they should

## Quick Reference

| Problem | Pattern | Example |
|---------|---------|---------|
| Loop killed by set -e | Extract to function + \| continue | `_f() { ...; }` + `_f "$x" \| warn; continue` |
| Backup fails fatally | if-then-else warn | `if cp; then log; else warn; fi` |
| Prompt kills on no | \| abort | `prompt_yn "x" \| { return 0; }` |
| Heredoc writes in dry-run | if DRY_RUN guard | `if [ "$DRY_RUN" = false ]; then { ... } > file; fi` |
| Stub files pass checks | Check content not just size | `grep -q "^model:" "$file"` |
| Counter increment kills script | Use `$((VAR + 1))` | `OK_COUNT=$((OK_COUNT + 1))` |
| Grep `***` broken regex | Use `.+` or `.*` | `grep -E '^KEY=.+'` |
| Command fails during capture | `set +e` / `set -e` toggle | `set +e; OUT=$(cmd); RC=$?; set -e` |
| `[ $var` too many arguments | Always quote: `["$var"` | `[ "$errors" -gt 0 ]` |
| Terminal lies about bytes | Hex verification | `python3 -c "open(f,'rb')..."` |
| `[ $var` too many arguments | Always quote: `["$var"` | `[ "$errors" -gt 0 ]` |
| Terminal lies about file contents | Hex verification with python3 | `python3 -c "open(f,'rb').read()"` |