#!/usr/bin/env python3
"""
Purpose: Detects Single Responsibility Principle violations in Python code
Scope: Python classes and modules across backend and tools directories
Overview: This analyzer detects potential SRP violations using multiple heuristics including
    method count and complexity analysis, method name clustering to identify unrelated
    responsibilities, dependency analysis to find excessive coupling, and cohesion metrics
    to measure class unity. It helps identify classes that are doing too much and suggests
    refactoring opportunities to improve code maintainability and adherence to SOLID principles.
Dependencies: ast for Python AST parsing, collections for data structures, pathlib for file operations
Exports: SRPAnalyzer class, SRPViolation dataclass, CohesionCalculator class
Interfaces: main() CLI function, analyze_file() returns List[SRPViolation]
Implementation: Uses AST analysis to calculate complexity metrics and semantic clustering algorithms
"""

import ast
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Optional
import argparse
import json

try:
    from . import (
    DEFAULT_SRP_THRESHOLDS,
    RESPONSIBILITY_PREFIXES,
    EXCLUDE_PATTERNS,
    Severity,
    SRPThresholds
)
except ImportError:
    # For direct script execution
    from __init__ import (
        DEFAULT_SRP_THRESHOLDS,
        RESPONSIBILITY_PREFIXES,
        EXCLUDE_PATTERNS,
        Severity,
        SRPThresholds
    )


class SRPViolation:
    """Represents a potential SRP violation."""

    def __init__(self, file_path: str, class_name: str, line: int, severity: str, reasons: List[str]):
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

    def __init__(self, file_path: str, thresholds: Optional[SRPThresholds] = None):
        self.file_path = file_path
        self.violations: List[SRPViolation] = []
        self.current_class = None
        self.class_metrics = {}
        self.thresholds = thresholds or DEFAULT_SRP_THRESHOLDS

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
                severity,
                violations
            )
            self.violations.append(violation)

        self.generic_visit(node)
        self.current_class = None

    def _analyze_class(self, node: ast.ClassDef) -> Dict:
        """Extract metrics from a class."""
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
        dependencies = set()
        for item in ast.walk(node):
            if isinstance(item, ast.Import):
                for alias in item.names:
                    dependencies.add(alias.name.split('.')[0])
            elif isinstance(item, ast.ImportFrom):
                if item.module:
                    dependencies.add(item.module.split('.')[0])
        return dependencies

    def _group_methods_by_responsibility(self, methods: List[ast.FunctionDef]) -> Dict[str, List[str]]:
        """Group methods by their likely responsibility based on naming."""
        groups = defaultdict(list)

        for method in methods:
            if method.name.startswith('_'):
                continue  # Skip private methods

            categorized = False
            for category, prefixes in RESPONSIBILITY_PREFIXES.items():
                for prefix in prefixes:
                    if method.name.lower().startswith(prefix):
                        groups[category].append(method.name)
                        categorized = True
                        break
                if categorized:
                    break

            if not categorized:
                groups['other'].append(method.name)

        return dict(groups)

    def _calculate_cohesion(self, methods: List[ast.FunctionDef], instance_vars: Set[str]) -> float:
        """
        Calculate cohesion score (0-1).
        Higher score means better cohesion (methods use similar instance variables).
        """
        if not methods or not instance_vars:
            return 1.0

        method_var_usage = {}
        for method in methods:
            used_vars = set()
            for node in ast.walk(method):
                if isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name) and node.value.id == 'self':
                        if node.attr in instance_vars:
                            used_vars.add(node.attr)
            method_var_usage[method.name] = used_vars

        # Calculate LCOM (Lack of Cohesion of Methods)
        # Lower LCOM = higher cohesion
        total_pairs = 0
        shared_pairs = 0

        method_names = list(method_var_usage.keys())
        for i in range(len(method_names)):
            for j in range(i + 1, len(method_names)):
                total_pairs += 1
                if method_var_usage[method_names[i]] & method_var_usage[method_names[j]]:
                    shared_pairs += 1

        if total_pairs == 0:
            return 1.0

        return shared_pairs / total_pairs

    def _check_srp_violations(self, metrics: Dict) -> List[str]:
        """Check if metrics indicate SRP violations."""
        violations = []

        if metrics['method_count'] > self.thresholds.MAX_METHODS_PER_CLASS:
            violations.append(f"Too many methods ({metrics['method_count']} > {self.thresholds.MAX_METHODS_PER_CLASS})")

        if metrics['responsibility_group_count'] > self.thresholds.MAX_METHOD_GROUPS:
            groups = ', '.join(metrics['responsibility_groups'].keys())
            violations.append(f"Multiple responsibility groups detected: {groups}")

        if metrics['line_count'] > self.thresholds.MAX_CLASS_LINES:
            violations.append(f"Class too large ({metrics['line_count']} lines > {self.thresholds.MAX_CLASS_LINES})")

        if metrics['instance_var_count'] > self.thresholds.MAX_INSTANCE_VARIABLES:
            violations.append(f"Too many instance variables ({metrics['instance_var_count']} > {self.thresholds.MAX_INSTANCE_VARIABLES})")

        if metrics['dependency_count'] > self.thresholds.MAX_DEPENDENCIES:
            violations.append(f"Too many dependencies ({metrics['dependency_count']} > {self.thresholds.MAX_DEPENDENCIES})")

        if metrics['cohesion_score'] < self.thresholds.MIN_COHESION_SCORE:
            violations.append(f"Low cohesion score ({metrics['cohesion_score']:.2f} < {self.thresholds.MIN_COHESION_SCORE})")

        # Check for "and" in class name (obvious SRP violation)
        if 'and' in metrics['name'].lower():
            violations.append(f"Class name contains 'and', suggesting multiple responsibilities")

        return violations

    def _determine_severity(self, metrics: Dict) -> str:
        """Determine violation severity based on metrics."""
        violation_count = 0

        if metrics['method_count'] > self.thresholds.MAX_METHODS_PER_CLASS:
            violation_count += 1
        if metrics['responsibility_group_count'] > self.thresholds.MAX_METHOD_GROUPS:
            violation_count += 2  # This is more serious
        if metrics['line_count'] > self.thresholds.MAX_CLASS_LINES:
            violation_count += 1
        if metrics['cohesion_score'] < self.thresholds.MIN_COHESION_SCORE:
            violation_count += 2

        if violation_count >= self.thresholds.ERROR_VIOLATION_COUNT:
            return Severity.ERROR
        elif violation_count >= self.thresholds.WARNING_VIOLATION_COUNT:
            return Severity.WARNING
        else:
            return Severity.INFO


def analyze_file(file_path: str, thresholds: Optional[SRPThresholds] = None) -> List[SRPViolation]:
    """Analyze a single Python file for SRP violations."""
    with open(file_path, 'r') as f:
        try:
            tree = ast.parse(f.read())
            analyzer = SRPAnalyzer(file_path, thresholds)
            analyzer.visit(tree)
            return analyzer.violations
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}", file=sys.stderr)
            return []


def analyze_directory(directory: str, exclude_patterns: List[str] = None, thresholds: Optional[SRPThresholds] = None) -> List[SRPViolation]:
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


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Analyze Python code for Single Responsibility Principle violations')
    parser.add_argument('path', help='File or directory to analyze')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--threshold', choices=['strict', 'normal', 'lenient'],
                       default='normal', help='Violation threshold')
    parser.add_argument('--fail-on-error', action='store_true',
                       help='Exit with non-zero code if errors found')

    args = parser.parse_args()

    # Adjust thresholds based on strictness
    thresholds = DEFAULT_SRP_THRESHOLDS
    if args.threshold == 'strict':
        from dataclasses import replace
        thresholds = replace(thresholds,
            MAX_METHODS_PER_CLASS=thresholds.STRICT_MAX_METHODS,
            MAX_METHOD_GROUPS=2,
            MAX_CLASS_LINES=thresholds.STRICT_MAX_LINES
        )
    elif args.threshold == 'lenient':
        from dataclasses import replace
        thresholds = replace(thresholds,
            MAX_METHODS_PER_CLASS=thresholds.LENIENT_MAX_METHODS,
            MAX_METHOD_GROUPS=4,
            MAX_CLASS_LINES=thresholds.LENIENT_MAX_LINES
        )

    # Analyze path
    if os.path.isfile(args.path):
        violations = analyze_file(args.path, thresholds)
    else:
        violations = analyze_directory(args.path, thresholds=thresholds)

    # Output results
    if args.json:
        print(json.dumps([v.to_dict() for v in violations], indent=2))
    else:
        if not violations:
            print("✅ No SRP violations detected!")
        else:
            print(f"Found {len(violations)} potential SRP violations:\n")
            for v in violations:
                icon = "❌" if v.severity == Severity.ERROR else "⚠️" if v.severity == Severity.WARNING else "ℹ️"
                print(f"{icon} {v.file_path}:{v.line} - {v.class_name}")
                for reason in v.reasons:
                    print(f"   - {reason}")
                print()

    # Exit code
    if args.fail_on_error:
        error_count = sum(1 for v in violations if v.severity == Severity.ERROR)
        if error_count > 0:
            sys.exit(1)


if __name__ == '__main__':
    main()
