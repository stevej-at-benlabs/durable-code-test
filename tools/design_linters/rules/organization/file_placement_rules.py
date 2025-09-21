#!/usr/bin/env python3
"""
Purpose: File organization and placement linting rule for the design linter framework
Scope: Organization category rule implementation with JSON-based layout configuration
Overview: This module implements a file placement rule that validates files against
    a JSON layout configuration file. It supports both AI-readable guidance and
    machine-readable regex patterns for comprehensive file organization enforcement.
Dependencies: Framework interfaces, pathlib for path analysis, json for config loading, re for regex
Exports: FileOrganizationRule implementation
Interfaces: Implements ASTLintRule interface from framework
Implementation: JSON-driven path validation with regex pattern matching
"""

import json
import re
from pathlib import Path
from typing import Any

from design_linters.framework.interfaces import ASTLintRule, LintContext, LintViolation, Severity
from loguru import logger


class FileOrganizationRule(ASTLintRule):
    """Detect improperly placed files based on JSON layout configuration."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the rule with configuration."""
        super().__init__()
        self.config = config or {}
        self.layout_rules = None

        # Load layout rules from JSON file if specified
        layout_file = self.config.get("layout_rules_file", ".ai/layout.json")
        self._load_layout_rules(layout_file)

        # Fallback to old config style if no JSON file found
        if not self.layout_rules:
            logger.warning(f"Layout rules file not found: {layout_file}, using default configuration")
            self._use_default_config()

    def _load_layout_rules(self, layout_file: str) -> None:
        """Load layout rules from JSON file."""
        try:
            layout_path = Path(layout_file)
            if not layout_path.is_absolute():
                # Try to find it relative to project root
                layout_path = Path.cwd() / layout_path

            if layout_path.exists():
                with open(layout_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "linter_rules" in data:
                        self.layout_rules = data["linter_rules"]
                        logger.debug(f"Loaded layout rules from {layout_path}")
                    else:
                        logger.error(f"No 'linter_rules' section found in {layout_path}")
        except Exception as e:
            logger.error(f"Failed to load layout rules from {layout_file}: {e}")

    def _use_default_config(self) -> None:
        """Fall back to default configuration for backward compatibility."""
        self.layout_rules = {
            "paths": {
                ".": {
                    "description": "Root directory (fallback rules)",
                    "allow": [
                        "^[^/]+\\.md$",
                        "^[^/]+\\.yml$",
                        "^[^/]+\\.yaml$",
                        "^[^/]+\\.json$",
                        "^[^/]+\\.toml$",
                        "^Makefile",
                        "^setup\\.py$",
                        "^conftest\\.py$"
                    ],
                    "deny": [
                        "^test[_-].*\\.py$",
                        "^debug[_-].*\\.py$",
                        "^tmp[_-].*\\.py$",
                        "^temp[_-].*\\.py$"
                    ]
                }
            },
            "global_patterns": {
                "test_files": {
                    "patterns": [
                        "test_.*\\.py$",
                        ".*_test\\.py$"
                    ],
                    "must_be_in": [
                        "^test/"
                    ]
                }
            }
        }

    @property
    def rule_id(self) -> str:
        return "organization.file-placement"

    @property
    def rule_name(self) -> str:
        return "File Placement Check"

    @property
    def description(self) -> str:
        return "Ensures files are placed in appropriate directories according to JSON layout configuration"

    @property
    def severity(self) -> Severity:
        return Severity.WARNING

    @property
    def categories(self) -> set[str]:
        return {"organization", "structure", "conventions"}

    def should_check_node(self, node: Any, context: LintContext) -> bool:
        """Check only module nodes to validate file placement once per file."""
        return hasattr(node, "__class__") and node.__class__.__name__ == "Module"

    def check_node(self, node: Any, context: LintContext) -> list[LintViolation]:
        """Check if the file is properly placed according to layout rules."""
        violations = []

        if not context.file_path or not self.layout_rules:
            return violations

        file_path = Path(context.file_path)

        # Get relative path from project root
        try:
            cwd = Path.cwd()
            rel_path = file_path.relative_to(cwd) if file_path.is_absolute() else file_path
        except ValueError as e:
            logger.debug(f"File is outside project directory: {file_path}, error: {e}")
            return violations

        # Convert to string for pattern matching
        path_str = str(rel_path).replace('\\', '/')  # Normalize path separators

        # Check global patterns first (like test files that shouldn't be in source)
        violations.extend(self._check_global_patterns(path_str, rel_path))

        # Check specific directory rules
        violations.extend(self._check_directory_rules(path_str, rel_path))

        return violations

    def _check_global_patterns(self, path_str: str, rel_path: Path) -> list[LintViolation]:
        """Check file against global patterns that apply everywhere."""
        violations = []

        if "global_patterns" not in self.layout_rules:
            return violations

        global_patterns = self.layout_rules["global_patterns"]

        # Check if file should be denied everywhere
        if "deny_everywhere" in global_patterns:
            for pattern in global_patterns["deny_everywhere"]:
                if re.search(pattern, path_str):
                    violations.append(LintViolation(
                        rule_id=self.rule_id,
                        file_path=str(rel_path),
                        line=1,
                        column=0,
                        severity=Severity.ERROR,
                        message=f"File type is forbidden: {rel_path.name}",
                        description=f"Files matching pattern '{pattern}' should not be committed",
                        suggestion="Remove this file or add it to .gitignore"
                    ))
                    return violations  # No need to check further if file is forbidden

        # Check test file placement
        if "test_files" in global_patterns:
            test_config = global_patterns["test_files"]
            is_test_file = any(re.search(pattern, path_str) for pattern in test_config["patterns"])

            if is_test_file:
                in_test_dir = any(re.match(pattern, path_str) for pattern in test_config["must_be_in"])
                if not in_test_dir:
                    violations.append(LintViolation(
                        rule_id=self.rule_id,
                        file_path=str(rel_path),
                        line=1,
                        column=0,
                        severity=self.severity,
                        message=f"Test file '{rel_path.name}' is not in test directory",
                        description="Test files must be placed in the test/ directory",
                        suggestion=f"Move to test/unit_test/ or test/integration_test/"
                    ))

        return violations

    def _check_directory_rules(self, path_str: str, rel_path: Path) -> list[LintViolation]:
        """Check file against specific directory rules."""
        violations = []

        if "paths" not in self.layout_rules:
            return violations

        # Find the most specific matching directory rule
        matched_rule = None
        matched_path = None

        for dir_path, rules in self.layout_rules["paths"].items():
            # Check if file is in this directory
            if dir_path == ".":
                # Root directory - check if file has no parent directories
                if len(rel_path.parts) == 1:
                    matched_rule = rules
                    matched_path = dir_path
            elif path_str.startswith(dir_path):
                # Use the most specific (longest) matching path
                if not matched_path or len(dir_path) > len(matched_path):
                    matched_rule = rules
                    matched_path = dir_path

        if not matched_rule:
            return violations

        # Check against deny patterns first
        if "deny" in matched_rule:
            for pattern in matched_rule["deny"]:
                if re.search(pattern, path_str):
                    violations.append(LintViolation(
                        rule_id=self.rule_id,
                        file_path=str(rel_path),
                        line=1,
                        column=0,
                        severity=self.severity,
                        message=f"File '{rel_path.name}' is forbidden in {matched_path or 'root'}",
                        description=f"Files matching pattern '{pattern}' are not allowed here",
                        suggestion=self._get_suggestion_for_file(rel_path.name, pattern)
                    ))
                    return violations  # Don't check allow if denied

        # Check against allow patterns (if specified)
        if "allow" in matched_rule:
            file_allowed = any(re.search(pattern, path_str) for pattern in matched_rule["allow"])
            if not file_allowed:
                # File doesn't match any allow pattern
                violations.append(LintViolation(
                    rule_id=self.rule_id,
                    file_path=str(rel_path),
                    line=1,
                    column=0,
                    severity=Severity.INFO,
                    message=f"File '{rel_path.name}' may not belong in {matched_path or 'root'}",
                    description=f"File doesn't match expected patterns for this directory",
                    suggestion=self._get_suggestion_for_file(rel_path.name, None)
                ))

        return violations

    def _get_suggestion_for_file(self, filename: str, pattern: str | None) -> str:
        """Generate suggestion for where to place a file."""
        if re.match(r"^debug|^tmp|^temp", filename):
            return "Move to 'scripts/debug/' or remove if no longer needed"
        elif re.match(r"test_.*\.py$|.*_test\.py$", filename):
            return "Move to 'test/unit_test/' following the project test structure"
        elif filename.endswith(".tsx") or filename.endswith(".ts"):
            if "service" in filename.lower():
                return "Move to 'features/[feature-name]/services/'"
            elif filename.startswith("use"):
                return "Move to appropriate hooks directory"
            else:
                return "Move to 'components/' for simple UI or 'features/' for complex components"
        elif filename.endswith(".py"):
            if pattern and "test" in pattern:
                return "Move to 'test/' directory"
            return "Move to appropriate module directory based on functionality"
        else:
            return "Review project layout rules in .ai/layout.json for proper placement"