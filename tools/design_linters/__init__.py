"""
Purpose: Provides configuration constants and thresholds for design principle linters
Scope: All design linting tools including SRP analyzer, magic number detector, and
    file placement linter
Overview: This module centralizes all thresholds and configuration constants used
    by design
    linting tools. It provides dataclasses for SRP thresholds, magic number
    detection patterns,
    responsibility detection rules, and file placement configurations. The module
    ensures
    consistent configuration across all linting tools and makes it easy to adjust
    sensitivity
    levels and detection rules from a single location.
Dependencies: dataclasses for configuration structures, typing for type hints
Exports: SRPThresholds, MagicNumberThresholds, Severity class, FILE_PLACEMENT_RULES
Interfaces: Configuration constants and default instances for all linters
Implementation: Uses frozen dataclasses for immutable configuration and constants
"""

from dataclasses import dataclass
from typing import Dict, List
try:
    from .constants import ALLOWED_STRING_PATTERNS, EXCLUDED_PATTERNS
except ImportError:
    from constants import (  # type: ignore[import-not-found, no-redef]
        ALLOWED_STRING_PATTERNS,
        EXCLUDED_PATTERNS,
    )


@dataclass(frozen=True)
class SRPLimits:
    """Single Responsibility Principle size and method limits."""
    MAX_METHODS_PER_CLASS: int = 7
    MAX_METHOD_GROUPS: int = 3
    MAX_CLASS_LINES: int = 200
    MAX_INSTANCE_VARIABLES: int = 7
    MAX_DEPENDENCIES: int = 5

@dataclass(frozen=True)
class SRPCohesion:
    """Single Responsibility Principle cohesion thresholds."""
    MIN_COHESION_SCORE: float = 0.3
    WARNING_COHESION_SCORE: float = 0.5
    GOOD_COHESION_SCORE: float = 0.7

@dataclass(frozen=True)
class SRPSeverity:
    """Single Responsibility Principle severity thresholds."""
    ERROR_VIOLATION_COUNT: int = 4
    WARNING_VIOLATION_COUNT: int = 2

@dataclass(frozen=True)
class SRPLevels:
    """Single Responsibility Principle strictness levels."""
    STRICT_MAX_METHODS: int = 5
    STRICT_MAX_LINES: int = 150
    LENIENT_MAX_METHODS: int = 10
    LENIENT_MAX_LINES: int = 300

@dataclass(frozen=True)
class SRPThresholds:
    """Combined Single Responsibility Principle thresholds."""
    limits: SRPLimits
    cohesion: SRPCohesion
    severity: SRPSeverity
    levels: SRPLevels


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

    # Reference shared constants
    ALLOWED_STRING_PATTERNS = ALLOWED_STRING_PATTERNS


# Responsibility detection patterns
RESPONSIBILITY_PREFIXES: Dict[str, List[str]] = {
    'data_access': ['get', 'fetch', 'load', 'read', 'query', 'find', 'search'],
    'data_mutation': ['set', 'save', 'write', 'update', 'delete', 'create',
                      'insert', 'remove'],
    'validation': ['validate', 'verify', 'check', 'ensure', 'assert', 'confirm',
                   'is_valid'],
    'transformation': ['convert', 'transform', 'parse', 'format', 'serialize',
                       'deserialize', 'encode', 'decode'],
    'notification': ['send', 'notify', 'email', 'alert', 'publish',
                     'broadcast', 'emit'],
    'calculation': ['calculate', 'compute', 'process', 'analyze', 'aggregate',
                    'sum', 'average'],
    'rendering': ['render', 'display', 'draw', 'show', 'print', 'format',
                  'present'],
    'authentication': ['login', 'logout', 'authenticate', 'authorize', 'verify',
                       'sign'],
    'configuration': ['configure', 'setup', 'init', 'register', 'bootstrap',
                      'initialize']
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
    'excluded_patterns': list(EXCLUDED_PATTERNS)[:7] + ['.pytest_cache']
}

# Default instances
DEFAULT_SRP_THRESHOLDS = SRPThresholds(
    limits=SRPLimits(),
    cohesion=SRPCohesion(),
    severity=SRPSeverity(),
    levels=SRPLevels()
)
DEFAULT_MAGIC_NUMBER_THRESHOLDS = MagicNumberThresholds()
DEFAULT_FILE_PLACEMENT_RULES = FILE_PLACEMENT_RULES
