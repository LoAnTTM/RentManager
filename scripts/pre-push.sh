#!/bin/bash
# =================================
# Pre-push Hook - Run CI checks before push
# =================================

# Get repo root directory (works from any location)
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Check if CI_CHECK_QUICK env var is set (for faster checks)
if [ "$CI_CHECK_QUICK" = "1" ]; then
    echo "⚡ Running quick CI checks..."
    cd "$REPO_ROOT" && make ci-quick
else
    # Run full CI checks
    "$REPO_ROOT/scripts/ci-check.sh"
fi

# If CI checks fail, prevent push
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Pre-push checks failed. Push aborted."
    echo "💡 To skip checks (not recommended): git push --no-verify"
    exit 1
fi

exit 0

