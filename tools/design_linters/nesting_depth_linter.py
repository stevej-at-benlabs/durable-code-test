#!/usr/bin/env python3
"""
Purpose: Detects excessive nesting depth in Python code blocks
Scope: Python source files across the project for maintainability enforcement
Overview: This analyzer identifies functions and methods with nesting depth exceeding
    specified thresholds by traversing Python AST and tracking indentation levels.
    It counts both control flow structures (if/for/while/with/try) and their
    combinations to ensure code remains readable and maintainable. Unlike cyclomatic
    complexity which counts decision points, this tool measures the actual depth
    of nested blocks regardless of the number of branches.
Dependencies: ast for Python AST parsing, pathlib for file operations, argparse for CLI
Exports: NestingDepthAnalyzer class, NestingViolation dataclass
Interfaces: main() CLI function, analyze_file() returns List[NestingViolation]
Implementation: Uses AST visitor pattern with depth tracking to identify deep nesting
"""

import ast
import sys
from pathlib import Path
from typing import List, Optional, Tuple, cast
import argparse
import json
from dataclasses import dataclass
try:
    from .constants import handle_syntax_error, analyze_with_visitor
except ImportError:
    # For direct script execution
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from constants import (  # type: ignore[import-not-found,no-redef]
        handle_syntax_error, analyze_with_visitor
    )


@dataclass
class NestingViolation:
    """Represents a nesting depth violation."""

    file_path: str
    function_name: str
    line: int
    column: int
    max_depth: int
    threshold: int
    nested_constructs: List[str]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'file_path': self.file_path,
            'function_name': self.function_name,
            'line': self.line,
            'column': self.column,
            'max_depth': self.max_depth,
            'threshold': self.threshold,
            'nested_constructs': self.nested_constructs
        }


class NestingDepthAnalyzer(ast.NodeVisitor):  # pylint: disable=too-many-instance-attributes
    """Analyzes Python code for excessive nesting depth."""

    NESTING_NODES = (
        ast.If, ast.For, ast.While, ast.With,
        ast.Try, ast.ExceptHandler, ast.AsyncFor,
        ast.AsyncWith, ast.Match
    )

    def __init__(self, file_path: str, max_depth: int = 3):
        """
        Initialize the analyzer.

        Args:
            file_path: Path to the file being analyzed
            max_depth: Maximum allowed nesting depth (default: 3)
        """
        self.file_path = file_path
        self.max_depth = max_depth
        self.violations: List[NestingViolation] = []
        self.current_function: Optional[str] = None
        self.current_depth = 0
        self.max_seen_depth = 0
        self.depth_stack: List[Tuple[int, str]] = []
        self.nested_constructs: List[str] = []

    def _get_node_type_name(self, node: ast.AST) -> str:
        """Get human-readable name for AST node type."""
        type_map = {
            ast.If: 'if',
            ast.For: 'for',
            ast.While: 'while',
            ast.With: 'with',
            ast.Try: 'try',
            ast.ExceptHandler: 'except',
            ast.AsyncFor: 'async for',
            ast.AsyncWith: 'async with',
            ast.Match: 'match'
        }
        return type_map.get(type(node), type(node).__name__.lower())

    def _enter_nesting_level(self, node: ast.AST) -> None:
        """Track entering a new nesting level."""
        if isinstance(node, self.NESTING_NODES):
            self.current_depth += 1
            node_name = self._get_node_type_name(node)
            self.depth_stack.append((self.current_depth, node_name))

            if self.current_depth > self.max_seen_depth:
                self.max_seen_depth = self.current_depth
                self.nested_constructs = [name for _, name in self.depth_stack]

    def _exit_nesting_level(self, node: ast.AST) -> None:
        """Track exiting a nesting level."""
        if isinstance(node, self.NESTING_NODES):
            self.current_depth -= 1
            if self.depth_stack:
                self.depth_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition and check its nesting depth."""
        prev_function = self.current_function
        prev_depth = self.current_depth
        prev_max_depth = self.max_seen_depth
        prev_stack = self.depth_stack.copy()
        prev_constructs = self.nested_constructs.copy()

        self.current_function = node.name
        self.current_depth = 0
        self.max_seen_depth = 0
        self.depth_stack = []
        self.nested_constructs = []

        # Visit function body
        self.generic_visit(node)

        # Check for violation
        if self.max_seen_depth > self.max_depth:
            violation = NestingViolation(
                file_path=self.file_path,
                function_name=node.name,
                line=node.lineno,
                column=node.col_offset,
                max_depth=self.max_seen_depth,
                threshold=self.max_depth,
                nested_constructs=self.nested_constructs.copy()
            )
            self.violations.append(violation)

        # Restore previous state
        self.current_function = prev_function
        self.current_depth = prev_depth
        self.max_seen_depth = prev_max_depth
        self.depth_stack = prev_stack
        self.nested_constructs = prev_constructs

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Handle async functions the same way as regular functions."""
        self.visit_FunctionDef(node)  # type: ignore[arg-type]

    def visit_If(self, node: ast.If) -> None:
        """Visit if statement."""
        self._enter_nesting_level(node)
        self.generic_visit(node)
        self._exit_nesting_level(node)

    def visit_For(self, node: ast.For) -> None:
        """Visit for loop."""
        self._enter_nesting_level(node)
        self.generic_visit(node)
        self._exit_nesting_level(node)

    def visit_While(self, node: ast.While) -> None:
        """Visit while loop."""
        self._enter_nesting_level(node)
        self.generic_visit(node)
        self._exit_nesting_level(node)

    def visit_With(self, node: ast.With) -> None:
        """Visit with statement."""
        self._enter_nesting_level(node)
        self.generic_visit(node)
        self._exit_nesting_level(node)

    def visit_Try(self, node: ast.Try) -> None:
        """Visit try statement."""
        self._enter_nesting_level(node)
        self.generic_visit(node)
        self._exit_nesting_level(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        """Visit except handler."""
        self._enter_nesting_level(node)
        self.generic_visit(node)
        self._exit_nesting_level(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        """Visit async for loop."""
        self._enter_nesting_level(node)
        self.generic_visit(node)
        self._exit_nesting_level(node)

    def visit_AsyncWith(self, node: ast.AsyncWith) -> None:
        """Visit async with statement."""
        self._enter_nesting_level(node)
        self.generic_visit(node)
        self._exit_nesting_level(node)

    def visit_Match(self, node: ast.Match) -> None:
        """Visit match statement (Python 3.10+)."""
        if hasattr(ast, 'Match'):  # Check for Python 3.10+
            self._enter_nesting_level(node)
            self.generic_visit(node)
            self._exit_nesting_level(node)


def analyze_file(file_path: Path, max_depth: int = 3) -> List[NestingViolation]:
    """
    Analyze a single Python file for nesting depth violations.

    Args:
        file_path: Path to the Python file
        max_depth: Maximum allowed nesting depth

    Returns:
        List of NestingViolation objects
    """
    try:
        return cast(List[NestingViolation],
                   analyze_with_visitor(str(file_path), NestingDepthAnalyzer,
                                       max_depth))
    except SyntaxError as e:
        handle_syntax_error(str(file_path), e)
        return []
    except (OSError, UnicodeDecodeError) as e:
        print(f"Error analyzing {file_path}: {e}", file=sys.stderr)
        return []


def analyze_directory(directory: Path, max_depth: int = 3,
                      recursive: bool = True) -> List[NestingViolation]:
    """
    Analyze all Python files in a directory for nesting depth violations.

    Args:
        directory: Directory to analyze
        max_depth: Maximum allowed nesting depth
        recursive: Whether to analyze subdirectories

    Returns:
        List of all violations found
    """
    all_violations = []
    pattern = '**/*.py' if recursive else '*.py'

    for py_file in directory.glob(pattern):
        # Skip test files and other excluded patterns
        exclude_parts = ['__pycache__', '.git', 'venv', '.venv']
        if any(part in py_file.parts for part in exclude_parts):
            continue

        violations = analyze_file(py_file, max_depth)
        all_violations.extend(violations)

    return all_violations


def format_violation(violation: NestingViolation, format_type: str = 'text') -> str:
    """
    Format a violation for output.

    Args:
        violation: The violation to format
        format_type: Output format ('text' or 'json')

    Returns:
        Formatted string
    """
    if format_type == 'json':
        return json.dumps(violation.to_dict())

    constructs = ' -> '.join(violation.nested_constructs)
    return (
        f"{violation.file_path}:{violation.line}:{violation.column}: "
        f"Function '{violation.function_name}' has nesting depth of "
        f"{violation.max_depth} (max allowed: {violation.threshold})\n"
        f"  Nesting chain: {constructs}"
    )


def main() -> None:
    """Main CLI entry point."""
    args = _parse_nesting_arguments()
    _validate_nesting_path(args.path)
    violations = _analyze_nesting_target(args)
    _output_nesting_results(violations, args)
    _handle_nesting_exit(violations, args.exit_zero)


def _parse_nesting_arguments() -> argparse.Namespace:
    """Parse command line arguments for nesting depth analyzer.

    Returns:
        Parsed arguments namespace
    """
    parser = _create_nesting_parser()
    _add_nesting_arguments(parser)
    return parser.parse_args()


def _create_nesting_parser() -> argparse.ArgumentParser:
    """Create the argument parser for nesting depth analyzer.

    Returns:
        Configured ArgumentParser
    """
    return argparse.ArgumentParser(
        description='Analyze Python code for excessive nesting depth'
    )


def _add_nesting_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments to the nesting depth parser.

    Args:
        parser: ArgumentParser to add arguments to
    """
    parser.add_argument(
        'path', type=Path, help='File or directory to analyze'
    )
    parser.add_argument(
        '--max-depth', type=int, default=3,
        help='Maximum allowed nesting depth (default: 3)'
    )
    parser.add_argument(
        '--format', choices=['text', 'json'], default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '--no-recursive', action='store_true',
        help='Do not analyze subdirectories'
    )
    parser.add_argument(
        '--exit-zero', action='store_true',
        help='Always exit with code 0'
    )


def _validate_nesting_path(path: Path) -> None:
    """Validate the provided path exists.

    Args:
        path: Path to validate

    Raises:
        SystemExit: If path doesn't exist
    """
    if not path.exists():
        print(f"Error: Path '{path}' does not exist", file=sys.stderr)
        sys.exit(1)


def _analyze_nesting_target(args: argparse.Namespace) -> List[NestingViolation]:
    """Analyze the target for nesting violations.

    Args:
        args: Parsed arguments

    Returns:
        List of violations found
    """
    if args.path.is_file():
        return _analyze_nesting_file(args.path, args.max_depth)

    return analyze_directory(
        args.path, args.max_depth, recursive=not args.no_recursive
    )


def _analyze_nesting_file(path: Path, max_depth: int) -> List[NestingViolation]:
    """Analyze a single file for nesting violations.

    Args:
        path: Path to the file
        max_depth: Maximum allowed nesting depth

    Returns:
        List of violations found

    Raises:
        SystemExit: If file is not a Python file
    """
    if path.suffix != '.py':
        print(f"Error: '{path}' is not a Python file", file=sys.stderr)
        sys.exit(1)

    return analyze_file(path, max_depth)


def _output_nesting_results(violations: List[NestingViolation],
                           args: argparse.Namespace) -> None:
    """Output the analysis results.

    Args:
        violations: List of violations to output
        args: Parsed arguments
    """
    if not violations:
        print("No nesting depth violations found")
        return

    if args.format == 'json':
        _output_json_nesting(violations)
    else:
        _output_text_nesting(violations)


def _output_json_nesting(violations: List[NestingViolation]) -> None:
    """Output violations in JSON format.

    Args:
        violations: List of violations to output
    """
    output = json.dumps([v.to_dict() for v in violations], indent=2)
    print(output)


def _output_text_nesting(violations: List[NestingViolation]) -> None:
    """Output violations in text format.

    Args:
        violations: List of violations to output
    """
    for violation in violations:
        print(format_violation(violation, 'text'))
    print(f"\nFound {len(violations)} nesting depth violation(s)")


def _handle_nesting_exit(violations: List[NestingViolation],
                        exit_zero: bool) -> None:
    """Handle the exit code based on violations.

    Args:
        violations: List of violations found
        exit_zero: Whether to always exit with code 0
    """
    if violations and not exit_zero:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
