#!/usr/bin/env python3
"""
Purpose: SOLID principle rules for the pluggable linter framework
Scope: Implements SOLID principle violations as pluggable rules
Overview: This package contains individual rules for detecting violations
    of SOLID principles (Single Responsibility, Open/Closed, Liskov Substitution,
    Interface Segregation, Dependency Inversion). Each principle is implemented
    as separate, focused rules that can be enabled/disabled independently.
Dependencies: Framework interfaces and AST analysis
Exports: Individual SOLID principle rules
Interfaces: All rules implement LintRule interface
Implementation: Rule-based architecture with focused responsibilities
"""

from .srp_rules import (
    TooManyMethodsRule,
    TooManyResponsibilitiesRule,
    LowCohesionRule,
    ClassTooBigRule,
    TooManyDependenciesRule
)

# Export all rules for discovery
__all__ = [
    # SRP Rules
    'TooManyMethodsRule',
    'TooManyResponsibilitiesRule',
    'LowCohesionRule',
    'ClassTooBigRule',
    'TooManyDependenciesRule',
]
