#!/usr/bin/env python3
"""
Purpose: Magic number and literal detection rules for the framework
Scope: Converts magic number detector to framework-based rules
Overview: This package contains rules for detecting magic literals (numbers,
    strings, complex values) that should be named constants. Rules are focused
    and can be enabled/disabled independently for fine-grained control.
Dependencies: Framework interfaces and literal analysis utilities
Exports: Individual literal detection rules
Interfaces: All rules implement LintRule interface
Implementation: Strategy-based rules with proper separation of concerns
"""

from .magic_number_rules import (
    MagicNumberRule,
    MagicComplexRule
)

from .magic_string_rules import (
    MagicStringRule,
    HardcodedPathRule
)

__all__ = [
    'MagicNumberRule',
    'MagicComplexRule',
    'MagicStringRule',
    'HardcodedPathRule',
]
