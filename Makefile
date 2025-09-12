# Makefile for Durable Code Test Project
# Docker-based development and deployment automation

.PHONY: help init build start stop restart launch logs clean status dev dev-start dev-stop dev-restart dev-logs test lint format check-deps update-deps

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
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
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
	@echo "$(YELLOW)Building Docker images...$(NC)"
	@$(DOCKER_COMPOSE) build --no-cache
	@echo "$(GREEN)✓ Initialization complete!$(NC)"

build: ## Build Docker images
	@echo "$(CYAN)Building Docker images...$(NC)"
	@$(DOCKER_COMPOSE) build
	@echo "$(GREEN)✓ Build complete!$(NC)"

start: ## Start all containers in production mode
	@echo "$(CYAN)Starting containers...$(NC)"
	@$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✓ Containers started!$(NC)"
	@echo "$(YELLOW)Frontend: $(FRONTEND_URL)$(NC)"
	@echo "$(YELLOW)Backend: $(BACKEND_URL)$(NC)"

stop: ## Stop all running containers
	@echo "$(CYAN)Stopping containers...$(NC)"
	@$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✓ Containers stopped!$(NC)"

restart: stop start ## Restart all containers

launch: start ## Start containers and open the web application
	@echo "$(CYAN)Launching application...$(NC)"
	@sleep 3 # Wait for services to be ready
	@echo "$(GREEN)Opening browser at $(FRONTEND_URL)...$(NC)"
	@if command -v xdg-open > /dev/null; then \
		xdg-open $(FRONTEND_URL); \
	elif command -v open > /dev/null; then \
		open $(FRONTEND_URL); \
	elif command -v start > /dev/null; then \
		start $(FRONTEND_URL); \
	else \
		echo "$(YELLOW)Please open your browser and navigate to $(FRONTEND_URL)$(NC)"; \
	fi

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

# Testing and quality targets
test: ## Run all tests
	@echo "$(CYAN)Running tests...$(NC)"
	@echo "$(YELLOW)Backend tests:$(NC)"
	@docker exec durable-code-backend pytest || docker exec durable-code-backend-dev pytest || echo "$(YELLOW)Backend container not running$(NC)"
	@echo "$(YELLOW)Frontend tests:$(NC)"
	@docker exec durable-code-frontend npm test || docker exec durable-code-frontend-dev npm test || echo "$(YELLOW)Frontend container not running$(NC)"

# Include comprehensive linting targets
-include Makefile.lint

lint: ## Run basic linters
	@echo "$(CYAN)Running linters...$(NC)"
	@echo "$(YELLOW)Backend linting:$(NC)"
	@docker exec durable-code-backend ruff check . || docker exec durable-code-backend-dev ruff check . || echo "$(YELLOW)Backend container not running$(NC)"
	@echo "$(YELLOW)Frontend linting:$(NC)"
	@docker exec durable-code-frontend npm run lint || docker exec durable-code-frontend-dev npm run lint || echo "$(YELLOW)Frontend container not running$(NC)"

format: ## Format code
	@echo "$(CYAN)Formatting code...$(NC)"
	@echo "$(YELLOW)Backend formatting:$(NC)"
	@docker exec durable-code-backend black . || docker exec durable-code-backend-dev black . || echo "$(YELLOW)Backend container not running$(NC)"
	@echo "$(YELLOW)Frontend formatting:$(NC)"
	@docker exec durable-code-frontend npm run format || docker exec durable-code-frontend-dev npm run format || echo "$(YELLOW)Frontend container not running$(NC)"

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