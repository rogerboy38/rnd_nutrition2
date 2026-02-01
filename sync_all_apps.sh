#!/bin/bash
echo "=== SYNC ALL APPS TO GITHUB ==="
echo ""

APPS=("rnd_nutrition" "rnd_warehouse_management" "amb_w_tds")

for app in "${APPS[@]}"; do
    echo "🔄 Syncing $app..."
    cd ~/frappe-bench/apps/"$app" 2>/dev/null || {
        echo "  ❌ Directory not found"
        continue
    }
    
    # Check if it's a git repo
    if [[ ! -d .git ]]; then
        echo "  ⚠️  Not a Git repository"
        continue
    fi
    
    # Get current branch
    current_branch=$(git branch --show-current 2>/dev/null || echo "")
    if [[ -z "$current_branch" ]]; then
        echo "  ⚠️  Detached HEAD - fixing..."
        git checkout -b main 2>/dev/null || git checkout main
        current_branch="main"
    fi
    
    # Add any changes
    if [[ -n "$(git status --porcelain)" ]]; then
        echo "  📝 Committing changes..."
        git add .
        git commit -m "Update: $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    # Push to GitHub
    echo "  📤 Pushing to GitHub..."
    if git push origin "$current_branch"; then
        echo "  ✅ $app synchronized"
    else
        echo "  ⚠️  Push failed. Trying with force..."
        git push origin "$current_branch" --force-with-lease && \
        echo "  ✅ $app force-pushed" || \
        echo "  ❌ $app still failing"
    fi
    
    echo ""
done

echo "=== SYNC COMPLETE ==="
echo ""
echo "All apps should now be synchronized with GitHub."
echo "Check: https://github.com/rogerboy38"
