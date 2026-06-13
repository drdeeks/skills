#!/usr/bin/env bash
# =============================================================================
# validate.sh — Validate agent workspace tools and structure
# =============================================================================
#
# Usage:
#   bash scripts/validate.sh                     # Auto-detect workspace
#   bash scripts/validate.sh /path/to/workspace  # Explicit path
#   bash scripts/validate.sh --fix               # Auto-fix issues
#   bash scripts/validate.sh --check-permissions # Check file permissions
#
# Validates:
#   - Required directories exist
#   - Required tools are present and executable
#   - Required files exist
#   - No chmod 700 violations
#   - SOUL.md identity matches workspace
#
# Workspace detection (in order):
#   1. AGENT_HOME, AGENT_WORKSPACE, WORKSPACE env vars
#   2. Common paths (/opt/${PACKAGE_NAME}/, /data/agents/, etc.)
#   3. Walk up from script location looking for SOUL.md, agent.json, MEMORY.md
#   4. First argument if provided
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

# ── Parse Arguments ──────────────────────────────────────────────────────────
FIX_MODE=false
CHECK_PERMS=false
WORKSPACE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --fix) FIX_MODE=true; shift ;;
        --check-permissions) CHECK_PERMS=true; shift ;;
        --help|-h)
            echo "Usage: $0 [--fix] [--check-permissions] [workspace-path]"
            echo "  --fix               Auto-fix issues"
            echo "  --check-permissions Check file permissions"
            echo "  workspace-path      Explicit workspace path"
            exit 0
            ;;
        *) WORKSPACE="$1"; shift ;;
    esac
done

# Auto-detect if not provided
if [ -z "$WORKSPACE" ]; then
    WORKSPACE="$(detect_workspace)"
fi

if [ -z "$WORKSPACE" ] || [ ! -d "$WORKSPACE" ]; then
    echo "ERROR: Could not detect agent workspace" >&2
    echo "Set AGENT_HOME, AGENT_WORKSPACE, or WORKSPACE env var" >&2
    echo "Or pass workspace path as argument" >&2
    exit 1
fi

echo "=== Agent Workspace Validation ==="
echo "Workspace: $WORKSPACE"
echo ""

ERRORS=0
WARNINGS=0
FIXED=0

# ── Colors ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass() { echo -e "${GREEN}✓ PASS${NC} $*"; }
fail() { echo -e "${RED}✗ FAIL${NC} $*"; ERRORS=$((ERRORS + 1)); }
warn() { echo -e "${YELLOW}⚠ WARN${NC} $*"; WARNINGS=$((WARNINGS + 1)); }
fixed() { echo -e "${GREEN}✓ FIXED${NC} $*"; FIXED=$((FIXED + 1)); }

# ── Required Directories ─────────────────────────────────────────────────────
echo "--- Required Directories ---"
REQUIRED_DIRS=("memory" "skills" "projects" "tools" "logs" ".secrets" ".archive")

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$WORKSPACE/$dir" ]; then
        pass "Directory: $dir/"
    else
        if $FIX_MODE; then
            mkdir -p "$WORKSPACE/$dir"
            fixed "Created missing directory: $dir/"
        else
            fail "Missing directory: $dir/"
        fi
    fi
done

# ── Required Files ───────────────────────────────────────────────────────────
echo ""
echo "--- Required Files ---"
REQUIRED_FILES=("SOUL.md" "USER.md" "agent.json" "config.yaml")

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$WORKSPACE/$file" ]; then
        pass "File: $file"
    else
        fail "Missing file: $file"
    fi
done

# ── Required Tools ───────────────────────────────────────────────────────────
echo ""
echo "--- Required Tools ---"
REQUIRED_TOOLS=(
    "enforce.sh"
    "secret.sh"
    "memory-log.sh"
    "memory-promote.sh"
    "jsonfmt.py"
    "TOOLS-GUIDE.md"
    "inject-context.sh"
)

for tool in "${REQUIRED_TOOLS[@]}"; do
    if [ -f "$WORKSPACE/tools/$tool" ]; then
        pass "Tool: $tool"
    else
        fail "Missing tool: $tool"
    fi
done

# ── Permission Check ─────────────────────────────────────────────────────────
if $CHECK_PERMS; then
    echo ""
    echo "--- Permission Check ---"

    # Check for chmod 700 violations
    CHMOD_VIOLATIONS=$(find "$WORKSPACE" -type d -perm 700 2>/dev/null | head -10)
    if [ -n "$CHMOD_VIOLATIONS" ]; then
        while IFS= read -r dir; do
            if $FIX_MODE; then
                chmod 755 "$dir"
                fixed "Fixed chmod 700 on: $dir"
            else
                fail "chmod 700 violation: $dir"
            fi
        done <<< "$CHMOD_VIOLATIONS"
    else
        pass "No chmod 700 violations"
    fi

    # Check for chmod 600 violations on non-secret files
    CHMOD_600=$(find "$WORKSPACE" -type f -perm 600 ! -path "*/.secrets/*" 2>/dev/null | head -10)
    if [ -n "$CHMOD_600" ]; then
        while IFS= read -r file; do
            if $FIX_MODE; then
                chmod 644 "$file"
                fixed "Fixed chmod 600 on: $file"
            else
                warn "chmod 600 on non-secret file: $file"
            fi
        done <<< "$CHMOD_600"
    else
        pass "No chmod 600 violations on non-secret files"
    fi
fi

# ── Identity Check ───────────────────────────────────────────────────────────
echo ""
echo "--- Identity Check ---"

if [ -f "$WORKSPACE/SOUL.md" ]; then
    FIRST_LINE=$(head -1 "$WORKSPACE/SOUL.md")
    AGENT_NAME=$(basename "$WORKSPACE")

    if echo "$FIRST_LINE" | grep -qi "$AGENT_NAME" 2>/dev/null; then
        pass "SOUL.md identity matches workspace name"
    else
        warn "SOUL.md first line doesn't contain workspace name ($AGENT_NAME)"
    fi
else
    fail "SOUL.md not found for identity check"
fi

# ── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo "=== Validation Summary ==="
echo "Errors:   $ERRORS"
echo "Warnings: $WARNINGS"
if $FIX_MODE; then
    echo "Fixed:    $FIXED"
fi

if [ $ERRORS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Workspace is valid${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}✗ Workspace has $ERRORS error(s)${NC}"
    exit 1
fi
