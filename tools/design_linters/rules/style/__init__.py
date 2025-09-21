#!/usr/bin/env python3
"""
Purpose: Code style and formatting rules for the framework
Scope: Converts style-related linters to framework-based rules
Overview: This package contains rules for code style violations including
    print statements, nesting depth, file headers, and file organization.
    Rules are focused and can be enabled/disabled independently.
Dependencies: Framework interfaces and style analysis utilities
Exports: Individual style-related rules
Interfaces: All rules implement LintRule interface
Implementation: Rule-based architecture with proper separation of concerns
"""

from .file_header_rules import FileHeaderRule
from .nesting_rules import DeepFunctionRule, ExcessiveNestingRule
from .print_statement_rules import ConsoleOutputRule, PrintStatementRule

__all__ = [
    # File header rules
    "FileHeaderRule",
    # Print statement rules
    "PrintStatementRule",
    "ConsoleOutputRule",
    # Nesting rules
    "ExcessiveNestingRule",
    "DeepFunctionRule",
]
