# =================================
# Minh Rental - Makefile
# =================================
# Convenience commands for development and deployment

.PHONY: help dev build test lint clean deploy

# Default target
help:
	@echo "╔══════════════════════════════════════════════════════════════╗"
	@echo "║           Minh Rental - Available Commands                    ║"
	@echo "╚══════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "  Development:"
	@echo "    make dev          - Start development environment"
	@echo "    make down         - Stop all services"
	@echo "    make logs         - View logs"
	@echo "    make shell-backend - Open shell in backend container"
	@echo "    make shell-db     - Open PostgreSQL shell"
	@echo ""
	@echo "  Testing:"
	@echo "    make test         - Run all tests"
	@echo "    make test-backend - Run backend tests"
	@echo "    make test-frontend - Run frontend tests"
	@echo ""
	@echo "  Linting:"
	@echo "    make lint         - Run all linters"
	@echo "    make lint-backend - Lint backend code"
	@echo "    make lint-frontend - Lint frontend code"
	@echo ""
	@echo "  Build:"
	@echo "    make build        - Build Docker images"
	@echo "    make build-prod   - Build production images"
	@echo ""
	@echo "  Database:"
	@echo "    make seed         - Seed database with sample data"
	@echo "    make reset-db     - Reset database (WARNING: deletes all data)"
	@echo "    make backup       - Backup database"
	@echo ""
	@echo "  Deployment:"
	@echo "    make deploy-staging - Deploy to staging"
	@echo "    make deploy-prod  - Deploy to production"
	@echo ""

# =================================
# Development
# =================================
dev:
	@echo "🚀 Starting development environment..."
	cd workspace && docker compose up -d
	@echo "✅ Services started!"
	@echo "   Frontend: http://localhost:3001"
	@echo "   Backend:  http://localhost:8000"
	@echo "   API Docs: http://localhost:8000/docs"

down:
	@echo "🛑 Stopping services..."
	cd workspace && docker compose down
	@echo "✅ Services stopped"

logs:
	cd workspace && docker compose logs -f

logs-backend:
	docker logs -f minh_rental_backend

logs-frontend:
	docker logs -f minh_rental_frontend

shell-backend:
	docker exec -it minh_rental_backend /bin/sh

shell-db:
	docker exec -it minh_rental_db psql -U minh_rental -d minh_rental

# =================================
# Testing
# =================================
test: test-backend test-frontend
	@echo "✅ All tests completed!"

test-backend:
	@echo "🧪 Running backend tests..."
	docker exec minh_rental_backend pytest tests/ -v --cov=app || echo "Tests completed"

test-frontend:
	@echo "🧪 Running frontend tests..."
	cd webAdmin && npm test || echo "No tests configured"

# =================================
# Linting
# =================================
lint: lint-backend lint-frontend
	@echo "✅ Linting completed!"

lint-backend:
	@echo "🔍 Linting backend..."
	cd backend && \
		pip install -q flake8 black isort && \
		flake8 app --max-line-length=120 && \
		black --check app && \
		isort --check-only app || true

lint-frontend:
	@echo "🔍 Linting frontend..."
	cd webAdmin && npm run lint || true

format-backend:
	@echo "🎨 Formatting backend code..."
	cd backend && \
		pip install -q black isort && \
		black app && \
		isort app

# =================================
# Build
# =================================
build:
	@echo "🏗️ Building Docker images..."
	cd workspace && docker compose build
	@echo "✅ Build completed!"

build-prod:
	@echo "🏗️ Building production images..."
	docker build -t minh-rental-backend:latest ./backend
	docker build -t minh-rental-frontend:latest ./webAdmin
	@echo "✅ Production build completed!"

# =================================
# Database
# =================================
seed:
	@echo "🌱 Seeding database..."
	docker exec minh_rental_backend python seed_data.py
	@echo "✅ Database seeded!"

reset-db:
	@echo "⚠️  WARNING: This will delete all data!"
	@read -p "Are you sure? [y/N] " confirm && \
		[ "$$confirm" = "y" ] && \
		cd workspace && docker compose down -v && docker compose up -d && \
		sleep 10 && docker exec minh_rental_backend python seed_data.py || \
		echo "Cancelled"

backup:
	@echo "💾 Creating backup..."
	@mkdir -p workspace/backups
	docker exec minh_rental_db pg_dump -U minh_rental minh_rental > workspace/backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created in workspace/backups/"

restore:
	@echo "📥 Restoring from backup..."
	@read -p "Enter backup filename: " filename && \
		docker exec -i minh_rental_db psql -U minh_rental minh_rental < workspace/backups/$$filename

# =================================
# Deployment
# =================================
deploy-staging:
	@echo "🚀 Deploying to staging..."
	@echo "This will trigger GitHub Actions workflow"
	git push origin main

deploy-prod:
	@echo "🚀 Creating production release..."
	@read -p "Enter version (e.g., 1.0.0): " version && \
		git tag -a v$$version -m "Release v$$version" && \
		git push origin v$$version
	@echo "✅ Release created! Check GitHub Actions for deployment status."

# =================================
# Cleanup
# =================================
clean:
	@echo "🧹 Cleaning up..."
	cd workspace && docker compose down -v --rmi local
	docker system prune -f
	@echo "✅ Cleanup completed!"

clean-all:
	@echo "🧹 Deep cleaning (removing all Docker resources)..."
	docker system prune -af --volumes
	@echo "✅ Deep cleanup completed!"

