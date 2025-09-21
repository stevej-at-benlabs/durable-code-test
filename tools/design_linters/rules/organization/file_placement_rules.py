#!/usr/bin/env python3
"""
Purpose: File organization and placement linting rule for the design linter framework
Scope: Organization category rule implementation with configurable parameters
Overview: This module implements comprehensive file organization rules that ensure proper project
    structure and prevent common placement mistakes that can lead to maintenance issues. It detects
    files placed in incorrect directories such as debug scripts in root, test files outside test
    directories, frontend code mixed with backend, and configuration files in source directories.
    The rule uses configurable patterns to identify file types and their allowed locations,
    supporting various project structures and conventions. It helps maintain clean separation of
    concerns, prevents accidental commits of temporary files, and ensures consistent project
    organization across team members. The implementation includes helpful suggestions for where
    files should be moved and can be configured to enforce organization standards specific to
    each project's architecture.
Dependencies: Framework interfaces, pathlib for path analysis, rule base classes
Exports: FileOrganizationRule implementation
Interfaces: Implements ASTLintRule interface from framework
Implementation: Path-based analysis with configurable patterns and clear violation reporting
"""

import re
from pathlib import Path
from typing import Any

from design_linters.framework.interfaces import ASTLintRule, LintContext, LintViolation, Severity
from loguru import logger


class FileOrganizationRule(ASTLintRule):
    """Detect improperly placed files in the project structure."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the rule with configuration."""
        super().__init__()
        self.config = config or {}

        # Default allowed root files
        self.allowed_root_files = self.config.get(
            "allowed_root_files",
            [
                "setup.py",
                "conftest.py",
                "manage.py",
                "wsgi.py",
                "asgi.py",
                "__init__.py",
            ],
        )

        # Patterns for files that should never be in root
        self.forbidden_root_patterns = self.config.get(
            "forbidden_root_patterns",
            [
                r"^debug[_\-].*\.py$",
                r"^test[_\-].*\.py$",
                r"^tmp[_\-].*\.py$",
                r"^temp[_\-].*\.py$",
                r".*_test\.py$",
                r".*_spec\.py$",
                r"^test\-.*\.py$",  # test-module.py pattern
            ],
        )

        # Directory rules: file pattern -> allowed directories
        # Note: Be careful with test patterns - only match actual test files
        self.placement_rules = self.config.get(
            "placement_rules",
            {
                r"^test_.*\.py$": ["test/"],  # Files starting with test_
                r".*_test\.py$": ["test/"],  # Files ending with _test
                r".*\.tsx?$": ["durable-code-app/frontend/", "frontend/", "src/"],
                r".*\.jsx?$": [
                    "durable-code-app/frontend/",
                    "frontend/",
                    "src/",
                    "scripts/",
                ],
                r".*\.html$": [
                    "durable-code-app/",
                    "templates/",
                    "static/",
                    "public/",
                    ".ai/",
                ],
                r".*\.css$": ["durable-code-app/", "static/", "public/", "src/"],
            },
        )

    @property
    def rule_id(self) -> str:
        return "organization.file-placement"

    @property
    def rule_name(self) -> str:
        return "File Placement Check"

    @property
    def description(self) -> str:
        return "Ensures files are placed in appropriate directories according to project conventions"

    @property
    def severity(self) -> Severity:
        return Severity.WARNING

    @property
    def categories(self) -> set[str]:
        return {"organization", "structure", "conventions"}

    def should_check_node(self, node: Any, context: LintContext) -> bool:
        """Always check the file path, regardless of node type."""
        # We only need to check once per file, so only check the module node
        # This rule is designed for Python files but can check paths of any file type
        return hasattr(node, "__class__") and node.__class__.__name__ == "Module"

    def check_node(self, node: Any, context: LintContext) -> list[LintViolation]:
        """Check if the file is properly placed according to project conventions."""
        violations = []

        if not context.file_path:
            return violations

        file_path = Path(context.file_path)

        # Get relative path from project root
        try:
            # Assume we're running from project root or can determine it
            cwd = Path.cwd()
            rel_path = file_path.relative_to(cwd) if file_path.is_absolute() else file_path
        except ValueError as e:
            # File is outside project directory
            logger.debug(
                "File is outside project directory",
                file_path=str(file_path),
                error=str(e),
            )
            return violations

        # Check if file is in root directory
        if len(rel_path.parts) == 1:
            violations.extend(self._check_root_file(rel_path, context))

        # Check placement rules for all files
        violations.extend(self._check_placement_rules(rel_path, context))

        return violations

    def _check_root_file(self, file_path: Path, context: LintContext) -> list[LintViolation]:
        """Check if a root-level file is allowed."""
        violations = []
        filename = file_path.name

        # Check if file is explicitly allowed
        if filename in self.allowed_root_files:
            return violations

        # Check against forbidden patterns
        for pattern in self.forbidden_root_patterns:
            if re.match(pattern, filename):
                violation = LintViolation(
                    rule_id=self.rule_id,
                    file_path=str(file_path),
                    line=1,
                    column=0,
                    severity=self.severity,
                    message=f"File '{filename}' should not be in the root directory",
                    description="Debug, test, and temporary files should be placed in appropriate directories",
                    suggestion=self._get_suggestion_for_file(filename),
                )
                violations.append(violation)
                return violations

        # Check if it's a Python file not in the allowed list
        if filename.endswith(".py") and filename not in self.allowed_root_files:
            violation = LintViolation(
                rule_id=self.rule_id,
                file_path=str(file_path),
                line=1,
                column=0,
                severity=Severity.INFO,
                message=f"Python file '{filename}' in root directory",
                description="Consider if this file belongs in a subdirectory",
                suggestion="Move to an appropriate module directory like 'tools/', 'scripts/', or 'src/'",
            )
            violations.append(violation)

        return violations

    def _check_placement_rules(self, file_path: Path, context: LintContext) -> list[LintViolation]:
        """Check if file matches placement rules."""
        violations = []
        filename = file_path.name
        path_str = str(file_path)

        for pattern, allowed_dirs in self.placement_rules.items():
            if not re.search(pattern, filename):
                continue

            # Check if file is in one of the allowed directories
            is_allowed = any(allowed_dir in path_str for allowed_dir in allowed_dirs)

            # Skip if allowed or if root file (already reported)
            if is_allowed or len(file_path.parts) <= 1:
                continue

            violation = LintViolation(
                rule_id=self.rule_id,
                file_path=str(file_path),
                line=1,
                column=0,
                severity=self.severity,
                message=f"File '{filename}' is not in an expected directory",
                description=f"Files matching pattern '{pattern}' should be in: {', '.join(allowed_dirs)}",
                suggestion=f"Move to one of: {', '.join(allowed_dirs)}",
            )
            violations.append(violation)

        return violations

    def _get_suggestion_for_file(self, filename: str) -> str:
        """Get suggestion for where to place a file."""
        if re.match(r"^debug|^tmp|^temp", filename):
            return "Move to 'scripts/debug/' or remove if no longer needed"
        elif re.match(r"^test[_\-].*\.py$|.*_test\.py$", filename):
            return "Move to 'test/' directory following the project test structure"
        elif filename.endswith(".py"):
            return "Move to an appropriate module directory like 'tools/' or 'scripts/'"
        else:
            return "Move to an appropriate directory based on file type and purpose"
