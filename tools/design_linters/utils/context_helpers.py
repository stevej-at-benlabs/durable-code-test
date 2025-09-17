#!/usr/bin/env python3
"""
Purpose: Context-related helper functions
Scope: Common context checking utilities
Overview: Provides shared logic for checking allowed contexts for rules
Dependencies: Framework interfaces
Exports: Context checking functions
Interfaces: N/A - utility functions
Implementation: Helper functions for rule context validation
"""

from typing import Any

from ..framework.interfaces import LintContext


def is_allowed_context(context: LintContext, config: dict[str, Any], default_patterns: list[str] | None = None) -> bool:
    """Check if output/logging is allowed in this context."""
    if default_patterns is None:
        default_patterns = ["test_", "__main__", "debug_", "example_", "demo_", "script_"]

    allowed_patterns = config.get("allowed_patterns", default_patterns)

    return (
        _is_test_file(context)
        or _is_main_function(context)
        or _is_allowed_function(context, allowed_patterns)
        or _is_cli_script(context)
    )


def _is_test_file(context: LintContext) -> bool:
    """Check if this is a test file."""
    file_name = str(context.file_path).lower()
    return any(pattern in file_name for pattern in ["test", "example", "demo", "script"])


def _is_main_function(context: LintContext) -> bool:
    """Check if this is the main function."""
    return context.current_function == "__main__"


def _is_allowed_function(context: LintContext, allowed_patterns: list[str]) -> bool:
    """Check if function name matches allowed patterns."""
    function_name = context.current_function or ""
    return any(pattern in function_name.lower() for pattern in allowed_patterns)


def _is_cli_script(context: LintContext) -> bool:
    """Check if this is a CLI script with argparse usage."""
    return "argparse" in str(context.file_content or "")
