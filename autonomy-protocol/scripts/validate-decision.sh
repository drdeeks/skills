#!/usr/bin/env bash
# validate-decision.sh — Validate autonomy protocol decision
# Usage: bash validate-decision.sh --task "task description" --layer <layer>

set -euo pipefail

TASK=""
LAYER=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --task) TASK="$2"; shift 2 ;;
        --layer) LAYER="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

if [ -z "$TASK" ] || [ -z "$LAYER" ]; then
    echo "Usage: $0 --task \"task description\" --layer <scripts|tools|skills|subagents|main>"
    exit 1
fi

case "$LAYER" in
    scripts|tools|skills|subagents|main)
        echo "VALID: Layer '$LAYER' is valid"
        ;;
    *)
        echo "INVALID: Layer '$LAYER' must be one of: scripts, tools, skills, subagents, main"
        exit 1
        ;;
esac

echo "Decision validated: $TASK -> $LAYER"
