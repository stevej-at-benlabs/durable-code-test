# Makefile for Durable Code Test Project
# Docker-based development and deployment automation

.PHONY: help init build start stop restart launch logs clean status dev dev-start dev-stop dev-restart dev-logs test lint format check-deps update-deps install-hooks

# Default target
.DEFAULT_GOAL := help

# Variables
# Get current git branch name, sanitized for Docker container names
# In CI, use GITHUB_HEAD_REF for PRs or GITHUB_REF_NAME for pushes
ifdef GITHUB_ACTIONS
  ifdef GITHUB_HEAD_REF
    BRANCH_NAME := $(shell echo "$(GITHUB_HEAD_REF)" | tr '/' '-' | tr '[:upper:]' '[:lower:]')
  else
    BRANCH_NAME := $(shell echo "$(GITHUB_REF_NAME)" | tr '/' '-' | tr '[:upper:]' '[:lower:]')
  endif
else
  BRANCH_NAME := $(shell git rev-parse --abbrev-ref HEAD 2>/dev/null | tr '/' '-' | tr '[:upper:]' '[:lower:]' || echo "main")
endif
export BRANCH_NAME

# Calculate dynamic ports based on branch name
# Note: We need to parse the export statements from the script
FRONTEND_PORT := $(shell ./scripts/get-branch-ports.sh "$(BRANCH_NAME)" export 2>/dev/null | grep FRONTEND_PORT | cut -d= -f2 || echo "5173")
BACKEND_PORT := $(shell ./scripts/get-branch-ports.sh "$(BRANCH_NAME)" export 2>/dev/null | grep BACKEND_PORT | cut -d= -f2 || echo "8000")
export FRONTEND_PORT
export BACKEND_PORT

DOCKER_COMPOSE = docker compose
DOCKER_COMPOSE_DEV = BRANCH_NAME=$(BRANCH_NAME) FRONTEND_PORT=$(FRONTEND_PORT) BACKEND_PORT=$(BACKEND_PORT) docker compose -f docker-compose.dev.yml
FRONTEND_URL = http://localhost:3000
FRONTEND_DEV_URL = http://localhost:$(FRONTEND_PORT)
BACKEND_URL = http://localhost:$(BACKEND_PORT)

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

stop: ## Stop containers for current branch
	@echo "$(CYAN)Stopping containers for branch: $(BRANCH_NAME)...$(NC)"
	@$(DOCKER_COMPOSE_DEV) down
	@echo "$(GREEN)✓ Containers for branch $(BRANCH_NAME) stopped!$(NC)"

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

port-status: ## Show port assignments for all branches
	@echo "$(CYAN)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(CYAN)║                Port Assignments by Branch                  ║$(NC)"
	@echo "$(CYAN)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)Current Branch: $(BRANCH_NAME)$(NC)"
	@./scripts/get-branch-ports.sh "$(BRANCH_NAME)" urls
	@echo ""
	@echo "$(CYAN)Running Containers:$(NC)"
	@docker ps --format "table {{.Names}}\t{{.Ports}}" | grep -E "durable-code.*-dev|NAMES" || echo "$(YELLOW)No dev containers running$(NC)"
	@echo ""
	@echo "$(YELLOW)Tip: Each branch gets unique ports to avoid conflicts$(NC)"
	@echo "$(YELLOW)Main/master/develop branches always use default ports (5173, 8000)$(NC)"

branch-ports: ## Display URLs for current branch
	@echo "$(CYAN)URLs for branch '$(BRANCH_NAME)':$(NC)"
	@./scripts/get-branch-ports.sh "$(BRANCH_NAME)" urls

show-ports: ## Show all active port mappings
	@echo "$(CYAN)Active Port Mappings:$(NC)"
	@docker ps --format "table {{.Names}}\t{{.Ports}}" | grep -E "0\.0\.0\.0|NAMES" || echo "$(YELLOW)No port mappings found$(NC)"

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
	@docker exec -it durable-code-backend /bin/bash || docker exec -it durable-code-backend-$(BRANCH_NAME)-dev /bin/bash

shell-frontend: ## Open shell in frontend container
	@docker exec -it durable-code-frontend /bin/sh || docker exec -it durable-code-frontend-$(BRANCH_NAME)-dev /bin/sh

# Pre-commit hooks
install-hooks: ## Install pre-commit hooks
	@echo "$(CYAN)Installing pre-commit hooks...$(NC)"
	@which pre-commit > /dev/null 2>&1 || (echo "$(YELLOW)Installing pre-commit...$(NC)" && pip3 install pre-commit)
	@pre-commit install
	@echo "$(GREEN)✓ Pre-commit hooks installed!$(NC)"
	@echo "$(YELLOW)Hooks will run automatically on git commit$(NC)"

pre-commit: lint-all-staged ## Run pre-commit checks on staged files only
	@echo "$(GREEN)✅ Ready to commit!$(NC)"

# Local GitHub Actions simulation
mock-push-local: ## Simulate GitHub Actions locally using act
	@echo "$(CYAN)Running GitHub Actions locally with act...$(NC)"
	@echo "$(YELLOW)This will run the Test Suite workflow locally$(NC)"
	@. ./.env && act --workflows .github/workflows/test.yml --secret GITHUB_TOKEN=$$GH_TOKEN --verbose

mock-push-local-fast: ## Run act with faster settings (skip heavy containers)
	@echo "$(CYAN)Running GitHub Actions locally (fast mode)...$(NC)"
	@. ./.env && act --workflows .github/workflows/test.yml --platform ubuntu-latest=catthehacker/ubuntu:act-latest --secret GITHUB_TOKEN=$$GH_TOKEN --verbose

mock-push-local-debug: ## Run act in debug mode with shell access
	@echo "$(CYAN)Running GitHub Actions locally in debug mode...$(NC)"
	@echo "$(YELLOW)Use 'exit' to continue to next step$(NC)"
	@. ./.env && act --workflows .github/workflows/test.yml --secret GITHUB_TOKEN=$$GH_TOKEN --verbose --shell

# Include comprehensive linting and testing targets
-include Makefile.lint
-include Makefile.test
-include Makefile.gh

# Dependency management
check-deps: ## Check for outdated dependencies
	@echo "$(CYAN)Checking dependencies...$(NC)"
	@echo "$(YELLOW)Backend dependencies:$(NC)"
	@docker exec durable-code-backend poetry show --outdated || docker exec durable-code-backend-$(BRANCH_NAME)-dev poetry show --outdated || echo "$(YELLOW)Backend container not running$(NC)"
	@echo "$(YELLOW)Frontend dependencies:$(NC)"
	@docker exec durable-code-frontend npm outdated || docker exec durable-code-frontend-$(BRANCH_NAME)-dev npm outdated || echo "$(YELLOW)Frontend container not running$(NC)"

update-deps: ## Update dependencies
	@echo "$(CYAN)Updating dependencies...$(NC)"
	@echo "$(YELLOW)Backend dependencies:$(NC)"
	@docker exec durable-code-backend poetry update || docker exec durable-code-backend-$(BRANCH_NAME)-dev poetry update || echo "$(YELLOW)Backend container not running$(NC)"
	@echo "$(YELLOW)Frontend dependencies:$(NC)"
	@docker exec durable-code-frontend npm update || docker exec durable-code-frontend-$(BRANCH_NAME)-dev npm update || echo "$(YELLOW)Frontend container not running$(NC)"

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

# Page content check
check-page: ## Check if the frontend page renders content properly
	@echo "$(CYAN)Checking page content...$(NC)"
	@docker exec durable-code-frontend-dev node /app/scripts/simple-check.js || echo "$(RED)Page check failed$(NC)"

check-page-full: ## Full page check with Playwright (requires setup)
	@echo "$(CYAN)Full page content check...$(NC)"
	@docker exec durable-code-frontend-dev node /app/scripts/check-page-content.js || echo "$(RED)Full page check failed$(NC)"

check-page-watch: ## Watch page content continuously
	@echo "$(CYAN)Watching page content (Ctrl+C to stop)...$(NC)"
	@while true; do \
		clear; \
		echo "$(CYAN)═══════════════════════════════════════════════════$(NC)"; \
		echo "$(CYAN)  Page Content Check - $$(date +%H:%M:%S)$(NC)"; \
		echo "$(CYAN)═══════════════════════════════════════════════════$(NC)"; \
		docker exec durable-code-frontend-dev node /app/scripts/check-page-content.js 2>&1; \
		sleep 5; \
	done
