#!/usr/bin/env bash
# =============================================================================
# memory-log.sh — Append to today's daily memory file
# =============================================================================
#
# Usage:
#   bash scripts/memory-log.sh "Completed auth-login.sh fix across all agents"
#   bash scripts/memory-log.sh -t "TODO" "Need to review backup timer"
#   bash scripts/memory-log.sh -t "LESSON" "Always use -it with docker exec"
#
# Writes to: $WORKSPACE_ROOT/memory/YYYY-MM-DD.md
# Creates the file with header if it doesn't exist.
# NEVER deletes old daily files.
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

    # Method 1: Environment variables
    for var in AGENT_HOME AGENT_WORKSPACE WORKSPACE; do
        local val="${!var:-}"
        if [ -n "$val" ] && [ -d "$val" ]; then
            if [ -f "$val/SOUL.md" ] || [ -f "$val/agent.json" ] || [ -f "$val/MEMORY.md" ]; then
                workspace="$val"
                break
            fi
        fi
    done

    # Method 2: Common paths
    if [ -z "$workspace" ]; then
        local common_paths=(
            "/opt/${PACKAGE_NAME}/" "/opt/${PACKAGE_NAME}/" "/data/agents/" "/data/agent/"
            "/srv/agents/" "/srv/agent/" "$HOME/agents/" "$HOME/.agents/"
            "$HOME/.agent/" "$HOME/workspace/" "$HOME/workspaces/"
        )
        for path in "${common_paths[@]}"; do
            if [ -d "$path" ]; then
                for agent_dir in "$path"/*/; do
                    [ -d "$agent_dir" ] || continue
                    if [ -f "$agent_dir/SOUL.md" ] || [ -f "$agent_dir/agent.json" ]; then
                        workspace="$agent_dir"
                        break 2
                    fi
                done
            fi
        done
    fi

    # Method 3: Walk up from script location
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

    # Method 4: Walk up from pwd
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

# ── Parse Arguments ──────────────────────────────────────────────────────────
TAG=""

while getopts "t:" opt; do
    case $opt in
        t) TAG="$OPTARG" ;;
        *) echo "Usage: memory-log.sh [-t TAG] \"message\""; exit 1 ;;
    esac
done
shift $((OPTIND - 1))

MESSAGE="${1:?Usage: memory-log.sh [-t TAG] \"message\"}"

TODAY=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
FILE="$WS/memory/$TODAY.md"

mkdir -p "$WS/memory"

# Create file with header if new
if [ ! -f "$FILE" ]; then
    echo "# Memory — $TODAY" > "$FILE"
    echo "" >> "$FILE"
fi

# Append entry
if [ -n "$TAG" ]; then
    echo "- **[$TAG]** $TIME — $MESSAGE" >> "$FILE"
else
    echo "- $TIME — $MESSAGE" >> "$FILE"
fi

echo "Logged to memory/$TODAY.md"
