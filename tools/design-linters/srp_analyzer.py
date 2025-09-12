#!/usr/bin/env python3
"""
Single Responsibility Principle Analyzer.

Detects potential SRP violations using multiple heuristics:
- Method count and complexity
- Method name clustering
- Dependency analysis
- Cohesion metrics
"""

import ast
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple
import argparse
import json


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
    
    # Thresholds for SRP violation detection
    MAX_METHODS = 7
    MAX_METHOD_GROUPS = 3
    MAX_LINES = 200
    MAX_DEPENDENCIES = 5
    MAX_INSTANCE_VARS = 7
    
    # Method prefixes that indicate different responsibilities
    RESPONSIBILITY_PREFIXES = {
        'data_access': ['get', 'fetch', 'load', 'read', 'query'],
        'data_mutation': ['set', 'save', 'write', 'update', 'delete', 'create'],
        'validation': ['validate', 'verify', 'check', 'ensure', 'assert'],
        'transformation': ['convert', 'transform', 'parse', 'format', 'serialize'],
        'notification': ['send', 'notify', 'email', 'alert', 'publish'],
        'calculation': ['calculate', 'compute', 'process', 'analyze'],
        'rendering': ['render', 'display', 'draw', 'show', 'print'],
        'authentication': ['login', 'logout', 'authenticate', 'authorize'],
        'configuration': ['configure', 'setup', 'init', 'register']
    }
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations: List[SRPViolation] = []
        self.current_class = None
        self.class_metrics = {}
    
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
            for category, prefixes in self.RESPONSIBILITY_PREFIXES.items():
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
        
        if metrics['method_count'] > self.MAX_METHODS:
            violations.append(f"Too many methods ({metrics['method_count']} > {self.MAX_METHODS})")
        
        if metrics['responsibility_group_count'] > self.MAX_METHOD_GROUPS:
            groups = ', '.join(metrics['responsibility_groups'].keys())
            violations.append(f"Multiple responsibility groups detected: {groups}")
        
        if metrics['line_count'] > self.MAX_LINES:
            violations.append(f"Class too large ({metrics['line_count']} lines > {self.MAX_LINES})")
        
        if metrics['instance_var_count'] > self.MAX_INSTANCE_VARS:
            violations.append(f"Too many instance variables ({metrics['instance_var_count']} > {self.MAX_INSTANCE_VARS})")
        
        if metrics['dependency_count'] > self.MAX_DEPENDENCIES:
            violations.append(f"Too many dependencies ({metrics['dependency_count']} > {self.MAX_DEPENDENCIES})")
        
        if metrics['cohesion_score'] < 0.3:
            violations.append(f"Low cohesion score ({metrics['cohesion_score']:.2f} < 0.3)")
        
        # Check for "and" in class name (obvious SRP violation)
        if 'and' in metrics['name'].lower():
            violations.append(f"Class name contains 'and', suggesting multiple responsibilities")
        
        return violations
    
    def _determine_severity(self, metrics: Dict) -> str:
        """Determine violation severity based on metrics."""
        violation_count = 0
        
        if metrics['method_count'] > self.MAX_METHODS:
            violation_count += 1
        if metrics['responsibility_group_count'] > self.MAX_METHOD_GROUPS:
            violation_count += 2  # This is more serious
        if metrics['line_count'] > self.MAX_LINES:
            violation_count += 1
        if metrics['cohesion_score'] < 0.3:
            violation_count += 2
        
        if violation_count >= 4:
            return 'error'
        elif violation_count >= 2:
            return 'warning'
        else:
            return 'info'


def analyze_file(file_path: str) -> List[SRPViolation]:
    """Analyze a single Python file for SRP violations."""
    with open(file_path, 'r') as f:
        try:
            tree = ast.parse(f.read())
            analyzer = SRPAnalyzer(file_path)
            analyzer.visit(tree)
            return analyzer.violations
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}", file=sys.stderr)
            return []


def analyze_directory(directory: str, exclude_patterns: List[str] = None) -> List[SRPViolation]:
    """Analyze all Python files in a directory."""
    exclude_patterns = exclude_patterns or ['test_', '__pycache__', '.git', 'venv', '.venv']
    violations = []
    
    for path in Path(directory).rglob('*.py'):
        # Skip excluded patterns
        if any(pattern in str(path) for pattern in exclude_patterns):
            continue
        
        file_violations = analyze_file(str(path))
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
    if args.threshold == 'strict':
        SRPAnalyzer.MAX_METHODS = 5
        SRPAnalyzer.MAX_METHOD_GROUPS = 2
        SRPAnalyzer.MAX_LINES = 150
    elif args.threshold == 'lenient':
        SRPAnalyzer.MAX_METHODS = 10
        SRPAnalyzer.MAX_METHOD_GROUPS = 4
        SRPAnalyzer.MAX_LINES = 300
    
    # Analyze path
    if os.path.isfile(args.path):
        violations = analyze_file(args.path)
    else:
        violations = analyze_directory(args.path)
    
    # Output results
    if args.json:
        print(json.dumps([v.to_dict() for v in violations], indent=2))
    else:
        if not violations:
            print("✅ No SRP violations detected!")
        else:
            print(f"Found {len(violations)} potential SRP violations:\n")
            for v in violations:
                icon = "❌" if v.severity == 'error' else "⚠️" if v.severity == 'warning' else "ℹ️"
                print(f"{icon} {v.file_path}:{v.line} - {v.class_name}")
                for reason in v.reasons:
                    print(f"   - {reason}")
                print()
    
    # Exit code
    if args.fail_on_error:
        error_count = sum(1 for v in violations if v.severity == 'error')
        if error_count > 0:
            sys.exit(1)


if __name__ == '__main__':
    main()