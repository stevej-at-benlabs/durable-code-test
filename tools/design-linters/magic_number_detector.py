#!/usr/bin/env python3
"""
Magic Number Detector.

Detects hardcoded numeric and string literals that should be constants.
This is a separate concern from design principles - it's about code clarity.
"""

import ast
import os
import sys
from pathlib import Path
from typing import List, Set, Union
import argparse
import json


class MagicNumberViolation:
    """Represents a magic number/literal violation."""

    def __init__(self, file_path: str, line: int, column: int, value: Union[int, float, str], context: str):
        self.file_path = file_path
        self.line = line
        self.column = column
        self.value = value
        self.context = context
        self.suggestion = self._generate_suggestion()

    def _generate_suggestion(self) -> str:
        """Generate a constant name suggestion."""
        if isinstance(self.value, (int, float)):
            # For numbers, try to infer meaning from context
            if self.value == 0:
                return "ZERO_VALUE"
            elif self.value == 1:
                return "SINGLE_ITEM"
            elif self.value == 100:
                return "PERCENTAGE_MAX"
            elif self.value == 60:
                return "SECONDS_PER_MINUTE"
            elif self.value == 3600:
                return "SECONDS_PER_HOUR"
            else:
                return f"THRESHOLD_{str(self.value).replace('.', '_').replace('-', 'NEG_')}"
        else:
            # For strings, convert to constant format
            return self.value.upper().replace(' ', '_').replace('-', '_')[:30] + "_CONSTANT"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON output."""
        return {
            'file': self.file_path,
            'line': self.line,
            'column': self.column,
            'value': str(self.value),
            'type': type(self.value).__name__,
            'context': self.context,
            'suggestion': self.suggestion
        }


class MagicNumberDetector(ast.NodeVisitor):
    """AST visitor that detects magic numbers and literals."""

    # Values that are generally acceptable as literals
    ALLOWED_NUMBERS = {
        -1,  # Common index/flag
        0,   # Zero initialization
        1,   # Unity/increment
        2,   # Binary/pair operations
        5,   # Common small value
        10,  # Decimal base
        100, # Percentage
        1000, # Kilo multiplier
        1024, # Binary kilo
    }

    # String patterns that are acceptable as literals
    ALLOWED_STRING_PATTERNS = {
        '',      # Empty string
        ' ',     # Space
        '\n',    # Newline
        '\t',    # Tab
        ',',     # Comma separator
        '.',     # Dot separator
        '/',     # Path separator
        ':',     # Colon separator
        'utf-8', # Encoding
        'utf8',  # Encoding variant
        'r',     # Read mode
        'w',     # Write mode
        'a',     # Append mode
        'rb',    # Read binary
        'wb',    # Write binary
    }

    def __init__(self, file_path: str, ignore_tests: bool = True):
        self.file_path = file_path
        self.violations: List[MagicNumberViolation] = []
        self.current_function = None
        self.in_constant_definition = False
        self.ignore_tests = ignore_tests
        self.is_test_file = 'test' in file_path.lower()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track current function for context."""
        old_function = self.current_function
        self.current_function = node.name

        # Skip test functions if configured
        if self.ignore_tests and node.name.startswith('test_'):
            return

        self.generic_visit(node)
        self.current_function = old_function

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Track current async function for context."""
        old_function = self.current_function
        self.current_function = node.name

        # Skip test functions if configured
        if self.ignore_tests and node.name.startswith('test_'):
            return

        self.generic_visit(node)
        self.current_function = old_function

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Check annotated assignments (might be constants)."""
        if isinstance(node.target, ast.Name):
            if node.target.id.isupper():
                # This is likely a constant definition
                self.in_constant_definition = True

        self.generic_visit(node)
        self.in_constant_definition = False

    def visit_Assign(self, node: ast.Assign) -> None:
        """Check assignments for constant definitions."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                if target.id.isupper():
                    # This is likely a constant definition
                    self.in_constant_definition = True
                    break

        self.generic_visit(node)
        self.in_constant_definition = False

    def visit_Constant(self, node: ast.Constant) -> None:
        """Check for magic numbers and strings."""
        # Skip if in test file and ignoring tests
        if self.ignore_tests and self.is_test_file:
            return

        # Skip if this is a constant definition
        if self.in_constant_definition:
            return

        # Skip docstrings
        if isinstance(node.value, str):
            if self._is_docstring(node):
                return

        # Check for magic numbers
        if isinstance(node.value, (int, float)):
            if node.value not in self.ALLOWED_NUMBERS:
                # Check for special contexts where numbers are OK
                if not self._is_acceptable_context(node):
                    context = f"in {self.current_function}" if self.current_function else "at module level"
                    violation = MagicNumberViolation(
                        self.file_path,
                        node.lineno,
                        node.col_offset,
                        node.value,
                        context
                    )
                    self.violations.append(violation)

        # Check for magic strings
        elif isinstance(node.value, str):
            if (len(node.value) > 1 and
                node.value not in self.ALLOWED_STRING_PATTERNS and
                not node.value.startswith(('test', '__'))):

                # Skip if it looks like a dict key or similar
                if not self._is_string_key(node) and not self._is_docstring(node):
                    context = f"in {self.current_function}" if self.current_function else "at module level"
                    violation = MagicNumberViolation(
                        self.file_path,
                        node.lineno,
                        node.col_offset,
                        node.value,
                        context
                    )
                    self.violations.append(violation)

    def _is_acceptable_context(self, node: ast.Constant) -> bool:
        """Check if the context makes the literal acceptable."""
        # Array/list indices are generally OK
        parent = getattr(node, 'parent', None)
        if parent:
            if isinstance(parent, ast.Subscript):
                return True
            # Range arguments are OK
            if isinstance(parent, ast.Call):
                if hasattr(parent.func, 'id') and parent.func.id in ('range', 'enumerate'):
                    return True
            # Slice values are OK
            if isinstance(parent, ast.Slice):
                return True

        return False

    def _is_string_key(self, node: ast.Constant) -> bool:
        """Check if string is used as a dictionary key or similar."""
        parent = getattr(node, 'parent', None)
        if parent:
            # Dictionary keys are generally OK
            if isinstance(parent, ast.Dict):
                # Check if this is a key (not a value)
                try:
                    key_index = parent.keys.index(node)
                    return True
                except (ValueError, AttributeError):
                    pass
            # Subscript strings (dict access) are OK
            if isinstance(parent, ast.Subscript):
                return True
            # Attribute access strings are OK
            if isinstance(parent, ast.Attribute):
                return True

        return False

    def _is_docstring(self, node: ast.Constant) -> bool:
        """Check if string is a docstring."""
        parent = getattr(node, 'parent', None)
        if parent and isinstance(parent, ast.Expr):
            # Check if this is the first statement in a function/class/module
            grandparent = getattr(parent, 'parent', None)
            if grandparent:
                if isinstance(grandparent, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                    # Find the first non-decorator statement
                    body = grandparent.body
                    if body:
                        # Skip any potential decorator or other non-expression statements
                        for stmt in body:
                            if isinstance(stmt, ast.Expr) and stmt == parent:
                                # This is a standalone expression that could be a docstring
                                # Check if it's a string literal at the beginning
                                if isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                                    # Check position - should be first real statement
                                    real_stmts = [s for s in body if not isinstance(s, (ast.Pass,))]
                                    if real_stmts and real_stmts[0] == stmt:
                                        return True
                            elif not isinstance(stmt, (ast.Pass, ast.Expr)):
                                # If we hit a non-expression, non-pass statement, no docstring here
                                break
        return False


def add_parent_refs(tree: ast.AST) -> None:
    """Add parent references to all nodes in the AST."""
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            setattr(child, 'parent', parent)


def analyze_file(file_path: str, ignore_tests: bool = True) -> List[MagicNumberViolation]:
    """Analyze a single Python file for magic numbers."""
    with open(file_path, 'r') as f:
        try:
            tree = ast.parse(f.read())
            add_parent_refs(tree)
            detector = MagicNumberDetector(file_path, ignore_tests)
            detector.visit(tree)
            return detector.violations
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}", file=sys.stderr)
            return []


def analyze_directory(directory: str, exclude_patterns: List[str] = None, ignore_tests: bool = True) -> List[MagicNumberViolation]:
    """Analyze all Python files in a directory."""
    exclude_patterns = exclude_patterns or ['__pycache__', '.git', 'venv', '.venv', 'migrations']
    violations = []

    for path in Path(directory).rglob('*.py'):
        # Skip excluded patterns
        if any(pattern in str(path) for pattern in exclude_patterns):
            continue

        file_violations = analyze_file(str(path), ignore_tests)
        violations.extend(file_violations)

    return violations


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Detect magic numbers and literals in Python code')
    parser.add_argument('path', help='File or directory to analyze')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--include-tests', action='store_true', help='Include test files in analysis')
    parser.add_argument('--fail-on-violation', action='store_true',
                       help='Exit with non-zero code if violations found')

    args = parser.parse_args()

    # Analyze path
    if os.path.isfile(args.path):
        violations = analyze_file(args.path, ignore_tests=not args.include_tests)
    else:
        violations = analyze_directory(args.path, ignore_tests=not args.include_tests)

    # Output results
    if args.json:
        print(json.dumps([v.to_dict() for v in violations], indent=2))
    else:
        if not violations:
            print("✅ No magic numbers detected!")
        else:
            print(f"Found {len(violations)} magic numbers/literals:\n")
            for v in violations:
                value_display = f'"{v.value}"' if isinstance(v.value, str) else str(v.value)
                print(f"⚠️  {v.file_path}:{v.line}:{v.column}")
                print(f"   Value: {value_display}")
                print(f"   Context: {v.context}")
                print(f"   Suggestion: Define as constant '{v.suggestion}'")
                print()

    # Exit code
    if args.fail_on_violation and violations:
        sys.exit(1)


if __name__ == '__main__':
    main()
