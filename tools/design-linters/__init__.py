"""
Design principle linters and constants.

All thresholds and configuration constants for design linting tools.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class SRPThresholds:
    """Single Responsibility Principle thresholds."""

    # Method and size limits
    MAX_METHODS_PER_CLASS: int = 7
    MAX_METHOD_GROUPS: int = 3
    MAX_CLASS_LINES: int = 200
    MAX_INSTANCE_VARIABLES: int = 7
    MAX_DEPENDENCIES: int = 5

    # Cohesion thresholds
    MIN_COHESION_SCORE: float = 0.3
    WARNING_COHESION_SCORE: float = 0.5
    GOOD_COHESION_SCORE: float = 0.7

    # Severity thresholds
    ERROR_VIOLATION_COUNT: int = 4
    WARNING_VIOLATION_COUNT: int = 2

    # Line counts for different severity levels
    STRICT_MAX_METHODS: int = 5
    STRICT_MAX_LINES: int = 150
    LENIENT_MAX_METHODS: int = 10
    LENIENT_MAX_LINES: int = 300


@dataclass(frozen=True)
class MagicNumberThresholds:
    """Magic number detection thresholds."""

    # Acceptable numeric literals
    ALLOWED_NUMBERS = frozenset({
        -1,  # Common index/flag
        0,   # Zero initialization
        1,   # Unity/increment
        2,   # Binary/pair operations
        10,  # Decimal base
        100, # Percentage
        1000, # Kilo multiplier
        1024, # Binary kilo
    })

    # Acceptable string literals
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


# Responsibility detection patterns
RESPONSIBILITY_PREFIXES: Dict[str, List[str]] = {
    'data_access': ['get', 'fetch', 'load', 'read', 'query', 'find', 'search'],
    'data_mutation': ['set', 'save', 'write', 'update', 'delete', 'create', 'insert', 'remove'],
    'validation': ['validate', 'verify', 'check', 'ensure', 'assert', 'confirm', 'is_valid'],
    'transformation': ['convert', 'transform', 'parse', 'format', 'serialize', 'deserialize', 'encode', 'decode'],
    'notification': ['send', 'notify', 'email', 'alert', 'publish', 'broadcast', 'emit'],
    'calculation': ['calculate', 'compute', 'process', 'analyze', 'aggregate', 'sum', 'average'],
    'rendering': ['render', 'display', 'draw', 'show', 'print', 'format', 'present'],
    'authentication': ['login', 'logout', 'authenticate', 'authorize', 'verify', 'sign'],
    'configuration': ['configure', 'setup', 'init', 'register', 'bootstrap', 'initialize']
}

# File patterns to exclude from analysis
EXCLUDE_PATTERNS: List[str] = [
    'test_',
    '__pycache__',
    '.git',
    'venv',
    '.venv',
    'migrations',
    'vendor',
    'node_modules',
    '__init__.py',
    'setup.py',
    'conftest.py'
]

# Severity levels
class Severity:
    """Severity level constants."""
    ERROR = 'error'
    WARNING = 'warning'
    INFO = 'info'

# File placement rules
FILE_PLACEMENT_RULES = {
    'python_allowed_dirs': [
        'durable-code-app/backend/app',
        'durable-code-app/backend/app/**',
        'tools',
        'tools/**',
        'test',
        'test/**',
        'durable-code-app/backend/tests',
        'durable-code-app/backend/tests/**'
    ],
    'html_allowed_dirs': [
        'durable-code-app/frontend/public',
        'durable-code-app/frontend/dist',
        'durable-code-app/frontend/dist/**',
        'docs'
    ],
    'frontend_allowed_dirs': [
        'durable-code-app/frontend/src',
        'durable-code-app/frontend/src/**',
        'durable-code-app/frontend/tests',
        'durable-code-app/frontend/tests/**'
    ],
    'prohibited_root_extensions': ['.py', '.js', '.ts', '.tsx', '.html', '.css'],
    'excluded_patterns': [
        '.git',
        '__pycache__',
        '.mypy_cache',
        '.ruff_cache',
        'node_modules',
        '.venv',
        'venv',
        '.pytest_cache'
    ]
}

# Default instances
DEFAULT_SRP_THRESHOLDS = SRPThresholds()
DEFAULT_MAGIC_NUMBER_THRESHOLDS = MagicNumberThresholds()
DEFAULT_FILE_PLACEMENT_RULES = FILE_PLACEMENT_RULES
