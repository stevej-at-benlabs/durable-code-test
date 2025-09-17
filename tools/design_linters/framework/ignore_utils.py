#!/usr/bin/env python3
# design-lint: ignore-file[literals.*]
"""
Purpose: Utilities for handling ignore/suppress directives in code
Scope: Framework utilities for skipping specific linting violations
Overview: Provides functionality to detect and process ignore directives
    (like # design-lint: ignore) in source code, allowing developers to
    selectively disable specific linting rules for lines or blocks of code.
Dependencies: AST, re for pattern matching
Exports: Functions for checking and processing ignore directives
Interfaces: Used by linting rules to determine if violations should be skipped
Implementation: Pattern-based detection of ignore comments
"""

import ast
import re
from typing import Any

# Common ignore directive patterns
IGNORE_PATTERNS = [
    r"#\s*design-lint:\s*ignore",  # Our custom ignore directive
    r"#\s*design-lint:\s*disable",  # Alternative disable directive
    r"#\s*noqa",  # Standard Python linting ignore
    r"#\s*type:\s*ignore",  # Type checking ignore
]

# Specific rule ignore patterns (e.g., # design-lint: ignore[literals.magic-number])
SPECIFIC_RULE_PATTERN = r"#\s*design-lint:\s*(?:ignore|disable)\[([^\]]+)\]"


def _has_general_ignore(line: str) -> bool:
    """Check if line has general ignore patterns."""
    return any(re.search(pattern, line, re.IGNORECASE) for pattern in IGNORE_PATTERNS)


def _rule_matches_ignore(rule_id: str, ignored_rule: str) -> bool:
    """Check if a rule ID matches an ignored rule pattern."""
    if ignored_rule.endswith("*"):
        prefix = ignored_rule[:-1]
        return rule_id.startswith(prefix)
    return ignored_rule == rule_id


def _has_specific_rule_ignore(line: str, rule_id: str) -> bool:
    """Check if line has specific rule ignore for given rule_id."""
    match = re.search(SPECIFIC_RULE_PATTERN, line, re.IGNORECASE)
    if not match:
        return False

    ignored_rules = [r.strip() for r in match.group(1).split(",")]
    return any(_rule_matches_ignore(rule_id, ignored_rule) for ignored_rule in ignored_rules)


def should_ignore_line(file_content: str, line_number: int, rule_id: str | None = None) -> bool:
    """
    Check if a specific line should be ignored based on inline comments.

    Args:
        file_content: The full file content
        line_number: The line number to check (1-indexed)
        rule_id: Optional specific rule ID to check for

    Returns:
        True if the line should be ignored, False otherwise
    """
    if not file_content:
        return False

    lines = file_content.splitlines()
    if line_number < 1 or line_number > len(lines):
        return False

    line = lines[line_number - 1]

    # Check for general ignore patterns
    if _has_general_ignore(line):
        return True

    # Check for specific rule ignores
    return bool(rule_id and _has_specific_rule_ignore(line, rule_id))


def should_ignore_node(node: ast.AST, file_content: str, rule_id: str | None = None) -> bool:
    """
    Check if an AST node should be ignored based on inline comments.

    Args:
        node: The AST node to check
        file_content: The full file content
        rule_id: Optional specific rule ID to check for

    Returns:
        True if the node should be ignored, False otherwise
    """
    if not hasattr(node, "lineno"):
        return False

    return should_ignore_line(file_content, node.lineno, rule_id)


def should_ignore_violation(violation: Any, file_content: str) -> bool:
    """
    Check if a violation should be ignored based on its location.

    Args:
        violation: The violation object (must have line_number and rule_id attributes)
        file_content: The full file content

    Returns:
        True if the violation should be ignored, False otherwise
    """
    if not hasattr(violation, "line_number") or not violation.line_number:
        return False

    rule_id = getattr(violation, "rule_id", None)
    return should_ignore_line(file_content, violation.line_number, rule_id)


def extract_ignore_next_line_directives(file_content: str) -> set[int]:
    """
    Extract line numbers that should be ignored based on "ignore next line" directives.

    Args:
        file_content: The full file content

    Returns:
        Set of line numbers (1-indexed) that should be ignored
    """
    ignored_lines = set()
    lines = file_content.splitlines()

    for i, line in enumerate(lines):
        # Check for "ignore next line" pattern
        if re.search(r"#\s*design-lint:\s*ignore-next-line", line, re.IGNORECASE):
            # Ignore the next non-empty line
            for j in range(i + 1, len(lines)):
                if lines[j].strip():
                    ignored_lines.add(j + 1)  # Convert to 1-indexed
                    break

    return ignored_lines


def has_file_level_ignore(file_content: str, rule_id: str | None = None) -> bool:
    """
    Check if the entire file should be ignored based on file-level directives.

    Args:
        file_content: The full file content
        rule_id: Optional specific rule ID to check for

    Returns:
        True if the entire file should be ignored, False otherwise
    """
    if not file_content:
        return False

    # Check first few lines for file-level ignore directives
    lines = file_content.splitlines()[:10]  # Check first 10 lines

    for line in lines:
        # Check for file-level ignore pattern
        if re.search(r"#\s*design-lint:\s*ignore-file", line, re.IGNORECASE):
            return True

        # Check for specific rule file-level ignore
        if not rule_id:
            continue

        match = re.search(r"#\s*design-lint:\s*ignore-file\[([^\]]+)\]", line, re.IGNORECASE)
        if not match:
            continue

        ignored_rules = [r.strip() for r in match.group(1).split(",")]
        if any(_rule_matches_ignore(rule_id, ignored_rule) for ignored_rule in ignored_rules):
            return True

    return False
