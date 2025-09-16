#!/usr/bin/env python3
"""
Purpose: Detects hardcoded numeric and string literals that should be named constants
Scope: Python source files across the project for code clarity enforcement
Overview: This analyzer identifies magic numbers and strings that reduce code
    readability and maintainability by scanning Python source code using AST parsing.
    It detects hardcoded literals that should be converted to named constants,
    excluding common acceptable values like 0, 1, and empty strings. The tool helps
    enforce coding standards that improve code self-documentation and make values
    easier to maintain.
Dependencies: ast for Python AST parsing, pathlib for file operations, argparse for CLI
Exports: MagicNumberDetector class, MagicLiteral dataclass, LiteralType enum
Interfaces: main() CLI function, analyze_file() returns List[MagicLiteral]
Implementation: Uses AST visitor pattern to traverse code and identify literal nodes
"""

import ast
import os
import sys
from pathlib import Path
from typing import List, Set, Union, Optional, Dict, cast
import argparse
import json
try:
    from .constants import ALLOWED_STRING_PATTERNS, handle_syntax_error
except ImportError:
    from constants import (  # type: ignore[import-not-found, no-redef]
        ALLOWED_STRING_PATTERNS,
        handle_syntax_error,
    )


class MagicNumberViolation:
    """Represents a magic number/literal violation."""

    def __init__(self, file_path: str, line: int, *, column: int,
                 value: Union[int, float, str], context: str):
        self.file_path = file_path
        self.line = line
        self.column = column
        self.value = value
        self.context = context
        self.suggestion = self._generate_suggestion()

    def _generate_suggestion(self) -> str:
        """Generate a constant name suggestion."""
        if isinstance(self.value, (int, float)):
            return self._generate_number_suggestion()
        # For strings, convert to constant format
        cleaned = self.value.upper().replace(' ', '_').replace('-', '_')[:30]
        return cleaned + "_CONSTANT"

    def _generate_number_suggestion(self) -> str:
        """Generate a suggestion for numeric values."""
        suggestions: Dict[Union[int, float], str] = {
            0: "ZERO_VALUE",
            1: "SINGLE_ITEM",
            100: "PERCENTAGE_MAX",
            60: "SECONDS_PER_MINUTE",
            3600: "SECONDS_PER_HOUR"
        }

        if isinstance(self.value, (int, float)) and self.value in suggestions:
            return suggestions[self.value]

        cleaned_value = str(self.value).replace('.', '_').replace('-', 'NEG_')
        return f"THRESHOLD_{cleaned_value}"

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


class MagicNumberConfig:
    """Configuration for magic number detection - follows OCP by allowing extension."""

    DEFAULT_ALLOWED_NUMBERS: Set[int] = {
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

    DEFAULT_ALLOWED_STRING_PATTERNS: Set[str] = set(ALLOWED_STRING_PATTERNS)

    def __init__(self, allowed_numbers: Optional[Set[Union[int, float]]] = None,
                 allowed_string_patterns: Optional[Set[str]] = None) -> None:
        """Initialize config with optional custom values."""
        self.allowed_numbers: Set[Union[int, float]] = set(
            allowed_numbers or self.DEFAULT_ALLOWED_NUMBERS
        )
        self.allowed_string_patterns = (
            allowed_string_patterns or self.DEFAULT_ALLOWED_STRING_PATTERNS.copy()
        )

    def add_allowed_number(self, number: Union[int, float]) -> None:
        """Add a new allowed number without modifying the class."""
        self.allowed_numbers.add(number)

    def add_allowed_string_pattern(self, pattern: str) -> None:
        """Add a new allowed string pattern without modifying the class."""
        self.allowed_string_patterns.add(pattern)


class MagicNumberDetector(ast.NodeVisitor):
    """AST visitor that detects magic numbers and literals."""

    def __init__(self, file_path: str, ignore_tests: bool = True,
                 config: Optional[MagicNumberConfig] = None) -> None:
        self.file_path = file_path
        self.violations: List[MagicNumberViolation] = []
        self.current_function: Optional[str] = None
        self.in_constant_definition = False
        self.ignore_tests = ignore_tests
        self.is_test_file = 'test' in file_path.lower()
        self.config = config or MagicNumberConfig()

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
        if self._should_skip_constant_check(node):
            return

        self._process_constant_node(node)

    def _should_skip_constant_check(self, node: ast.Constant) -> bool:
        """Check if constant checking should be skipped.

        Args:
            node: AST Constant node

        Returns:
            True if checking should be skipped
        """
        if self._should_skip_test_file():
            return True

        if self._should_skip_constant_definition():
            return True

        return self._should_skip_docstring(node)

    def _should_skip_test_file(self) -> bool:
        """Check if test file should be skipped.

        Returns:
            True if test file should be skipped
        """
        return self.ignore_tests and self.is_test_file

    def _should_skip_constant_definition(self) -> bool:
        """Check if constant definition should be skipped.

        Returns:
            True if in constant definition
        """
        return self.in_constant_definition

    def _should_skip_docstring(self, node: ast.Constant) -> bool:
        """Check if docstring should be skipped.

        Args:
            node: AST Constant node

        Returns:
            True if node is a docstring
        """
        return isinstance(node.value, str) and self._is_docstring(node)

    def _process_constant_node(self, node: ast.Constant) -> None:
        """Process a constant node for magic literal detection.

        Args:
            node: AST Constant node
        """
        if isinstance(node.value, (int, float)):
            self._check_magic_number(node)
        elif isinstance(node.value, str):
            self._check_magic_string(node)

    def _check_magic_number(self, node: ast.Constant) -> None:
        """Check if a number is a magic number."""
        # Type guard for int/float values
        if not isinstance(node.value, (int, float)):
            raise TypeError(f"Expected int or float, got {type(node.value)}")

        if node.value in self.config.allowed_numbers:
            return

        # Check for special contexts where numbers are OK
        if self._is_acceptable_context(node):
            return

        context = (
            f"in {self.current_function}"
            if self.current_function else "at module level"
        )
        violation = MagicNumberViolation(
            self.file_path,
            node.lineno,
            column=node.col_offset,
            value=node.value,
            context=context
        )
        self.violations.append(violation)

    def _check_magic_string(self, node: ast.Constant) -> None:
        """Check if a string is a magic string."""
        self._validate_string_type(node)

        if self._should_skip_string_check(node):
            return

        self._create_string_violation(node)

    def _validate_string_type(self, node: ast.Constant) -> None:
        """Validate that node contains a string value.

        Args:
            node: AST Constant node

        Raises:
            TypeError: If node value is not a string
        """
        if not isinstance(node.value, str):
            raise TypeError(f"Expected str, got {type(node.value)}")

    def _should_skip_string_check(self, node: ast.Constant) -> bool:
        """Check if string checking should be skipped.

        Args:
            node: AST Constant node

        Returns:
            True if checking should be skipped
        """
        return (self._is_short_string(node) or
                self._is_allowed_string_pattern(node) or
                self._is_test_related_string(node) or
                self._is_special_string_usage(node))

    def _is_short_string(self, node: ast.Constant) -> bool:
        """Check if string is too short to be considered magic.

        Args:
            node: AST Constant node

        Returns:
            True if string is short
        """
        if not isinstance(node.value, str):
            return False
        return len(node.value) <= 1

    def _is_allowed_string_pattern(self, node: ast.Constant) -> bool:
        """Check if string matches allowed patterns.

        Args:
            node: AST Constant node

        Returns:
            True if string is in allowed patterns
        """
        return node.value in self.config.allowed_string_patterns

    def _is_test_related_string(self, node: ast.Constant) -> bool:
        """Check if string is test-related.

        Args:
            node: AST Constant node

        Returns:
            True if string is test-related
        """
        if not isinstance(node.value, str):
            return False
        return node.value.startswith(('test', '__'))

    def _is_special_string_usage(self, node: ast.Constant) -> bool:
        """Check if string has special usage (key, docstring, etc.).

        Args:
            node: AST Constant node

        Returns:
            True if string has special usage
        """
        return self._is_string_key(node) or self._is_docstring(node)

    def _create_string_violation(self, node: ast.Constant) -> None:
        """Create a violation for a magic string.

        Args:
            node: AST Constant node
        """
        context = self._get_current_context()
        violation = MagicNumberViolation(
            self.file_path,
            node.lineno,
            column=node.col_offset,
            value=(node.value if isinstance(node.value, (int, float, str))
                   else str(node.value)),
            context=context
        )
        self.violations.append(violation)

    def _get_current_context(self) -> str:
        """Get the current context description.

        Returns:
            Context description string
        """
        return (
            f"in {self.current_function}"
            if self.current_function else "at module level"
        )

    def _is_acceptable_context(self, node: ast.Constant) -> bool:
        """Check if the context makes the literal acceptable."""
        parent = getattr(node, 'parent', None)
        if not parent:
            return False

        return (self._is_subscript_context(parent) or
                self._is_range_call_context(parent) or
                self._is_slice_context(parent))

    def _is_subscript_context(self, parent: ast.AST) -> bool:
        """Check if parent is a subscript (array/list index).

        Args:
            parent: Parent AST node

        Returns:
            True if parent is a subscript
        """
        return isinstance(parent, ast.Subscript)

    def _is_range_call_context(self, parent: ast.AST) -> bool:
        """Check if parent is a call to range or enumerate.

        Args:
            parent: Parent AST node

        Returns:
            True if parent is a range/enumerate call
        """
        if not isinstance(parent, ast.Call):
            return False

        return (hasattr(parent.func, 'id') and
                parent.func.id in ('range', 'enumerate'))

    def _is_slice_context(self, parent: ast.AST) -> bool:
        """Check if parent is a slice.

        Args:
            parent: Parent AST node

        Returns:
            True if parent is a slice
        """
        return isinstance(parent, ast.Slice)

    def _is_string_key(self, node: ast.Constant) -> bool:
        """Check if string is used as a dictionary key or similar."""
        parent = getattr(node, 'parent', None)
        if not parent:
            return False

        # Subscript strings (dict access) are OK
        if isinstance(parent, ast.Subscript):
            return True

        # Attribute access strings are OK
        if isinstance(parent, ast.Attribute):
            return True

        # Dictionary keys are generally OK
        if isinstance(parent, ast.Dict):
            return self._is_dict_key(parent, node)

        return False

    def _is_dict_key(self, dict_node: ast.Dict, node: ast.Constant) -> bool:
        """Check if node is a key in dict_node."""
        try:
            dict_node.keys.index(node)
            return True
        except (ValueError, AttributeError):
            return False

    def _is_docstring(self, node: ast.Constant) -> bool:
        """Check if string is a docstring."""
        parent = self._get_parent_expr(node)
        if not parent:
            return False

        grandparent = self._get_grandparent_container(parent)
        if not grandparent:
            return False

        body = self._get_container_body(grandparent)
        if not body:
            return False

        return self._is_first_string_statement(parent, body)

    def _get_parent_expr(self, node: ast.Constant) -> ast.Expr | None:
        """Get parent expression node if valid.

        Args:
            node: AST Constant node

        Returns:
            Parent expression node or None
        """
        parent = getattr(node, 'parent', None)
        if not parent or not isinstance(parent, ast.Expr):
            return None
        return cast(ast.Expr, parent)

    def _get_grandparent_container(self, parent: ast.Expr) -> Optional[ast.AST]:
        """Get grandparent container if it's a valid docstring container.

        Args:
            parent: Parent expression node

        Returns:
            Grandparent container or None
        """
        grandparent = getattr(parent, 'parent', None)
        if not grandparent:
            return None

        allowed_types = (
            ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module
        )
        if not isinstance(grandparent, allowed_types):
            return None

        return grandparent

    def _get_container_body(self, container: ast.AST) -> Optional[list]:
        """Get the body of a container node.

        Args:
            container: Container AST node

        Returns:
            Body list or None
        """
        body = getattr(container, 'body', None)
        return body if body else None

    def _is_first_string_statement(self, expr_node: ast.Expr, body: list) -> bool:
        """Check if an expression node is the first string statement in a body."""
        for stmt in body:
            if self._should_skip_statement(stmt):
                continue

            if self._is_target_expression(stmt, expr_node):
                return self._is_valid_string_constant(stmt)

            # If we hit any other statement type first, it's not a docstring
            return False

        return False

    def _should_skip_statement(self, stmt: ast.stmt) -> bool:
        """Check if statement should be skipped.

        Args:
            stmt: AST statement

        Returns:
            True if statement should be skipped
        """
        return isinstance(stmt, ast.Pass)

    def _is_target_expression(self, stmt: ast.stmt, target_expr: ast.Expr) -> bool:
        """Check if statement is the target expression.

        Args:
            stmt: AST statement
            target_expr: Target expression to find

        Returns:
            True if statement is the target expression
        """
        return isinstance(stmt, ast.Expr) and stmt == target_expr

    def _is_valid_string_constant(self, stmt: ast.Expr) -> bool:
        """Check if expression contains a valid string constant.

        Args:
            stmt: Expression statement

        Returns:
            True if expression contains a string constant
        """
        if not isinstance(stmt.value, ast.Constant):
            return False

        return isinstance(stmt.value.value, str)


def add_parent_refs(tree: ast.AST) -> None:
    """Add parent references to all nodes in the AST."""
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            setattr(child, 'parent', parent)


def analyze_file(file_path: str, ignore_tests: bool = True,
                 config: Optional[MagicNumberConfig] = None
                 ) -> List[MagicNumberViolation]:
    """Analyze a single Python file for magic numbers."""
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read())
            add_parent_refs(tree)
            detector = MagicNumberDetector(file_path, ignore_tests, config)
            detector.visit(tree)
            return detector.violations
        except SyntaxError as e:
            handle_syntax_error(file_path, e)
            return []


def analyze_directory(
        directory: str, exclude_patterns: Optional[List[str]] = None,
        ignore_tests: bool = True, config: Optional[MagicNumberConfig] = None
) -> List[MagicNumberViolation]:
    """Analyze all Python files in a directory."""
    exclude_patterns = exclude_patterns or [
        '__pycache__', '.git', 'venv', '.venv', 'migrations'
    ]
    violations = []

    for path in Path(directory).rglob('*.py'):
        # Skip excluded patterns
        if any(pattern in str(path) for pattern in exclude_patterns):
            continue

        file_violations = analyze_file(str(path), ignore_tests, config)
        violations.extend(file_violations)

    return violations


def main() -> None:
    """Main entry point."""
    args = _parse_magic_number_arguments()
    violations = _analyze_path(args)
    _output_magic_number_results(violations, args.json)
    _handle_magic_number_exit_code(violations, args.fail_on_violation)


def _parse_magic_number_arguments() -> argparse.Namespace:
    """Parse command line arguments for magic number detector.

    Returns:
        Parsed arguments namespace
    """
    parser = _create_magic_number_parser()
    _add_magic_number_arguments(parser)
    return parser.parse_args()


def _create_magic_number_parser() -> argparse.ArgumentParser:
    """Create the argument parser for magic number detector.

    Returns:
        Configured ArgumentParser
    """
    return argparse.ArgumentParser(
        description='Detect magic numbers and literals in Python code'
    )


def _add_magic_number_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments to the magic number parser.

    Args:
        parser: ArgumentParser to add arguments to
    """
    parser.add_argument('path', help='File or directory to analyze')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument(
        '--include-tests', action='store_true',
        help='Include test files in analysis'
    )
    parser.add_argument(
        '--fail-on-violation', action='store_true',
        help='Exit with non-zero code if violations found'
    )


def _analyze_path(args: argparse.Namespace) -> List[MagicNumberViolation]:
    """Analyze the specified path for magic numbers.

    Args:
        args: Parsed arguments

    Returns:
        List of violations found
    """
    ignore_tests = not args.include_tests

    if os.path.isfile(args.path):
        return analyze_file(args.path, ignore_tests=ignore_tests)

    return analyze_directory(args.path, ignore_tests=ignore_tests)


def _output_magic_number_results(violations: List[MagicNumberViolation],
                                 json_output: bool) -> None:
    """Output the analysis results.

    Args:
        violations: List of violations to output
        json_output: Whether to use JSON format
    """
    if json_output:
        _output_json_magic_numbers(violations)
    else:
        _output_text_magic_numbers(violations)


def _output_json_magic_numbers(violations: List[MagicNumberViolation]) -> None:
    """Output violations in JSON format.

    Args:
        violations: List of violations to output
    """
    print(json.dumps([v.to_dict() for v in violations], indent=2))


def _output_text_magic_numbers(violations: List[MagicNumberViolation]) -> None:
    """Output violations in text format.

    Args:
        violations: List of violations to output
    """
    if not violations:
        print("✅ No magic numbers detected!")
        return

    print(f"Found {len(violations)} magic numbers/literals:\n")
    _print_violation_details(violations)


def _print_violation_details(violations: List[MagicNumberViolation]) -> None:
    """Print detailed information about each violation.

    Args:
        violations: List of violations to print
    """
    for violation in violations:
        value_display = _format_violation_value(violation.value)
        print(f"⚠️  {violation.file_path}:{violation.line}:{violation.column}")
        print(f"   Value: {value_display}")
        print(f"   Context: {violation.context}")
        print(f"   Suggestion: Define as constant '{violation.suggestion}'")
        print()


def _format_violation_value(value: Union[int, float, str]) -> str:
    """Format the violation value for display.

    Args:
        value: The violation value

    Returns:
        Formatted value string
    """
    return f'"{value}"' if isinstance(value, str) else str(value)


def _handle_magic_number_exit_code(violations: List[MagicNumberViolation],
                                   fail_on_violation: bool) -> None:
    """Handle the exit code based on violations.

    Args:
        violations: List of violations found
        fail_on_violation: Whether to exit with error code on violations
    """
    if fail_on_violation and violations:
        sys.exit(1)


if __name__ == '__main__':
    main()
