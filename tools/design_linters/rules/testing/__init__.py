#!/usr/bin/env python3
"""
Purpose: Testing rules package for design linting framework
Scope: Rules for enforcing testing best practices and preventing test anti-patterns
Overview: This package contains rules that ensure proper testing practices are followed,
    including prevention of skipped tests, enforcement of test coverage requirements,
    and detection of testing anti-patterns that reduce test suite effectiveness.
Dependencies: Framework interfaces and AST analysis utilities
Exports: Testing-related linting rules
Interfaces: All rules implement the framework's LintRule interfaces
Implementation: AST-based analysis of test files and test patterns
"""

from .test_skip_rules import NoSkippedTestsRule

__all__ = ["NoSkippedTestsRule"]
