#!/bin/bash
# gitpush_rnd.sh - Fixed version for RND Nutrition

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
REMOTE="${GIT_REMOTE:-origin}"
REPO_URL="${GIT_REMOTE_URL:-git@github.com:rogerboy38/rnd_nutrition2.git}"
SCRIPT_VERSION="1.0.0"

print_status() { echo -e "${BLUE}➤${NC} $1"; }
print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }

show_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                   RND Nutrition Git Helper                   ║"
    echo "║                        Version $SCRIPT_VERSION                         ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo "Repository: https://github.com/rogerboy38/rnd_nutrition2"
    echo "Current Branch: $(git branch --show-current 2>/dev/null || echo 'unknown')"
    echo "================================================================"
}

# Main function
main() {
    show_header
    
    # Check SSH
    print_status "Testing SSH connection..."
    if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
        print_success "SSH connection verified"
    else
        print_error "SSH connection failed"
        return 1
    fi
    
    # Set remote if needed
    if ! git remote get-url origin > /dev/null 2>&1; then
        print_status "Setting remote origin..."
        git remote add origin "$REPO_URL"
        print_success "Remote set to: $REPO_URL"
    fi
    
    # Check for changes
    if [ -z "$(git status --porcelain)" ]; then
        print_status "No changes to commit"
        return 0
    fi
    
    # Add, commit, push
    print_status "Adding changes..."
    git add .
    
    COMMIT_MSG="${1:-Update: $(date '+%Y-%m-%d %H:%M:%S')}"
    print_status "Committing: $COMMIT_MSG"
    git commit -m "$COMMIT_MSG"
    
    BRANCH=$(git branch --show-current)
    print_status "Pushing to origin/$BRANCH..."
    git push origin "$BRANCH"
    
    print_success "✅ Push completed!"
}

main "$@"
