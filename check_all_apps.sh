#!/bin/bash
echo "=== ALL APPS STATUS CHECK ==="
echo ""

APPS=("rnd_nutrition" "rnd_warehouse_management" "amb_w_tds")

for app in "${APPS[@]}"; do
    echo "📦 $app:"
    cd ~/frappe-bench/apps/"$app" 2>/dev/null || {
        echo "  ⚠️  Directory not found"
        continue
    }
    
    # Git status
    if [[ -d .git ]]; then
        echo "  ✅ Git repository"
        echo "  Branch: $(git branch --show-current 2>/dev/null || echo 'unknown')"
        
        # Check if remote is set
        remote_url=$(git remote get-url origin 2>/dev/null || echo "none")
        echo "  Remote: $remote_url"
        
        # Check if ahead/behind
        git fetch origin 2>/dev/null
        ahead=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "?")
        behind=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "?")
        echo "  Status: Ahead: $ahead, Behind: $behind"
        
        # Check for uncommitted changes
        if [[ -n "$(git status --porcelain)" ]]; then
            echo "  ⚠️  Uncommitted changes"
        else
            echo "  ✅ Clean working directory"
        fi
    else
        echo "  ⚠️  Not a Git repository"
    fi
    
    echo ""
done

echo "=== SSH STATUS ==="
ssh -T git@github.com 2>&1 | head -1
echo ""
echo "=== FRAMEWORK STATUS ==="
echo "frappe-cloud-git-framework:"
cd ~/frappe-cloud-git-framework && {
    echo "  Branch: $(git branch --show-current)"
    echo "  Remote: $(git remote get-url origin)"
    echo "  URL: https://github.com/rogerboy38/frappe-cloud-git-framework"
}
