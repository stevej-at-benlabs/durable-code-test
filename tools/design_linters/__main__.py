#!/usr/bin/env python3
"""
Purpose: Main entry point for the unified design linter framework
Scope: Provides CLI access to all design linting functionality
Overview: This module serves as the main entry point for the unified design
    linter framework, replacing individual CLI tools with a single, extensible
    interface. It supports backward compatibility while enabling the new
    pluggable architecture with proper SOLID principle compliance.
Dependencies: Framework CLI components
Exports: Main entry point for package execution
Interfaces: Command-line interface for all linting operations
Implementation: Delegates to unified CLI with rule discovery and orchestration
"""

from .cli import main

if __name__ == '__main__':
    main()
