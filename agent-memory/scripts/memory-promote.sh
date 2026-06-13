#!/usr/bin/env bash
# =============================================================================
# memory-promote.sh — Review daily notes and promote to MEMORY.md
# =============================================================================
#
# Usage:
#   bash scripts/memory-promote.sh                  # Review today + yesterday
#   bash scripts/memory-promote.sh 2026-04-20       # Specific date
#   bash scripts/memory-promote.sh --week           # Last 7 days
#
# Shows daily notes and prompts for which entries to promote to MEMORY.md.
# NEVER deletes daily files — they are preserved forever.
#
# Workspace detection (in order):
#   1. AGENT_HOME, AGENT_WORKSPACE, WORKSPACE env vars
#   2. Common paths (/opt/${PACKAGE_NAME}/, /data/agents/, etc.)
#   3. Walk up from script location looking for SOUL.md, agent.json, MEMORY.md
# =============================================================================

set -euo pipefail

# ── Workspace Detection ──────────────────────────────────────────────────────
detect_workspace() {
    local workspace=""
    for var in AGENT_HOME AGENT_WORKSPACE WORKSPACE; do
        local val="${!var:-}"
        if [ -n "$val" ] && [ -d "$val" ]; then
            if [ -f "$val/SOUL.md" ] || [ -f "$val/agent.json" ] || [ -f "$val/MEMORY.md" ]; then
                workspace="$val"
                break
            fi
        fi
    done
    if [ -z "$workspace" ]; then
        local common_paths=(
            "/opt/${PACKAGE_NAME}/" "/opt/${PACKAGE_NAME}/" "/data/agents/" "/data/agent/"
            "/srv/agents/" "/srv/agent/" "$HOME/agents/" "$HOME/.agents/"
            "$HOME/.agent/" "$HOME/workspace/" "$HOME/workspaces/"
        )
        for path in "${common_paths[@]}"; do
            [ -d "$path" ] || continue
            for agent_dir in "$path"/*/; do
                [ -d "$agent_dir" ] || continue
                if [ -f "$agent_dir/SOUL.md" ] || [ -f "$agent_dir/agent.json" ]; then
                    workspace="$agent_dir"
                    break 2
                fi
            done
        done
    fi
    if [ -z "$workspace" ]; then
        local script_dir
        script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        local current="$script_dir"
        for i in {1..10}; do
            if [ -f "$current/SOUL.md" ] || [ -f "$current/agent.json" ] || [ -f "$current/MEMORY.md" ]; then
                workspace="$current"
                break
            fi
            local parent
            parent="$(dirname "$current")"
            [ "$parent" = "$current" ] && break
            current="$parent"
        done
    fi
    if [ -z "$workspace" ]; then
        local current="$(pwd)"
        for i in {1..10}; do
            if [ -f "$current/SOUL.md" ] || [ -f "$current/agent.json" ] || [ -f "$current/MEMORY.md" ]; then
                workspace="$current"
                break
            fi
            local parent
            parent="$(dirname "$current")"
            [ "$parent" = "$current" ] && break
            current="$parent"
        done
    fi
    echo "$workspace"
}

WS="$(detect_workspace)"
if [ -z "$WS" ]; then
    echo "ERROR: Could not detect agent workspace" >&2
    echo "Set AGENT_HOME, AGENT_WORKSPACE, or WORKSPACE env var" >&2
    exit 1
fi

MEMORY_DIR="$WS/memory"
LONG_TERM="$WS/MEMORY.md"

mkdir -p "$MEMORY_DIR"

# Ensure MEMORY.md exists
if [ ! -f "$LONG_TERM" ]; then
    cat > "$LONG_TERM" << 'EOF'
# MEMORY.md — Long-Term Curated Memory

Distilled wisdom from daily notes. Updated periodically.
Daily raw logs stay in memory/YYYY-MM-DD.md forever.

---

## Key Decisions

## Lessons Learned

## Active Context

## Recurring Patterns

EOF
    echo "Created MEMORY.md"
fi

# Determine date range
DATES=()
if [ "${1:-}" = "--week" ]; then
    for i in $(seq 0 6); do
        DATES+=("$(date -d "$i days ago" +%Y-%m-%d 2>/dev/null || date -v-${i}d +%Y-%m-%d 2>/dev/null || date +%Y-%m-%d)")
    done
elif [ -n "${1:-}" ]; then
    DATES=("$1")
else
    DATES=("$(date +%Y-%m-%d)")
    DATES+=("$(date -d "1 day ago" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null || date +%Y-%m-%d)")
fi

echo "=== Memory Promotion Review ==="
echo ""

FOUND=0
for DATE in "${DATES[@]}"; do
    FILE="$MEMORY_DIR/$DATE.md"
    if [ -f "$FILE" ]; then
        echo "--- $DATE ---"
        cat "$FILE"
        echo ""
        FOUND=$((FOUND + 1))
    fi
done

if [ "$FOUND" -eq 0 ]; then
    echo "No daily files found for the selected dates."
    echo "Files checked: ${DATES[*]}"
    echo ""
    echo "Daily notes live at: memory/YYYY-MM-DD.md"
    echo "Log entries with: bash scripts/memory-log.sh \"message\""
    exit 0
fi

echo "=== End of Daily Notes ==="
echo ""
echo "To promote entries to MEMORY.md:"
echo "  1. Read the entries above"
echo "  2. Add key insights to $LONG_TERM"
echo "  3. Daily files are NEVER deleted — they stay in memory/ forever"
echo ""
echo "Log new entries with:"
echo "  bash scripts/memory-log.sh \"what happened\""
echo "  bash scripts/memory-log.sh -t LESSON \"what I learned\""
echo "  bash scripts/memory-log.sh -t TODO \"what needs doing\""
