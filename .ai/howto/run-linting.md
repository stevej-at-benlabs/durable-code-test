# How to Run Linting

## Important: Always Check Available Make Targets First

```bash
# Get basic list of available commands
make help

# Get comprehensive list of all make targets (recommended)
make help-full
```

## Quick Commands

```bash
# Run all linting rules
make lint-all

# Run custom design linters only
make lint-custom

# Auto-fix issues where possible
make lint-fix

# List available rules
make lint-list-rules
```

> **Note**: The project uses Make targets exclusively for linting. Always run `make help` or `make help-full` to see all available linting commands before proceeding.

## Make Target Details

### Complete Linting Suite
```bash
make lint-all
```
**What it runs**:
- Design linters (custom framework)
- Python linting (flake8, black, mypy)
- Frontend linting (ESLint, Prettier)
- Pre-commit hooks validation

### Custom Design Linters
```bash
make lint-custom
```
**What it runs**:
- SOLID principle enforcement
- Magic number detection
- Print statement detection
- Code complexity analysis
- Logging best practices

### Auto-fix Linting Issues
```bash
make lint-fix
```
**What it fixes**:
- Code formatting (Black, Prettier)
- Import sorting (isort)
- Simple style violations
- Trailing whitespace

### Rule Discovery
```bash
make lint-list-rules
```
**Output**: All available linting rules organized by category

## Design Linter Framework

### Direct CLI Usage
```bash
# Basic usage
docker exec -it durable-code-test-tools-1 design-linter tools/

# Specific rules
docker exec -it durable-code-test-tools-1 design-linter tools/ --rules solid.srp.too-many-methods,literals.magic-number

# JSON output
docker exec -it durable-code-test-tools-1 design-linter tools/ --format json --output /tmp/lint-report.json

# Category filtering
docker exec -it durable-code-test-tools-1 design-linter tools/ --categories solid,style
```

### Configuration File
**Location**: `.design-lint.yml`

```yaml
rules:
  solid.srp.too-many-methods:
    max_methods: 15
  literals.magic-number:
    allowed_numbers: [0, 1, -1, 2, 100]
    ignore_test_files: true

categories:
  - solid
  - literals
  - style
  - logging

exclude_patterns:
  - "*/test_*"
  - "*/migrations/*"
```

## Linting Categories

### SOLID Principles
**Rules**:
- `solid.srp.too-many-methods`: Class method count limits
- `solid.srp.class-too-big`: Class size analysis

**Configuration**:
```bash
# Strict mode
docker exec -it durable-code-test-tools-1 design-linter tools/ --strict

# Custom thresholds
docker exec -it durable-code-test-tools-1 design-linter tools/ --rules solid.srp.too-many-methods --config custom-config.yml
```

### Style Rules
**Rules**:
- `style.print-statement`: Print statement detection
- `style.nesting-level`: Excessive nesting detection

**Usage**:
```bash
docker exec -it durable-code-test-tools-1 design-linter tools/ --categories style
```

### Literals
**Rules**:
- `literals.magic-number`: Hardcoded number detection

**Usage**:
```bash
docker exec -it durable-code-test-tools-1 design-linter tools/ --categories literals
```

### Logging
**Rules**:
- `logging.general`: General logging patterns
- `logging.loguru`: Loguru-specific rules

**Usage**:
```bash
docker exec -it durable-code-test-tools-1 design-linter tools/ --categories logging
```

## Ignore Functionality

### Line-Level Ignores
```python
# design-lint-ignore: rule-name
problematic_code()

# Multiple rules
# design-lint-ignore: solid.srp.too-many-methods,style.print-statement
def complex_function():
    pass
```

### File-Level Ignores
```python
# design-lint-ignore-file: solid.srp
# This entire file ignores SRP rules

class ComplexLegacyClass:
    # Many methods allowed in this file
    pass
```

## Output Formats

### Text Output (Default)
```
tools/design_linters/cli.py:45: [ERROR] solid.srp.too-many-methods
  Class 'ArgumentParser' has 12 methods, exceeds limit of 10
  Consider splitting into smaller, focused classes

tools/example.py:23: [WARNING] literals.magic-number
  Magic number '42' detected
  Consider using a named constant
```

### JSON Output
```bash
docker exec -it durable-code-test-tools-1 design-linter tools/ --format json
```
```json
{
  "violations": [
    {
      "file": "tools/design_linters/cli.py",
      "line": 45,
      "rule_id": "solid.srp.too-many-methods",
      "severity": "ERROR",
      "message": "Class has too many methods"
    }
  ],
  "summary": {
    "total_violations": 1,
    "files_analyzed": 15
  }
}
```

### SARIF Output
```bash
docker exec -it durable-code-test-tools-1 design-linter tools/ --format sarif
```
**Usage**: IDE integration, CI/CD pipeline integration

## Frontend Linting

### ESLint
```bash
# Via Make target (recommended)
make lint-all

# Direct execution
cd durable-code-app/frontend
npm run lint

# Auto-fix
npm run lint:fix
```

### Prettier
```bash
# Check formatting
cd durable-code-app/frontend
npm run format:check

# Auto-format
npm run format
```

### TypeScript Checking
```bash
cd durable-code-app/frontend
npm run type-check
```

## Python Linting

### Flake8
**Configuration**: `tools/.flake8`
```bash
# Via Make target
make lint-all

# Direct execution
docker exec -it durable-code-test-tools-1 flake8 tools/
```

### Black (Formatting)
```bash
# Check formatting
docker exec -it durable-code-test-tools-1 black --check tools/

# Auto-format
docker exec -it durable-code-test-tools-1 black tools/
```

### MyPy (Type Checking)
```bash
docker exec -it durable-code-test-tools-1 mypy tools/
```

## Pre-commit Hooks

### Configuration
**Location**: `.pre-commit-config.yaml`

### Manual Execution
```bash
# Run all hooks
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Run on staged files only
pre-commit run
```

## CI/CD Integration

### GitHub Actions
**Location**: `.github/workflows/`
- Automatic linting on PR
- Multi-environment validation
- Comment with linting results

### Quality Gates
- **Zero tolerance** for ERROR level violations
- **Warning threshold** configurable
- **Coverage requirements** enforced

## Troubleshooting

### Common Issues

**Module Import Errors**:
```bash
# Ensure proper Python path
PYTHONPATH=/home/stevejackson/Projects/durable-code-test/tools design-linter
```

**Docker Container Not Running**:
```bash
# Start development environment
make dev

# Check container status
make status
```

**Configuration Not Found**:
```bash
# Specify config file explicitly
docker exec -it durable-code-test-tools-1 design-linter tools/ --config .design-lint.yml
```

### Debug Mode
```bash
# Verbose output
docker exec -it durable-code-test-tools-1 design-linter tools/ --verbose

# List available rules
docker exec -it durable-code-test-tools-1 design-linter --list-rules

# Show configuration
docker exec -it durable-code-test-tools-1 design-linter tools/ --verbose --dry-run
```

## Best Practices

### Development Workflow
1. **Run linting early**: `make lint-custom` during development
2. **Fix violations promptly**: Address issues as they arise
3. **Use auto-fix**: `make lint-fix` for formatting issues
4. **Full validation**: `make lint-all` before commits

### Rule Configuration
1. **Project-specific rules**: Customize `.design-lint.yml`
2. **Team standards**: Align rule thresholds with team preferences
3. **Gradual adoption**: Start lenient, tighten over time
4. **Exception handling**: Use ignores sparingly and document reasons

### Performance Optimization
- **Target specific files**: Lint only changed files during development
- **Cache results**: Use CI caching for faster pipeline execution
- **Parallel execution**: Run different linters concurrently
- **Incremental analysis**: Focus on new/changed code

## Legacy Compatibility

### Backward Compatibility Mode
```bash
# Old SRP analyzer behavior
docker exec -it durable-code-test-tools-1 design-linter tools/ --legacy srp

# Old magic number detector behavior
docker exec -it durable-code-test-tools-1 design-linter tools/ --legacy magic
```

### Migration Guide
1. **Replace old commands** with new unified CLI
2. **Update CI/CD scripts** to use Make targets
3. **Migrate configurations** to `.design-lint.yml`
4. **Update documentation** to reference new commands
