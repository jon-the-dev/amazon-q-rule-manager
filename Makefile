.PHONY: help sync-frontend install-hooks dev-frontend build-frontend clean update-catalog

help: ## Show this help message
	@echo "Amazon Q Rule Manager - Development Commands"
	@echo "============================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

update-catalog: ## Update the rules catalog from rule files
	@echo "📋 Updating rules catalog..."
	@python3 update_json.py

sync-frontend: update-catalog ## Sync catalog and rules data to frontend
	@echo "🔄 Syncing frontend data..."
	@python3 scripts/sync-frontend-data.py

install-hooks: ## Install Git hooks for automatic syncing
	@echo "🪝 Installing Git hooks..."
	@python3 scripts/install-hooks.py

dev-frontend: sync-frontend ## Start frontend development server
	@echo "🚀 Starting frontend development server..."
	@cd frontend && npm start

build-frontend: sync-frontend ## Build frontend for production
	@echo "🏗️  Building frontend..."
	@cd frontend && npm run build

clean: ## Clean build artifacts
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf frontend/build/
	@rm -rf frontend/node_modules/
	@rm -rf dist/
	@rm -rf *.egg-info/

test: ## Run Python tests
	@echo "🧪 Running tests..."
	@pytest --cov=amazon_q_rule_manager

lint: ## Run linting
	@echo "🔍 Running linters..."
	@flake8 amazon_q_rule_manager
	@mypy amazon_q_rule_manager

format: ## Format code
	@echo "✨ Formatting code..."
	@black amazon_q_rule_manager/
	@black scripts/

install-dev: ## Install development dependencies
	@echo "📦 Installing development dependencies..."
	@pip install -e ".[dev]"
	@cd frontend && npm install

setup-dev: install-dev install-hooks sync-frontend ## Complete development setup
	@echo "✅ Development environment setup complete!"
	@echo "   Run 'make dev-frontend' to start the frontend server"
	@echo "   Run 'make help' to see all available commands"
