#!/usr/bin/env python3
"""
Purpose: Core interfaces for the pluggable design linter framework
Scope: Defines contracts for rules, analyzers, reporters, and orchestrators
Overview: This module establishes the foundational interfaces that enable a pluggable
    architecture for the design linter framework, providing the core abstractions that all
    components must implement. It defines the contracts for lint rules (both AST-based and
    file-based), violation reporting with severity levels, analysis contexts with comprehensive
    file information, and output reporters for various formats. The interfaces support dynamic
    rule discovery and registration, allowing new rules to be added without modifying the
    framework core. The design follows SOLID principles with clear separation of concerns,
    dependency injection, and extensibility points. The module also includes ignore directive
    handling for suppressing specific violations, node stack tracking for context-aware analysis,
    and helper functions for creating consistent violation messages across all rules.
Dependencies: abc for abstract base classes, typing for type hints, ast for AST nodes
Exports: LintRule, LintViolation, LintReporter, LintAnalyzer, LintOrchestrator
Interfaces: All classes are abstract interfaces requiring implementation
Implementation: Enables plugin architecture with dynamic rule loading
"""

import ast

# Ignore functionality implementation - moved to top for proper imports
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


def has_file_level_ignore(file_content: str, rule_id: str) -> bool:
    """Check if file has file-level ignore directive for given rule."""
    lines = file_content.split("\n")
    for line in lines[:10]:  # Check only first 10 lines
        if "# design-lint: ignore-file[" in line:
            pattern = _extract_ignore_pattern(line, "ignore-file")
            if pattern and _matches_rule_pattern(rule_id, pattern):
                return True
    return False


def should_ignore_violation(violation: "LintViolation", file_content: str) -> bool:
    """Check if a violation should be ignored based on inline directives."""
    lines = file_content.split("\n")

    # Check line-level ignore on same line
    if violation.line <= len(lines):
        line_content = lines[violation.line - 1]  # lines are 1-indexed
        if "# design-lint: ignore[" in line_content:
            pattern = _extract_ignore_pattern(line_content, "ignore")
            if pattern and _matches_rule_pattern(violation.rule_id, pattern):
                return True

    # Check ignore-next-line directive on previous line
    if violation.line > 1:
        prev_line = lines[violation.line - 2]  # previous line
        if "# design-lint: ignore-next-line" in prev_line:
            return True

    return False


def _extract_ignore_pattern(line: str, directive_type: str) -> str | None:
    """Extract ignore pattern from directive line."""
    if directive_type == "ignore-file":
        match = re.search(r"# design-lint: ignore-file\[([^\]]+)\]", line)
    elif directive_type == "ignore":
        match = re.search(r"# design-lint: ignore\[([^\]]+)\]", line)
    else:
        return None

    return match.group(1) if match else None


def _matches_rule_pattern(rule_id: str, pattern: str) -> bool:
    """Check if rule ID matches ignore pattern."""
    # Handle comma-separated patterns
    patterns = [p.strip() for p in pattern.split(",")]

    for p in patterns:
        if p == rule_id:
            return True

        # Handle wildcard patterns like "literals.*"
        if p.endswith(".*"):
            prefix = p[:-2]
            if rule_id.startswith(prefix + "."):
                return True

    return False


def parse_ignore_directives(file_content: str, context: "LintContext") -> None:
    """Parse ignore directives from file content and populate context."""
    lines = file_content.split("\n")

    for line_num, line in enumerate(lines, 1):
        _process_file_level_ignore(line_num, line, context)
        _process_line_level_ignore(line_num, line, context)
        _process_ignore_next_line(line_num, line, context)


def _process_file_level_ignore(line_num: int, line: str, context: "LintContext") -> None:
    """Process file-level ignore directives."""
    if line_num > 10 or "# design-lint: ignore-file[" not in line:
        return
    pattern = _extract_ignore_pattern(line, "ignore-file")
    if pattern:
        context.file_ignores.append(pattern)


def _process_line_level_ignore(line_num: int, line: str, context: "LintContext") -> None:
    """Process line-level ignore directives."""
    if "# design-lint: ignore[" not in line:
        return
    pattern = _extract_ignore_pattern(line, "ignore")
    if not pattern:
        return
    if line_num not in context.line_ignores:
        context.line_ignores[line_num] = []
    context.line_ignores[line_num].append(pattern)


def _process_ignore_next_line(line_num: int, line: str, context: "LintContext") -> None:
    """Process ignore-next-line directives."""
    if "# design-lint: ignore-next-line" in line:
        context.ignore_next_line.add(line_num + 1)  # Next line


def should_ignore_node(node: ast.AST, file_content: str, rule_id: str) -> bool:
    """Check if an AST node should be ignored for a specific rule."""
    if not hasattr(node, "lineno"):
        return False

    line_num = node.lineno
    lines = file_content.split("\n")

    # Check if line is in ignore_next_line set (previous line had ignore-next-line)
    if line_num in {
        line_num
        for line_num in range(1, len(lines) + 1)
        if line_num > 1 and "# design-lint: ignore-next-line" in lines[line_num - 2]
    }:
        return True

    # Check line-level ignore on same line
    if line_num <= len(lines):
        line_content = lines[line_num - 1]  # lines are 1-indexed
        if "# design-lint: ignore[" in line_content:
            pattern = _extract_ignore_pattern(line_content, "ignore")
            if pattern and _matches_rule_pattern(rule_id, pattern):
                return True

    return False


class Severity(Enum):
    """Enumeration of violation severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class LintViolation:  # pylint: disable=too-many-instance-attributes
    """Represents a detected linting violation."""

    rule_id: str
    file_path: str
    line: int
    column: int
    severity: Severity
    message: str
    description: str
    suggestion: str | None = None
    context: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert violation to dictionary format."""
        return {
            "rule_id": self.rule_id,
            "file": self.file_path,
            "line": self.line,
            "column": self.column,
            "severity": self.severity.value,
            "message": self.message,
            "description": self.description,
            "suggestion": self.suggestion,
            "context": self.context or {},
        }


class LintRule(ABC):
    """Abstract base class for all linting rules."""

    @property
    @abstractmethod
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        raise NotImplementedError("Subclasses must implement rule_id")

    @property
    @abstractmethod
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        raise NotImplementedError("Subclasses must implement rule_name")

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what this rule checks."""
        raise NotImplementedError("Subclasses must implement description")

    @property
    @abstractmethod
    def severity(self) -> Severity:
        """Default severity level for violations of this rule."""
        raise NotImplementedError("Subclasses must implement severity")

    @property
    def categories(self) -> set[str]:
        """Categories this rule belongs to (e.g., 'solid', 'style', 'complexity')."""
        return set()

    @abstractmethod
    def check(self, context: "LintContext") -> list[LintViolation]:
        """Check for violations in the given context."""
        raise NotImplementedError("Subclasses must implement check")

    def is_enabled(self, config: dict[str, Any] | None) -> bool:
        """Check if this rule is enabled in the given configuration."""
        if config is None:
            return True
        rules_config = config.get("rules", {})
        rule_config = rules_config.get(self.rule_id, {})

        # Check if there's a default rule enabled setting (used when specific rules are requested)
        default_enabled = config.get("default_rule_enabled", True)
        return bool(rule_config.get("enabled", default_enabled))

    def get_configuration(self, config: dict[str, Any] | None) -> dict[str, Any]:
        """Get configuration for this rule."""
        if config is None:
            return {}
        rules_config = config.get("rules", {})
        rule_config = rules_config.get(self.rule_id, {})
        return dict(rule_config.get("config", {}))

    def create_violation(
        self,
        context: "LintContext",
        node: ast.AST,
        message: str,
        description: str,
        *,
        suggestion: str | None = None,
        violation_context: dict[str, Any] | None = None,
    ) -> LintViolation:
        """Helper method to create a violation with consistent structure."""
        return LintViolation(
            rule_id=self.rule_id,
            file_path=str(context.file_path),
            line=getattr(node, "lineno", 1),
            column=getattr(node, "col_offset", 0),
            severity=self.severity,
            message=message,
            description=description,
            suggestion=suggestion,
            context=violation_context,
        )


class _ASTRuleNodeVisitor(ast.NodeVisitor):
    """Helper visitor class to reduce nesting in ASTLintRule.check()."""

    def __init__(self, rule: "ASTLintRule", context: "LintContext") -> None:
        """Initialize visitor with rule and context."""
        self.rule = rule
        self.context = context
        self.violations: list[LintViolation] = []

    def visit(self, node: ast.AST) -> None:
        """Visit node and execute rule checks."""
        if self.context.node_stack is None:
            raise RuntimeError("Node stack should be initialized")
        self.context.node_stack.append(node)

        # Track current context
        old_function = self.context.current_function
        old_class = self.context.current_class

        update_context_for_node(self.context, node)

        try:
            self._check_node_if_applicable(node)
            self.generic_visit(node)
        finally:
            self._restore_context_and_stack(node, old_function, old_class)

    def _check_node_if_applicable(self, node: ast.AST) -> None:
        """Check node if rule conditions are met."""
        if not self.rule.should_check_node(node, self.context):
            return
        if not self.context.file_content:
            return
        if should_ignore_node(node, self.context.file_content, self.rule.rule_id):
            return
        self.violations.extend(self.rule.check_node(node, self.context))

    def _restore_context_and_stack(self, node: ast.AST, old_function: str | None, old_class: str | None) -> None:
        """Restore context stack and function/class tracking."""
        if self.context.node_stack is None:
            raise RuntimeError("Node stack should be initialized")
        self.context.node_stack.pop()
        # Only restore if we changed them
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            self.context.current_function = old_function
        elif isinstance(node, ast.ClassDef):
            self.context.current_class = old_class


class ASTLintRule(LintRule):
    """Base class for rules that analyze AST nodes."""

    @abstractmethod
    def check_node(self, node: ast.AST, context: "LintContext") -> list[LintViolation]:
        """Check a specific AST node for violations."""
        raise NotImplementedError("Subclasses must implement check_node")

    def check(self, context: "LintContext") -> list[LintViolation]:
        """Default implementation that traverses AST and checks each node."""
        violations: list[LintViolation] = []

        # Check for file-level ignore directives
        if context.file_content and has_file_level_ignore(context.file_content, self.rule_id):
            return violations

        if not context.ast_tree:
            return violations

        # Initialize node stack if not already set
        if context.node_stack is None:
            context.node_stack = []

        # Use a visitor to maintain node stack
        visitor = _ASTRuleNodeVisitor(self, context)
        visitor.visit(context.ast_tree)
        return visitor.violations

    def should_check_node(self, node: ast.AST, context: "LintContext") -> bool:  # pylint: disable=unused-argument
        """Determine if this node should be checked by this rule."""
        return True


class FileBasedLintRule(LintRule):
    """Base class for rules that analyze entire files."""

    @abstractmethod
    def check_file(self, file_path: Path, content: str, context: "LintContext") -> list[LintViolation]:
        """Check an entire file for violations."""
        raise NotImplementedError("Subclasses must implement check_file")

    def check(self, context: "LintContext") -> list[LintViolation]:
        """Default implementation that checks entire file."""
        violations: list[LintViolation] = []

        # Check for file-level ignore directives
        if context.file_content and has_file_level_ignore(context.file_content, self.rule_id):
            return violations

        if context.file_path and context.file_content:
            violations = self.check_file(context.file_path, context.file_content, context)
            # Filter out violations on ignored lines
            if context.file_content:
                violations = [v for v in violations if not should_ignore_violation(v, context.file_content)]

        return violations


@dataclass
class LintContext:  # pylint: disable=too-many-instance-attributes
    """Context information for rule checking."""

    file_path: Path | None = None
    file_content: str | None = None
    ast_tree: ast.AST | None = None
    current_function: str | None = None
    current_class: str | None = None
    current_module: str | None = None
    node_stack: list[ast.AST] | None = None
    metadata: dict[str, Any] | None = None
    file_ignores: list[str] = field(default_factory=list)  # File-level ignore patterns
    line_ignores: dict[int, list[str]] = field(default_factory=dict)  # Line number -> ignore patterns
    ignore_next_line: set[int] = field(default_factory=set)  # Line numbers to ignore next line

    def get_parent_node(self, offset: int = 1) -> ast.AST | None:
        """Get parent node at specified offset in the stack."""
        if self.node_stack and len(self.node_stack) > offset:
            return self.node_stack[-(offset + 1)]
        return None

    def get_context_description(self) -> str:
        """Get human-readable context description."""
        parts = []
        if self.current_module:
            parts.append(f"module {self.current_module}")
        if self.current_class:
            parts.append(f"class {self.current_class}")
        if self.current_function:
            parts.append(f"function {self.current_function}")

        return " -> ".join(parts) if parts else "global scope"


def update_context_for_node(context: "LintContext", node: ast.AST) -> None:
    """Update context based on current node type."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        context.current_function = node.name
    elif isinstance(node, ast.ClassDef):
        context.current_class = node.name


class LintReporter(ABC):
    """Abstract base class for violation reporters."""

    @abstractmethod
    def generate_report(self, violations: list[LintViolation], metadata: dict[str, Any] | None = None) -> str:
        """Generate a report from the list of violations."""
        raise NotImplementedError("Subclasses must implement generate_report")

    @abstractmethod
    def get_supported_formats(self) -> list[str]:
        """Get list of output formats this reporter supports."""
        raise NotImplementedError("Subclasses must implement get_supported_formats")

    def filter_violations(self, violations: list[LintViolation], filters: dict[str, Any]) -> list[LintViolation]:
        """Filter violations based on criteria."""
        filtered = violations

        filtered = self._filter_by_severity(filtered, filters)
        filtered = self._filter_by_rules(filtered, filters)
        filtered = self._filter_by_files(filtered, filters)

        return filtered

    def _filter_by_severity(self, violations: list[LintViolation], filters: dict[str, Any]) -> list[LintViolation]:
        """Filter violations by minimum severity level."""
        if "min_severity" not in filters:
            return violations

        min_sev = filters["min_severity"]
        severity_order = [Severity.INFO, Severity.WARNING, Severity.ERROR]
        min_index = severity_order.index(min_sev)
        return [v for v in violations if severity_order.index(v.severity) >= min_index]

    def _filter_by_rules(self, violations: list[LintViolation], filters: dict[str, Any]) -> list[LintViolation]:
        """Filter violations by rule IDs."""
        if "rules" not in filters:
            return violations

        rule_ids = set(filters["rules"])
        return [v for v in violations if v.rule_id in rule_ids]

    def _filter_by_files(self, violations: list[LintViolation], filters: dict[str, Any]) -> list[LintViolation]:
        """Filter violations by file patterns."""
        if "files" not in filters:
            return violations

        patterns = filters["files"]
        return [v for v in violations if any(pattern in str(v.file_path) for pattern in patterns)]


class LintAnalyzer(ABC):
    """Abstract base class for code analyzers."""

    @abstractmethod
    def analyze_file(self, file_path: Path) -> LintContext:
        """Analyze a single file and return context."""
        raise NotImplementedError("Subclasses must implement analyze_file")

    @abstractmethod
    def get_supported_extensions(self) -> set[str]:
        """Get file extensions this analyzer supports."""
        raise NotImplementedError("Subclasses must implement get_supported_extensions")


class RuleRegistry(ABC):
    """Abstract interface for rule management."""

    @abstractmethod
    def register_rule(self, rule: LintRule) -> None:
        """Register a new rule."""
        raise NotImplementedError("Subclasses must implement register_rule")

    @abstractmethod
    def unregister_rule(self, rule_id: str) -> None:
        """Unregister a rule by ID."""
        raise NotImplementedError("Subclasses must implement unregister_rule")

    @abstractmethod
    def get_rule(self, rule_id: str) -> LintRule | None:
        """Get a rule by ID."""
        raise NotImplementedError("Subclasses must implement get_rule")

    @abstractmethod
    def get_all_rules(self) -> list[LintRule]:
        """Get all registered rules."""
        raise NotImplementedError("Subclasses must implement get_all_rules")

    @abstractmethod
    def get_rules_by_category(self, category: str) -> list[LintRule]:
        """Get rules belonging to a specific category."""
        raise NotImplementedError("Subclasses must implement get_rules_by_category")

    @abstractmethod
    def discover_rules(self, package_paths: list[str]) -> int:
        """Discover and register rules from package paths."""
        raise NotImplementedError("Subclasses must implement discover_rules")


class LintOrchestrator(ABC):
    """Abstract interface for coordinating the linting process."""

    @abstractmethod
    def lint_file(self, file_path: Path, config: dict[str, Any] | None = None) -> list[LintViolation]:
        """Lint a single file."""
        raise NotImplementedError("Subclasses must implement lint_file")

    @abstractmethod
    def lint_directory(
        self,
        directory_path: Path,
        config: dict[str, Any] | None = None,
        recursive: bool = True,
    ) -> list[LintViolation]:
        """Lint all files in a directory."""
        raise NotImplementedError("Subclasses must implement lint_directory")

    @abstractmethod
    def get_available_rules(self) -> list[str]:
        """Get list of available rule IDs."""
        raise NotImplementedError("Subclasses must implement get_available_rules")

    @abstractmethod
    def generate_report(self, violations: list[LintViolation], output_format: str = "text") -> str:
        """Generate a report in the specified format."""
        raise NotImplementedError("Subclasses must implement generate_report")

    @abstractmethod
    def get_rule_registry(self) -> "RuleRegistry":
        """Get the rule registry."""
        raise NotImplementedError("Subclasses must implement get_rule_registry")


class ConfigurationProvider(ABC):
    """Abstract interface for configuration management."""

    @abstractmethod
    def load_config(self, config_path: Path | None = None) -> dict[str, Any]:
        """Load configuration from file or use defaults."""
        raise NotImplementedError("Subclasses must implement load_config")

    @abstractmethod
    def get_rule_config(self, rule_id: str) -> dict[str, Any]:
        """Get configuration for a specific rule."""
        raise NotImplementedError("Subclasses must implement get_rule_config")

    @abstractmethod
    def is_rule_enabled(self, rule_id: str) -> bool:
        """Check if a rule is enabled."""
        raise NotImplementedError("Subclasses must implement is_rule_enabled")

    @abstractmethod
    def get_output_config(self) -> dict[str, Any]:
        """Get output/reporting configuration."""
        raise NotImplementedError("Subclasses must implement get_output_config")
