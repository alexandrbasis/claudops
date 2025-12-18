#!/bin/bash
# sync-to-public.sh
# Syncs .claude/ directory to public wythm-claude-workflows repository
# Excludes sensitive files and auto-pushes to GitHub

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SOURCE_CLAUDE_DIR="$PROJECT_ROOT/.claude"

# Public repo path from environment or default
if [[ -z "$PUBLIC_REPO_PATH" ]]; then
    PUBLIC_REPO_PATH="$PROJECT_ROOT/wythm-claude-workflows"
fi

TARGET_CLAUDE_DIR="$PUBLIC_REPO_PATH/.claude"

# Log file
LOG_FILE="$SOURCE_CLAUDE_DIR/sync-public.log"

# Function to log messages
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}✗${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1" | tee -a "$LOG_FILE"
}

# Validation
if [[ ! -d "$SOURCE_CLAUDE_DIR" ]]; then
    log_error "Source .claude directory not found: $SOURCE_CLAUDE_DIR"
    exit 1
fi

if [[ ! -d "$PUBLIC_REPO_PATH" ]]; then
    log_error "Public repository not found: $PUBLIC_REPO_PATH"
    log_error "Please ensure wythm-claude-workflows is cloned"
    exit 1
fi

if [[ ! -d "$PUBLIC_REPO_PATH/.git" ]]; then
    log_error "Target directory is not a git repository: $PUBLIC_REPO_PATH"
    exit 1
fi

log "Starting sync from $SOURCE_CLAUDE_DIR to $TARGET_CLAUDE_DIR"

# Files and directories to EXCLUDE (sensitive data)
EXCLUDE_PATTERNS=(
    "settings.local.json"
    "*.local.json.backup"
    "hook-debug.log"
    "sync-public.log"
    "*.log"
    "__pycache__"
    "*.pyc"
    "*.pyo"
    ".DS_Store"
    "history.jsonl"
    "session-env"
    "todos"
    "debug"
    "file-history"
    ".state"
    # MCP configs with API keys
    "mcp/todoist.json"
    "mcp/context7.json"
    "mcp/ref.json"
)

# Build rsync exclude parameters
EXCLUDE_ARGS=()
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    EXCLUDE_ARGS+=(--exclude="$pattern")
done

# Sync .claude/ directory using rsync
log "Syncing .claude/ directory (excluding sensitive files)..."

rsync -av --delete \
    "${EXCLUDE_ARGS[@]}" \
    "$SOURCE_CLAUDE_DIR/" \
    "$TARGET_CLAUDE_DIR/" \
    >> "$LOG_FILE" 2>&1

if [[ $? -eq 0 ]]; then
    log_success "Files synced successfully"
else
    log_error "rsync failed"
    exit 1
fi

# Git operations in public repo
cd "$PUBLIC_REPO_PATH" || exit 1

# Check if there are changes
if [[ -z $(git status --porcelain) ]]; then
    log_warning "No changes to sync"
    exit 0
fi

log "Changes detected. Preparing commit..."

# Show what changed
echo ""
log "Files changed:"
git status --short | tee -a "$LOG_FILE"
echo ""

# Stage all changes
git add .claude/ >> "$LOG_FILE" 2>&1

# Create commit
COMMIT_MSG="chore: sync Claude Code configuration

Auto-synced from main Wythm repository

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

git commit -m "$COMMIT_MSG" >> "$LOG_FILE" 2>&1

if [[ $? -eq 0 ]]; then
    log_success "Commit created successfully"
else
    log_error "Failed to create commit"
    exit 1
fi

# Push to remote
log "Pushing to GitHub..."

git push origin main >> "$LOG_FILE" 2>&1

if [[ $? -eq 0 ]]; then
    log_success "Successfully pushed to GitHub"
    echo ""
    log_success "Sync complete! View at: https://github.com/alexandrbasis/wythm-claude-workflows"
else
    log_error "Failed to push to GitHub"
    log_warning "Commit created locally but not pushed. You can push manually with:"
    log_warning "  cd $PUBLIC_REPO_PATH && git push origin main"
    exit 1
fi

# Summary
echo ""
log "=== Sync Summary ==="
log "Source: $SOURCE_CLAUDE_DIR"
log "Target: $TARGET_CLAUDE_DIR"
log "Excluded patterns: ${EXCLUDE_PATTERNS[*]}"
log "===================="
echo ""
