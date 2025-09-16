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
from typing import List, Set, Union, Optional, Dict, Any
import argparse
import json
from abc import ABC, abstractmethod

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
                 value: Union[int, float, str, complex], context: str):
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
        if isinstance(self.value, str):
            # For strings, convert to constant format
            cleaned = self.value.upper().replace(' ', '_').replace('-', '_')[:30]
            return cleaned + "_CONSTANT"
        if isinstance(self.value, complex):
            # For complex numbers, create a descriptive name
            complex_str = str(self.value).replace('(', '').replace(')', '').replace('+', '_PLUS_').replace('j', 'J')
            return f"COMPLEX_{complex_str}"
        # For other types
        return f"{type(self.value).__name__.upper()}_CONSTANT"

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


# Strategy Pattern for Type Checking
class LiteralCheckStrategy(ABC):
    """Abstract base class for literal checking strategies."""

    @abstractmethod
    def can_handle(self, value: Any) -> bool:
        """Check if this strategy can handle the given value type."""
        raise NotImplementedError

    @abstractmethod
    def check(self, node: ast.Constant, detector: 'MagicNumberDetector') -> Optional[MagicNumberViolation]:
        """Check if the node contains a magic literal and return a violation if found."""
        raise NotImplementedError


class NumberCheckStrategy(LiteralCheckStrategy):
    """Strategy for checking numeric literals."""

    def can_handle(self, value: Any) -> bool:
        """Check if value is a number."""
        return isinstance(value, (int, float))

    def check(self, node: ast.Constant, detector: 'MagicNumberDetector') -> Optional[MagicNumberViolation]:
        """Check if a number is a magic number."""
        if not isinstance(node.value, (int, float)):
            return None

        if node.value in detector.config.allowed_numbers:
            return None

        # Check for special contexts where numbers are OK
        if detector._is_acceptable_context(node):
            return None

        context = (
            f"in {detector.current_function}"
            if detector.current_function else "at module level"
        )

        return MagicNumberViolation(
            detector.file_path,
            node.lineno,
            column=node.col_offset,
            value=node.value,
            context=context
        )


class StringCheckStrategy(LiteralCheckStrategy):
    """Strategy for checking string literals."""

    def can_handle(self, value: Any) -> bool:
        """Check if value is a string."""
        return isinstance(value, str)

    def check(self, node: ast.Constant, detector: 'MagicNumberDetector') -> Optional[MagicNumberViolation]:
        """Check if a string is a magic string."""
        if not isinstance(node.value, str) or not node.value:
            return None

        if self._should_skip_string(node, detector):
            return None

        context = (
            f"in {detector.current_function}"
            if detector.current_function else "at module level"
        )

        return MagicNumberViolation(
            detector.file_path,
            node.lineno,
            column=node.col_offset,
            value=node.value,
            context=context
        )

    def _should_skip_string(self, node: ast.Constant, detector: 'MagicNumberDetector') -> bool:
        """Check if string should be skipped based on various criteria."""
        return (self._is_allowed_pattern(node, detector) or
                self._is_url_or_path(node) or
                detector._is_acceptable_string_context(node))

    def _is_allowed_pattern(self, node: ast.Constant, detector: 'MagicNumberDetector') -> bool:
        """Check if string matches allowed patterns."""
        if not isinstance(node.value, str):
            return False
        return node.value.lower() in detector.config.allowed_string_patterns

    def _is_url_or_path(self, node: ast.Constant) -> bool:
        """Check if string is a URL or path."""
        if not isinstance(node.value, str):
            return False
        return any(node.value.startswith(prefix) for prefix in ['http://', 'https://', '/', './'])


class ComplexNumberCheckStrategy(LiteralCheckStrategy):
    """Strategy for checking complex number literals."""

    def can_handle(self, value: Any) -> bool:
        """Check if value is a complex number."""
        return isinstance(value, complex)

    def check(self, node: ast.Constant, detector: 'MagicNumberDetector') -> Optional[MagicNumberViolation]:
        """Check if a complex number is a magic literal."""
        if not isinstance(node.value, complex):
            return None

        # Complex numbers are usually domain-specific, so flag them
        context = (
            f"in {detector.current_function}"
            if detector.current_function else "at module level"
        )

        return MagicNumberViolation(
            detector.file_path,
            node.lineno,
            column=node.col_offset,
            value=node.value,
            context=context
        )


class BooleanCheckStrategy(LiteralCheckStrategy):
    """Strategy for checking boolean literals - usually allowed."""

    def can_handle(self, value: Any) -> bool:
        """Check if value is a boolean."""
        return isinstance(value, bool)

    def check(self, node: ast.Constant, detector: 'MagicNumberDetector') -> Optional[MagicNumberViolation]:
        """Booleans are typically allowed - no violation."""
        return None


class NoneCheckStrategy(LiteralCheckStrategy):
    """Strategy for checking None literals - always allowed."""

    def can_handle(self, value: Any) -> bool:
        """Check if value is None."""
        return value is None

    def check(self, node: ast.Constant, detector: 'MagicNumberDetector') -> Optional[MagicNumberViolation]:
        """None is always allowed - no violation."""
        return None


class LiteralCheckStrategyManager:
    """Manages literal checking strategies."""

    def __init__(self, strategies: Optional[List[LiteralCheckStrategy]] = None):
        """Initialize with default or custom strategies."""
        self.strategies = strategies or [
            NumberCheckStrategy(),
            StringCheckStrategy(),
            ComplexNumberCheckStrategy(),
            BooleanCheckStrategy(),
            NoneCheckStrategy(),
        ]

    def add_strategy(self, strategy: LiteralCheckStrategy) -> None:
        """Add a new strategy to the manager."""
        self.strategies.append(strategy)

    def check_literal(self, node: ast.Constant, detector: 'MagicNumberDetector') -> Optional[MagicNumberViolation]:
        """Check a literal using the appropriate strategy."""
        for strategy in self.strategies:
            if strategy.can_handle(node.value):
                return strategy.check(node, detector)
        return None


class MagicNumberDetector(ast.NodeVisitor):  # pylint: disable=too-many-instance-attributes
    """AST visitor that detects magic numbers and literals using strategy pattern."""

    def __init__(self, file_path: str, ignore_tests: bool = True,
                 config: Optional[MagicNumberConfig] = None,
                 strategy_manager: Optional[LiteralCheckStrategyManager] = None) -> None:
        self.file_path = file_path
        self.violations: List[MagicNumberViolation] = []
        self.current_function: Optional[str] = None
        self.in_constant_definition = False
        self.ignore_tests = ignore_tests
        self.is_test_file = 'test' in file_path.lower()
        self.config = config or MagicNumberConfig()
        self.strategy_manager = strategy_manager or LiteralCheckStrategyManager()

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
        """Check for magic numbers and strings using strategy pattern."""
        if self._should_skip_constant_check(node):
            return

        # Use strategy pattern to check the literal
        violation = self.strategy_manager.check_literal(node, self)
        if violation:
            self.violations.append(violation)

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

    def _is_docstring(self, node: ast.Constant) -> bool:
        """Check if a string constant is a docstring."""
        parent = getattr(node, 'parent', None)
        if parent is None:
            return False

        # Docstrings are the first statement in a function/class/module
        return (self._is_function_docstring(parent, node) or
                self._is_class_docstring(parent, node))

    def _is_function_docstring(self, parent: ast.AST, node: ast.Constant) -> bool:
        """Check if node is a function docstring."""
        return (isinstance(parent, ast.FunctionDef) and
                bool(parent.body) and isinstance(parent.body[0], ast.Expr) and
                parent.body[0].value == node)

    def _is_class_docstring(self, parent: ast.AST, node: ast.Constant) -> bool:
        """Check if node is a class docstring."""
        return (isinstance(parent, ast.ClassDef) and
                bool(parent.body) and isinstance(parent.body[0], ast.Expr) and
                parent.body[0].value == node)

    def _is_acceptable_context(self, node: ast.Constant) -> bool:
        """Check if the numeric constant is in an acceptable context."""
        parent = getattr(node, 'parent', None)
        if parent is None:
            return False

        return (self._is_range_parameter(parent) or
                self._is_acceptable_array_index(parent, node) or
                self._is_acceptable_arithmetic_value(parent, node))

    def _is_range_parameter(self, parent: ast.AST) -> bool:
        """Check if parent is a range() call."""
        return (isinstance(parent, ast.Call) and
                isinstance(parent.func, ast.Name) and
                parent.func.id == 'range')

    def _is_acceptable_array_index(self, parent: ast.AST, node: ast.Constant) -> bool:
        """Check if node is an acceptable array index."""
        return (isinstance(parent, ast.Subscript) and
                isinstance(node.value, int) and
                node.value in {0, 1, -1, -2})

    def _is_acceptable_arithmetic_value(self, parent: ast.AST, node: ast.Constant) -> bool:
        """Check if node is an acceptable arithmetic value."""
        return (isinstance(parent, ast.BinOp) and
                isinstance(node.value, (int, float)) and
                node.value in {2, 10, 100, 1000})

    def _is_acceptable_string_context(self, node: ast.Constant) -> bool:
        """Check if the string constant is in an acceptable context."""
        parent = getattr(node, 'parent', None)
        if parent is None:
            return False

        return (self._is_dictionary_access(parent) or
                self._is_dictionary_key(parent, node) or
                self._is_format_string(parent) or
                self._is_logging_call(parent))

    def _is_dictionary_access(self, parent: ast.AST) -> bool:
        """Check if parent is a dictionary subscript access."""
        return isinstance(parent, ast.Subscript)

    def _is_dictionary_key(self, parent: ast.AST, node: ast.Constant) -> bool:
        """Check if node is a dictionary key in a literal."""
        if not isinstance(parent, ast.Dict):
            return False
        return any(key == node for key in parent.keys)

    def _is_format_string(self, parent: ast.AST) -> bool:
        """Check if parent is a format string."""
        return isinstance(parent, ast.JoinedStr)

    def _is_logging_call(self, parent: ast.AST) -> bool:
        """Check if parent is a logging/print call."""
        return (isinstance(parent, ast.Call) and
                isinstance(parent.func, ast.Attribute) and
                parent.func.attr in {'debug', 'info', 'warning', 'error', 'critical', 'print'})


def add_parent_refs(tree: ast.AST) -> None:
    """Add parent references to AST nodes for backward compatibility with tests."""
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            setattr(child, 'parent', node)


def analyze_directory(directory_path: str, ignore_tests: bool = True,
                     config: Optional[MagicNumberConfig] = None) -> List[MagicNumberViolation]:
    """Analyze all Python files in a directory for magic numbers.

    Args:
        directory_path: Path to directory to analyze
        ignore_tests: Whether to skip test files/functions
        config: Optional configuration for detection

    Returns:
        List of MagicNumberViolation objects from all files
    """
    all_violations: List[MagicNumberViolation] = []
    path_obj = Path(directory_path)

    if path_obj.is_dir():
        for py_file in path_obj.rglob('*.py'):
            violations = analyze_file(str(py_file), ignore_tests, config)
            all_violations.extend(violations)

    return all_violations


def analyze_file(file_path: str, ignore_tests: bool = True,
                 config: Optional[MagicNumberConfig] = None) -> List[MagicNumberViolation]:
    """Analyze a single file for magic numbers.

    Args:
        file_path: Path to Python file to analyze
        ignore_tests: Whether to skip test files/functions
        config: Optional configuration for detection

    Returns:
        List of MagicNumberViolation objects
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())

        # Add parent references for context checking
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                setattr(child, 'parent', node)

        detector = MagicNumberDetector(file_path, ignore_tests, config)
        detector.visit(tree)
        return detector.violations

    except SyntaxError as e:
        handle_syntax_error(file_path, e)
        return []
    except OSError as e:
        print(f"Error analyzing {file_path}: {str(e)}")
        return []


def main() -> None:
    """CLI entry point."""
    args = _parse_arguments()
    config = _load_config(args.config)
    all_violations = _analyze_paths(args.paths, not args.include_tests, config)
    _output_results(all_violations, args.json)
    sys.exit(1 if all_violations else 0)


def _parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Detect magic numbers and literals in Python code'
    )
    parser.add_argument('paths', nargs='+', help='Files or directories to analyze')
    parser.add_argument('--include-tests', action='store_true',
                        help='Include test files and functions')
    parser.add_argument('--json', action='store_true',
                        help='Output results as JSON')
    parser.add_argument('--config', type=str,
                        help='Path to configuration file')
    return parser.parse_args()


def _load_config(config_path: Optional[str]) -> Optional[MagicNumberConfig]:
    """Load configuration from file if provided."""
    if not config_path or not os.path.exists(config_path):
        return None

    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
        return MagicNumberConfig(
            allowed_numbers=set(config_data.get('allowed_numbers', [])),
            allowed_string_patterns=set(config_data.get('allowed_strings', []))
        )


def _analyze_paths(paths: List[str], ignore_tests: bool,
                   config: Optional[MagicNumberConfig]) -> List[MagicNumberViolation]:
    """Analyze all provided paths for magic literals."""
    all_violations: List[MagicNumberViolation] = []

    for path in paths:
        path_obj = Path(path)
        if path_obj.is_file():
            violations = analyze_file(str(path_obj), ignore_tests, config)
            all_violations.extend(violations)
        elif path_obj.is_dir():
            for py_file in path_obj.rglob('*.py'):
                violations = analyze_file(str(py_file), ignore_tests, config)
                all_violations.extend(violations)

    return all_violations


def _output_results(violations: List[MagicNumberViolation], json_output: bool) -> None:
    """Output the analysis results."""
    if json_output:
        print(json.dumps([v.to_dict() for v in violations], indent=2))
    else:
        if violations:
            print(f"Found {len(violations)} magic literals:\n")
            for v in violations:
                print(f"{v.file_path}:{v.line}:{v.column} - "
                      f"{v.value} ({type(v.value).__name__}) {v.context}")
                print(f"  Suggestion: {v.suggestion}\n")
        else:
            print("No magic literals found!")


if __name__ == '__main__':
    main()
