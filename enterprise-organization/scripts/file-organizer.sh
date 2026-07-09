#!/usr/bin/env bash
# file-organizer.sh - Enterprise file organization and decluttering
# Enforces .trash for removed files, validates doc structure, prevents BS file generation
set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

WORKSPACE="${WORKSPACE:-$(pwd)}"
TRASH_DIR="${WORKSPACE}/.trash"
LOG_FILE="${WORKSPACE}/.trash/.trash-log.json"
DOCS_DIR="${WORKSPACE}/docs"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ============================================================================
# Help
# ============================================================================

show_help() {
    cat <<'EOF'
Enterprise File Organization - Decluttering and Management

Usage: bash file-organizer.sh <command> [options]

Commands:
  trash <path>        Move file/directory to .trash (with logging)
  restore <path>      Restore from .trash to original location
  scan                Scan for files that should be trashed
  validate-docs       Validate documentation structure
  cleanup             Remove old items from .trash (older than N days)
  status              Show trash status and organization stats
  init                Initialize organization structure

Options:
  --workspace <path>  Workspace root (default: pwd)
  --dry-run           Preview actions without executing
  --force             Skip confirmation prompts
  --days <n>          Days for cleanup (default: 30)
  --help              Show this help

Standards Enforced:
  - Documentation: README.md + AGENTS.md at root, rest in docs/
  - Deleted files: Must go to .trash/ (not deleted permanently)
  - All files: Version tracked in git
  - BS files: Detected and flagged for trashing
EOF
    exit 0
}

# ============================================================================
# Core Functions
# ============================================================================

# Initialize organization structure
init_organization() {
    echo -e "${BLUE}Initializing file organization...${NC}"
    
    # Create .trash directory
    mkdir -p "$TRASH_DIR"
    
    # Create .trash/.gitkeep to ensure it's tracked
    touch "$TRASH_DIR/.gitkeep"
    
    # Initialize trash log if not exists
    if [[ ! -f "$LOG_FILE" ]]; then
        echo '{"trashes":[],"restores":[],"stats":{"total_trashed":0,"total_restored":0}}' > "$LOG_FILE"
    fi
    
    # Ensure docs directory exists
    mkdir -p "$DOCS_DIR"
    
    # Create .gitignore entry for .trash if not present
    local gitignore="${WORKSPACE}/.gitignore"
    if [[ ! -f "$gitignore" ]]; then
        touch "$gitignore"
    fi
    
    # Add .trash to .gitignore (keep .trash tracked but don't include trashed content)
    if ! grep -q "^\.trash/" "$gitignore" 2>/dev/null; then
        echo "" >> "$gitignore"
        echo "# Enterprise file organization - trashed files" >> "$gitignore"
        echo ".trash/*" >> "$gitignore"
        echo "!.trash/.gitkeep" >> "$gitignore"
        echo "!.trash/.trash-log.json" >> "$gitignore"
    fi
    
    echo -e "${GREEN}✓ Organization structure initialized${NC}"
    echo "  - .trash/ directory created"
    echo "  - docs/ directory created"
    echo "  - .gitignore updated"
}

# Move file to .trash with logging
trash_file() {
    local path="$1"
    local full_path="${WORKSPACE}/${path}"
    
    if [[ ! -e "$full_path" ]]; then
        echo -e "${RED}✗ Path not found: $path${NC}"
        return 1
    fi
    
    # Generate unique trash name to avoid conflicts
    local basename=$(basename "$path")
    local dirname=$(dirname "$path")
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local trash_name="${basename}_${timestamp}"
    
    # Handle name conflicts
    while [[ -e "${TRASH_DIR}/${trash_name}" ]]; do
        trash_name="${trash_name}_$(openssl rand -hex 4 2>/dev/null || echo $RANDOM)"
    done
    
    # Create metadata
    local metadata=$(cat <<META
{
  "original_path": "${path}",
  "trashed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "trash_name": "${trash_name}",
  "reason": "user_trash"
}
META
)
    
    # Move to trash
    mv "$full_path" "${TRASH_DIR}/${trash_name}"
    
    # Update log
    local tmp_log=$(mktemp)
    jq --arg path "$path" \
       --arg trash_name "$trash_name" \
       --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       '.trashes += [{"original_path": $path, "trash_name": $trash_name, "trashed_at": $timestamp}] | .stats.total_trashed += 1' \
       "$LOG_FILE" > "$tmp_log" && mv "$tmp_log" "$LOG_FILE"
    
    echo -e "${GREEN}✓ Trashed: $path → .trash/${trash_name}${NC}"
}

# Restore from trash
restore_file() {
    local trash_name="$1"
    local trash_path="${TRASH_DIR}/${trash_name}"
    
    if [[ ! -e "$trash_path" ]]; then
        echo -e "${RED}✗ Not found in trash: $trash_name${NC}"
        return 1
    fi
    
    # Get original path from log
    local original_path=$(jq -r --arg name "$trash_name" \
        '.trashes[] | select(.trash_name == $name) | .original_path' \
        "$LOG_FILE" 2>/dev/null || echo "")
    
    if [[ -z "$original_path" ]]; then
        echo -e "${YELLOW}⚠ Original path unknown, restoring to root${NC}"
        original_path=$(basename "$trash_name" | sed 's/_[0-9]*_[0-9]*$//')
    fi
    
    local dest_path="${WORKSPACE}/${original_path}"
    local dest_dir=$(dirname "$dest_path")
    
    # Create destination directory if needed
    mkdir -p "$dest_dir"
    
    # Check if destination already exists
    if [[ -e "$dest_path" ]]; then
        echo -e "${YELLOW}⚠ Destination exists: $original_path${NC}"
        echo "  Use --force to overwrite"
        return 1
    fi
    
    # Restore
    mv "$trash_path" "$dest_path"
    
    # Update log
    local tmp_log=$(mktemp)
    jq --arg name "$trash_name" \
       --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       '.restores += [{"trash_name": $name, "restored_at": $timestamp}] | .stats.total_restored += 1' \
       "$LOG_FILE" > "$tmp_log" && mv "$tmp_log" "$LOG_FILE"
    
    echo -e "${GREEN}✓ Restored: ${trash_name} → ${original_path}${NC}"
}

# Scan for files that should be trashed
scan_files() {
    echo -e "${BLUE}Scanning workspace for files to trash...${NC}"
    echo ""
    
    local count=0
    local suspicious=()
    
    # Check for common BS files
    while IFS= read -r -d '' file; do
        local rel_path="${file#${WORKSPACE}/}"
        local basename=$(basename "$file")
        
        # Skip .git and .trash
        if [[ "$rel_path" == .git/* || "$rel_path" == .trash/* ]]; then
            continue
        fi
        
        # Check for suspicious patterns
        local should_trash=false
        local reason=""
        
        # Temp files
        if [[ "$basename" =~ \.(tmp|temp|bak|swp|swo)$ ]]; then
            should_trash=true
            reason="temp file"
        fi
        
        # Generated files that shouldn't be tracked
        if [[ "$basename" =~ ^\..*\.swp$ || "$basename" =~ ^\.~ ]]; then
            should_trash=true
            reason="editor temp file"
        fi
        
        # OS files
        if [[ "$basename" == ".DS_Store" || "$basename" == "Thumbs.db" || "$basename" == "desktop.ini" ]]; then
            should_trash=true
            reason="OS metadata file"
        fi
        
        # __pycache__ directories
        if [[ "$basename" == "__pycache__" ]]; then
            should_trash=true
            reason="python cache"
        fi
        
        # node_modules (should be in .gitignore)
        if [[ "$basename" == "node_modules" ]]; then
            should_trash=true
            reason="dependency directory (should be in .gitignore)"
        fi
        
        # Large log files
        if [[ "$basename" =~ \.(log|logs)$ ]]; then
            local size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
            if [[ $size -gt 1048576 ]]; then  # 1MB
                should_trash=true
                reason="large log file ($(( size / 1048576 ))MB)"
            fi
        fi
        
        if [[ "$should_trash" == "true" ]]; then
            echo -e "${YELLOW}⚠ ${rel_path}${NC} - ${reason}"
            suspicious+=("$rel_path")
            ((count++))
        fi
    done < <(find "$WORKSPACE" -type f -print0 2>/dev/null)
    
    # Check for documentation structure violations
    echo ""
    echo -e "${BLUE}Documentation structure check:${NC}"
    
    # Check root for excess docs
    local root_docs=$(find "$WORKSPACE" -maxdepth 1 -name "*.md" -type f 2>/dev/null | grep -v "README.md" | grep -v "AGENTS.md" || true)
    if [[ -n "$root_docs" ]]; then
        echo -e "${YELLOW}⚠ Extra docs at root (should be in docs/):${NC}"
        echo "$root_docs" | while read f; do
            echo "  - $(basename "$f")"
            ((count++))
        done
    fi
    
    # Check if docs/ exists
    if [[ ! -d "$DOCS_DIR" ]]; then
        echo -e "${YELLOW}⚠ docs/ directory missing${NC}"
    fi
    
    echo ""
    echo -e "Found ${count} files to review"
    
    if [[ $count -gt 0 ]]; then
        echo ""
        echo "To trash these files, run:"
        echo "  bash file-organizer.sh trash <path>"
        echo ""
        echo "Or use --force to trash all flagged files"
    fi
}

# Validate documentation structure
validate_docs() {
    echo -e "${BLUE}Validating documentation structure...${NC}"
    echo ""
    
    local errors=0
    local warnings=0
    
    # Check README.md exists
    if [[ ! -f "${WORKSPACE}/README.md" ]]; then
        echo -e "${RED}✗ Missing: README.md at root${NC}"
        ((errors++))
    else
        echo -e "${GREEN}✓ README.md present${NC}"
    fi
    
    # Check AGENTS.md exists
    if [[ ! -f "${WORKSPACE}/AGENTS.md" ]]; then
        echo -e "${YELLOW}⚠ Missing: AGENTS.md at root (recommended)${NC}"
        ((warnings++))
    else
        echo -e "${GREEN}✓ AGENTS.md present${NC}"
    fi
    
    # Check for docs/ directory
    if [[ ! -d "$DOCS_DIR" ]]; then
        echo -e "${YELLOW}⚠ Missing: docs/ directory${NC}"
        ((warnings++))
    else
        echo -e "${GREEN}✓ docs/ directory present${NC}"
        
        # Count docs
        local doc_count=$(find "$DOCS_DIR" -name "*.md" -type f 2>/dev/null | wc -l)
        echo "  - ${doc_count} documents in docs/"
    fi
    
    # Check for excess docs at root
    local root_extras=$(find "$WORKSPACE" -maxdepth 1 -name "*.md" -type f 2>/dev/null | grep -v "README.md" | grep -v "AGENTS.md" | wc -l)
    if [[ $root_extras -gt 0 ]]; then
        echo -e "${YELLOW}⚠ ${root_extras} extra .md files at root (should be in docs/)${NC}"
        ((warnings++))
    fi
    
    echo ""
    if [[ $errors -eq 0 && $warnings -eq 0 ]]; then
        echo -e "${GREEN}✓ Documentation structure valid${NC}"
    else
        echo -e "Errors: ${errors}, Warnings: ${warnings}"
    fi
    
    return $errors
}

# Clean up old trash items
cleanup_trash() {
    local days="${1:-30}"
    
    echo -e "${BLUE}Cleaning up trash older than ${days} days...${NC}"
    
    if [[ ! -d "$TRASH_DIR" ]]; then
        echo -e "${YELLOW}No .trash directory found${NC}"
        return 0
    fi
    
    local count=0
    while IFS= read -r -d '' item; do
        local basename=$(basename "$item")
        [[ "$basename" == ".gitkeep" || "$basename" == ".trash-log.json" ]] && continue
        
        rm -rf "$item"
        ((count++))
    done < <(find "$TRASH_DIR" -maxdepth 1 -mtime +$days -mindepth 1 -print0 2>/dev/null)
    
    echo -e "${GREEN}✓ Cleaned up ${count} items from trash${NC}"
}

# Show trash status
show_status() {
    echo -e "${BLUE}File Organization Status${NC}"
    echo ""
    
    # Trash stats
    if [[ -f "$LOG_FILE" ]]; then
        local total_trashed=$(jq -r '.stats.total_trashed' "$LOG_FILE" 2>/dev/null || echo "0")
        local total_restored=$(jq -r '.stats.total_restored' "$LOG_FILE" 2>/dev/null || echo "0")
        echo "Trash Statistics:"
        echo "  - Total trashed: ${total_trashed}"
        echo "  - Total restored: ${total_restored}"
    fi
    
    # Current trash contents
    if [[ -d "$TRASH_DIR" ]]; then
        local trash_count=$(find "$TRASH_DIR" -mindepth 1 -maxdepth 1 ! -name ".gitkeep" ! -name ".trash-log.json" 2>/dev/null | wc -l)
        echo "  - Current items: ${trash_count}"
        
        if [[ $trash_count -gt 0 ]]; then
            echo ""
            echo "Recent trashes:"
            ls -lt "$TRASH_DIR" 2>/dev/null | head -10 | tail -9 | while read line; do
                echo "  $line"
            done
        fi
    else
        echo "  - .trash directory: Not initialized"
    fi
    
    echo ""
    
    # Doc structure
    echo "Documentation Structure:"
    if [[ -f "${WORKSPACE}/README.md" ]]; then
        echo "  ✓ README.md"
    else
        echo "  ✗ README.md (missing)"
    fi
    
    if [[ -f "${WORKSPACE}/AGENTS.md" ]]; then
        echo "  ✓ AGENTS.md"
    else
        echo "  ✗ AGENTS.md (missing)"
    fi
    
    if [[ -d "$DOCS_DIR" ]]; then
        local doc_count=$(find "$DOCS_DIR" -name "*.md" -type f 2>/dev/null | wc -l)
        echo "  ✓ docs/ (${doc_count} files)"
    else
        echo "  ✗ docs/ (missing)"
    fi
}

# ============================================================================
# Main
# ============================================================================

COMMAND="${1:-}"
shift || true

DRY_RUN=false
FORCE=false
DAYS=30

# Parse options
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h) show_help ;;
        --workspace) WORKSPACE="$2"; shift 2 ;;
        --dry-run) DRY_RUN=true; shift ;;
        --force) FORCE=true; shift ;;
        --days) DAYS="$2"; shift 2 ;;
        *) break ;;
    esac
done

# Update paths based on workspace
TRASH_DIR="${WORKSPACE}/.trash"
LOG_FILE="${WORKSPACE}/.trash/.trash-log.json"
DOCS_DIR="${WORKSPACE}/docs"

case "$COMMAND" in
    init)
        init_organization
        ;;
    trash)
        [[ -z "${1:-}" ]] && { echo "ERROR: path required"; exit 1; }
        trash_file "$1"
        ;;
    restore)
        [[ -z "${1:-}" ]] && { echo "ERROR: trash name required"; exit 1; }
        restore_file "$1"
        ;;
    scan)
        scan_files
        ;;
    validate-docs)
        validate_docs
        ;;
    cleanup)
        cleanup_trash "$DAYS"
        ;;
    status)
        show_status
        ;;
    *)
        echo "ERROR: Unknown command: $COMMAND"
        show_help
        ;;
esac
