#!/usr/bin/env python3
"""
Purpose: Core interfaces for the pluggable design linter framework
Scope: Defines contracts for rules, analyzers, reporters, and orchestrators
Overview: This module establishes the foundational interfaces that enable
    a pluggable architecture for design linters. Rules can be added dynamically,
    reporters can format output in multiple ways, and analyzers can process
    different types of code structures. This follows SOLID principles with
    clear separation of concerns and dependency injection.
Dependencies: abc for abstract base classes, typing for type hints, ast for AST nodes
Exports: LintRule, LintViolation, LintReporter, LintAnalyzer, LintOrchestrator
Interfaces: All classes are abstract interfaces requiring implementation
Implementation: Enables plugin architecture with dynamic rule loading
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Set, Union
import ast
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class Severity(Enum):
    """Enumeration of violation severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class LintViolation:
    """Represents a detected linting violation."""
    rule_id: str
    file_path: str
    line: int
    column: int
    severity: Severity
    message: str
    description: str
    suggestion: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert violation to dictionary format."""
        return {
            'rule_id': self.rule_id,
            'file': self.file_path,
            'line': self.line,
            'column': self.column,
            'severity': self.severity.value,
            'message': self.message,
            'description': self.description,
            'suggestion': self.suggestion,
            'context': self.context or {}
        }


class LintRule(ABC):
    """Abstract base class for all linting rules."""

    @property
    @abstractmethod
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        pass

    @property
    @abstractmethod
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what this rule checks."""
        pass

    @property
    @abstractmethod
    def severity(self) -> Severity:
        """Default severity level for violations of this rule."""
        pass

    @property
    def categories(self) -> Set[str]:
        """Categories this rule belongs to (e.g., 'solid', 'style', 'complexity')."""
        return set()

    @abstractmethod
    def check(self, context: 'LintContext') -> List[LintViolation]:
        """Check for violations in the given context."""
        pass

    def is_enabled(self, config: Dict[str, Any]) -> bool:
        """Check if this rule is enabled in the given configuration."""
        if config is None:
            return True
        return config.get('rules', {}).get(self.rule_id, {}).get('enabled', True)

    def get_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get configuration for this rule."""
        if config is None:
            return {}
        return config.get('rules', {}).get(self.rule_id, {}).get('config', {})


class ASTLintRule(LintRule):
    """Base class for rules that analyze AST nodes."""

    @abstractmethod
    def check_node(self, node: ast.AST, context: 'LintContext') -> List[LintViolation]:
        """Check a specific AST node for violations."""
        pass

    def check(self, context: 'LintContext') -> List[LintViolation]:
        """Default implementation that traverses AST and checks each node."""
        violations = []
        if context.ast_tree:
            # Initialize node stack if not already set
            if context.node_stack is None:
                context.node_stack = []

            # Use a visitor to maintain node stack
            class NodeVisitor(ast.NodeVisitor):
                def __init__(self, rule, ctx):
                    self.rule = rule
                    self.context = ctx
                    self.violations = []

                def visit(self, node):
                    self.context.node_stack.append(node)

                    # Track current context
                    old_function = self.context.current_function
                    old_class = self.context.current_class

                    if isinstance(node, ast.FunctionDef):
                        self.context.current_function = node.name
                    elif isinstance(node, ast.AsyncFunctionDef):
                        self.context.current_function = node.name
                    elif isinstance(node, ast.ClassDef):
                        self.context.current_class = node.name

                    try:
                        if self.rule.should_check_node(node, self.context):
                            self.violations.extend(self.rule.check_node(node, self.context))
                        self.generic_visit(node)
                    finally:
                        self.context.node_stack.pop()
                        # Only restore if we changed them
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            self.context.current_function = old_function
                        elif isinstance(node, ast.ClassDef):
                            self.context.current_class = old_class

            visitor = NodeVisitor(self, context)
            visitor.visit(context.ast_tree)
            violations = visitor.violations
        return violations

    def should_check_node(self, node: ast.AST, context: 'LintContext') -> bool:
        """Determine if this node should be checked by this rule."""
        return True


class FileBasedLintRule(LintRule):
    """Base class for rules that analyze entire files."""

    @abstractmethod
    def check_file(self, file_path: Path, content: str, context: 'LintContext') -> List[LintViolation]:
        """Check an entire file for violations."""
        pass

    def check(self, context: 'LintContext') -> List[LintViolation]:
        """Check the current file."""
        if context.file_path and context.file_content:
            return self.check_file(context.file_path, context.file_content, context)
        return []


@dataclass
class LintContext:
    """Context information for rule checking."""
    file_path: Optional[Path] = None
    file_content: Optional[str] = None
    ast_tree: Optional[ast.AST] = None
    current_function: Optional[str] = None
    current_class: Optional[str] = None
    current_module: Optional[str] = None
    node_stack: Optional[List[ast.AST]] = None
    metadata: Optional[Dict[str, Any]] = None

    def get_parent_node(self, offset: int = 1) -> Optional[ast.AST]:
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


class LintReporter(ABC):
    """Abstract base class for violation reporters."""

    @abstractmethod
    def generate_report(self, violations: List[LintViolation],
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """Generate a report from the list of violations."""
        pass

    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Get list of output formats this reporter supports."""
        pass

    def filter_violations(self, violations: List[LintViolation],
                         filters: Dict[str, Any]) -> List[LintViolation]:
        """Filter violations based on criteria."""
        filtered = violations

        # Filter by severity
        if 'min_severity' in filters:
            min_sev = filters['min_severity']
            severity_order = [Severity.INFO, Severity.WARNING, Severity.ERROR]
            min_index = severity_order.index(min_sev)
            filtered = [v for v in filtered if severity_order.index(v.severity) >= min_index]

        # Filter by rule IDs
        if 'rules' in filters:
            rule_ids = set(filters['rules'])
            filtered = [v for v in filtered if v.rule_id in rule_ids]

        # Filter by file patterns
        if 'files' in filters:
            patterns = filters['files']
            filtered = [v for v in filtered
                       if any(pattern in str(v.file_path) for pattern in patterns)]

        return filtered


class LintAnalyzer(ABC):
    """Abstract base class for code analyzers."""

    @abstractmethod
    def analyze_file(self, file_path: Path) -> LintContext:
        """Analyze a single file and return context."""
        pass

    @abstractmethod
    def get_supported_extensions(self) -> Set[str]:
        """Get file extensions this analyzer supports."""
        pass


class RuleRegistry(ABC):
    """Abstract interface for rule management."""

    @abstractmethod
    def register_rule(self, rule: LintRule) -> None:
        """Register a new rule."""
        pass

    @abstractmethod
    def unregister_rule(self, rule_id: str) -> None:
        """Unregister a rule by ID."""
        pass

    @abstractmethod
    def get_rule(self, rule_id: str) -> Optional[LintRule]:
        """Get a rule by ID."""
        pass

    @abstractmethod
    def get_all_rules(self) -> List[LintRule]:
        """Get all registered rules."""
        pass

    @abstractmethod
    def get_rules_by_category(self, category: str) -> List[LintRule]:
        """Get rules belonging to a specific category."""
        pass

    @abstractmethod
    def discover_rules(self, package_paths: List[str]) -> int:
        """Discover and register rules from package paths."""
        pass


class LintOrchestrator(ABC):
    """Abstract interface for coordinating the linting process."""

    @abstractmethod
    def lint_file(self, file_path: Path, config: Optional[Dict[str, Any]] = None) -> List[LintViolation]:
        """Lint a single file."""
        pass

    @abstractmethod
    def lint_directory(self, directory_path: Path,
                      config: Optional[Dict[str, Any]] = None,
                      recursive: bool = True) -> List[LintViolation]:
        """Lint all files in a directory."""
        pass

    @abstractmethod
    def get_available_rules(self) -> List[str]:
        """Get list of available rule IDs."""
        pass

    @abstractmethod
    def generate_report(self, violations: List[LintViolation],
                       format: str = 'text') -> str:
        """Generate a report in the specified format."""
        pass


class ConfigurationProvider(ABC):
    """Abstract interface for configuration management."""

    @abstractmethod
    def load_config(self, config_path: Optional[Path] = None) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        pass

    @abstractmethod
    def get_rule_config(self, rule_id: str) -> Dict[str, Any]:
        """Get configuration for a specific rule."""
        pass

    @abstractmethod
    def is_rule_enabled(self, rule_id: str) -> bool:
        """Check if a rule is enabled."""
        pass

    @abstractmethod
    def get_output_config(self) -> Dict[str, Any]:
        """Get output/reporting configuration."""
        pass
