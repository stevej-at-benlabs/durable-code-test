#!/usr/bin/env python3
"""
Purpose: Detects Single Responsibility Principle violations in Python code
Scope: Python classes and modules across backend and tools directories
Overview: This analyzer detects potential SRP violations using multiple heuristics
    including
    method count and complexity analysis, method name clustering to identify
    unrelated
    responsibilities, dependency analysis to find excessive coupling, and cohesion
    metrics
    to measure class unity. It helps identify classes that are doing too much and
    suggests
    refactoring opportunities to improve code maintainability and adherence to
    SOLID principles.
Dependencies: ast for Python AST parsing, collections for data structures,
    pathlib for file operations
Exports: SRPAnalyzer class, SRPViolation dataclass, CohesionCalculator class
Interfaces: main() CLI function, analyze_file() returns List[SRPViolation]
Implementation: Uses AST analysis to calculate complexity metrics and semantic
    clustering algorithms
"""

import ast
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, cast
import argparse
import json
from abc import ABC, abstractmethod
from dataclasses import replace

try:
    from . import (
    DEFAULT_SRP_THRESHOLDS,
    RESPONSIBILITY_PREFIXES,
    EXCLUDE_PATTERNS,
    Severity,
    SRPThresholds
)
    from .constants import analyze_with_visitor
except ImportError:
    # For direct script execution
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from __init__ import (  # type: ignore[import-not-found,no-redef]
        DEFAULT_SRP_THRESHOLDS,
        RESPONSIBILITY_PREFIXES,
        EXCLUDE_PATTERNS,
        Severity,
        SRPThresholds
    )
    from constants import (  # type: ignore[import-not-found,no-redef]
        analyze_with_visitor
    )


class ClassAnalyzer(ABC):
    """Abstract interface for class analysis techniques - follows OCP."""

    @abstractmethod
    def analyze(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Analyze a class and return metrics."""

    @abstractmethod
    def get_metric_names(self) -> List[str]:
        """Get the names of metrics this analyzer provides."""


class DefaultClassAnalyzer(ClassAnalyzer):
    """Default implementation of class analysis."""

    def __init__(self, responsibility_prefixes: Dict[str, List[str]]) -> None:
        self.responsibility_prefixes = responsibility_prefixes

    def analyze(self, node: ast.ClassDef) -> Dict[str, Any]:
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        instance_vars = self._extract_instance_variables(node)
        dependencies = self._extract_dependencies(node)
        responsibility_groups = self._group_methods_by_responsibility(methods)

        return {
            'name': node.name,
            'method_count': len(methods),
            'line_count': node.end_lineno - node.lineno if node.end_lineno else 0,
            'instance_var_count': len(instance_vars),
            'dependency_count': len(dependencies),
            'responsibility_groups': responsibility_groups,
            'responsibility_group_count': len(responsibility_groups),
            'methods': [m.name for m in methods],
            'cohesion_score': self._calculate_cohesion(methods, instance_vars)
        }

    def get_metric_names(self) -> List[str]:
        return ['name', 'method_count', 'line_count', 'instance_var_count',
                'dependency_count', 'responsibility_groups',
                'responsibility_group_count', 'methods', 'cohesion_score']

    def _extract_instance_variables(self, node: ast.ClassDef) -> Set[str]:
        """Extract instance variables from a class."""
        instance_vars = set()
        for item in ast.walk(node):
            if isinstance(item, ast.Attribute):
                if isinstance(item.value, ast.Name) and item.value.id == 'self':
                    instance_vars.add(item.attr)
        return instance_vars

    def _extract_dependencies(self, node: ast.ClassDef) -> Set[str]:
        """Extract external dependencies from a class."""
        dependencies: Set[str] = set()
        for item in ast.walk(node):
            self._process_import_node(item, dependencies)
        return dependencies

    def _process_import_node(self, item: ast.AST, dependencies: Set[str]) -> None:
        """Process an import node and add dependencies."""
        if isinstance(item, ast.Import):
            for alias in item.names:
                dependencies.add(alias.name.split('.')[0])
            return

        if isinstance(item, ast.ImportFrom) and item.module:
            dependencies.add(item.module.split('.')[0])

    def _group_methods_by_responsibility(
            self, methods: List[ast.FunctionDef]) -> Dict[str, List[str]]:
        """Group methods by their likely responsibility based on naming."""
        groups = defaultdict(list)

        for method in methods:
            if method.name.startswith('_'):
                continue  # Skip private methods

            category = self._find_method_category(method.name)
            groups[category].append(method.name)

        return dict(groups)

    def _find_method_category(self, method_name: str) -> str:
        """Find the category for a method based on its name."""
        for category, prefixes in self.responsibility_prefixes.items():
            for prefix in prefixes:
                if method_name.lower().startswith(prefix):
                    return category
        return 'other'

    def _calculate_cohesion(self, methods: List[ast.FunctionDef],
                            instance_vars: Set[str]) -> float:
        """Calculate cohesion score (0-1)."""
        if not methods or not instance_vars:
            return 1.0

        method_var_usage = self._extract_method_variable_usage(methods,
                                                               instance_vars)
        return self._compute_cohesion_score(method_var_usage)

    def _extract_method_variable_usage(self, methods: List[ast.FunctionDef],
                                        instance_vars: Set[str]) -> Dict[str, Set[str]]:
        """Extract which instance variables each method uses."""
        method_var_usage = {}
        for method in methods:
            used_vars = self._find_used_instance_vars(method, instance_vars)
            method_var_usage[method.name] = used_vars
        return method_var_usage

    def _find_used_instance_vars(self, method: ast.FunctionDef,
                                  instance_vars: Set[str]) -> Set[str]:
        """Find instance variables used by a method."""
        used_vars = set()
        for node in ast.walk(method):
            if self._is_self_attribute_access(node, instance_vars):
                # We know this is an Attribute node due to the check above
                used_vars.add(node.attr)  # type: ignore[attr-defined]
        return used_vars

    def _is_self_attribute_access(self, node: ast.AST, instance_vars: Set[str]) -> bool:
        """Check if node is a self.attribute access to an instance variable."""
        return (isinstance(node, ast.Attribute) and
                isinstance(node.value, ast.Name) and
                node.value.id == 'self' and
                node.attr in instance_vars)

    def _compute_cohesion_score(self, method_var_usage: Dict[str, Set[str]]) -> float:
        """Compute cohesion score based on shared variable usage between methods."""
        total_pairs = 0
        shared_pairs = 0

        method_names = list(method_var_usage.keys())
        for i, method_i in enumerate(method_names):
            for method_j in method_names[i + 1:]:
                total_pairs += 1
                if method_var_usage[method_i] & method_var_usage[method_j]:
                    shared_pairs += 1

        return 1.0 if total_pairs == 0 else shared_pairs / total_pairs


class SRPViolation:
    """Represents a potential SRP violation."""

    def __init__(self, file_path: str, class_name: str, line: int,
                 *, severity: str, reasons: List[str]):
        self.file_path = file_path
        self.class_name = class_name
        self.line = line
        self.severity = severity  # 'error', 'warning', 'info'
        self.reasons = reasons

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON output."""
        return {
            'file': self.file_path,
            'class': self.class_name,
            'line': self.line,
            'severity': self.severity,
            'reasons': self.reasons
        }


class SRPAnalyzer(ast.NodeVisitor):
    """Analyzes Python code for SRP violations."""

    def __init__(self, file_path: str, thresholds: Optional[SRPThresholds] = None,
                 analyzers: Optional[List[ClassAnalyzer]] = None):
        self.file_path = file_path
        self.violations: List[SRPViolation] = []
        self.current_class: Optional[str] = None
        self.class_metrics: Dict[str, Any] = {}
        self.thresholds = thresholds or DEFAULT_SRP_THRESHOLDS
        self.analyzers = analyzers or self._get_default_analyzers()

    def _get_default_analyzers(self) -> List[ClassAnalyzer]:
        """Get the default set of analyzers."""
        return [DefaultClassAnalyzer(RESPONSIBILITY_PREFIXES)]

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Analyze a class definition for SRP violations."""
        self.current_class = node.name
        metrics = self._analyze_class(node)

        violations = self._check_srp_violations(metrics)
        if violations:
            severity = self._determine_severity(metrics)
            violation = SRPViolation(
                self.file_path,
                node.name,
                node.lineno,
                severity=severity,
                reasons=violations
            )
            self.violations.append(violation)

        self.generic_visit(node)
        self.current_class = None

    def _analyze_class(self, node: ast.ClassDef) -> Dict:
        """Extract metrics from a class using pluggable analyzers."""
        metrics = {}

        # Run all analyzers and combine their results
        for analyzer in self.analyzers:
            analyzer_metrics = analyzer.analyze(node)
            metrics.update(analyzer_metrics)

        return metrics

    def _extract_instance_variables(self, node: ast.ClassDef) -> Set[str]:
        """Extract instance variables from a class."""
        instance_vars = set()
        for item in ast.walk(node):
            if isinstance(item, ast.Attribute):
                if isinstance(item.value, ast.Name) and item.value.id == 'self':
                    instance_vars.add(item.attr)
        return instance_vars

    def _extract_dependencies(self, node: ast.ClassDef) -> Set[str]:
        """Extract external dependencies from a class."""
        dependencies: Set[str] = set()
        for item in ast.walk(node):
            self._process_import_item(item, dependencies)
        return dependencies

    def _process_import_item(self, item: ast.AST, dependencies: Set[str]) -> None:
        """Process an import item and add dependencies."""
        if isinstance(item, ast.Import):
            for alias in item.names:
                dependencies.add(alias.name.split('.')[0])
            return

        if isinstance(item, ast.ImportFrom) and item.module:
            dependencies.add(item.module.split('.')[0])

    def _group_methods_by_responsibility(
            self, methods: List[ast.FunctionDef]) -> Dict[str, List[str]]:
        """Group methods by their likely responsibility based on naming."""
        groups = defaultdict(list)

        for method in methods:
            if method.name.startswith('_'):
                continue  # Skip private methods

            category = self._determine_method_category(method.name)
            groups[category].append(method.name)

        return dict(groups)

    def _determine_method_category(self, method_name: str) -> str:
        """Determine the category for a method based on its name."""
        for category, prefixes in RESPONSIBILITY_PREFIXES.items():
            for prefix in prefixes:
                if method_name.lower().startswith(prefix):
                    return category
        return 'other'

    def _calculate_cohesion(self, methods: List[ast.FunctionDef],
                            instance_vars: Set[str]) -> float:
        """
        Calculate cohesion score (0-1).
        Higher score means better cohesion (methods use similar instance variables).
        """
        if not methods or not instance_vars:
            return 1.0

        method_var_usage = self._build_method_var_usage_map(methods,
                                                           instance_vars)
        return self._calculate_lcom_score(method_var_usage)

    def _build_method_var_usage_map(self, methods: List[ast.FunctionDef],
                                     instance_vars: Set[str]) -> Dict[str, Set[str]]:
        """Build a map of which instance variables each method uses."""
        method_var_usage = {}
        for method in methods:
            used_vars = self._get_method_instance_vars(method, instance_vars)
            method_var_usage[method.name] = used_vars
        return method_var_usage

    def _get_method_instance_vars(self, method: ast.FunctionDef,
                                   instance_vars: Set[str]) -> Set[str]:
        """Get instance variables used by a method."""
        used_vars = set()
        for node in ast.walk(method):
            if self._is_instance_var_access(node, instance_vars):
                # We know this is an Attribute node due to the check above
                used_vars.add(node.attr)  # type: ignore[attr-defined]
        return used_vars

    def _is_instance_var_access(self, node: ast.AST, instance_vars: Set[str]) -> bool:
        """Check if node is an access to an instance variable."""
        return (isinstance(node, ast.Attribute) and
                isinstance(node.value, ast.Name) and
                node.value.id == 'self' and
                node.attr in instance_vars)

    def _calculate_lcom_score(self, method_var_usage: Dict[str, Set[str]]) -> float:
        """Calculate LCOM (Lack of Cohesion of Methods) score."""
        total_pairs = 0
        shared_pairs = 0

        method_names = list(method_var_usage.keys())
        for i, method_i in enumerate(method_names):
            for method_j in method_names[i + 1:]:
                total_pairs += 1
                if method_var_usage[method_i] & method_var_usage[method_j]:
                    shared_pairs += 1

        return 1.0 if total_pairs == 0 else shared_pairs / total_pairs

    def _check_srp_violations(self, metrics: Dict) -> List[str]:
        """Check if metrics indicate SRP violations."""
        violations = []

        violations.extend(self._check_method_violations(metrics))
        violations.extend(self._check_structure_violations(metrics))
        violations.extend(self._check_cohesion_violations(metrics))
        violations.extend(self._check_naming_violations(metrics))

        return violations

    def _check_method_violations(self, metrics: Dict) -> List[str]:
        """Check for method-related SRP violations."""
        violations = []

        if metrics['method_count'] > self.thresholds.limits.MAX_METHODS_PER_CLASS:
            violations.append(
                f"Too many methods ({metrics['method_count']} > "
                f"{self.thresholds.limits.MAX_METHODS_PER_CLASS})")

        if (metrics['responsibility_group_count'] >
                self.thresholds.limits.MAX_METHOD_GROUPS):
            groups = ', '.join(metrics['responsibility_groups'].keys())
            violations.append(
                f"Multiple responsibility groups detected: {groups}")

        return violations

    def _check_structure_violations(self, metrics: Dict) -> List[str]:
        """Check for structural SRP violations."""
        violations = []

        if metrics['line_count'] > self.thresholds.limits.MAX_CLASS_LINES:
            violations.append(
                f"Class too large ({metrics['line_count']} lines > "
                f"{self.thresholds.limits.MAX_CLASS_LINES})")

        if (metrics['instance_var_count'] >
                self.thresholds.limits.MAX_INSTANCE_VARIABLES):
            violations.append(
                f"Too many instance variables ({metrics['instance_var_count']} > "
                f"{self.thresholds.limits.MAX_INSTANCE_VARIABLES})")

        if metrics['dependency_count'] > self.thresholds.limits.MAX_DEPENDENCIES:
            violations.append(
                f"Too many dependencies ({metrics['dependency_count']} > "
                f"{self.thresholds.limits.MAX_DEPENDENCIES})")

        return violations

    def _check_cohesion_violations(self, metrics: Dict) -> List[str]:
        """Check for cohesion-related SRP violations."""
        violations = []

        if metrics['cohesion_score'] < self.thresholds.cohesion.MIN_COHESION_SCORE:
            violations.append(
                f"Low cohesion score ({metrics['cohesion_score']:.2f} < "
                f"{self.thresholds.cohesion.MIN_COHESION_SCORE})")

        return violations

    def _check_naming_violations(self, metrics: Dict) -> List[str]:
        """Check for naming-related SRP violations."""
        violations = []

        if 'and' in metrics['name'].lower():
            violations.append(
                "Class name contains 'and', suggesting multiple responsibilities")

        return violations

    def _determine_severity(self, metrics: Dict) -> str:
        """Determine violation severity based on metrics."""
        violation_count = self._calculate_violation_score(metrics)
        return self._get_severity_level(violation_count)

    def _calculate_violation_score(self, metrics: Dict) -> int:
        """Calculate total violation score based on metrics."""
        score = 0
        score += self._get_method_violation_score(metrics)
        score += self._get_structure_violation_score(metrics)
        score += self._get_cohesion_violation_score(metrics)
        return score

    def _get_method_violation_score(self, metrics: Dict) -> int:
        """Get violation score for method-related issues."""
        score = 0
        if metrics['method_count'] > self.thresholds.limits.MAX_METHODS_PER_CLASS:
            score += 1
        if (metrics['responsibility_group_count'] >
                self.thresholds.limits.MAX_METHOD_GROUPS):
            score += 2  # More serious violation
        return score

    def _get_structure_violation_score(self, metrics: Dict) -> int:
        """Get violation score for structural issues."""
        score = 0
        if metrics['line_count'] > self.thresholds.limits.MAX_CLASS_LINES:
            score += 1
        return score

    def _get_cohesion_violation_score(self, metrics: Dict) -> int:
        """Get violation score for cohesion issues."""
        score = 0
        if metrics['cohesion_score'] < self.thresholds.cohesion.MIN_COHESION_SCORE:
            score += 2  # Cohesion issues are serious
        return score

    def _get_severity_level(self, violation_count: int) -> str:
        """Convert violation count to severity level."""
        if violation_count >= self.thresholds.severity.ERROR_VIOLATION_COUNT:
            return Severity.ERROR
        if violation_count >= self.thresholds.severity.WARNING_VIOLATION_COUNT:
            return Severity.WARNING
        return Severity.INFO


def analyze_file(file_path: str,
                 thresholds: Optional[SRPThresholds] = None) -> List[SRPViolation]:
    """Analyze a single Python file for SRP violations."""
    return cast(List[SRPViolation],
               analyze_with_visitor(file_path, SRPAnalyzer, thresholds))


def analyze_directory(directory: str,
                      exclude_patterns: Optional[List[str]] = None,
                      thresholds: Optional[SRPThresholds] = None
                      ) -> List[SRPViolation]:
    """Analyze all Python files in a directory."""
    exclude_patterns = exclude_patterns or EXCLUDE_PATTERNS
    violations = []

    for path in Path(directory).rglob('*.py'):
        # Skip excluded patterns
        if any(pattern in str(path) for pattern in exclude_patterns):
            continue

        file_violations = analyze_file(str(path), thresholds)
        violations.extend(file_violations)

    return violations


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description=('Analyze Python code for Single Responsibility '
                    'Principle violations'))
    parser.add_argument('path', help='File or directory to analyze')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--threshold', choices=['strict', 'normal', 'lenient'],
                       default='normal', help='Violation threshold')
    parser.add_argument('--fail-on-error', action='store_true',
                       help='Exit with non-zero code if errors found')

    args = parser.parse_args()

    thresholds = _get_adjusted_thresholds(args.threshold)
    violations = _analyze_path(args.path, thresholds)
    _output_results(violations, args.json)
    _handle_exit_code(violations, args.fail_on_error)


def _get_adjusted_thresholds(threshold_level: str) -> 'SRPThresholds':
    """Get thresholds adjusted for the specified strictness level."""
    thresholds = DEFAULT_SRP_THRESHOLDS

    if threshold_level == 'strict':
        limits = replace(thresholds.limits,
                        MAX_METHODS_PER_CLASS=thresholds.levels.STRICT_MAX_METHODS,
                        MAX_METHOD_GROUPS=2,
                        MAX_CLASS_LINES=thresholds.levels.STRICT_MAX_LINES)
        return replace(thresholds, limits=limits)

    if threshold_level == 'lenient':
        limits = replace(thresholds.limits,
                        MAX_METHODS_PER_CLASS=thresholds.levels.LENIENT_MAX_METHODS,
                        MAX_METHOD_GROUPS=4,
                        MAX_CLASS_LINES=thresholds.levels.LENIENT_MAX_LINES)
        return replace(thresholds, limits=limits)

    return thresholds


def _analyze_path(path: str, thresholds: 'SRPThresholds') -> List[SRPViolation]:
    """Analyze the specified path for SRP violations."""
    if os.path.isfile(path):
        return analyze_file(path, thresholds)
    return analyze_directory(path, thresholds=thresholds)


def _output_results(violations: List[SRPViolation], json_output: bool) -> None:
    """Output the analysis results."""
    if json_output:
        _output_json_results(violations)
        return

    _output_text_results(violations)


def _output_json_results(violations: List[SRPViolation]) -> None:
    """Output results in JSON format."""
    print(json.dumps([v.to_dict() for v in violations], indent=2))


def _output_text_results(violations: List[SRPViolation]) -> None:
    """Output results in human-readable text format."""
    if not violations:
        _output_no_violations_message()
        return

    _output_violations_summary(violations)
    _output_violation_details(violations)


def _output_no_violations_message() -> None:
    """Output message when no violations are found."""
    print("✅ No SRP violations detected!")


def _output_violations_summary(violations: List[SRPViolation]) -> None:
    """Output summary of violations found."""
    print(f"Found {len(violations)} potential SRP violations:\n")


def _output_violation_details(violations: List[SRPViolation]) -> None:
    """Output detailed information for each violation."""
    for violation in violations:
        _output_single_violation(violation)


def _output_single_violation(violation: SRPViolation) -> None:
    """Output details for a single violation."""
    icon = _get_severity_icon(violation.severity)
    print(f"{icon} {violation.file_path}:{violation.line} - {violation.class_name}")
    _output_violation_reasons(violation.reasons)
    print()


def _output_violation_reasons(reasons: List[str]) -> None:
    """Output the reasons for a violation."""
    for reason in reasons:
        print(f"   - {reason}")


def _get_severity_icon(severity: str) -> str:
    """Get the icon for a severity level."""
    if severity == Severity.ERROR:
        return "❌"
    if severity == Severity.WARNING:
        return "⚠️"
    return "ℹ️"


def _handle_exit_code(violations: List[SRPViolation], fail_on_error: bool) -> None:
    """Handle exit code based on violations and fail_on_error setting."""
    if not fail_on_error:
        return

    error_count = sum(1 for v in violations if v.severity == Severity.ERROR)
    if error_count > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
