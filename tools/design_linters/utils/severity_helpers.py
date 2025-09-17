#!/usr/bin/env python3
"""
Purpose: Severity-related helper functions
Scope: Common severity handling utilities
Overview: Provides shared logic for severity icons and formatting
Dependencies: Framework interfaces
Exports: Severity display functions
Interfaces: N/A - utility functions
Implementation: Helper functions for severity visualization
"""

from ..framework.interfaces import Severity


def get_severity_icon(severity: Severity) -> str:
    """Get emoji icon for severity level."""
    icons = {Severity.ERROR: "❌", Severity.WARNING: "⚠️", Severity.INFO: "ℹ️"}
    return icons.get(severity, "❓")
