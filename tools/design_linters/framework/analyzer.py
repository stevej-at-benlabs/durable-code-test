#!/usr/bin/env python3
"""
Purpose: Core analyzer and orchestrator for the pluggable linter framework
Scope: Coordinates rule execution, context management, and result aggregation
Overview: This module implements the main orchestration logic for the pluggable
    linter framework. It manages AST analysis, context tracking, rule execution,
    and result aggregation. The analyzer follows the Single Responsibility
    Principle and uses dependency injection for extensibility.
Dependencies: ast for Python AST parsing, pathlib for file operations
Exports: PythonAnalyzer, LintOrchestrator, DefaultLintOrchestrator
Interfaces: Implements LintAnalyzer and LintOrchestrator interfaces
Implementation: Visitor pattern with plugin architecture coordination
"""

import ast
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field

from .interfaces import (
    LintAnalyzer,
    LintOrchestrator,
    LintRule,
    LintContext,
    LintViolation,
    LintReporter,
    RuleRegistry,
    ConfigurationProvider,
    Severity
)


class PythonAnalyzer(LintAnalyzer):
    """Analyzer for Python source code using AST parsing."""

    def __init__(self):
        """Initialize Python analyzer."""
        self._logger = logging.getLogger(__name__)

    def analyze_file(self, file_path: Path) -> LintContext:
        """Analyze a Python file and return rich context."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Parse AST
            ast_tree = ast.parse(content, filename=str(file_path))

            # Extract module-level information
            context = LintContext(
                file_path=file_path,
                file_content=content,
                ast_tree=ast_tree,
                current_module=self._get_module_name(file_path),
                node_stack=[],
                metadata={'encoding': 'utf-8', 'ast_parsed': True}
            )

            return context

        except SyntaxError as e:
            self._logger.warning(f"Syntax error in {file_path}: {e}")
            return LintContext(
                file_path=file_path,
                file_content=content if 'content' in locals() else None,
                metadata={'syntax_error': str(e), 'ast_parsed': False}
            )
        except Exception as e:
            self._logger.error(f"Error analyzing {file_path}: {e}")
            return LintContext(
                file_path=file_path,
                metadata={'error': str(e), 'ast_parsed': False}
            )

    def get_supported_extensions(self) -> Set[str]:
        """Get file extensions this analyzer supports."""
        return {'.py', '.pyi'}

    def _get_module_name(self, file_path: Path) -> str:
        """Extract module name from file path."""
        return file_path.stem


class ContextualASTVisitor(ast.NodeVisitor):
    """AST visitor that maintains context and executes rules."""

    def __init__(self, context: LintContext, rules: List[LintRule], config: Dict[str, Any]):
        """Initialize visitor with context and rules."""
        self.context = context
        self.rules = rules
        self.config = config
        self.violations: List[LintViolation] = []

        # Initialize context tracking
        if self.context.node_stack is None:
            self.context.node_stack = []

    def visit(self, node: ast.AST):
        """Visit node and execute applicable rules."""
        # Push node to context stack
        self.context.node_stack.append(node)

        # Update context based on node type
        self._update_context_for_node(node)

        # Execute AST-based rules
        self._execute_rules_for_node(node)

        # Continue visiting child nodes
        self.generic_visit(node)

        # Pop node from context stack
        self.context.node_stack.pop()

        # Restore previous context
        self._restore_context_for_node(node)

    def _update_context_for_node(self, node: ast.AST):
        """Update context based on current node type."""
        if isinstance(node, ast.FunctionDef):
            self.context.current_function = node.name
        elif isinstance(node, ast.AsyncFunctionDef):
            self.context.current_function = node.name
        elif isinstance(node, ast.ClassDef):
            self.context.current_class = node.name

    def _restore_context_for_node(self, node: ast.AST):
        """Restore context when leaving a node."""
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Find previous function in stack
            self.context.current_function = None
            for stack_node in reversed(self.context.node_stack[:-1]):
                if isinstance(stack_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    self.context.current_function = stack_node.name
                    break

        elif isinstance(node, ast.ClassDef):
            # Find previous class in stack
            self.context.current_class = None
            for stack_node in reversed(self.context.node_stack[:-1]):
                if isinstance(stack_node, ast.ClassDef):
                    self.context.current_class = stack_node.name
                    break

    def _execute_rules_for_node(self, node: ast.AST):
        """Execute all applicable rules for the current node."""
        from .interfaces import ASTLintRule

        for rule in self.rules:
            if not rule.is_enabled(self.config):
                continue

            if isinstance(rule, ASTLintRule):
                if rule.should_check_node(node, self.context):
                    try:
                        violations = rule.check_node(node, self.context)
                        self.violations.extend(violations)
                    except Exception as e:
                        logging.getLogger(__name__).warning(
                            f"Error executing rule {rule.rule_id} on {type(node).__name__}: {e}")


@dataclass
class LintResults:
    """Container for linting results and metadata."""
    violations: List[LintViolation] = field(default_factory=list)
    files_analyzed: int = 0
    files_with_violations: int = 0
    rules_executed: int = 0
    analysis_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        by_severity = {}
        by_rule = {}

        for violation in self.violations:
            # Count by severity
            sev_key = violation.severity.value
            by_severity[sev_key] = by_severity.get(sev_key, 0) + 1

            # Count by rule
            by_rule[violation.rule_id] = by_rule.get(violation.rule_id, 0) + 1

        return {
            'total_violations': len(self.violations),
            'files_analyzed': self.files_analyzed,
            'files_with_violations': self.files_with_violations,
            'rules_executed': self.rules_executed,
            'analysis_time_ms': self.analysis_time_ms,
            'by_severity': by_severity,
            'by_rule': by_rule,
        }


class DefaultLintOrchestrator(LintOrchestrator):
    """Default implementation of the linting orchestrator."""

    def __init__(self,
                 rule_registry: RuleRegistry,
                 analyzers: Optional[Dict[str, LintAnalyzer]] = None,
                 reporters: Optional[Dict[str, LintReporter]] = None,
                 config_provider: Optional[ConfigurationProvider] = None):
        """Initialize orchestrator with dependencies."""
        self.rule_registry = rule_registry
        self.analyzers = analyzers or {'python': PythonAnalyzer()}
        self.reporters = reporters or {}
        self.config_provider = config_provider
        self._logger = logging.getLogger(__name__)

    def lint_file(self, file_path: Path, config: Optional[Dict[str, Any]] = None) -> List[LintViolation]:
        """Lint a single file."""
        config = config or self._get_default_config()

        # Determine analyzer based on file extension
        analyzer = self._get_analyzer_for_file(file_path)
        if not analyzer:
            self._logger.warning(f"No analyzer available for {file_path}")
            return []

        # Analyze file to get context
        context = analyzer.analyze_file(file_path)
        if not context.ast_tree and context.metadata.get('ast_parsed', True):
            # Skip files that couldn't be parsed
            return []

        # Get enabled rules
        enabled_rules = self._get_enabled_rules(config)

        # Execute file-based rules
        violations = []
        violations.extend(self._execute_file_based_rules(enabled_rules, context, config))

        # Execute AST-based rules if we have an AST
        if context.ast_tree:
            violations.extend(self._execute_ast_based_rules(enabled_rules, context, config))

        return violations

    def lint_directory(self, directory_path: Path,
                      config: Optional[Dict[str, Any]] = None,
                      recursive: bool = True) -> List[LintViolation]:
        """Lint all supported files in a directory."""
        config = config or self._get_default_config()
        all_violations = []

        # Get file patterns to include/exclude
        include_patterns = config.get('include', ['**/*.py'])
        exclude_patterns = config.get('exclude', ['__pycache__/**', '.git/**', '.venv/**'])

        # Find files to analyze
        files_to_analyze = self._find_files_to_analyze(
            directory_path, include_patterns, exclude_patterns, recursive)

        for file_path in files_to_analyze:
            try:
                violations = self.lint_file(file_path, config)
                all_violations.extend(violations)
            except Exception as e:
                self._logger.error(f"Error linting {file_path}: {e}")

        return all_violations

    def get_available_rules(self) -> List[str]:
        """Get list of available rule IDs."""
        return [rule.rule_id for rule in self.rule_registry.get_all_rules()]

    def generate_report(self, violations: List[LintViolation], format: str = 'text') -> str:
        """Generate a report in the specified format."""
        if format not in self.reporters:
            from .reporters import ReporterFactory
            reporter = ReporterFactory.create_reporter(format)
        else:
            reporter = self.reporters[format]

        metadata = {
            'timestamp': str(__import__('datetime').datetime.now()),
            'total_violations': len(violations),
            'files_with_violations': len(set(v.file_path for v in violations))
        }

        return reporter.generate_report(violations, metadata)

    def _get_analyzer_for_file(self, file_path: Path) -> Optional[LintAnalyzer]:
        """Get appropriate analyzer for file based on extension."""
        extension = file_path.suffix.lower()

        for analyzer_name, analyzer in self.analyzers.items():
            if extension in analyzer.get_supported_extensions():
                return analyzer

        return None

    def _get_enabled_rules(self, config: Dict[str, Any]) -> List[LintRule]:
        """Get list of enabled rules based on configuration."""
        all_rules = self.rule_registry.get_all_rules()
        return [rule for rule in all_rules if rule.is_enabled(config)]

    def _execute_file_based_rules(self, rules: List[LintRule], context: LintContext,
                                 config: Dict[str, Any]) -> List[LintViolation]:
        """Execute file-based rules."""
        from .interfaces import FileBasedLintRule
        violations = []

        for rule in rules:
            if isinstance(rule, FileBasedLintRule):
                try:
                    rule_violations = rule.check(context)
                    violations.extend(rule_violations)
                except Exception as e:
                    self._logger.warning(f"Error executing file rule {rule.rule_id}: {e}")

        return violations

    def _execute_ast_based_rules(self, rules: List[LintRule], context: LintContext,
                                config: Dict[str, Any]) -> List[LintViolation]:
        """Execute AST-based rules using visitor pattern."""
        from .interfaces import ASTLintRule
        ast_rules = [rule for rule in rules if isinstance(rule, ASTLintRule)]

        if not ast_rules or not context.ast_tree:
            return []

        visitor = ContextualASTVisitor(context, ast_rules, config)
        visitor.visit(context.ast_tree)
        return visitor.violations

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        if self.config_provider:
            return self.config_provider.load_config()

        return {
            'rules': {},  # All rules enabled by default
            'include': ['**/*.py'],
            'exclude': ['__pycache__/**', '.git/**', '.venv/**', '**/.pytest_cache/**']
        }

    def _find_files_to_analyze(self, directory: Path, include_patterns: List[str],
                              exclude_patterns: List[str], recursive: bool) -> List[Path]:
        """Find files to analyze based on patterns."""
        import fnmatch

        files = []
        pattern = '**/*' if recursive else '*'

        for path in directory.glob(pattern):
            if not path.is_file():
                continue

            # Check if file matches include patterns
            relative_path = path.relative_to(directory)
            included = any(fnmatch.fnmatch(str(relative_path), pattern)
                          for pattern in include_patterns)

            if not included:
                continue

            # Check if file matches exclude patterns
            excluded = any(fnmatch.fnmatch(str(relative_path), pattern)
                          for pattern in exclude_patterns)

            if excluded:
                continue

            files.append(path)

        return files
