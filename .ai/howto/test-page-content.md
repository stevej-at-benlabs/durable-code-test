# How to Test Page Content

## Overview
This guide explains how to verify that React applications render correctly using various testing tools, especially when implementing error boundaries or debugging blank page issues.

## Quick Start

### Basic Verification
```bash
# Start development environment
make dev

# Basic page content check
make check-page

# Expected output:
# ✅ SUCCESS: App structure looks correct
```

### Advanced Verification
```bash
# Continuous monitoring
make check-page-watch

# Full page verification (requires Playwright setup)
make check-page-full

# Direct Node.js verification
node test-rendered-content.js
```

## Available Testing Tools

### 1. Make Targets (Recommended)

#### `make check-page`
- **Purpose**: Basic HTML structure verification
- **Speed**: Fast (~1-2 seconds)
- **Scope**: Checks for root div, main script, and Vite client
- **Best for**: Quick verification during development

```bash
make check-page

# Output:
# 🔍 Checking page content...
# ✅ Has root div: true
# ✅ Has main script: true
# ✅ Has vite client: true
# ✅ SUCCESS: App structure looks correct
```

#### `make check-page-watch`
- **Purpose**: Continuous monitoring of page content
- **Speed**: Updates every 5 seconds
- **Scope**: Real-time page content verification
- **Best for**: Development monitoring while making changes

```bash
make check-page-watch

# Ctrl+C to stop
# Shows continuous updates every 5 seconds
```

#### `make check-page-full`
- **Purpose**: Complete page verification with JavaScript execution
- **Speed**: Slower (~5-10 seconds)
- **Scope**: Full DOM inspection, console error detection
- **Requirements**: Playwright installed in container
- **Best for**: Comprehensive testing and debugging

### 2. Node.js Tools

#### `test-rendered-content.js`
- **Location**: Project root
- **Purpose**: Simple HTTP-based content verification
- **Usage**: `node test-rendered-content.js`
- **Best for**: Quick local testing without Docker

```bash
node test-rendered-content.js

# Output:
# 🔍 Checking rendered content...
# Response length: 637
# ✅ Has root div: true
# ✅ Has main script: true
# ✅ Has vite client: true
# ✅ SUCCESS: App structure looks correct
```

#### Container-based Scripts
- **simple-check.js**: Basic container verification
- **check-page-content.js**: Advanced container verification

### 3. Python Tools

#### `check-page.py`
- **Purpose**: Playwright-based verification with console error detection
- **Features**: JavaScript execution, console monitoring, DOM inspection
- **Usage**: Standalone Python script

```bash
python check-page.py

# Automatically detects if page loads correctly
# Reports console errors and warnings
```

## Testing Workflow

### 1. Development Workflow
```bash
# 1. Start development
make dev

# 2. Make changes to code
# (edit React components, add error boundaries, etc.)

# 3. Quick verification
make check-page

# 4. If issues detected, debug with:
node test-rendered-content.js

# 5. For continuous monitoring:
make check-page-watch
```

### 2. Error Boundary Testing Workflow
```bash
# 1. Before adding error boundaries
make check-page  # Should pass

# 2. Add error boundary (e.g., to main.tsx)
# Edit code...

# 3. Immediate verification
make check-page

# 4. If fails, debug systematically:
# - Remove error boundary
# - Test again: make check-page
# - Add back with simpler implementation
# - Test again: make check-page
```

### 3. Blank Page Debugging Workflow
```bash
# 1. Identify the issue
make check-page
# If shows empty root div, proceed with debugging

# 2. Check basic HTML structure
node test-rendered-content.js
# Verify server is responding with correct HTML

# 3. Check for JavaScript errors
make check-page-full
# Look for console errors in output

# 4. Systematic component removal
# Remove complex components one by one
# Test after each removal: make check-page

# 5. Identify problematic component
# When make check-page succeeds, last removed component is the issue
```

## Understanding Test Output

### Successful Output
```bash
🔍 Checking rendered content...
Response length: 637
✅ Has root div: true
✅ Has main script: true
✅ Has vite client: true

📄 First 500 chars of response:
──────────────────────────────────────────────────
<!doctype html>
<html lang="en">
  <head>
    <script type="module">import { injectIntoGlobalHook }
    ...
    <div id="root"></div>
    <script type="module" src="/src/main.tsx?t=1234567890">

✅ SUCCESS: App structure looks correct
```

### Failed Output (Blank Page)
```bash
🔍 Checking rendered content...
Response length: 400
✅ Has root div: true
✅ Has main script: true
✅ Has vite client: true

📄 First 500 chars of response:
──────────────────────────────────────────────────
<!doctype html>
<html lang="en">
  ...
  <div id="root"></div>  <!-- Empty! -->

⚠️ ISSUE: Root div exists but may be empty
```

### Failed Output (Server Error)
```bash
❌ ERROR: ECONNREFUSED
❌ FAILURE: Cannot connect to development server

# Solution: Run `make dev` first
```

## Common Testing Scenarios

### Scenario 1: Adding Error Boundaries
```bash
# Test pattern for error boundary implementation
make check-page          # Baseline - should pass
# Add error boundary
make check-page          # Verify still works
# Add another error boundary
make check-page          # Verify still works
# Continue incrementally
```

### Scenario 2: Debugging Blank Page
```bash
# Step-by-step debugging
make check-page          # Confirm issue exists
node test-rendered-content.js  # Check HTTP response
make check-page-full     # Check for JS errors

# If JavaScript errors found:
# 1. Check console in browser
# 2. Fix JavaScript errors
# 3. Test again: make check-page
```

### Scenario 3: Component Development
```bash
# During component development
make check-page-watch &  # Start continuous monitoring
# Edit components in another terminal
# Watch output for immediate feedback
```

### Scenario 4: Production Readiness
```bash
# Comprehensive testing before deployment
make check-page          # Basic structure
make check-page-full     # Complete verification
make test               # Full test suite
make build              # Ensure builds successfully
```

## Advanced Usage

### Custom Content Verification
You can modify `test-rendered-content.js` for custom checks:

```javascript
// Add custom verification logic
function checkCustomContent() {
  const response = execSync('curl -s http://localhost:5173', { encoding: 'utf8' });

  // Custom checks
  const hasMyComponent = response.includes('my-component-id');
  const hasMyText = response.includes('Expected Text');

  console.log('✅ Has my component:', hasMyComponent);
  console.log('✅ Has expected text:', hasMyText);

  return hasMyComponent && hasMyText;
}
```

### Automated Testing Integration
```bash
# In CI/CD pipelines
make dev &               # Start in background
sleep 10                 # Wait for startup
make check-page         # Verify page loads
make test               # Run full test suite
```

### Performance Monitoring
```bash
# Monitor page load performance
time make check-page

# Continuous performance monitoring
while true; do
  echo "=== $(date) ==="
  time make check-page
  sleep 30
done
```

## Troubleshooting

### Tool Not Working
```bash
# If make targets fail:
docker ps                # Ensure containers running
make status             # Check service status
make logs               # Check for errors

# If Node.js tools fail:
node --version          # Ensure Node.js available
npm list               # Check dependencies
```

### False Positives
- **Issue**: Tool reports success but page appears blank in browser
- **Cause**: Tool only checks initial HTML, not JavaScript-rendered content
- **Solution**: Use `make check-page-full` for JavaScript execution verification

### Container Issues
```bash
# If container-based checks fail:
docker exec durable-code-frontend-dev node scripts/simple-check.js

# Direct container inspection:
docker exec -it durable-code-frontend-dev bash
cd scripts
node simple-check.js
```

## Performance Considerations

### Tool Performance Comparison
- `make check-page`: ~1-2 seconds (HTTP only)
- `node test-rendered-content.js`: ~0.5-1 second (HTTP only)
- `make check-page-full`: ~5-10 seconds (Full browser)
- `make check-page-watch`: Continuous (5-second intervals)

### Best Practices
1. Use `make check-page` for quick development feedback
2. Use `make check-page-full` for comprehensive testing
3. Use `make check-page-watch` during active development
4. Use `node test-rendered-content.js` for external scripts

## Integration with Development Workflow

### Pre-commit Testing
```bash
# Add to pre-commit hooks or development workflow
make check-page || echo "Page content verification failed"
```

### Development Scripts
```bash
# Add to package.json scripts
"scripts": {
  "verify-page": "node test-rendered-content.js",
  "check-page": "make check-page",
  "dev-with-monitoring": "make dev && make check-page-watch"
}
```

## Related Documentation
- `.ai/features/error-boundaries.md` - Error boundary implementation
- `.ai/howto/implement-error-boundaries.md` - Error boundary guide
- `Makefile` - Make target definitions
- `durable-code-app/frontend/scripts/` - Script implementations