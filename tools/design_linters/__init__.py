#!/usr/bin/env python3
"""
Purpose: Unified design linter framework package
Scope: Framework-based implementation for all design linting functionality
Overview: This module provides the main entry point for the unified design
    linter framework. It follows SOLID principles with proper separation
    of concerns and uses a pluggable rule-based system for extensible
    design pattern enforcement.
Dependencies: Framework components and rule system
Exports: Framework-based design analysis
Interfaces: Uses unified framework CLI and rule system
Implementation: Clean, extensible architecture with focused rule-based design
"""

from .framework import interfaces, analyzer, rule_registry, reporters
from .cli import main

__version__ = "1.0.0"
__all__ = [
    "interfaces",
    "analyzer",
    "rule_registry",
    "reporters",
    "main"
]
