#!/usr/bin/env python3
"""
Purpose: File header validation linting rule for the design linter framework
Scope: Style category rule implementation for enforcing file header standards
Overview: This module validates that all source files contain comprehensive documentation headers
    according to project standards, ensuring consistent documentation across the codebase. It checks
    for required fields including Purpose, Scope, and Overview in all files, plus additional fields
    like Dependencies, Exports, and Interfaces for code files. The rule supports multiple file types
    with format-specific header patterns for Python, TypeScript, JavaScript, HTML, YAML, and Markdown.
    It validates not just the presence of fields but also their content quality, ensuring descriptions
    are substantive rather than placeholders. The module provides file-type specific templates for
    missing headers and helpful suggestions for improving incomplete headers. This ensures every file
    in the project is self-documenting, helping developers understand file purposes without examining
    implementation details, which is especially valuable for onboarding and maintenance.
Dependencies: Framework interfaces, pathlib for file operations, re for pattern matching
Exports: FileHeaderRule implementation
Interfaces: Implements ASTLintRule interface from framework
Implementation: Pattern-based header extraction with file-type specific validation
"""

import re
from pathlib import Path
from typing import Any

from design_linters.framework.interfaces import ASTLintRule, LintContext, LintViolation, Severity
from loguru import logger


class FileHeaderRule(ASTLintRule):
    """Validate file headers according to project standards."""

    # Required fields for all files
    REQUIRED_FIELDS = {"purpose", "scope"}

    # Required comprehensive overview field
    REQUIRED_OVERVIEW = {"overview"}

    # Additional required fields for code files
    CODE_REQUIRED_FIELDS = {"dependencies", "exports", "interfaces"}

    # Recommended fields that generate warnings if missing
    RECOMMENDED_FIELDS = {"implementation"}

    # File type configurations for header extraction
    FILE_CONFIGS = {
        ".py": {
            "header_pattern": re.compile(r'^(#!/usr/bin/env python3\n)?"""[\s\S]*?"""', re.MULTILINE),
            "field_pattern": re.compile(r"^(\w+(?:/\w+)?):?\s*(.+)$", re.MULTILINE),
            "is_code": True,
            "min_header_lines": 5,
        },
        ".ts": {
            "header_pattern": re.compile(r"^/\*\*[\s\S]*?\*/", re.MULTILINE),
            "field_pattern": re.compile(r"^\s*\*?\s*(\w+(?:/\w+)?):?\s*(.+)$", re.MULTILINE),
            "is_code": True,
            "min_header_lines": 5,
        },
        ".tsx": {
            "header_pattern": re.compile(r"^/\*\*[\s\S]*?\*/", re.MULTILINE),
            "field_pattern": re.compile(r"^\s*\*?\s*(\w+(?:/\w+)?):?\s*(.+)$", re.MULTILINE),
            "is_code": True,
            "min_header_lines": 5,
        },
        ".js": {
            "header_pattern": re.compile(r"^/\*\*[\s\S]*?\*/", re.MULTILINE),
            "field_pattern": re.compile(r"^\s*\*?\s*(\w+(?:/\w+)?):?\s*(.+)$", re.MULTILINE),
            "is_code": True,
            "min_header_lines": 5,
        },
        ".jsx": {
            "header_pattern": re.compile(r"^/\*\*[\s\S]*?\*/", re.MULTILINE),
            "field_pattern": re.compile(r"^\s*\*?\s*(\w+(?:/\w+)?):?\s*(.+)$", re.MULTILINE),
            "is_code": True,
            "min_header_lines": 5,
        },
        ".md": {
            "header_pattern": re.compile(r"^# .+?\n\n(\*\*\w+\*\*:.+?\n)+", re.MULTILINE),
            "field_pattern": re.compile(r"^\*\*(\w+)\*\*:\s*(.+)$", re.MULTILINE),
            "is_code": False,
            "min_header_lines": 3,
        },
        ".html": {
            "header_pattern": re.compile(r"^<!DOCTYPE html>\s*\n<!--[\s\S]*?-->", re.MULTILINE),
            "field_pattern": re.compile(r"^(\w+):\s*(.+)$", re.MULTILINE),
            "is_code": True,
            "min_header_lines": 3,
        },
        ".yml": {
            "header_pattern": re.compile(r"^# Purpose:[\s\S]*?(?=\n[^#]|\Z)", re.MULTILINE),
            "field_pattern": re.compile(r"^# (\w+):\s*(.+)$", re.MULTILINE),
            "is_code": False,
            "min_header_lines": 2,
        },
        ".yaml": {
            "header_pattern": re.compile(r"^# Purpose:[\s\S]*?(?=\n[^#]|\Z)", re.MULTILINE),
            "field_pattern": re.compile(r"^# (\w+):\s*(.+)$", re.MULTILINE),
            "is_code": False,
            "min_header_lines": 2,
        },
    }

    # Files/patterns to skip
    SKIP_PATTERNS = [
        "__pycache__",
        ".git",
        "node_modules",
        ".pytest_cache",
        "dist",
        "build",
        ".egg-info",
        "migrations",
        "__init__.py",  # Often empty or minimal
        "conftest.py",  # Test configuration
        "test_*.py",  # Test files have different standards
        "*_test.py",  # Test files
        "*.min.js",  # Minified files
        "*.min.css",  # Minified files
        "package-lock.json",
        "poetry.lock",
        "*.pyc",
        ".env*",
        "*.log",
        "*.tmp",
        "*.temp",
        "*.cache",
        "*.sqlite",
        "*.db",
    ]

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the rule with configuration."""
        super().__init__()
        self.config = config or {}
        self.strict_mode = self.config.get("strict_mode", True)
        self.min_overview_words = self.config.get("min_overview_words", 20)
        self.check_all_files = self.config.get("check_all_files", True)
        self.skip_test_files = self.config.get("skip_test_files", False)  # Don't skip test files by default

    @property
    def rule_id(self) -> str:
        return "style.file-header"

    @property
    def rule_name(self) -> str:
        return "File Header Validation"

    @property
    def description(self) -> str:
        return "Ensures all files have proper headers with required fields according to FILE_HEADER_STANDARDS.md"

    @property
    def severity(self) -> Severity:
        return Severity.WARNING

    @property
    def categories(self) -> set[str]:
        return {"style", "documentation", "standards"}

    def should_check_node(self, node: Any, context: LintContext) -> bool:
        """Check the module node for header validation."""
        # We only check the module node once per file
        return hasattr(node, "__class__") and node.__class__.__name__ == "Module"

    def check_node(self, node: Any, context: LintContext) -> list[LintViolation]:
        """Check if the file has a proper header."""
        violations = []

        # Get file path and check if we should skip it
        file_path = Path(context.file_path)
        if self._should_skip_file(file_path):
            return violations

        # Get file extension and check if supported
        file_ext = file_path.suffix
        if file_ext not in self.FILE_CONFIGS:
            # If check_all_files is enabled, report unsupported files
            if self.check_all_files and file_ext not in [".json", ".txt", ".csv", ".xml"]:
                logger.debug(f"Unsupported file type for header check: {file_ext}")
            return violations

        config = self.FILE_CONFIGS[file_ext]

        # Get file content from context or read from disk
        if context.file_content is not None:
            content = context.file_content
        else:
            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception as e:
                logger.error(f"Could not read file {file_path}: {e}")
                return violations

        # Extract header
        header_match = config["header_pattern"].search(content[:2000])  # Check first 2000 chars
        if not header_match:
            violations.append(
                self.create_violation(
                    context=context,
                    node=node,
                    message=f"Missing file header in {file_path.name}",
                    description="File must have a properly formatted header with required fields",
                    suggestion=self._get_header_template(file_ext),
                )
            )
            return violations

        # Parse header fields
        header_content = header_match.group(0)
        fields = self._parse_header_fields(header_content, config["field_pattern"])

        # Validate required fields
        missing_required = self.REQUIRED_FIELDS - set(fields.keys())
        if missing_required:
            violations.append(
                self.create_violation(
                    context=context,
                    node=node,
                    message=f"Missing required header fields: {', '.join(sorted(missing_required))}",
                    description="All files must have Purpose and Scope fields in their headers",
                    suggestion=f"Add the missing fields to the file header:\n{self._format_missing_fields(missing_required)}",
                )
            )

        # Check for Overview field (required but checked separately for better messaging)
        if "overview" not in fields:
            violations.append(
                self.create_violation(
                    context=context,
                    node=node,
                    message="Missing required Overview field in header",
                    description="Overview field must provide comprehensive summary of the file's role",
                    suggestion="Add an Overview field with detailed explanation of what this file does and how it fits into the system",
                )
            )
        elif self.strict_mode:
            # Validate Overview content quality
            overview_content = fields.get("overview", "")
            word_count = len(overview_content.split())
            if word_count < self.min_overview_words:
                violations.append(
                    self.create_violation(
                        context=context,
                        node=node,
                        message=f"Overview field too brief ({word_count} words, minimum {self.min_overview_words})",
                        description="Overview should be comprehensive enough to understand the file without reading code",
                        suggestion="Expand the Overview field to include: responsibilities, workflows, architectural role, and key behaviors",
                    )
                )

        # Check code-specific required fields
        if config.get("is_code", False):
            missing_code_fields = self.CODE_REQUIRED_FIELDS - set(fields.keys())
            if missing_code_fields:
                violations.append(
                    self.create_violation(
                        context=context,
                        node=node,
                        message=f"Missing required code header fields: {', '.join(sorted(missing_code_fields))}",
                        description="Code files must have Dependencies, Exports, and Interfaces fields",
                        suggestion=f"Add the missing fields:\n{self._format_missing_fields(missing_code_fields)}",
                    )
                )

            # Check recommended fields (warnings only)
            if self.strict_mode:
                missing_recommended = self.RECOMMENDED_FIELDS - set(fields.keys())
                if missing_recommended:
                    violations.append(
                        self.create_violation(
                            context=context,
                            node=node,
                            message="Missing recommended header field: Implementation",
                            description="Implementation field helps document architectural decisions and patterns",
                            suggestion="Add Implementation field describing notable algorithms, patterns, or architectural decisions",
                        )
                    )

        # Validate field content quality
        if self.strict_mode:
            content_issues = self._validate_field_content(fields)
            for issue in content_issues:
                violations.append(
                    self.create_violation(
                        context=context,
                        node=node,
                        message=issue["message"],
                        description=issue["description"],
                        suggestion=issue["suggestion"],
                    )
                )

        return violations

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        path_str = str(file_path)

        for pattern in self.SKIP_PATTERNS:
            if pattern.startswith("*"):
                if path_str.endswith(pattern[1:]):
                    return True
            elif pattern.endswith("*"):
                if Path(path_str).name.startswith(pattern[:-1]):
                    return True
            elif pattern in path_str:
                return True

        # Skip test files only if explicitly configured to skip them
        return self.skip_test_files and ("test" in path_str.lower() or "spec" in path_str.lower())

    def _parse_header_fields(self, header_content: str, field_pattern: re.Pattern) -> dict[str, str]:
        """Parse header fields from content."""
        fields = {}

        # Split into lines and process
        lines = header_content.split("\n")
        current_field = None
        current_value = []

        for line in lines:
            # Check if this line starts with significant indentation (continuation line)
            is_continuation = line.startswith("    ") or (line.startswith(" *") and ":" not in line)

            # Try to match a field only if not a continuation line
            if not is_continuation:
                match = field_pattern.match(line.strip())
                if match and ":" in line:  # Ensure it has a colon to be a field
                    # Save previous field if exists
                    if current_field:
                        fields[current_field.lower()] = " ".join(current_value).strip()
                    # Start new field
                    current_field = match.group(1)
                    current_value = [match.group(2)] if len(match.groups()) > 1 else []
                    continue

            # Handle continuation lines
            if current_field and line.strip():
                cleaned_line = line.strip()
                # Remove comment markers
                cleaned_line = re.sub(r"^\*\s*", "", cleaned_line)
                cleaned_line = re.sub(r"^#\s*", "", cleaned_line)
                # Skip docstring delimiters
                if (
                    cleaned_line
                    and not cleaned_line.startswith('"""')
                    and not cleaned_line.startswith("*/")
                    and not (match and ":" in line and not is_continuation)
                ):
                    current_value.append(cleaned_line)

        # Save last field
        if current_field:
            fields[current_field.lower()] = " ".join(current_value).strip()

        return fields

    def _validate_field_content(self, fields: dict[str, str]) -> list[dict[str, str]]:
        """Validate the quality of field content."""
        issues = []

        # Check Purpose field
        if "purpose" in fields:
            purpose = fields["purpose"]
            if len(purpose.split()) < 3:
                issues.append(
                    {
                        "message": "Purpose field too brief",
                        "description": "Purpose should be a clear, descriptive sentence",
                        "suggestion": "Expand Purpose to clearly describe what this file does (1-2 sentences)",
                    }
                )
            if purpose.lower().startswith("todo") or purpose.lower() == "tbd":
                issues.append(
                    {
                        "message": "Purpose field contains placeholder text",
                        "description": "Purpose must be properly documented, not a placeholder",
                        "suggestion": "Replace placeholder with actual purpose description",
                    }
                )

        # Check Scope field
        if "scope" in fields:
            scope = fields["scope"]
            if len(scope.split()) < 3:
                issues.append(
                    {
                        "message": "Scope field too brief",
                        "description": "Scope should describe what areas/components this file covers",
                        "suggestion": "Expand Scope to describe what this file handles or affects",
                    }
                )

        return issues

    def _get_header_template(self, file_ext: str) -> str:
        """Get header template for file type."""
        templates = {
            ".py": '''Add this header at the beginning of the file:
"""
Purpose: Brief description of module functionality (1-2 lines)
Scope: What this module handles (e.g., API endpoints, data models, etc.)
Overview: Comprehensive summary of what this module does and its role in the system.
Dependencies: Key external dependencies or internal modules required
Exports: Main classes, functions, or constants this module provides
Interfaces: Key APIs, endpoints, or methods this module exposes
Implementation: Notable algorithms, patterns, or architectural decisions
"""''',
            ".ts": """Add this header at the beginning of the file:
/**
 * Purpose: Brief description of component/module functionality (1-2 lines)
 * Scope: What this file handles (e.g., React component, API service, etc.)
 * Overview: Comprehensive summary of what this component/module does and its role.
 * Dependencies: Key libraries, components, or services this file depends on
 * Exports: Main components, functions, types, or constants this file provides
 * Props/Interfaces: Key interfaces this component accepts or module provides
 * State/Behavior: Important state management or behavioral patterns used
 */""",
            ".tsx": """Add this header at the beginning of the file:
/**
 * Purpose: Brief description of component functionality (1-2 lines)
 * Scope: What this component handles in the UI
 * Overview: Comprehensive summary of component's role and user interactions.
 * Dependencies: Key libraries, components, or services this file depends on
 * Exports: Main components and types this file provides
 * Props/Interfaces: Component props and their purpose
 * State/Behavior: State management and key behaviors
 */""",
            ".md": """Add this header after the main title:
# Document Title

**Purpose**: Brief description of what this document covers
**Scope**: What areas/components this document applies to

---""",
            ".html": """Add this header after <!DOCTYPE html>:
<!--
Purpose: Brief description of this HTML file's purpose
Scope: What this file is used for
Dependencies: Key libraries or frameworks used
-->""",
            ".yml": """Add this header at the top:
# Purpose: Brief description of configuration purpose
# Scope: What this configuration applies to
# Dependencies: Services or tools that use this configuration""",
            ".yaml": """Add this header at the top:
# Purpose: Brief description of configuration purpose
# Scope: What this configuration applies to
# Dependencies: Services or tools that use this configuration""",
        }

        return templates.get(file_ext, file_ext.join([".js", ".jsx"]))

    def _format_missing_fields(self, fields: set[str]) -> str:
        """Format missing fields for suggestion."""
        formatted = []
        for field in sorted(fields):
            formatted.append(f"{field.capitalize()}: [Add description here]")
        return "\n".join(formatted)
