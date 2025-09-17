#!/usr/bin/env python3
"""
Purpose: Single Responsibility Principle rules for pluggable framework
Scope: Implements SRP violation detection as individual, focused rules
Overview: This module converts the monolithic SRP analyzer into focused,
    pluggable rules. Each rule checks for a specific aspect of SRP violations
    (method count, responsibilities, cohesion, size, dependencies) enabling
    fine-grained control and easier testing.
Dependencies: Framework interfaces, AST analysis utilities
Exports: Individual SRP-focused rules
Interfaces: All rules implement ASTLintRule interface
Implementation: Rule-based architecture with single responsibility per rule
"""

import ast
from typing import List, Set, Dict, Any
from collections import defaultdict

from ...framework.interfaces import ASTLintRule, LintViolation, LintContext, Severity


class TooManyMethodsRule(ASTLintRule):
    """Rule to detect classes with too many methods."""

    @property
    def rule_id(self) -> str:
        return "solid.srp.too-many-methods"

    @property
    def rule_name(self) -> str:
        return "Too Many Methods"

    @property
    def description(self) -> str:
        return "Classes should not have too many methods as it may indicate multiple responsibilities"

    @property
    def severity(self) -> Severity:
        return Severity.WARNING

    @property
    def categories(self) -> Set[str]:
        return {"solid", "srp", "complexity"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        return isinstance(node, ast.ClassDef)

    def check_node(self, node: ast.ClassDef, context: LintContext) -> List[LintViolation]:
        config = self.get_configuration(context.metadata or {})
        max_methods = config.get('max_methods', 15)

        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        method_count = len(methods)

        if method_count > max_methods:
            return [LintViolation(
                rule_id=self.rule_id,
                file_path=str(context.file_path),
                line=node.lineno,
                column=node.col_offset,
                severity=self.severity,
                message=f"Class '{node.name}' has {method_count} methods (max: {max_methods})",
                description=f"Classes with many methods often violate SRP by handling multiple responsibilities",
                suggestion=f"Consider splitting '{node.name}' into smaller, focused classes"
            )]

        return []


class TooManyResponsibilitiesRule(ASTLintRule):
    """Rule to detect classes with multiple responsibility groups."""

    @property
    def rule_id(self) -> str:
        return "solid.srp.multiple-responsibilities"

    @property
    def rule_name(self) -> str:
        return "Multiple Responsibilities"

    @property
    def description(self) -> str:
        return "Classes should have a single responsibility based on method naming patterns"

    @property
    def severity(self) -> Severity:
        return Severity.ERROR

    @property
    def categories(self) -> Set[str]:
        return {"solid", "srp"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        return isinstance(node, ast.ClassDef)

    def check_node(self, node: ast.ClassDef, context: LintContext) -> List[LintViolation]:
        config = self.get_configuration(context.metadata or {})
        max_groups = config.get('max_responsibility_groups', 2)

        responsibility_prefixes = config.get('responsibility_prefixes', {
            'data': ['get', 'set', 'fetch', 'load', 'save', 'store'],
            'validation': ['validate', 'check', 'verify', 'confirm'],
            'formatting': ['format', 'render', 'display', 'print'],
            'calculation': ['calculate', 'compute', 'sum', 'count'],
            'communication': ['send', 'receive', 'notify', 'broadcast'],
            'file_io': ['read', 'write', 'open', 'close', 'export', 'import'],
            'network': ['connect', 'disconnect', 'upload', 'download', 'sync'],
            'ui': ['show', 'hide', 'update', 'refresh', 'draw']
        })

        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        responsibility_groups = self._group_methods_by_responsibility(methods, responsibility_prefixes)

        if len(responsibility_groups) > max_groups:
            groups_list = ', '.join(responsibility_groups.keys())
            return [LintViolation(
                rule_id=self.rule_id,
                file_path=str(context.file_path),
                line=node.lineno,
                column=node.col_offset,
                severity=self.severity,
                message=f"Class '{node.name}' has {len(responsibility_groups)} responsibility groups",
                description=f"Multiple responsibility groups detected: {groups_list}",
                suggestion=f"Split '{node.name}' by responsibility: {groups_list}",
                context={'responsibility_groups': responsibility_groups}
            )]

        return []

    def _group_methods_by_responsibility(self, methods: List[ast.FunctionDef],
                                       responsibility_prefixes: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Group methods by their likely responsibility based on naming."""
        groups = defaultdict(list)

        for method in methods:
            if method.name.startswith('_'):
                continue  # Skip private methods

            category = self._find_method_category(method.name, responsibility_prefixes)
            groups[category].append(method.name)

        return dict(groups)

    def _find_method_category(self, method_name: str, responsibility_prefixes: Dict[str, List[str]]) -> str:
        """Find the category for a method based on its name."""
        for category, prefixes in responsibility_prefixes.items():
            for prefix in prefixes:
                if method_name.lower().startswith(prefix):
                    return category
        return 'other'


class LowCohesionRule(ASTLintRule):
    """Rule to detect classes with low cohesion."""

    @property
    def rule_id(self) -> str:
        return "solid.srp.low-cohesion"

    @property
    def rule_name(self) -> str:
        return "Low Cohesion"

    @property
    def description(self) -> str:
        return "Classes should have high cohesion with methods using shared instance variables"

    @property
    def severity(self) -> Severity:
        return Severity.WARNING

    @property
    def categories(self) -> Set[str]:
        return {"solid", "srp", "cohesion"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        return isinstance(node, ast.ClassDef)

    def check_node(self, node: ast.ClassDef, context: LintContext) -> List[LintViolation]:
        config = self.get_configuration(context.metadata or {})
        min_cohesion = config.get('min_cohesion_score', 0.3)

        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        instance_vars = self._extract_instance_variables(node)

        if not methods or not instance_vars:
            return []  # Can't calculate cohesion

        cohesion_score = self._calculate_cohesion(methods, instance_vars)

        if cohesion_score < min_cohesion:
            return [LintViolation(
                rule_id=self.rule_id,
                file_path=str(context.file_path),
                line=node.lineno,
                column=node.col_offset,
                severity=self.severity,
                message=f"Class '{node.name}' has low cohesion ({cohesion_score:.2f})",
                description=f"Methods in the class share few instance variables (cohesion: {cohesion_score:.2f}, min: {min_cohesion})",
                suggestion="Consider splitting the class into more cohesive units"
            )]

        return []

    def _extract_instance_variables(self, node: ast.ClassDef) -> Set[str]:
        """Extract instance variables from a class."""
        instance_vars = set()
        for item in ast.walk(node):
            if isinstance(item, ast.Attribute):
                if isinstance(item.value, ast.Name) and item.value.id == 'self':
                    instance_vars.add(item.attr)
        return instance_vars

    def _calculate_cohesion(self, methods: List[ast.FunctionDef], instance_vars: Set[str]) -> float:
        """Calculate cohesion score using LCOM metric."""
        method_var_usage = {}
        for method in methods:
            used_vars = self._find_used_instance_vars(method, instance_vars)
            method_var_usage[method.name] = used_vars

        method_names = list(method_var_usage.keys())
        if len(method_names) < 2:
            return 1.0

        total_pairs = 0
        shared_pairs = 0

        for i, method_i in enumerate(method_names):
            for method_j in method_names[i + 1:]:
                total_pairs += 1
                if method_var_usage[method_i] & method_var_usage[method_j]:
                    shared_pairs += 1

        return shared_pairs / total_pairs if total_pairs > 0 else 1.0

    def _find_used_instance_vars(self, method: ast.FunctionDef, instance_vars: Set[str]) -> Set[str]:
        """Find instance variables used by a method."""
        used_vars = set()
        for node in ast.walk(method):
            if (isinstance(node, ast.Attribute) and
                isinstance(node.value, ast.Name) and
                node.value.id == 'self' and
                node.attr in instance_vars):
                used_vars.add(node.attr)
        return used_vars


class ClassTooBigRule(ASTLintRule):
    """Rule to detect classes that are too large."""

    @property
    def rule_id(self) -> str:
        return "solid.srp.class-too-big"

    @property
    def rule_name(self) -> str:
        return "Class Too Big"

    @property
    def description(self) -> str:
        return "Classes should not be excessively large as it may indicate multiple responsibilities"

    @property
    def severity(self) -> Severity:
        return Severity.INFO

    @property
    def categories(self) -> Set[str]:
        return {"solid", "srp", "size"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        return isinstance(node, ast.ClassDef)

    def check_node(self, node: ast.ClassDef, context: LintContext) -> List[LintViolation]:
        config = self.get_configuration(context.metadata or {})
        max_lines = config.get('max_class_lines', 200)

        if node.end_lineno and node.lineno:
            line_count = node.end_lineno - node.lineno

            if line_count > max_lines:
                return [LintViolation(
                    rule_id=self.rule_id,
                    file_path=str(context.file_path),
                    line=node.lineno,
                    column=node.col_offset,
                    severity=self.severity,
                    message=f"Class '{node.name}' is large ({line_count} lines)",
                    description=f"Large classes may violate SRP by handling multiple concerns",
                    suggestion=f"Consider breaking down '{node.name}' into smaller classes"
                )]

        return []


class TooManyDependenciesRule(ASTLintRule):
    """Rule to detect classes with too many dependencies."""

    @property
    def rule_id(self) -> str:
        return "solid.srp.too-many-dependencies"

    @property
    def rule_name(self) -> str:
        return "Too Many Dependencies"

    @property
    def description(self) -> str:
        return "Classes should not have excessive dependencies as it may indicate multiple responsibilities"

    @property
    def severity(self) -> Severity:
        return Severity.WARNING

    @property
    def categories(self) -> Set[str]:
        return {"solid", "srp", "dependencies"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        return isinstance(node, ast.ClassDef)

    def check_node(self, node: ast.ClassDef, context: LintContext) -> List[LintViolation]:
        config = self.get_configuration(context.metadata or {})
        max_dependencies = config.get('max_dependencies', 10)

        dependencies = self._extract_dependencies(node)

        if len(dependencies) > max_dependencies:
            return [LintViolation(
                rule_id=self.rule_id,
                file_path=str(context.file_path),
                line=node.lineno,
                column=node.col_offset,
                severity=self.severity,
                message=f"Class '{node.name}' has {len(dependencies)} dependencies",
                description=f"Classes with many dependencies may be handling multiple concerns",
                suggestion=f"Consider reducing dependencies or splitting '{node.name}'"
            )]

        return []

    def _extract_dependencies(self, node: ast.ClassDef) -> Set[str]:
        """Extract external dependencies from a class."""
        dependencies: Set[str] = set()
        for item in ast.walk(node):
            if isinstance(item, ast.Import):
                for alias in item.names:
                    dependencies.add(alias.name.split('.')[0])
            elif isinstance(item, ast.ImportFrom) and item.module:
                dependencies.add(item.module.split('.')[0])
        return dependencies
