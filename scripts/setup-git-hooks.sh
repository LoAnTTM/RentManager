#!/bin/bash
# =================================
# Setup Git Hooks
# =================================

set -e

echo "🔧 Setting up Git hooks..."

# Make scripts executable
chmod +x scripts/ci-check.sh
chmod +x scripts/pre-push.sh

# Setup pre-push hook
if [ -d ".git" ]; then
    mkdir -p .git/hooks
    
    # Create pre-push hook that calls our script
    cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
# Pre-push hook - Run CI checks
REPO_ROOT="$(git rev-parse --show-toplevel)"
"$REPO_ROOT/scripts/pre-push.sh"
EOF
    
    chmod +x .git/hooks/pre-push
    echo "✅ Pre-push hook installed"
    echo "   CI checks will run automatically before git push"
else
    echo "⚠️  Not a git repository, skipping hook installation"
fi

echo ""
echo "✅ Git hooks setup complete!"
echo ""
echo "💡 Usage:"
echo "   - Run CI checks manually: make ci-check"
echo "   - Quick check (no Docker): make ci-quick"
echo "   - Skip hooks (not recommended): git push --no-verify"

