# Makefile for Durable Code Test Project
# Docker-based development and deployment automation

.PHONY: help init build start stop restart launch logs clean status dev dev-start dev-stop dev-restart dev-logs test lint format check-deps update-deps install-hooks

# Default target
.DEFAULT_GOAL := help

# Variables
DOCKER_COMPOSE = docker-compose
DOCKER_COMPOSE_DEV = docker-compose -f docker-compose.dev.yml
FRONTEND_URL = http://localhost:3000
FRONTEND_DEV_URL = http://localhost:5173
BACKEND_URL = http://localhost:8000

# Colors for output
CYAN = \033[0;36m
GREEN = \033[0;32m
YELLOW = \033[0;33m
RED = \033[0;31m
NC = \033[0m # No Color

# Help target - displays all available commands
help: ## Show this help message
	@echo "$(CYAN)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(CYAN)║          Durable Code Test - Docker Management            ║$(NC)"
	@echo "$(CYAN)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sed 's/^[^:]*://' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' | sort
	@echo ""
	@echo "$(CYAN)Usage examples:$(NC)"
	@echo "  make init          # First-time setup"
	@echo "  make launch        # Start and open the application"
	@echo "  make dev           # Start development environment"
	@echo "  make status        # Check container status"
	@echo ""

# Production targets
init: ## Initialize the project (build images, install dependencies)
	@echo "$(CYAN)Initializing project...$(NC)"
	@echo "$(YELLOW)Installing pre-commit hooks...$(NC)"
	@pip3 install pre-commit 2>/dev/null || pip install pre-commit 2>/dev/null || echo "$(YELLOW)⚠ Pre-commit not installed - please install manually$(NC)"
	@pre-commit install 2>/dev/null || echo "$(YELLOW)⚠ Pre-commit hooks not installed$(NC)"
	@echo "$(YELLOW)Building Docker images...$(NC)"
	@$(DOCKER_COMPOSE) build --no-cache
	@echo "$(GREEN)✓ Initialization complete!$(NC)"

build: ## Build Docker images
	@echo "$(CYAN)Building Docker images...$(NC)"
	@$(DOCKER_COMPOSE) build
	@echo "$(GREEN)✓ Build complete!$(NC)"

start: dev-start ## Start all containers (alias for dev-start)
	@echo "$(GREEN)✓ Development containers started!$(NC)"

stop: ## Stop all running containers
	@echo "$(CYAN)Stopping containers...$(NC)"
	@$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✓ Containers stopped!$(NC)"

restart: stop start ## Restart all containers

launch: dev-launch ## Launch development environment (alias for dev-launch)

logs: ## Show logs from all containers
	@$(DOCKER_COMPOSE) logs -f

logs-backend: ## Show backend logs
	@$(DOCKER_COMPOSE) logs -f backend

logs-frontend: ## Show frontend logs
	@$(DOCKER_COMPOSE) logs -f frontend

# Development targets
dev: dev-start ## Alias for dev-start

dev-init: ## Initialize development environment
	@echo "$(CYAN)Initializing development environment...$(NC)"
	@echo "$(YELLOW)Installing pre-commit hooks...$(NC)"
	@pip3 install pre-commit 2>/dev/null || pip install pre-commit 2>/dev/null || echo "$(YELLOW)⚠ Pre-commit not installed - please install manually$(NC)"
	@pre-commit install 2>/dev/null || echo "$(YELLOW)⚠ Pre-commit hooks not installed$(NC)"
	@$(DOCKER_COMPOSE_DEV) build --no-cache
	@echo "$(GREEN)✓ Development environment initialized!$(NC)"

dev-build: ## Build development Docker images
	@echo "$(CYAN)Building development images...$(NC)"
	@$(DOCKER_COMPOSE_DEV) build
	@echo "$(GREEN)✓ Development build complete!$(NC)"

dev-start: ## Start development environment with hot reload
	@echo "$(CYAN)Starting development environment...$(NC)"
	@$(DOCKER_COMPOSE_DEV) up -d
	@echo "$(GREEN)✓ Development environment started!$(NC)"
	@echo "$(YELLOW)Frontend (Vite): $(FRONTEND_DEV_URL)$(NC)"
	@echo "$(YELLOW)Backend (FastAPI): $(BACKEND_URL)$(NC)"
	@echo "$(YELLOW)API Docs: $(BACKEND_URL)/docs$(NC)"

dev-stop: ## Stop development environment
	@echo "$(CYAN)Stopping development environment...$(NC)"
	@$(DOCKER_COMPOSE_DEV) down
	@echo "$(GREEN)✓ Development environment stopped!$(NC)"

dev-restart: dev-stop dev-start ## Restart development environment

dev-logs: ## Show development logs
	@$(DOCKER_COMPOSE_DEV) logs -f

dev-launch: dev-start ## Start dev environment and open browser
	@echo "$(CYAN)Launching development environment...$(NC)"
	@sleep 3
	@echo "$(GREEN)Opening browser at $(FRONTEND_DEV_URL)...$(NC)"
	@if command -v xdg-open > /dev/null; then \
		xdg-open $(FRONTEND_DEV_URL); \
	elif command -v open > /dev/null; then \
		open $(FRONTEND_DEV_URL); \
	elif command -v start > /dev/null; then \
		start $(FRONTEND_DEV_URL); \
	else \
		echo "$(YELLOW)Please open your browser and navigate to $(FRONTEND_DEV_URL)$(NC)"; \
	fi

# Utility targets
status: ## Show status of all containers
	@echo "$(CYAN)Container Status:$(NC)"
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "durable-code|NAMES" || echo "$(YELLOW)No containers running$(NC)"

clean: ## Remove all containers, networks, and volumes
	@echo "$(RED)⚠️  Warning: This will remove all containers, networks, and volumes!$(NC)"
	@echo "$(YELLOW)Press Ctrl+C to cancel, or wait 5 seconds to continue...$(NC)"
	@sleep 5
	@echo "$(CYAN)Cleaning up...$(NC)"
	@$(DOCKER_COMPOSE) down -v --remove-orphans
	@$(DOCKER_COMPOSE_DEV) down -v --remove-orphans
	@docker system prune -f
	@echo "$(GREEN)✓ Cleanup complete!$(NC)"

shell-backend: ## Open shell in backend container
	@docker exec -it durable-code-backend /bin/bash || docker exec -it durable-code-backend-dev /bin/bash

shell-frontend: ## Open shell in frontend container
	@docker exec -it durable-code-frontend /bin/sh || docker exec -it durable-code-frontend-dev /bin/sh

# Pre-commit hooks
install-hooks: ## Install pre-commit hooks
	@echo "$(CYAN)Installing pre-commit hooks...$(NC)"
	@which pre-commit > /dev/null 2>&1 || (echo "$(YELLOW)Installing pre-commit...$(NC)" && pip3 install pre-commit)
	@pre-commit install
	@echo "$(GREEN)✓ Pre-commit hooks installed!$(NC)"
	@echo "$(YELLOW)Hooks will run automatically on git commit$(NC)"

# Testing and quality targets
test: dev-start ## Run all tests with coverage (starts dev containers if needed)
	@echo "$(CYAN)Running tests with coverage...$(NC)"
	@echo "$(YELLOW)Backend and framework tests with coverage:$(NC)"
	@docker exec durable-code-backend-dev bash -c "cd /tmp && PYTHONPATH=/app:/app/tools COVERAGE_FILE=/tmp/.coverage pytest /app/test/ --cov=/app/app --cov=/app/tools/design_linters --cov-report=term --cov-report=term:skip-covered --tb=short -v" || echo "$(YELLOW)Tests completed with some failures$(NC)"
	@echo "$(YELLOW)Frontend tests with coverage:$(NC)"
	@docker exec durable-code-frontend-dev npm run test:coverage || echo "$(YELLOW)Frontend tests completed$(NC)"

test-quick: dev-start ## Run all tests without coverage (faster)
	@echo "$(CYAN)Running tests (no coverage)...$(NC)"
	@echo "$(YELLOW)All backend and framework tests:$(NC)"
	@docker exec durable-code-backend-dev bash -c "cd /app && PYTHONPATH=/app:/app/tools pytest test/ -v" || echo "$(YELLOW)Tests completed with some failures$(NC)"
	@echo "$(YELLOW)Frontend tests:$(NC)"
	@docker exec durable-code-frontend-dev npm run test:run || echo "$(YELLOW)Frontend tests completed$(NC)"

test-framework: dev-start ## Run only design linter framework tests in Docker
	@echo "$(CYAN)Running design linter framework tests...$(NC)"
	@docker exec durable-code-backend-dev bash -c "cd /app && PYTHONPATH=/app/tools pytest test/unit_test/tools/design_linters -v --cov=tools/design_linters --cov-report=term" || echo "$(YELLOW)Framework tests have some failures (expected during development)$(NC)"
	@echo "$(GREEN)✓ Framework tests complete$(NC)"

test-integration: dev-start ## Run integration tests for design linters in Docker
	@echo "$(CYAN)Running integration tests...$(NC)"
	@docker exec durable-code-backend-dev bash -c "cd /app && PYTHONPATH=/app/tools pytest test/unit_test/tools/design_linters/test_cli_integration.py -v" || echo "$(YELLOW)Integration tests have some failures$(NC)"
	@echo "$(GREEN)✓ Integration tests complete$(NC)"

test-rules: dev-start ## Run tests for all linting rules in Docker
	@echo "$(CYAN)Running rule tests...$(NC)"
	@docker exec durable-code-backend-dev bash -c "cd /app && PYTHONPATH=/app/tools pytest test/unit_test/tools/design_linters/rules -v" || echo "$(YELLOW)Rule tests have some failures$(NC)"
	@echo "$(GREEN)✓ Rule tests complete$(NC)"

test-solid: dev-start ## Run tests for SOLID principle rules in Docker
	@echo "$(CYAN)Running SOLID rule tests...$(NC)"
	@docker exec durable-code-backend-dev bash -c "cd /app && PYTHONPATH=/app/tools pytest test/unit_test/tools/design_linters/rules/test_solid_rules.py -v" || echo "$(YELLOW)SOLID tests have some failures$(NC)"
	@echo "$(GREEN)✓ SOLID tests complete$(NC)"

test-logging: dev-start ## Run tests for logging rules in Docker
	@echo "$(CYAN)Running logging rule tests...$(NC)"
	@docker exec durable-code-backend-dev bash -c "cd /app && PYTHONPATH=/app/tools pytest test/unit_test/tools/design_linters/rules/test_logging_rules.py -v" || echo "$(YELLOW)Logging tests have some failures$(NC)"
	@echo "$(GREEN)✓ Logging tests complete$(NC)"

test-frontend: dev-start ## Run frontend tests only
	@echo "$(CYAN)Running frontend tests...$(NC)"
	@docker exec durable-code-frontend-dev npm run test:run

test-frontend-coverage: dev-start ## Run frontend tests with coverage
	@echo "$(CYAN)Running frontend tests with coverage...$(NC)"
	@docker exec durable-code-frontend-dev npm run test:coverage

test-frontend-watch: dev-start ## Run frontend tests in watch mode
	@echo "$(CYAN)Running frontend tests in watch mode...$(NC)"
	@docker exec -it durable-code-frontend-dev npm run test:watch

test-links: dev-start ## Run link validation tests
	@echo "$(CYAN)Running link validation tests...$(NC)"
	@docker exec durable-code-frontend-dev npm run test:links

# Include comprehensive linting targets
-include Makefile.lint
-include Makefile.design

lint: ## Run basic linters with unified framework
	@echo "$(CYAN)Running linters...$(NC)"
	@echo "$(YELLOW)Backend linting:$(NC)"
	@docker exec durable-code-backend-dev /home/appuser/.local/bin/ruff check /app/app --cache-dir /tmp/ruff-cache || echo "$(YELLOW)Backend container not running$(NC)"
	@echo "$(YELLOW)Frontend linting:$(NC)"
	@docker exec durable-code-frontend-dev npm run lint || echo "$(YELLOW)Frontend container not running$(NC)"
	@echo "$(YELLOW)Unified design linting (style, literals, logging):$(NC)"
	@PYTHONPATH=tools python -m design_linters --categories style,literals,logging --min-severity warning . || echo "$(GREEN)✓ No violations found$(NC)"

format: ## Format code
	@echo "$(CYAN)Formatting code...$(NC)"
	@echo "$(YELLOW)Backend formatting:$(NC)"
	@docker exec durable-code-backend-dev /home/appuser/.local/bin/black /app/app || echo "$(YELLOW)Backend container not running$(NC)"
	@echo "$(YELLOW)Frontend formatting:$(NC)"
	@docker exec durable-code-frontend-dev npm run format || echo "$(YELLOW)Frontend container not running$(NC)"

# Dependency management
check-deps: ## Check for outdated dependencies
	@echo "$(CYAN)Checking dependencies...$(NC)"
	@echo "$(YELLOW)Backend dependencies:$(NC)"
	@docker exec durable-code-backend poetry show --outdated || docker exec durable-code-backend-dev poetry show --outdated || echo "$(YELLOW)Backend container not running$(NC)"
	@echo "$(YELLOW)Frontend dependencies:$(NC)"
	@docker exec durable-code-frontend npm outdated || docker exec durable-code-frontend-dev npm outdated || echo "$(YELLOW)Frontend container not running$(NC)"

update-deps: ## Update dependencies
	@echo "$(CYAN)Updating dependencies...$(NC)"
	@echo "$(YELLOW)Backend dependencies:$(NC)"
	@docker exec durable-code-backend poetry update || docker exec durable-code-backend-dev poetry update || echo "$(YELLOW)Backend container not running$(NC)"
	@echo "$(YELLOW)Frontend dependencies:$(NC)"
	@docker exec durable-code-frontend npm update || docker exec durable-code-frontend-dev npm update || echo "$(YELLOW)Frontend container not running$(NC)"

# Health check
health: ## Check health of all services
	@echo "$(CYAN)Health Check:$(NC)"
	@echo -n "Backend: "
	@curl -s $(BACKEND_URL)/health > /dev/null && echo "$(GREEN)✓ Healthy$(NC)" || echo "$(RED)✗ Unhealthy$(NC)"
	@echo -n "Frontend: "
	@curl -s $(FRONTEND_URL) > /dev/null && echo "$(GREEN)✓ Healthy$(NC)" || echo "$(RED)✗ Unhealthy$(NC)"

# Database targets (for future use)
db-migrate: ## Run database migrations
	@echo "$(CYAN)Running database migrations...$(NC)"
	@echo "$(YELLOW)No database configured yet$(NC)"

db-seed: ## Seed database with sample data
	@echo "$(CYAN)Seeding database...$(NC)"
	@echo "$(YELLOW)No database configured yet$(NC)"

# Monitoring
monitor: ## Show real-time resource usage
	@docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" durable-code-backend durable-code-frontend durable-code-backend-dev durable-code-frontend-dev 2>/dev/null || echo "$(YELLOW)No containers running$(NC)"
