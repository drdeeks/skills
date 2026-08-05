#!/usr/bin/env bash
# watchdog.sh -- keeps the guardrail watcher (monitor.py) scanning forever.
#
# Self-resolving (FOREVER-SYSTEM.md Sec 2 -- env override -> home default ->
# built-in default, resolved fresh on every call, no hardcoded absolutes):
#   1. $GUARDRAIL_SKILLS_ROOT   -- explicit override
#   2. this script's own location: <skills-root>/guardrail-enforcement/scripts/watchdog.sh
#      -> skills-root is two directories up from here
# Fails closed if neither resolves to a real .monitor.json.
#
# $GUARDRAIL_SCAN_INTERVAL (seconds, default 900 = 15 min) controls the loop
# period. This script IS the watchdog -- it never exits on a single failed
# scan (a bad scan is logged and retried next interval), so the only thing
# an outer supervisor (e.g. systemd Restart=always) needs to handle is the
# process dying outright, not routine transient failures.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
    cat <<EOF
usage: watchdog.sh [--help] [--dry-run] [--once]

Runs monitor.py scan in a loop forever, self-resolving the skills repo root
and honoring version bumps as they happen.

Environment:
  GUARDRAIL_SKILLS_ROOT    Override the skills repo root (default: auto-detect
                           from this script's own location).
  GUARDRAIL_SCAN_INTERVAL  Seconds between scans (default: 900).

Options:
  --dry-run   Resolve paths, print the plan, run one scan with monitor.py's
              own --dry-run (fires nothing), then exit -- no loop.
  --once      Run exactly one real scan and exit (no loop). For cron/manual use.
  --help      Show this help message.
EOF
}

DRY_RUN=false
ONCE=false
for arg in "$@"; do
    case "$arg" in
        -h|--help) usage; exit 0 ;;
        --dry-run) DRY_RUN=true ;;
        --once) ONCE=true ;;
        *) echo "error: unrecognized argument: $arg" >&2; usage >&2; exit 2 ;;
    esac
done

resolve_skills_root() {
    if [[ -n "${GUARDRAIL_SKILLS_ROOT:-}" ]]; then
        if [[ -f "${GUARDRAIL_SKILLS_ROOT}/.monitor.json" ]]; then
            printf '%s\n' "$GUARDRAIL_SKILLS_ROOT"
            return 0
        fi
        echo "error: \$GUARDRAIL_SKILLS_ROOT is set to '${GUARDRAIL_SKILLS_ROOT}' but no .monitor.json there." >&2
        return 1
    fi
    local candidate
    candidate="$(cd "$SCRIPT_DIR/../.." && pwd)"
    if [[ -f "$candidate/.monitor.json" ]]; then
        printf '%s\n' "$candidate"
        return 0
    fi
    echo "error: could not find .monitor.json at '${candidate}' (this script's own" \
         "skills-root guess) and \$GUARDRAIL_SKILLS_ROOT is unset. Run" \
         "'monitor.py setup' in the skills repo first, or set" \
         "\$GUARDRAIL_SKILLS_ROOT explicitly." >&2
    return 1
}

SKILLS_ROOT="$(resolve_skills_root)" || exit 1
INTERVAL="${GUARDRAIL_SCAN_INTERVAL:-900}"
MONITOR_PY="$SKILLS_ROOT/guardrail-enforcement/scripts/monitor.py"
CONFIG="$SKILLS_ROOT/.monitor.json"

if [[ ! -f "$MONITOR_PY" ]]; then
    echo "error: monitor.py not found at $MONITOR_PY" >&2
    exit 1
fi

echo "watchdog.sh: skills root = $SKILLS_ROOT"
echo "watchdog.sh: scan interval = ${INTERVAL}s"

if $DRY_RUN; then
    echo "[DRY RUN] would loop: python3 \"$MONITOR_PY\" scan --config \"$CONFIG\" every ${INTERVAL}s"
    python3 "$MONITOR_PY" scan --config "$CONFIG" --dry-run
    exit 0
fi

run_scan() {
    if ! python3 "$MONITOR_PY" scan --config "$CONFIG"; then
        echo "watchdog.sh: scan failed (exit $?) -- will retry next interval" >&2
    fi
}

if $ONCE; then
    run_scan
    exit 0
fi

echo "watchdog.sh: starting scan loop (pid $$)"
while true; do
    run_scan
    sleep "$INTERVAL"
done
