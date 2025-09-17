#!/usr/bin/env python3
"""
Purpose: Magic number detection rules for the framework
Scope: Converts magic number detector to framework-based rules
Overview: This package contains rules for detecting magic numbers that should
    be named constants. Rules are focused and can be enabled/disabled
    independently for fine-grained control.
Dependencies: Framework interfaces and literal analysis utilities
Exports: Individual literal detection rules
Interfaces: All rules implement LintRule interface
Implementation: Strategy-based rules with proper separation of concerns
"""

from .magic_number_rules import MagicComplexRule, MagicNumberRule

__all__ = [
    "MagicNumberRule",
    "MagicComplexRule",
]
