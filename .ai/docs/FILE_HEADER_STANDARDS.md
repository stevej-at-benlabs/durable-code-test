# File Header Standards

**Purpose**: Define practical and maintainable file headers for all documentation and code files
**Scope**: Documentation files in `/docs` directory and code files throughout the project

---

## Overview

This document establishes a simplified, practical format for file headers that focuses on essential operational information. Git already tracks creation dates, modification history, and authorship, so headers should focus on describing what the file does and how it fits into the system.

## Standard Header Formats

### Markdown Documentation Files (.md)

```markdown
# Document Title

**Purpose**: Brief description of what this document covers
**Scope**: What areas/components this document applies to

---

## Overview
Document content starts here...
```

### HTML Files (.html)

```html
<!DOCTYPE html>
<!--
Purpose: Brief description of this HTML file's purpose and operation
Scope: What this file is used for (UI component, documentation, etc.)
Dependencies: Key libraries or frameworks used
-->
<html lang="en">
```

### Python Files (.py)

```python
"""
Purpose: Brief description of module/script functionality (1-2 lines)
Scope: What this module handles (API endpoints, data models, business logic, etc.)
Overview: Comprehensive summary of what this module does and its role in the system.
    Detailed explanation of the module's responsibilities, how it fits into the larger
    architecture, key workflows it supports, and important behavioral characteristics.
    This should be sufficient for a developer to understand the module without reading code.
Dependencies: Key external dependencies or internal modules required
Exports: Main classes, functions, or constants this module provides
Interfaces: Key APIs, endpoints, or methods this module exposes
Implementation: Notable algorithms, patterns, or architectural decisions
"""
```

### TypeScript/JavaScript Files (.ts, .tsx, .js, .jsx)

```typescript
/**
 * Purpose: Brief description of component/module functionality (1-2 lines)
 * Scope: What this file handles (React component, utility functions, API service, etc.)
 * Overview: Comprehensive summary of what this component/module does and its role in the application.
 *     Detailed explanation of the component's responsibilities, how it fits into the UI/system,
 *     key user interactions it supports, and important behavioral characteristics.
 *     This should be sufficient for a developer to understand the component without reading code.
 * Dependencies: Key libraries, components, or services this file depends on
 * Exports: Main components, functions, types, or constants this file provides
 * Props/Interfaces: Key interfaces this component accepts or module provides
 * State/Behavior: Important state management or behavioral patterns used
 */
```

### Configuration Files (.yml, .yaml, .json, .toml)

```yaml
# Purpose: Brief description of configuration file and what it configures
# Scope: What this configuration applies to (development, production, specific services)
# Dependencies: Services or tools that use this configuration
```

## Required Header Fields

### Mandatory Fields (All Files)
- **Purpose**: Brief description of file's functionality (1-2 lines)
  - What does this file do?
  - What is its primary responsibility?
- **Scope**: What areas/components this file covers or affects (1-2 lines)
- **Overview**: Comprehensive summary explaining the file's role and operation
  - How does it contribute to the system?
  - What are its key responsibilities and workflows?
  - How does it fit into the larger architecture?
  - Should be sufficient to understand the file without reading code

### Code Files Additional Fields (Python, TypeScript, JavaScript)
- **Dependencies**: Key dependencies, libraries, or related files
- **Exports**: Main classes, functions, components, or constants this file provides
- **Interfaces/Props**: Key APIs, interfaces, or props this file exposes or accepts

### Recommended Fields (Code Files)
- **Implementation**: Notable algorithms, patterns, or architectural decisions
- **State/Behavior**: Important state management or behavioral patterns used
- **Notes**: Any special considerations, warnings, or important operational details

### Optional Fields (All Files)
- **Related**: Links to related files, documentation, or external resources
- **Configuration**: Environment variables or config this file uses

## Implementation Guidelines

### 1. Header Placement
- **Markdown**: Header immediately after the main title
- **Code files**: Header as the first comment block (after shebang if present)
- **HTML**: Header in HTML comment after DOCTYPE
- **Configuration**: Header as comment at top of file

### 2. Content Guidelines
- Keep Purpose field concise but descriptive (1-3 sentences)
- Focus on operational details: what the file does and how it works
- Include key dependencies that aren't obvious from imports
- Mention any special considerations or operational notes

### 3. Automated Validation
The header linter tool validates:
- Presence of mandatory Purpose field
- Header structure and placement
- Field completeness and format
- Consistent formatting across file types

## Examples

### Good Header Example (Python Linter)
```python
"""
Purpose: Validates file placement according to project structure standards
Scope: Project-wide file organization enforcement across all directories
Overview: This linter analyzes Python, HTML, TypeScript, and configuration files to ensure
    they are located in appropriate directories as defined in STANDARDS.md. It enforces
    project organization rules by checking files against configurable placement rules,
    detecting violations, and providing suggested corrections. The linter supports multiple
    file types and can be integrated into CI/CD pipelines to maintain consistent project structure.
Dependencies: pathlib for file operations, fnmatch for pattern matching, argparse for CLI interface
Exports: FilePlacementLinter class, ViolationType enum, PlacementRule dataclass
Interfaces: main() CLI function, analyze_project() returns List[FilePlacementViolation]
Implementation: Uses rule-based pattern matching with configurable directory allowlists/blocklists
"""
```

### Good Header Example (React Component)
```typescript
/**
 * Purpose: Reusable loading spinner component with customizable styling
 * Scope: UI components across the application for async state management
 * Overview: Displays animated spinner during async operations and data fetching with full
 *     accessibility support. Provides multiple size variants and color themes that integrate
 *     with the design system. Handles loading states for API calls, file uploads, and other
 *     asynchronous operations. Includes proper ARIA labeling and reduced motion support for
 *     accessibility compliance.
 * Dependencies: React, CSS modules for styling, clsx for conditional classes
 * Exports: LoadingSpinner component as default export
 * Props/Interfaces: LoadingSpinnerProps { size?: 'sm' | 'md' | 'lg', color?: string, label?: string }
 * State/Behavior: No internal state, purely presentational component with CSS animations
 */
```

### Good Header Example (API Service)
```typescript
/**
 * Purpose: Handles all HTTP requests to the backend API with authentication
 * Scope: Frontend API integration layer, used by all components needing backend data
 * Overview: Provides typed interfaces for user management, data fetching, and file uploads.
 *     Implements automatic authentication token handling, request/response interceptors,
 *     error normalization, and retry logic for failed requests. Centralizes all backend
 *     communication to ensure consistent error handling, loading states, and data formatting
 *     across the application. Supports file uploads with progress tracking and CRUD operations
 *     for all major entities.
 * Dependencies: axios for HTTP requests, jwt-decode for token handling, custom types from @/types
 * Exports: ApiService class, apiClient instance, ApiError class, RequestConfig type
 * Interfaces: CRUD operations for User, Project, File entities; uploadFile(), downloadFile()
 * Implementation: Uses axios interceptors for auth tokens, implements retry logic and error normalization
 */
```

### Good Header Example (Markdown)
```markdown
# API Documentation Standards

**Purpose**: Define REST API documentation requirements and standards for consistent API docs across all backend services
**Scope**: All API endpoints in the backend application

---
```

### Bad Header Example
```python
"""
This file does stuff with files.
"""
```

## Migration Strategy

### Phase 1: Update Existing Files
1. Add headers to all existing documentation files in `/docs`
2. Update core Python files in `/tools` and `/durable-code-app/backend`
3. Update key TypeScript files in `/durable-code-app/frontend/src`
4. Ensure all mandatory Purpose fields are present and descriptive

### Phase 2: Implement Enhanced Linter
1. Create automated header validation tool
2. Integrate into pre-commit hooks
3. Add to CI/CD pipeline

### Phase 3: Enforce Standards
1. Make header linter blocking in CI/CD
2. Update contribution guidelines
3. Train team on new standards

## Tools and Automation

### Header Linter
- Location: `/tools/design_linters/header_linter.py` (to be created)
- Usage: `python tools/design_linters/header_linter.py --path .`
- Validates: Purpose field presence, header structure, formatting
- Exit codes: 0 (pass), 1 (warnings), 2 (failures)

### Pre-commit Integration
```yaml
- repo: local
  hooks:
    - id: header-check
      name: Check file headers
      entry: python tools/design_linters/header_linter.py
      language: system
      files: \.(md|py|ts|tsx|js|jsx|html|yml|yaml)$
```

## Benefits

1. **Clarity**: Easy to understand what each file does and how it operates
2. **Maintainability**: Clear operational descriptions help with maintenance
3. **Onboarding**: New developers can quickly understand file purposes and dependencies
4. **Documentation**: Headers serve as minimal, always-current documentation
5. **Git Integration**: No redundant metadata that git already tracks

## Exceptions

Files that may not need headers:
- Auto-generated files (clearly marked as such)
- Very small configuration files (<10 lines)
- Template files used by generators
- Third-party files (should be clearly identified)
- Test fixture files that only contain data
