# Development Tools

**Purpose**: Documentation for development and linting tools used in the project
**Scope**: Custom tools, scripts, and utilities for code quality enforcement
**Created**: 2025-09-12
**Updated**: 2025-09-12
**Author**: Development Team
**Version**: 1.0

---

## Header Linter Tool

### Purpose

The `design-linters/header_linter.py` tool enforces standardized file headers across all documentation and source code files in the project.

### Usage

#### Lint a directory

```bash
# Lint all files in docs/ directory
python tools/design-linters/header_linter.py --path docs/

# Lint all files recursively from root
python tools/design-linters/header_linter.py --path . --recursive

# Strict mode (warnings treated as errors)
python tools/design-linters/header_linter.py --path docs/ --strict
```

#### Lint a single file

```bash
# Check specific file
python tools/design-linters/header_linter.py --file README.md
```

#### Integration options

```bash
# Quiet mode (errors only)
python tools/design-linters/header_linter.py --path . --quiet

# Get help
python tools/design-linters/header_linter.py --help
```

### Exit Codes

- **0**: All files passed validation
- **1**: Files have warnings (non-strict mode)
- **2**: Files have errors or failures

### Pre-commit Integration

The tool is automatically run as part of pre-commit hooks. Install with:

```bash
pre-commit install
```

### Supported File Types

- **Markdown** (`.md`) - Uses `**Field**: value` format
- **Python** (`.py`) - Uses docstring format
- **TypeScript/JavaScript** (`.ts`, `.tsx`, `.js`, `.jsx`) - Uses JSDoc format
- **HTML** (`.html`) - Uses HTML comment format
- **YAML** (`.yml`, `.yaml`) - Uses comment format

### Required Fields

All files must include:

- **Purpose**: Brief description of file's functionality
- **Created**: Creation date (YYYY-MM-DD format)
- **Author**: Creator's name or team

### Recommended Fields

- **Scope**: What the file covers
- **Updated**: Last update date (YYYY-MM-DD format)
- **Version**: Semantic version number

### Example Headers

#### Markdown File

```markdown
# Document Title

**Purpose**: Brief description of what this document covers
**Scope**: What areas/components this document applies to
**Created**: 2025-09-12
**Updated**: 2025-09-12
**Author**: Development Team
**Version**: 1.0

---

Content starts here...
```

#### Python File

```python
"""
Purpose: Brief description of module functionality
Scope: What this module handles
Created: 2025-09-12
Updated: 2025-09-12
Author: Development Team
Version: 1.0
"""
```

### Configuration

The linter is configured in the tool itself. Key settings:

- Required fields validation
- Date format validation (YYYY-MM-DD)
- File type detection by extension
- Warning vs. error categorization

For more details, see `/docs/FILE_HEADER_STANDARDS.md`.
