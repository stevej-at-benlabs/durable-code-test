#!/usr/bin/env python3
"""
Purpose: Organization and structure rules for the design linter framework
Scope: Rules that enforce proper file organization and project structure
Overview: This module contains rules that ensure files are properly organized
    within the project structure, preventing common mistakes in file placement.
Dependencies: Framework interfaces
Exports: FileOrganizationRule and other organization-related rules
Interfaces: All rules implement the framework's rule interfaces
Implementation: Path and structure-based analysis rules
"""

from .file_placement_rules import FileOrganizationRule

__all__ = ["FileOrganizationRule"]
