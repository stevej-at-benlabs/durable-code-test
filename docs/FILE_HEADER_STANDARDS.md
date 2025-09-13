# File Header Standards

**Purpose**: Define standardized file headers for all documentation and code files  
**Scope**: Documentation files in `/docs` directory and code files throughout the project  
**Created**: 2025-09-12  
**Updated**: 2025-09-12  
**Author**: Development Team  
**Version**: 1.0  

---

## Overview

This document establishes the standardized format for file headers across all documentation and code files. Consistent headers improve maintainability, provide essential metadata, and help with automated tooling.

## Standard Header Formats

### Markdown Documentation Files (.md)

```markdown
# Document Title

**Purpose**: Brief description of what this document covers  
**Scope**: What areas/components this document applies to  
**Created**: YYYY-MM-DD  
**Updated**: YYYY-MM-DD  
**Author**: Author name or team  
**Version**: Semantic version (1.0, 1.1, etc.)  

---

## Overview
Document content starts here...
```

### HTML Files (.html)

```html
<!DOCTYPE html>
<!--
Purpose: Brief description of this HTML file's purpose
Scope: What this file is used for (UI component, documentation, etc.)
Created: YYYY-MM-DD
Updated: YYYY-MM-DD
Author: Author name or team
Version: Semantic version
-->
<html lang="en">
```

### Python Files (.py)

```python
"""
Purpose: Brief description of module/script functionality
Scope: What this module handles (API endpoints, data models, etc.)
Created: YYYY-MM-DD
Updated: YYYY-MM-DD
Author: Author name or team
Version: Semantic version
"""
```

### TypeScript/JavaScript Files (.ts, .tsx, .js, .jsx)

```typescript
/**
 * Purpose: Brief description of component/module functionality
 * Scope: What this file handles (React component, utility functions, etc.)
 * Created: YYYY-MM-DD
 * Updated: YYYY-MM-DD
 * Author: Author name or team
 * Version: Semantic version
 */
```

### Configuration Files (.yml, .yaml, .json, .toml)

```yaml
# Purpose: Brief description of configuration file
# Scope: What this configuration applies to
# Created: YYYY-MM-DD
# Updated: YYYY-MM-DD
# Author: Author name or team
# Version: Semantic version
```

## Required Header Fields

### Mandatory Fields (All Files)
- **Purpose**: 1-2 sentence description of file's purpose
- **Created**: Date when file was originally created (YYYY-MM-DD format)
- **Author**: Creator's name or team name

### Recommended Fields
- **Scope**: What areas/components this file covers
- **Updated**: Date of last significant update (YYYY-MM-DD format)  
- **Version**: Semantic version number

### Optional Fields
- **Dependencies**: Key dependencies or requirements
- **Related**: Links to related files or documentation
- **Notes**: Any special considerations or warnings

## Implementation Guidelines

### 1. Header Placement
- **Markdown**: Header immediately after the main title
- **Code files**: Header as the first comment block (after shebang if present)
- **HTML**: Header in HTML comment after DOCTYPE
- **Configuration**: Header as comment at top of file

### 2. Content Guidelines
- Keep Purpose field concise but descriptive
- Use ISO date format (YYYY-MM-DD) consistently
- Update the "Updated" field when making significant changes
- Version numbers should follow semantic versioning where applicable

### 3. Automated Validation
The header linter tool validates:
- Presence of mandatory fields
- Date format compliance
- Header structure and placement
- Field completeness and format

## Examples

### Good Header Example (Markdown)
```markdown
# API Documentation Standards

**Purpose**: Define REST API documentation requirements and standards  
**Scope**: All API endpoints in the backend application  
**Created**: 2025-01-15  
**Updated**: 2025-09-12  
**Author**: Backend Team  
**Version**: 2.1  

---

## Overview
This document outlines...
```

### Bad Header Example
```markdown
# Some Documentation
This is about APIs or something.
```

## Migration Strategy

### Phase 1: Update Existing Files
1. Add headers to all existing documentation files
2. Focus on core documentation first
3. Ensure all mandatory fields are present

### Phase 2: Implement Linter
1. Create automated header validation tool
2. Integrate into pre-commit hooks
3. Add to CI/CD pipeline

### Phase 3: Enforce Standards  
1. Make header linter blocking in CI/CD
2. Update contribution guidelines
3. Train team on new standards

## Tools and Automation

### Header Linter
- Location: `/tools/design-linters/header_linter.py`
- Usage: `python tools/design-linters/header_linter.py --path docs/`
- Exit codes: 0 (pass), 1 (warnings), 2 (failures)

### Pre-commit Integration
```yaml
- repo: local
  hooks:
    - id: header-check
      name: Check file headers
      entry: python tools/design-linters/header_linter.py
      language: system
      files: \.(md|py|ts|tsx|js|jsx|html|yml|yaml)$
```

## Benefits

1. **Consistency**: All files follow the same header format
2. **Maintainability**: Easy to identify file purpose and ownership
3. **Automation**: Linter enforces standards automatically
4. **Metadata**: Structured information for tooling and processes
5. **Onboarding**: New developers can quickly understand file purposes

## Exceptions

Files that may not need headers:
- Auto-generated files (clearly marked as such)
- Very small configuration files (&lt;10 lines)
- Template files used by generators
- Third-party files (should be clearly identified)