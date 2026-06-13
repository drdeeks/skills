#!/usr/bin/env bash
# =============================================================================
# safe-write.sh — Safely write files without overwriting critical data
# =============================================================================
#
# Usage:
#   bash scripts/safe-write.sh /path/to/file "new content"
#   bash scripts/safe-write.sh /path/to/file --from-source /path/to/source
#   bash scripts/safe-write.sh /path/to/file --check-only
#
# This script:
#   1. Checks if the target file is critical (config, identity, credentials, etc.)
#   2. If critical: stores override in .override/TIMESTAMP/, never modifies original
#   3. If not critical: writes directly
#   4. Always creates EXPLANATION.md for overrides
#   5. Always notifies user/manager
#
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

WORKSPACE="$(detect_workspace)"

# ── Critical File Detection ──────────────────────────────────────────────────
is_critical_file() {
    local filepath="$1"
    local filename
    filename=$(basename "$filepath")
    local dirpath
    dirpath=$(dirname "$filepath")

    # Credential files
    case "$filename" in
        .env|.env.*|auth.json|*.secret|*.key|*.pem|*.cert)
            echo "credentials"
            return 0
            ;;
    esac

    # Check if inside .secrets directory
    if [[ "$filepath" == *".secrets/"* ]]; then
        echo "credentials"
        return 0
    fi

    # Configuration files
    case "$filename" in
        config.yaml|config.json|config.yml|opencode.json|agent.json|package.json|*.config.*)
            echo "configuration"
            return 0
            ;;
    esac

    # Identity files
    case "$filename" in
        SOUL.md|IDENTITY.md|USER.md|AGENTS.md)
            echo "identity"
            return 0
            ;;
    esac

    # Memory files
    case "$filename" in
        MEMORY.md|HEARTBEAT.md)
            echo "memory"
            return 0
            ;;
    esac

    # Check if inside memory directory
    if [[ "$filepath" == *"/memory/"* ]] && [[ "$filename" == *.md ]]; then
        echo "memory"
        return 0
    fi

    # Tooling files
    if [[ "$filepath" == *"/tools/"* ]]; then
        case "$filename" in
            *.sh|*.py|TOOLS-GUIDE.md)
                echo "tooling"
                return 0
                ;;
        esac
    fi

    # Skill files
    if [[ "$filepath" == *"/skills/"* ]] && [[ "$filename" == "SKILL.md" ]]; then
        echo "skills"
        return 0
    fi

    # Not critical
    return 1
}

# ── Parse Arguments ──────────────────────────────────────────────────────────
TARGET_FILE=""
CONTENT=""
SOURCE_FILE=""
CHECK_ONLY=false
REASON=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --from-source) SOURCE_FILE="$2"; shift 2 ;;
        --check-only) CHECK_ONLY=true; shift ;;
        --reason) REASON="$2"; shift 2 ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS] <target-file> [content]"
            echo "  --from-source PATH  Copy from source file instead of content"
            echo "  --check-only        Only check if file is critical, don't write"
            echo "  --reason TEXT        Reason for the override"
            exit 0
            ;;
        *)
            if [ -z "$TARGET_FILE" ]; then
                TARGET_FILE="$1"
            elif [ -z "$CONTENT" ] && [ -z "$SOURCE_FILE" ]; then
                CONTENT="$1"
            fi
            shift
            ;;
    esac
done

if [ -z "$TARGET_FILE" ]; then
    echo "ERROR: No target file specified" >&2
    exit 1
fi

# Make target file absolute if relative
if [[ "$TARGET_FILE" != /* ]]; then
    TARGET_FILE="$(pwd)/$TARGET_FILE"
fi

# ── Check Only Mode ──────────────────────────────────────────────────────────
if $CHECK_ONLY; then
    if is_critical_file "$TARGET_FILE"; then
        echo "CRITICAL: $TARGET_FILE"
        exit 1
    else
        echo "SAFE: $TARGET_FILE"
        exit 0
    fi
fi

# ── Determine Write Strategy ─────────────────────────────────────────────────
CRITICAL_TYPE=$(is_critical_file "$TARGET_FILE" 2>/dev/null || true)

if [ -n "$CRITICAL_TYPE" ]; then
    # ════════════════════════════════════════════════════════════════════════
    # CRITICAL FILE — USE OVERRIDE PROTOCOL
    # ════════════════════════════════════════════════════════════════════════

    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    OVERRIDE_DIR="$WORKSPACE/.override/$TIMESTAMP"
    mkdir -p "$OVERRIDE_DIR"

    # Store override file
    OVERRIDE_FILE="$OVERRIDE_DIR/$(basename "$TARGET_FILE")"
    if [ -n "$SOURCE_FILE" ]; then
        cp "$SOURCE_FILE" "$OVERRIDE_FILE"
    else
        echo "$CONTENT" > "$OVERRIDE_FILE"
    fi

    # Create explanation
    RELATIVE_TARGET="${TARGET_FILE#$WORKSPACE/}"
    cat > "$OVERRIDE_DIR/EXPLANATION.md" << EOF
# Override Explanation

**Timestamp**: $(date -Iseconds)
**Original File**: $TARGET_FILE
**Override File**: $OVERRIDE_FILE
**Critical Type**: $CRITICAL_TYPE

## Why This Override Exists

${REASON:-No reason provided.}

## What This Override Does

This override stores a new version of a critical file WITHOUT modifying the original.
The agent continues running with the current configuration.

## How to Apply

To apply this override, manually copy:
\`\`\`bash
cp "$OVERRIDE_FILE" "$TARGET_FILE"
\`\`\`

## How to Reject

To reject this override and keep the original:
\`\`\`bash
rm -rf "$OVERRIDE_DIR"
\`\`\`

## Risk Assessment

- **Would applying this kill the agent?** Depends on the change
- **Is this a breaking change?** Unknown — review the file
- **Does this require restart?** Likely yes for configuration changes

## Protected Categories

This file was flagged as critical because it matches:
- Category: $CRITICAL_TYPE
- Pattern: $(basename "$TARGET_FILE")

Critical files are NEVER modified directly to prevent agent failure.
EOF

    # Notify user
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════════╗"
    echo "║  ⚠️  CRITICAL FILE OVERRIDE CREATED                                ║"
    echo "╠══════════════════════════════════════════════════════════════════════╣"
    echo "║  Category:  $CRITICAL_TYPE"
    echo "║  File:      $TARGET_FILE"
    echo "║  Override:  $OVERRIDE_FILE"
    echo "║"
    echo "║  Original file was NOT modified."
    echo "║  Agent continues running with current configuration."
    echo "║"
    echo "║  To review:  cat $OVERRIDE_DIR/EXPLANATION.md"
    echo "║  To apply:   cp $OVERRIDE_FILE $TARGET_FILE"
    echo "║  To reject:  rm -rf $OVERRIDE_DIR"
    echo "╚══════════════════════════════════════════════════════════════════════╝"
    echo ""

    # Log to memory if available
    if [ -n "$WORKSPACE" ] && [ -f "$WORKSPACE/tools/memory-log.sh" ]; then
        bash "$WORKSPACE/tools/memory-log.sh" -t "OVERRIDE" \
            "Critical file override created: $TARGET_FILE → $OVERRIDE_DIR (original NOT modified)"
    fi

    exit 0

else
    # ════════════════════════════════════════════════════════════════════════
    # NON-CRITICAL FILE — WRITE DIRECTLY
    # ════════════════════════════════════════════════════════════════════════

    # Create directory if needed
    mkdir -p "$(dirname "$TARGET_FILE")"

    # Write file
    if [ -n "$SOURCE_FILE" ]; then
        cp "$SOURCE_FILE" "$TARGET_FILE"
    else
        echo "$CONTENT" > "$TARGET_FILE"
    fi

    echo "Written: $TARGET_FILE"
    exit 0
fi
