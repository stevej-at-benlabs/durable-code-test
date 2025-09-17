# How to Debug Issues

## Quick Debugging Commands

```bash
# Check service status
make status

# View all logs
make logs

# View specific service logs
docker logs durable-code-test-frontend-1
docker logs durable-code-test-backend-1

# Interactive debugging
docker exec -it durable-code-test-backend-1 python
docker exec -it durable-code-test-frontend-1 npm run dev
```

## Common Issue Categories

### Container Issues

#### Services Not Starting
```bash
# Check container status
make status
docker ps -a

# View startup logs
docker logs durable-code-test-frontend-1 --tail=50
docker logs durable-code-test-backend-1 --tail=50

# Check resource usage
docker stats --no-stream
```

**Common Causes**:
- Port conflicts (8000, 3000, 5173 already in use)
- Insufficient memory/disk space
- Missing environment variables
- Docker daemon not running

**Solutions**:
```bash
# Kill conflicting processes
sudo fuser -k 8000/tcp
sudo fuser -k 3000/tcp

# Free up disk space
docker system prune -a

# Restart Docker daemon
sudo systemctl restart docker
```

#### Container Crashes
```bash
# Check exit codes
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# View crash logs
docker logs durable-code-test-backend-1 --since=1h

# Restart crashed containers
docker restart durable-code-test-backend-1
```

### Frontend Issues

#### Build Failures
```bash
# Check build logs
docker exec -it durable-code-test-frontend-1 npm run build

# View detailed npm logs
docker exec -it durable-code-test-frontend-1 npm run build -- --verbose

# Check for missing dependencies
docker exec -it durable-code-test-frontend-1 npm ls
```

**Common Issues**:
- TypeScript compilation errors
- Missing dependencies
- Memory issues during build
- Linting failures blocking build

**Debug Steps**:
```bash
# TypeScript errors
docker exec -it durable-code-test-frontend-1 npm run type-check

# Linting issues
docker exec -it durable-code-test-frontend-1 npm run lint

# Memory issues
docker stats durable-code-test-frontend-1

# Dependency issues
docker exec -it durable-code-test-frontend-1 npm audit
```

#### Runtime Errors
```bash
# View browser console (access http://localhost:5173 and open DevTools)
# Check network requests in DevTools Network tab

# View Vite dev server logs
docker logs durable-code-test-frontend-1 --follow

# Hot reload issues
docker exec -it durable-code-test-frontend-1 ls -la /app/node_modules
```

### Backend Issues

#### API Errors
```bash
# Test API endpoints
curl -v http://localhost:8000/health
curl -v http://localhost:8000/docs

# Check FastAPI logs
docker logs durable-code-test-backend-1 --follow

# View error details
docker exec -it durable-code-test-backend-1 python -c "
import requests
try:
    response = requests.get('http://localhost:8000/health')
    print(f'Status: {response.status_code}')
    print(f'Response: {response.text}')
except Exception as e:
    print(f'Error: {e}')
"
```

#### Database Connection Issues
```bash
# Check database status
docker exec -it durable-code-test-db-1 pg_isready

# Test connection from backend
docker exec -it durable-code-test-backend-1 python -c "
import psycopg2
try:
    conn = psycopg2.connect('postgresql://postgres:password@db:5432/durable_code')
    print('Database connection successful')
    conn.close()
except Exception as e:
    print(f'Database connection failed: {e}')
"

# View database logs
docker logs durable-code-test-db-1 --tail=50
```

#### Python Import/Module Errors
```bash
# Check Python path
docker exec -it durable-code-test-backend-1 python -c "import sys; print('\\n'.join(sys.path))"

# Test imports
docker exec -it durable-code-test-backend-1 python -c "
try:
    from app.main import app
    print('Main app import successful')
except ImportError as e:
    print(f'Import error: {e}')
"

# Check installed packages
docker exec -it durable-code-test-backend-1 pip list
```

### Linting and Testing Issues

#### Linting Failures
```bash
# Run specific linter
make lint-custom

# Check design linter logs
docker exec -it durable-code-test-tools-1 design-linter tools/ --verbose

# Debug specific rule
docker exec -it durable-code-test-tools-1 design-linter tools/design_linters/cli.py --rules solid.srp.too-many-methods --verbose
```

**Common Linting Issues**:
```bash
# Module not found
export PYTHONPATH=/home/stevejackson/Projects/durable-code-test/tools
docker exec -it durable-code-test-tools-1 design-linter tools/

# Configuration issues
docker exec -it durable-code-test-tools-1 cat .design-lint.yml

# Rule discovery problems
docker exec -it durable-code-test-tools-1 design-linter --list-rules
```

#### Test Failures
```bash
# Run tests with verbose output
make test-unit

# Run specific test file
PYTHONPATH=/home/stevejackson/Projects/durable-code-test/tools python -m pytest test/unit_test/tools/design_linters/test_basic.py -v -s

# Debug test with pdb
PYTHONPATH=/home/stevejackson/Projects/durable-code-test/tools python -m pytest test/unit_test/tools/design_linters/test_basic.py::TestIgnoreFunctionality::test_line_level_ignore --pdb
```

## Network and Connectivity Issues

### Port Conflicts
```bash
# Check what's using ports
netstat -tulpn | grep :8000
lsof -i :8000

# Kill conflicting processes
sudo fuser -k 8000/tcp

# Change ports in docker-compose
# Edit docker-compose.dev.yml to use different ports
```

### DNS Resolution
```bash
# Test container-to-container communication
docker exec -it durable-code-test-frontend-1 ping backend
docker exec -it durable-code-test-backend-1 ping db

# Check Docker network
docker network ls
docker network inspect durable-code-test_default
```

### CORS Issues
```bash
# Check CORS configuration in FastAPI
docker exec -it durable-code-test-backend-1 python -c "
from app.main import app
print('CORS middleware configured')
"

# Test CORS headers
curl -H "Origin: http://localhost:5173" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     http://localhost:8000/health
```

## Performance Debugging

### Resource Usage
```bash
# Monitor container resources
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

# Check disk usage
docker system df
df -h

# Memory usage by service
docker exec -it durable-code-test-backend-1 python -c "
import psutil
print(f'Memory usage: {psutil.virtual_memory().percent}%')
print(f'CPU usage: {psutil.cpu_percent()}%')
"
```

### Database Performance
```bash
# Check active connections
docker exec -it durable-code-test-db-1 psql -U postgres -c "
SELECT count(*) as active_connections
FROM pg_stat_activity
WHERE state = 'active';
"

# Check slow queries
docker exec -it durable-code-test-db-1 psql -U postgres -c "
SELECT query, mean_time, calls
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
"
```

### Application Performance
```bash
# Frontend bundle analysis
docker exec -it durable-code-test-frontend-1 npm run build -- --analyze

# Backend response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health

# Create curl-format.txt:
echo "     time_namelookup:  %{time_namelookup}\\n
        time_connect:  %{time_connect}\\n
     time_appconnect:  %{time_appconnect}\\n
    time_pretransfer:  %{time_pretransfer}\\n
       time_redirect:  %{time_redirect}\\n
  time_starttransfer:  %{time_starttransfer}\\n
                     ----------\\n
          time_total:  %{time_total}\\n" > curl-format.txt
```

## Environment and Configuration Issues

### Environment Variables
```bash
# Check environment variables in containers
docker exec -it durable-code-test-backend-1 env | grep -E "DATABASE_URL|DEBUG|SECRET"
docker exec -it durable-code-test-frontend-1 env | grep NODE_ENV

# Validate .env file
cat .env
# Compare with .env.example
diff .env .env.example
```

### Configuration Files
```bash
# Check Docker Compose configuration
docker-compose config

# Validate configuration syntax
docker-compose -f docker-compose.dev.yml config

# Check mounted volumes
docker inspect durable-code-test-backend-1 | jq '.[0].Mounts'
```

### File Permissions
```bash
# Check file ownership
ls -la .env docker-compose.yml

# Fix permissions if needed
sudo chown $USER:$USER .env
chmod 644 .env

# Docker socket permissions
ls -la /var/run/docker.sock
```

## Advanced Debugging

### Interactive Debugging Sessions
```bash
# Python debugging session
docker exec -it durable-code-test-backend-1 python

# Node.js debugging
docker exec -it durable-code-test-frontend-1 node

# Shell access for investigation
docker exec -it durable-code-test-backend-1 bash
docker exec -it durable-code-test-frontend-1 sh
```

### Log Analysis
```bash
# Search for specific errors
docker logs durable-code-test-backend-1 2>&1 | grep -i error

# Monitor logs in real-time
docker logs -f durable-code-test-backend-1 | grep -E "(ERROR|WARNING|CRITICAL)"

# Export logs for analysis
docker logs durable-code-test-backend-1 > backend-debug.log
```

### Memory Debugging
```bash
# Python memory profiling
docker exec -it durable-code-test-backend-1 python -c "
import tracemalloc
tracemalloc.start()
# Your code here
current, peak = tracemalloc.get_traced_memory()
print(f'Current memory usage: {current / 1024 / 1024:.1f} MB')
print(f'Peak memory usage: {peak / 1024 / 1024:.1f} MB')
"

# Node.js memory debugging
docker exec -it durable-code-test-frontend-1 node --inspect=0.0.0.0:9229 index.js
# Connect Chrome DevTools to localhost:9229
```

## Systematic Debugging Approach

### 1. Gather Information
```bash
# System overview
make status
docker ps -a
docker images
docker network ls

# Recent logs
docker logs durable-code-test-backend-1 --since=10m
docker logs durable-code-test-frontend-1 --since=10m
```

### 2. Isolate the Problem
```bash
# Test individual components
curl http://localhost:8000/health  # Backend health
curl http://localhost:5173         # Frontend accessibility

# Test dependencies
docker exec -it durable-code-test-db-1 pg_isready
```

### 3. Check Recent Changes
```bash
# Git history
git log --oneline -10

# File changes
git diff HEAD~1

# Environment changes
diff .env.example .env
```

### 4. Reproduce the Issue
```bash
# Clean environment
make clean
make init

# Step-by-step recreation
make dev
# Test after each step
```

## Error Pattern Recognition

### Common Error Patterns

**"Module not found"**:
- Check PYTHONPATH
- Verify file locations
- Check import statements

**"Connection refused"**:
- Verify service is running
- Check port configuration
- Test network connectivity

**"Permission denied"**:
- Check file permissions
- Verify user/group ownership
- Check Docker socket access

**"Out of memory"**:
- Check available memory
- Monitor container limits
- Analyze memory leaks

### Quick Fix Commands
```bash
# Reset everything
make clean && make init && make dev

# Restart specific service
docker restart durable-code-test-backend-1

# Clear Docker cache
docker system prune -a

# Reset database
docker volume rm durable-code-test_postgres_data
make dev
```

## When to Escalate

### Check These First
1. **System Resources**: Memory, disk space, CPU
2. **Service Status**: All containers running and healthy
3. **Network Connectivity**: Container-to-container communication
4. **Recent Changes**: Git history, configuration changes
5. **Log Files**: Error messages and stack traces

### Document the Issue
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Error messages and logs**
- **Environment details**
- **Recent changes made**

This systematic approach will help identify and resolve most common issues in the development environment.
