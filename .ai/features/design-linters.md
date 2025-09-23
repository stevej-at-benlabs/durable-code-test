# Design Linters Framework

## Overview

A comprehensive, pluggable design linting framework that enforces SOLID principles, coding standards, and best practices across Python codebases. The framework provides a unified CLI replacing multiple individual linters with a single, extensible tool.

## Core Components

### Framework Architecture

**Location**: `tools/design_linters/framework/`

- **`analyzer.py`**: Core analysis engine that orchestrates rule execution
- **`interfaces.py`**: Base interfaces and abstract classes for rules and violations
- **`reporters.py`**: Output formatting and reporting system
- **`rule_registry.py`**: Rule discovery and management system
- **`ignore_utils.py`**: Comment-based ignore functionality for rules

### CLI Interface

**Location**: `tools/design_linters/cli.py`

The unified command-line interface provides:
- Single entry point replacing individual linter CLIs
- Configurable rule selection and filtering
- Multiple output formats (text, JSON, SARIF, GitHub)
- Legacy compatibility mode for existing tools
- Comprehensive argument parsing and configuration management

### Rule Categories

#### SOLID Principles (`tools/design_linters/rules/solid/`)

**Single Responsibility Principle Rules**:
- **`srp_rules.py`**: Detects classes with too many methods or excessive line counts
  - `TooManyMethodsRule`: Configurable method count thresholds
  - `ClassTooBigRule`: Line count analysis for class size violations

#### Literals (`tools/design_linters/rules/literals/`)

**Magic Number Detection**:
- **`magic_number_rules.py`**: Identifies hardcoded numeric literals
  - Configurable exclusions (0, 1, -1, etc.)
  - Context-aware analysis (avoiding false positives)
  - Support for complex numbers and edge cases

#### Style Rules (`tools/design_linters/rules/style/`)

**Code Style Enforcement**:
- **`print_statement_rules.py`**: Detects print statements in production code
- **`nesting_rules.py`**: Identifies excessive nesting levels in functions and classes

#### Logging Rules (`tools/design_linters/rules/logging/`)

**Logging Best Practices**:
- **`general_logging_rules.py`**: General logging pattern enforcement
- **`loguru_rules.py`**: Loguru-specific usage patterns and best practices

## Configuration System

### Configuration File

**Location**: `.design-lint.yml`

Comprehensive YAML configuration supporting:
- Rule-specific parameter overrides
- Category-based filtering
- Severity level customization
- File and directory exclusions
- Custom rule configurations

### CLI Configuration Options

- `--rules`: Comma-separated list of specific rules
- `--exclude`: Rules to exclude from analysis
- `--categories`: Filter by rule categories
- `--min-severity`: Minimum severity threshold
- `--strict`: Enhanced checking mode
- `--legacy`: Backward compatibility mode

## Integration Features

### Make Targets

**Location**: `Makefile.lint`

- `make lint-custom`: Run design linters with custom rules
- `make lint-all`: Comprehensive linting across all categories
- `make lint-fix`: Automated fixing where possible
- `make lint-list-rules`: Display all available rules

### Testing Repository

**Location**: `test/unit_test/tools/design_linters/`

Comprehensive test suites for each rule category:
- `test_basic.py`: Core framework functionality
- `test_magic_number_rules.py`: Literal analysis testing
- `test_loguru_rules.py`: Logging rule validation
- `test_srp_rules.py`: SOLID principle enforcement
- Category-specific test coverage

### Docker Integration

**Location**: `docker-compose.yml`, `docker-compose.dev.yml`

- Containerized linting environment
- Isolated rule execution
- Consistent analysis across environments

## Advanced Features

### Ignore Functionality

**Location**: `tools/design_linters/framework/ignore_utils.py`

- Line-level ignores: `# design-lint-ignore: rule-name`
- File-level ignores: `# design-lint-ignore-file: category.rule`
- Contextual ignore processing with proper scope handling

### Rule Discovery

**Location**: `tools/design_linters/framework/rule_registry.py`

- Automatic rule detection and registration
- Plugin-style architecture for extensibility
- Category-based organization and filtering

### Output Formats

**Location**: `tools/design_linters/framework/reporters.py`

- **Text**: Human-readable console output
- **JSON**: Machine-readable structured data
- **SARIF**: Static Analysis Results Interchange Format
- **GitHub**: GitHub Actions annotation format

## Extension Points

### Custom Rule Development

Framework supports easy rule extension through:
- Base rule interface implementation
- AST-based node analysis
- Configurable severity and parameters
- Automatic discovery and registration

### Integration Patterns

- Pre-commit hook integration
- CI/CD pipeline compatibility
- IDE plugin support through standardized output formats
- Make target integration for workflow automation

## Usage Examples

```bash
# Basic usage
design-linter src/

# Specific rules
design-linter src/ --rules solid.srp.too-many-methods,literals.magic-number

# Category filtering
design-linter src/ --categories solid,style

# Output formats
design-linter src/ --format json --output report.json

# Legacy compatibility
design-linter myfile.py --legacy srp
```

## Performance Features

- Efficient AST analysis with minimal overhead
- Parallel processing capabilities
- Configurable analysis depth and scope
- Memory-efficient rule execution

## Quality Assurance

- Comprehensive test coverage across all rule categories
- Integration testing with real codebases
- Performance benchmarking and optimization
- Error handling and graceful degradation
