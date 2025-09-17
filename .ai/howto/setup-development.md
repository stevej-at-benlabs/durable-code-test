# How to Setup Development Environment

## Quick Start

```bash
# Complete project initialization
make init

# Start development environment
make dev

# Verify setup
make status
```

## Initial Setup (First Time)

### Prerequisites
- **Docker** and **Docker Compose**
- **Make** (build automation)
- **Git** (version control)
- **Node.js 18+** (for frontend development)
- **Python 3.11+** (for backend development)

### Complete Initialization
```bash
make init
```
**What it does**:
1. Installs pre-commit hooks
2. Builds Docker images with `--no-cache`
3. Sets up development dependencies
4. Validates environment configuration

### Verify Installation
```bash
# Check container status
make status

# View service logs
make logs

# Test API connectivity
curl http://localhost:8000/health

# Test frontend
open http://localhost:5173
```

## Development Environment

### Start Development
```bash
make dev
```
**Services Started**:
- **Frontend**: React dev server on `http://localhost:5173`
- **Backend**: FastAPI server on `http://localhost:8000`
- **Development tools**: Linting, testing, hot reload

### Development with Browser Launch
```bash
make launch
```
**What it does**:
1. Builds production images
2. Starts all services
3. Opens browser to `http://localhost:3000`

### Environment Management
```bash
# Stop development environment
make dev-stop

# Restart development environment
make dev-restart

# View development logs
make dev-logs

# Clean and rebuild
make clean && make dev
```

## Environment Configuration

### Environment Files
**Template**: `.env.example`
**Active**: `.env` (create from template)

```bash
# Copy template
cp .env.example .env

# Edit configuration
nano .env
```

**Key Variables**:
```env
# Database configuration
DATABASE_URL=postgresql://user:pass@db:5432/durable_code

# API configuration
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173

# Development flags
DEBUG=true
HOT_RELOAD=true
```

### Docker Configuration

#### Development Configuration
**File**: `docker-compose.dev.yml`
**Features**:
- Hot module replacement
- Volume mounting for live code changes
- Development tool integration
- Debug port exposure

#### Production Configuration
**File**: `docker-compose.yml`
**Features**:
- Optimized build process
- Multi-stage Docker builds
- Production security settings
- Resource limits

## IDE Setup

### VS Code Configuration
**Location**: `.vscode/` (if exists)

**Recommended Extensions**:
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.flake8",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next"
  ]
}
```

### Python Environment
```bash
# Install Poetry (dependency management)
curl -sSL https://install.python-poetry.org | python3 -

# Install backend dependencies
cd durable-code-app/backend
poetry install

# Activate virtual environment
poetry shell
```

### Node.js Environment
```bash
# Install frontend dependencies
cd durable-code-app/frontend
npm install

# Start development server
npm run dev
```

## Git Configuration

### Pre-commit Hooks
**Automatic Installation**: Handled by `make init`

**Manual Installation**:
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Test hooks
pre-commit run --all-files
```

### Git Workflow
**Branch Protection**: See `.ai/docs/BRANCH_PROTECTION.md`

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/your-feature-name
```

## Development Tools

### Make Targets Reference
```bash
# Environment management
make init          # First-time setup
make dev           # Start development
make build         # Build production images
make clean         # Clean environment

# Quality assurance
make test          # Run all tests
make lint-all      # Run all linting
make lint-fix      # Auto-fix issues

# Monitoring
make status        # Container status
make logs          # View logs
make help          # Show all commands
```

### Docker Commands
```bash
# View running containers
docker ps

# Execute commands in containers
docker exec -it durable-code-test-frontend-1 npm run dev
docker exec -it durable-code-test-backend-1 python -m pytest

# View container logs
docker logs durable-code-test-frontend-1
docker logs durable-code-test-backend-1
```

## Frontend Development

### Development Server
```bash
# Via Make (recommended)
make dev

# Direct execution
cd durable-code-app/frontend
npm run dev
```

### Build Process
```bash
# Development build
npm run build:dev

# Production build
npm run build

# Preview production build
npm run preview
```

### Key Development Features
- **Hot Module Replacement**: Instant code updates
- **TypeScript**: Real-time type checking
- **ESLint**: Code quality enforcement
- **Prettier**: Automatic code formatting

## Backend Development

### Development Server
```bash
# Via Make (recommended)
make dev

# Direct execution (in Poetry environment)
cd durable-code-app/backend
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Development Features
- **Auto-reload**: Automatic server restart on code changes
- **Debug Mode**: Enhanced error messages
- **API Documentation**: Automatic OpenAPI docs at `/docs`
- **Health Checks**: Monitoring endpoints

## Database Setup

### Development Database
```bash
# Start database service
make dev

# View database logs
docker logs durable-code-test-db-1

# Connect to database
docker exec -it durable-code-test-db-1 psql -U postgres -d durable_code
```

### Database Migrations
```bash
# Run migrations
docker exec -it durable-code-test-backend-1 alembic upgrade head

# Create new migration
docker exec -it durable-code-test-backend-1 alembic revision --autogenerate -m "description"
```

## Troubleshooting

### Common Issues

**Port Already in Use**:
```bash
# Check what's using the port
lsof -i :3000
lsof -i :8000

# Kill processes or change ports in docker-compose.dev.yml
```

**Docker Build Failures**:
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
make clean
make init
```

**Permission Issues**:
```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Docker permission issues
sudo usermod -aG docker $USER
# Logout and login again
```

**Module Import Errors**:
```bash
# Ensure proper Python path
export PYTHONPATH=/home/stevejackson/Projects/durable-code-test/tools

# Reinstall dependencies
cd durable-code-app/backend
poetry install --no-cache
```

### Debug Mode

**Frontend Debug**:
```bash
# Enable debug mode
cd durable-code-app/frontend
npm run dev -- --debug

# Browser developer tools
# Open Network tab to monitor API calls
# Use React Developer Tools extension
```

**Backend Debug**:
```bash
# Enable debug logging
cd durable-code-app/backend
DEBUG=true poetry run uvicorn app.main:app --reload

# Python debugger
# Add `import pdb; pdb.set_trace()` in code
```

## Performance Optimization

### Development Performance
- **Use volume mounts** for hot reloading
- **Enable build caching** in Docker
- **Use incremental builds** where possible
- **Optimize dependency installation**

### Resource Monitoring
```bash
# Monitor Docker resource usage
docker stats

# Monitor container logs
make logs

# Check disk usage
docker system df
```

## Environment Validation

### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Frontend accessibility
curl http://localhost:5173

# Database connectivity
docker exec -it durable-code-test-backend-1 python -c "import psycopg2; print('DB OK')"
```

### Service Verification
```bash
# All services running
make status

# API endpoints working
curl http://localhost:8000/docs

# Frontend compilation
cd durable-code-app/frontend && npm run type-check
```

### Quality Validation
```bash
# Run linting
make lint-all

# Run tests
make test

# Check pre-commit hooks
pre-commit run --all-files
```
