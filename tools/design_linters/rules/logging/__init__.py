#!/usr/bin/env python3
"""
Purpose: Logging best practices rules for the framework
Scope: Implements logging-specific rules with focus on loguru
Overview: This package contains rules for enforcing logging best practices,
    with specific support for loguru. Rules detect improper logging usage,
    suggest loguru patterns, and enforce consistent logging practices across
    the codebase for better observability and debugging.
Dependencies: Framework interfaces and logging analysis utilities
Exports: Individual logging-focused rules
Interfaces: All rules implement LintRule interface
Implementation: Rule-based architecture for logging standards
"""

from .loguru_rules import (
    UseLoguruRule,
    LoguruConfigurationRule,
    StructuredLoggingRule,
    LogLevelConsistencyRule,
    LoguruImportRule
)

from .general_logging_rules import (
    NoPlainPrintRule,
    ProperLogLevelsRule,
    LoggingInExceptionsRule
)

__all__ = [
    # Loguru-specific rules
    'UseLoguruRule',
    'LoguruConfigurationRule',
    'StructuredLoggingRule',
    'LogLevelConsistencyRule',
    'LoguruImportRule',

    # General logging rules
    'NoPlainPrintRule',
    'ProperLogLevelsRule',
    'LoggingInExceptionsRule',
]
