#!/bin/bash
# =================================
# CI Check Script - Run locally before push
# =================================

set -e  # Exit on error

# Get repo root directory (works from any location)
if REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null); then
    # We're in a git repo
    :
else
    # Fallback: assume script is in scripts/ directory
    REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fi

# Verify directory exists
if [ ! -d "$REPO_ROOT" ]; then
    echo "❌ Error: Cannot find repository root directory"
    exit 1
fi

cd "$REPO_ROOT" || exit 1

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              Running CI Checks Locally                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Track failures
FAILED=0

# =================================
# Backend Checks
# =================================
echo -e "${YELLOW}🔍 Checking Backend...${NC}"
cd "$REPO_ROOT/backend" || exit 1

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    FAILED=1
else
    # Install dependencies if needed
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    echo "📦 Installing backend dependencies..."
    pip install -q -r requirements.txt
    pip install -q pytest pytest-cov flake8 black isort mypy httpx
    
    # Lint
    echo "🔍 Running flake8..."
    if flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics; then
        echo -e "${GREEN}✅ flake8 (errors) passed${NC}"
    else
        echo -e "${RED}❌ flake8 (errors) failed${NC}"
        FAILED=1
    fi
    
    if flake8 app --count --exit-zero --max-complexity=10 --max-line-length=120 --statistics; then
        echo -e "${GREEN}✅ flake8 (warnings) passed${NC}"
    else
        echo -e "${YELLOW}⚠️  flake8 has warnings (non-blocking)${NC}"
    fi
    
    # Format check
    echo "🎨 Checking code formatting (black)..."
    if black --check --diff app; then
        echo -e "${GREEN}✅ black formatting check passed${NC}"
    else
        echo -e "${RED}❌ Code formatting issues found. Run: make format-backend${NC}"
        FAILED=1
    fi
    
    # Import sorting
    echo "📋 Checking import sorting (isort)..."
    if isort --check-only --diff app; then
        echo -e "${GREEN}✅ isort check passed${NC}"
    else
        echo -e "${RED}❌ Import sorting issues found. Run: isort app${NC}"
        FAILED=1
    fi
    
    # Type check (non-blocking)
    echo "🔬 Running type check (mypy)..."
    if mypy app --ignore-missing-imports; then
        echo -e "${GREEN}✅ mypy type check passed${NC}"
    else
        echo -e "${YELLOW}⚠️  mypy found issues (non-blocking)${NC}"
    fi
    
    # Tests (if tests exist and PostgreSQL is available)
    if [ -d "tests" ] && [ "$(ls -A tests/*.py 2>/dev/null)" ]; then
        echo "🧪 Running tests..."
        # Check if PostgreSQL is available
        if command -v psql &> /dev/null && pg_isready -h localhost -p 5432 &> /dev/null; then
            if pytest tests/ -v --tb=short; then
                echo -e "${GREEN}✅ Backend tests passed${NC}"
            else
                echo -e "${RED}❌ Backend tests failed${NC}"
                FAILED=1
            fi
        else
            echo -e "${YELLOW}⚠️  PostgreSQL not available, skipping tests (expected in local CI)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  No tests found, skipping...${NC}"
    fi
    
    deactivate
fi

echo ""

# =================================
# Frontend Checks
# =================================
echo -e "${YELLOW}🔍 Checking Frontend...${NC}"
cd "$REPO_ROOT/webAdmin" || exit 1

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found${NC}"
    FAILED=1
else
    # Install dependencies
    echo "📦 Installing frontend dependencies..."
    npm ci --silent
    
    # Type check
    echo "🔬 Running TypeScript type check..."
    if npx tsc --noEmit; then
        echo -e "${GREEN}✅ TypeScript type check passed${NC}"
    else
        echo -e "${RED}❌ TypeScript type check failed${NC}"
        FAILED=1
    fi
    
    # Lint (skip if ESLint not configured)
    if [ -f ".eslintrc.json" ] || [ -f ".eslintrc.js" ] || [ -f "eslint.config.js" ]; then
        echo "🔍 Running ESLint..."
        if npm run lint; then
            echo -e "${GREEN}✅ ESLint passed${NC}"
        else
            echo -e "${YELLOW}⚠️  ESLint found issues (non-blocking)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  ESLint not configured, skipping...${NC}"
    fi
    
    # Build check
    echo "🏗️  Building frontend..."
    if NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 npm run build; then
        echo -e "${GREEN}✅ Frontend build passed${NC}"
    else
        echo -e "${RED}❌ Frontend build failed${NC}"
        FAILED=1
    fi
fi

echo ""

# =================================
# Docker Build Check
# =================================
echo -e "${YELLOW}🐳 Checking Docker builds...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker not found, skipping Docker checks${NC}"
else
    cd "$REPO_ROOT" || exit 1
    
    # Build backend image
    echo "🏗️  Building backend Docker image..."
    if docker build -t minh-rental-backend:test ./backend > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend Docker build passed${NC}"
    else
        echo -e "${RED}❌ Backend Docker build failed${NC}"
        FAILED=1
    fi
    
    # Build frontend image
    echo "🏗️  Building frontend Docker image..."
    if docker build -t minh-rental-frontend:test ./webAdmin > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend Docker build passed${NC}"
    else
        echo -e "${RED}❌ Frontend Docker build failed${NC}"
        FAILED=1
    fi
    
    # Cleanup test images
    docker rmi minh-rental-backend:test minh-rental-frontend:test > /dev/null 2>&1 || true
fi

echo ""

# =================================
# Summary
# =================================
if [ $FAILED -eq 0 ]; then
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo -e "║  ${GREEN}✅ All CI checks passed! Safe to push.${NC}                    ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    exit 0
else
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo -e "║  ${RED}❌ Some CI checks failed. Please fix before pushing.${NC}        ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    exit 1
fi

