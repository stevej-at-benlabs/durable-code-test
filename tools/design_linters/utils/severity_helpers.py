#!/usr/bin/env python3
"""
Purpose: Severity-related helper functions
Scope: Common severity handling utilities
Overview: Overview: This utility module provides comprehensive severity level management for the design
    linter framework, enabling consistent classification and prioritization of violations across
    all rules. It defines severity levels (ERROR, WARNING, INFO) with associated properties like
    exit codes, display colors, and sorting priorities. The module includes helper functions for
    severity comparison, filtering violations by minimum severity, converting between string
    and enum representations, and aggregating severity statistics. It also provides severity
    escalation logic for promoting warnings to errors based on configuration, severity threshold
    validation for CI/CD integration, and customizable severity mappings for different
    environments. The consistent severity handling ensures violations are properly prioritized
    and that the linter can be configured to fail builds only for serious issues.
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
