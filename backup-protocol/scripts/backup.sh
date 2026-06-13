#!/usr/bin/env bash
# =============================================================================
# Agent Backup — Full System Backup (Provider-Agnostic)
# =============================================================================
#
# Complete backup of agent workspace including:
#   - Workspace root (config, auth, env, hooks, cron, memories)
#   - Memory files
#   - Skills (read-only reference)
#   - Tools (agent-specific)
#
# Sensitive files (.env, auth.json, .secrets/*) are encrypted at rest.
# Everything else is copied as-is.
#
# Usage:
#   ./backup.sh              # Full backup
#   ./backup.sh --init       # First-time setup (generates encryption key)
#   ./backup.sh --restore    # Restore from backup
#   ./backup.sh --status     # Show backup status
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

WORKSPACE="$(detect_workspace)"
if [ -z "$WORKSPACE" ]; then
    echo "ERROR: Could not detect agent workspace" >&2
    echo "Set AGENT_HOME, AGENT_WORKSPACE, or WORKSPACE env var" >&2
    exit 1
fi

# ── Configuration ────────────────────────────────────────────────────────────
BACKUP_DIR="${BACKUP_DIR:-$WORKSPACE/.backups}"
KEY_FILE="${BACKUP_DIR}/.backup-key"
ENCRYPT_CMD="openssl enc -aes-256-cbc -salt -pbkdf2 -pass file:${KEY_FILE}"
DECRYPT_CMD="openssl enc -d -aes-256-cbc -pbkdf2 -pass file:${KEY_FILE}"

# ── Colors ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

log()  { echo -e "${GREEN}✓${NC} $*"; }
warn() { echo -e "${YELLOW}⚠${NC}  $*"; }
err()  { echo -e "${RED}✗${NC} $*" >&2; }
info() { echo -e "${CYAN}→${NC} $*"; }

# ── Init ─────────────────────────────────────────────────────────────────────

cmd_init() {
    echo -e "${BOLD}${CYAN}Agent Backup — First-Time Setup${NC}"
    echo ""

    mkdir -p "$BACKUP_DIR"

    if [ -f "$KEY_FILE" ]; then
        warn "Encryption key already exists at ${KEY_FILE}"
        return 1
    fi

    openssl rand -base64 32 > "$KEY_FILE"
    chmod 600 "$KEY_FILE"
    log "Encryption key generated: ${KEY_FILE}"
    echo ""
    echo -e "${BOLD}IMPORTANT:${NC} Back up this key separately!"
    echo "  Key location: ${KEY_FILE}"
    echo "  Key preview:  $(head -c 20 "$KEY_FILE")..."
    echo ""
    warn "Store a copy in your password manager, USB drive, or print it."
}

# ── Backup ───────────────────────────────────────────────────────────────────

cmd_backup() {
    echo -e "${BOLD}${CYAN}Agent Backup — Running${NC}"
    echo ""

    if [ ! -f "$KEY_FILE" ]; then
        err "No encryption key found. Run: $0 --init"
        return 1
    fi

    mkdir -p "$BACKUP_DIR"
    cd "$BACKUP_DIR"
    git pull --rebase --quiet 2>/dev/null || true

    # ── 1. Full copy of workspace ──────────────────────────────────────────
    info "Syncing workspace (full copy)..."
    mkdir -p "${BACKUP_DIR}/workspace"
    rsync -a --delete \
        --exclude='.git/' \
        --exclude='checkpoints/' \
        --exclude='.backups/' \
        --exclude='logs/' \
        --exclude='node_modules/' \
        --exclude='__pycache__/' \
        "${WORKSPACE}/" "${BACKUP_DIR}/workspace/" 2>/dev/null
    log "Workspace synced"

    # ── 2. Encrypt sensitive files ─────────────────────────────────────────
    info "Encrypting sensitive files..."
    local enc_count=0

    # Find and encrypt .env files
    while IFS= read -r -d '' env_file; do
        $ENCRYPT_CMD -in "$env_file" -out "${env_file}.enc" 2>/dev/null
        rm -f "$env_file"
        enc_count=$((enc_count + 1))
    done < <(find "${BACKUP_DIR}/workspace" -name ".env" -type f -print0 2>/dev/null)

    # Find and encrypt auth.json files
    while IFS= read -r -d '' auth_file; do
        $ENCRYPT_CMD -in "$auth_file" -out "${auth_file}.enc" 2>/dev/null
        rm -f "$auth_file"
        enc_count=$((enc_count + 1))
    done < <(find "${BACKUP_DIR}/workspace" -name "auth.json" -type f -print0 2>/dev/null)

    # Encrypt .secrets directory contents
    if [ -d "${BACKUP_DIR}/workspace/.secrets" ]; then
        while IFS= read -r -d '' sf; do
            local sname
            sname=$(basename "$sf")
            [[ "$sname" == *.enc ]] && continue
            $ENCRYPT_CMD -in "$sf" -out "${sf}.enc" 2>/dev/null
            rm -f "$sf"
            enc_count=$((enc_count + 1))
        done < <(find "${BACKUP_DIR}/workspace/.secrets" -type f -print0 2>/dev/null)
    fi

    log "Encrypted ${enc_count} sensitive file(s)"

    # ── 3. Record timestamp ──────────────────────────────────────────────
    date -u +%Y-%m-%dT%H:%M:%SZ > "${BACKUP_DIR}/.last-backup"

    # ── 4. Commit and push ──────────────────────────────────────────────
    cd "$BACKUP_DIR"
    git add -A

    if git diff --cached --quiet 2>/dev/null; then
        log "No changes detected. Backup up to date."
        return 0
    fi

    local timestamp
    timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    git commit -m "backup: ${timestamp}" --quiet

    if git push --quiet 2>&1; then
        log "Backup pushed to remote"
    else
        warn "Push failed — changes committed locally but not pushed"
        warn "Run 'git push' manually from ${BACKUP_DIR}"
    fi

    # ── Summary ─────────────────────────────────────────────────────────
    local total_files
    total_files=$(find "${BACKUP_DIR}" -type f | wc -l)
    local total_size
    total_size=$(du -sh "${BACKUP_DIR}" --exclude='.git' 2>/dev/null | cut -f1)

    echo ""
    log "Backup complete"
    echo "  Local:   ${BACKUP_DIR}"
    echo "  Files:   ${total_files}"
    echo "  Size:    ${total_size}"
    echo "  Commit:  $(git log -1 --format='%h %s' 2>/dev/null)"
}

# ── Restore ──────────────────────────────────────────────────────────────────

cmd_restore() {
    echo -e "${BOLD}${CYAN}Agent Backup — Restore${NC}"
    echo ""

    if [ ! -d "$BACKUP_DIR/workspace" ]; then
        err "No backup data found at ${BACKUP_DIR}/workspace/"
        return 1
    fi

    echo "Available directories in backup:"
    ls -1 "${BACKUP_DIR}/workspace/" | head -20
    echo ""

    read -rp "Enter directory name to restore (or 'all'): " target

    if [ "$target" = "all" ]; then
        info "Restoring entire workspace..."
        rsync -a "${BACKUP_DIR}/workspace/" "${WORKSPACE}/"
    else
        local src="${BACKUP_DIR}/workspace/${target}"
        local dst="${WORKSPACE}/${target}"
        if [ -d "$src" ]; then
            info "Restoring ${target}..."
            mkdir -p "$dst"
            rsync -a "$src/" "$dst/"
        else
            err "No backup found for ${target}"
            return 1
        fi
    fi

    # Decrypt sensitive files
    if [ -f "$KEY_FILE" ]; then
        info "Decrypting sensitive files..."
        while IFS= read -r -d '' enc; do
            local plain="${enc%.enc}"
            $DECRYPT_CMD -in "$enc" -out "$plain" 2>/dev/null && chmod 600 "$plain"
            rm -f "$enc"
        done < <(find "${WORKSPACE}" -name "*.enc" -type f -print0 2>/dev/null)
    else
        warn "No encryption key — .env, auth.json, .secrets will remain encrypted"
    fi

    log "Restore complete"
}

# ── Status ───────────────────────────────────────────────────────────────────

cmd_status() {
    echo -e "${BOLD}${CYAN}Agent Backup Status${NC}"
    echo ""

    cd "$BACKUP_DIR" 2>/dev/null || { err "Backup dir not found: ${BACKUP_DIR}"; return 1; }

    local last_backup
    last_backup=$(cat .last-backup 2>/dev/null || echo "never")

    echo "  Remote:       $(git remote get-url origin 2>/dev/null || echo 'no remote')"
    echo "  Branch:       $(git branch --show-current 2>/dev/null || echo 'unknown')"
    echo "  Last backup:  ${last_backup}"
    echo "  Last commit:  $(git log -1 --format='%h %ai %s' 2>/dev/null || echo 'no commits')"
    echo "  Encryption:   $([ -f "$KEY_FILE" ] && echo 'key present' || echo 'KEY MISSING')"
    echo ""

    echo "  Workspace contents:"
    if [ -d workspace ]; then
        for d in workspace/*/; do
            [ -d "$d" ] || continue
            local name
            name=$(basename "$d")
            local count
            count=$(find "$d" -type f 2>/dev/null | wc -l)
            local size
            size=$(du -sh "$d" 2>/dev/null | cut -f1)
            echo "    ${name}: ${count} files, ${size}"
        done
    fi

    echo ""
    echo "  Total: $(find . -type f -not -path './.git/*' 2>/dev/null | wc -l) files, $(du -sh --exclude='.git' . 2>/dev/null | cut -f1)"
}

# ── Main ─────────────────────────────────────────────────────────────────────

case "${1:-}" in
    --init|-i)    cmd_init ;;
    --restore|-r) cmd_restore ;;
    --status|-s)  cmd_status ;;
    --help|-h)
        echo "Usage: $0 [--init|--restore|--status]"
        echo "  (no args)    Run backup"
        echo "  --init       First-time setup"
        echo "  --restore    Restore from backup"
        echo "  --status     Show backup status"
        ;;
    *)            cmd_backup ;;
esac
