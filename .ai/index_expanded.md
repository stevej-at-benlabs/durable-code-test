# AI Agent Expanded Documentation

> **Note**: This file provides detailed information referenced by `index.json`. Read the JSON file first for quick navigation.

## Templates

### Template Usage Guide

All templates use `{{PLACEHOLDER}}` variables that must be replaced with project-specific values. Each template includes comprehensive documentation headers, error handling patterns, and usage instructions.

#### linting-rule.py.template

**Purpose**: Extend the design linting framework with custom rules
**Location**: Place in `tools/design_linters/rules/[category]/`
**Example**: `tools/design_linters/rules/solid/srp_rules.py`

**Key Placeholders**:
- `{{RULE_CLASS_NAME}}`: PascalCase rule class name
- `{{RULE_CATEGORY}}`: Category (solid, literals, style, logging)
- `{{TARGET_NODE_TYPE}}`: AST node type (ast.ClassDef, ast.FunctionDef, etc.)
- `{{VIOLATION_CONDITION}}`: Python condition for rule violation
- `{{SEVERITY_LEVEL}}`: ERROR, WARNING, or INFO

**Integration**: Automatically discovered by rule registry system

#### react-component.tsx.template

**Purpose**: Create modern React components with TypeScript
**Location**: Place in `durable-code-app/frontend/src/components/`
**Example**: `durable-code-app/frontend/src/components/ParticleBackground.tsx`

**Key Placeholders**:
- `{{COMPONENT_NAME}}`: PascalCase component name
- `{{COMPONENT_PURPOSE}}`: Brief component description
- `{{STATE_INTERFACE}}`: TypeScript state interface
- `{{PROPS_DEFINITION}}`: Component props interface

**Features**: Hooks, accessibility, performance optimization, error handling

#### web-tab.tsx.template

**Purpose**: Add new tabs to the web application
**Location**: Place in `durable-code-app/frontend/src/components/tabs/`
**Example**: `durable-code-app/frontend/src/components/tabs/InfrastructureTab.tsx`

**Integration Steps**:
1. Create component using template
2. Add to `App.tsx` tab configuration
3. Update navigation logic
4. Add corresponding CSS

#### fastapi-endpoint.py.template

**Purpose**: Production-ready API endpoints
**Location**: Place in `durable-code-app/backend/app/`
**Example**: `durable-code-app/backend/app/main.py`

**Key Placeholders**:
- `{{ENDPOINT_FUNCTION_NAME}}`: Function name for endpoint
- `{{REQUEST_MODEL_NAME}}`: Pydantic request model
- `{{RESPONSE_MODEL_NAME}}`: Pydantic response model
- `{{HTTP_METHOD}}`: get, post, put, delete

**Features**: Pydantic validation, comprehensive error handling, OpenAPI docs

#### test-suite.py.template

**Purpose**: Comprehensive test coverage
**Location**: Place in `test/unit_test/tools/design_linters/` or appropriate test directory
**Example**: `test/unit_test/tools/design_linters/test_basic.py`

**Test Types**: Unit tests, integration tests, edge cases, performance tests, async tests

#### workflow.html.template

**Purpose**: Interactive workflow documentation
**Usage**: Process documentation, sequence diagrams, training materials

**Features**: Mermaid diagram integration, responsive design, interactive elements

## Features

### design-linters

**File**: `features/design-linters.md`

**Core Components**:
- **Framework**: `tools/design_linters/framework/` - Rule engine, interfaces, reporters
- **CLI**: `tools/design_linters/cli.py` - Unified command-line interface
- **Rules**: `tools/design_linters/rules/` - SOLID, style, literals, logging rules

**Configuration**: `.design-lint.yml` for rule customization

**Usage Examples**:
```bash
# Basic linting
design-linter src/

# Specific rules
design-linter src/ --rules solid.srp.too-many-methods

# JSON output
design-linter src/ --format json --output report.json
```

### web-application

**File**: `features/web-application.md`

**Architecture**:
- **Frontend**: React 18 + TypeScript + Vite (`durable-code-app/frontend/`)
- **Backend**: FastAPI + Python 3.11+ (`durable-code-app/backend/`)

**Key Components**:
- **Main App**: `src/App.tsx` - Tabbed navigation system
- **Tabs**: `src/components/tabs/` - Five main application sections
- **Services**: `src/utils/` - Link validation, HTTP services, particle system
- **API**: `app/main.py` - FastAPI server with CORS and health endpoints

**Development Commands**:
```bash
make dev      # Start development environment
make launch   # Build and start with browser
make build    # Production build
```

### development-tooling

**File**: `features/development-tooling.md`

**Build System**:
- **Core Makefile**: Container lifecycle, environment setup
- **Makefile.lint**: Linting automation and rule management
- **Makefile.test**: Comprehensive testing strategies

**Docker Configuration**:
- **Production**: `docker-compose.yml` - Optimized for deployment
- **Development**: `docker-compose.dev.yml` - Hot reloading, debugging

**Key Commands**:
```bash
make help         # Show all available commands
make init         # Complete project setup
make test         # Run all tests
make lint-all     # Run all linting rules
```

### claude-integration

**File**: `features/claude-integration.md`

**Command System**:
- **`/new-code`**: Enhanced code generation with template integration
- **`/ask`**: AI-powered Q&A system
- **`/solid`**: SOLID principles guidance

**Integration Features**:
- Automatic standards reference
- Template-based code generation
- Hook system for workflow automation
- Project-specific AI behavior

### testing-framework

**File**: `features/testing-framework.md`

**Test Organization**:
- **Unit Tests**: `test/unit_test/tools/design_linters/`
- **Framework Tests**: Core linting framework validation
- **Rule Tests**: Individual rule functionality
- **Integration Tests**: End-to-end workflow validation

**Execution Strategy**:
```bash
make test              # Complete test suite
make test-unit         # Unit tests only
make test-integration  # Integration tests
make test-coverage     # Coverage analysis
```

## Howto Guides

### Available Guides

The `.ai/howto/` directory contains step-by-step guides for common development tasks:

#### run-tests.md
**Purpose**: Execute tests using Make targets and Docker
**Key Commands**:
- `make help` / `make help-full` - Always check available commands first
- `make test` - Complete test suite
- `make test-unit` - Unit tests only
- `make test-coverage` - Coverage analysis

**Important**: Always use Make targets, never run tests locally per `CLAUDE.md`

#### run-linting.md
**Purpose**: Run linting and code quality checks
**Key Commands**:
- `make help` / `make help-full` - Check available linting commands
- `make lint-all` - Complete linting suite
- `make lint-custom` - Design linters only
- `make lint-fix` - Auto-fix issues

**Features**: Design linter framework, ignore functionality, multiple output formats

#### setup-development.md
**Purpose**: Complete development environment setup
**Key Commands**:
- `make init` - First-time project setup
- `make dev` - Start development environment
- `make status` - Check container status

**Coverage**: Prerequisites, Docker configuration, IDE setup, troubleshooting

#### deploy-application.md
**Purpose**: Production deployment and monitoring
**Key Commands**:
- `make build` - Production image builds
- `make start` - Production environment
- `make status` - Deployment verification

**Coverage**: Cloud deployment, SSL/TLS, monitoring, backup strategies

#### debug-issues.md
**Purpose**: Systematic debugging and troubleshooting
**Key Commands**:
- `make logs` - View all service logs
- `docker logs [container]` - Specific service logs
- `make status` - Container health check

**Coverage**: Container issues, network problems, performance debugging

#### debug-with-tests-and-logging.md
**Purpose**: Test-driven debugging methodology
**Philosophy**: Use unit tests and Loguru logging, never create temporary files

**Workflow**:
1. Write failing test to reproduce bug
2. Add Loguru logging for investigation
3. Fix issue based on test and logs
4. Verify fix with tests

**Forbidden**: Temporary test files, print statements, bypassing test framework

## Standards

### STANDARDS.md

**Purpose**: Core development guidelines
**Coverage**: Code style, testing requirements, security practices, performance guidelines
**Enforcement**: Pre-commit hooks, linting rules, CI/CD pipeline

**Key Requirements**:
- Comprehensive file headers for all files
- 100% test coverage for new features
- Type safety (TypeScript for frontend, type hints for Python)
- Security-first development practices

### FILE_HEADER_STANDARDS.md

**Purpose**: Required documentation headers
**Template Structure**:
```
Purpose: [Brief description of file's purpose]
Scope: [What this file covers/handles]
Overview: [Detailed description with context]
Dependencies: [External dependencies and requirements]
Exports: [What this file exports/provides]
Interfaces: [External interfaces and contracts]
Implementation: [Implementation approach and patterns]
```

**Enforcement**: Automated via linting rules

### CSS_LAYOUT_STABILITY.md

**Purpose**: Frontend consistency guidelines
**Applies To**: React components, CSS modules, responsive design
**Key Principles**: Mobile-first design, component isolation, accessibility compliance

### BRANCH_PROTECTION.md

**Purpose**: Git workflow standards
**Requirements**: Branch protection rules, review processes, merge requirements
**Enforcement**: GitHub branch protection settings

## Common Workflows

### Adding Linting Rules

1. **Use Template**: `linting-rule.py.template`
2. **Choose Category**: Place in appropriate `tools/design_linters/rules/[category]/`
3. **Configure Rule**: Set rule ID, severity, parameters
4. **Add Tests**: Create comprehensive test coverage
5. **Update Config**: Add to `.design-lint.yml` if needed

**Example Placement**:
- SOLID rules: `tools/design_linters/rules/solid/`
- Style rules: `tools/design_linters/rules/style/`
- Literal rules: `tools/design_linters/rules/literals/`

### Adding Web Tabs

1. **Use Template**: `web-tab.tsx.template`
2. **Create Component**: Place in `durable-code-app/frontend/src/components/tabs/`
3. **Update App.tsx**: Add to tab configuration and navigation
4. **Add Styling**: Create corresponding CSS module
5. **Test Integration**: Ensure proper navigation and state management

**Integration Points**:
- Tab configuration in `App.tsx`
- Navigation system update
- URL routing integration

### Adding API Endpoints

1. **Use Template**: `fastapi-endpoint.py.template`
2. **Create Models**: Define Pydantic request/response models
3. **Implement Logic**: Add business logic and error handling
4. **Add Router**: Integrate with FastAPI router system
5. **Add Tests**: Create endpoint and integration tests

**File Organization**:
- Main app: `durable-code-app/backend/app/main.py`
- Additional routers: `durable-code-app/backend/app/routers/`
- Models: `durable-code-app/backend/app/models/`

## Development Environment

### Quick Start

1. **Initial Setup**: `make init` - Complete project initialization
2. **Development**: `make dev` - Start development environment
3. **Testing**: `make test` - Run quality assurance
4. **Code Generation**: Use `/new-code` with templates

### Environment Commands

```bash
# Development
make dev          # Start development environment
make dev-logs     # View development logs
make dev-stop     # Stop development environment

# Production
make build        # Build production images
make start        # Start production environment
make status       # Check container status

# Quality Assurance
make test         # Run all tests
make lint-all     # Run all linting
make clean        # Clean environment
```

### Configuration Files

- **Environment**: `.env.example` - Template for environment variables
- **Docker**: `docker-compose.yml`, `docker-compose.dev.yml`
- **Linting**: `.design-lint.yml`, `tools/.flake8`
- **Testing**: `pytest` configuration in `pyproject.toml`
- **Pre-commit**: `.pre-commit-config.yaml`

## Extension Points

### Custom Template Creation

1. **Identify Pattern**: Find repeated code patterns in project
2. **Create Template**: Use existing templates as reference
3. **Add Variables**: Define `{{PLACEHOLDER}}` variables
4. **Document Usage**: Add to this expanded documentation
5. **Test Template**: Validate with actual usage scenarios

### Feature Integration

1. **Document Feature**: Add to `features/` directory
2. **Create Templates**: Add supporting templates
3. **Update Index**: Add references to `index.json`
4. **Add Tests**: Comprehensive test coverage
5. **Update Standards**: Modify standards if needed

This expanded documentation provides comprehensive guidance for AI agents while maintaining efficient structure and clear cross-references to the compact `index.json` navigation file.
