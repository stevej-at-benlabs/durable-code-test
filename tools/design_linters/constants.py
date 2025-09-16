"""
Purpose: Shared constants for design linters to avoid code duplication
Scope: All design linting tools that need common constants
Overview: This module provides shared constants to eliminate duplicate code
    across different linter modules while maintaining consistency.
Dependencies: None
Exports: Common constants used across multiple linters
"""

import ast
import sys
from typing import Any, Type, List

# Acceptable string literals for magic number detection
ALLOWED_STRING_PATTERNS = frozenset({
    '',      # Empty string
    ' ',     # Space
    '\n',    # Newline
    '\t',    # Tab
    ',',     # Comma separator
    '.',     # Dot separator
    '/',     # Path separator
    ':',     # Colon separator
    'utf-8', # Encoding
    'utf8',  # Encoding variant
    'r',     # Read mode
    'w',     # Write mode
    'a',     # Append mode
    'rb',    # Read binary
    'wb',    # Write binary
})

# Patterns to exclude from analysis
EXCLUDED_PATTERNS = [
    '.git',
    '__pycache__',
    '.mypy_cache',
    '.ruff_cache',
    'node_modules',
    '.venv',
    'venv',
    '.pytest_cache',
    '.coverage',
    '*.pyc',
    '*.pyo',
    '*.egg-info',
    '.DS_Store',
    'Thumbs.db'
]


# Common syntax error handling template
def handle_syntax_error(file_path: str, error: Exception) -> None:
    """Handle syntax errors consistently across linters."""
    print(f"Syntax error in {file_path}: {error}", file=sys.stderr)


# Common analyze function template
def analyze_with_visitor(file_path: str, visitor_class: Type[Any],
                        *args: Any, **kwargs: Any) -> List[Any]:
    """Analyze a file with a given AST visitor class."""
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read())
            analyzer = visitor_class(file_path, *args, **kwargs)
            analyzer.visit(tree)
            return list(analyzer.violations)
        except SyntaxError as e:
            handle_syntax_error(file_path, e)
            return []
