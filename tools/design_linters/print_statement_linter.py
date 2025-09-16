#!/usr/bin/env python3
"""
Purpose: Detects and reports print statements, console.log, alert, and debugger
    statements
Scope: Python, JavaScript, TypeScript source files across the entire project
Overview: This linter enforces proper logging standards by detecting print statements,
    console.log, alert, and debugger statements in production code. It analyzes
    Python,
    JavaScript, and TypeScript files to ensure developers use proper logging libraries
    (like loguru for Python) instead of debug statements that can leak sensitive
    information
    or degrade performance. The tool helps maintain clean, production-ready code.
Dependencies: ast for Python AST parsing, pathlib for file operations, re for
    pattern matching
Exports: PrintStatementLinter class, PrintViolation class, ViolationType enum
Interfaces: main() CLI function, analyze_file() returns List[PrintViolation]
Implementation: Uses AST parsing for Python and regex patterns for JavaScript/TypeScript
"""

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Tuple


class PrintViolation(NamedTuple):
    """Represents a print statement violation."""
    file_path: Path
    line_number: int
    column: int
    statement: str
    context: str
    language: str
    severity: str  # 'error', 'warning', 'info'


class PatternRegistry:
    """Registry for print statement patterns - follows OCP by allowing extension."""

    def __init__(self) -> None:
        self.language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.mjs': 'javascript',
            '.cjs': 'javascript',
        }

        self.print_patterns = {
            'python': [
                (r'\bprint\s*\(', 'print()'),
                (r'\bpprint\s*\(', 'pprint()'),
                (r'\bpp\s*\(', 'pp()'),  # common pprint alias
            ],
            'javascript': [
                (r'\bconsole\s*\.\s*log\s*\(', 'console.log()'),
                (r'\bconsole\s*\.\s*debug\s*\(', 'console.debug()'),
                (r'\bconsole\s*\.\s*info\s*\(', 'console.info()'),
                (r'\bconsole\s*\.\s*warn\s*\(', 'console.warn()'),
                (r'\bconsole\s*\.\s*error\s*\(', 'console.error()'),
                (r'\bconsole\s*\.\s*trace\s*\(', 'console.trace()'),
                (r'\bconsole\s*\.\s*dir\s*\(', 'console.dir()'),
                (r'\bconsole\s*\.\s*table\s*\(', 'console.table()'),
                (r'\bconsole\s*\.\s*time\s*\(', 'console.time()'),
                (r'\bconsole\s*\.\s*timeEnd\s*\(', 'console.timeEnd()'),
                (r'\balert\s*\(', 'alert()'),
                (r'\bdebugger\b', 'debugger'),
            ],
            'typescript': [
                (r'\bconsole\s*\.\s*log\s*\(', 'console.log()'),
                (r'\bconsole\s*\.\s*debug\s*\(', 'console.debug()'),
                (r'\bconsole\s*\.\s*info\s*\(', 'console.info()'),
                (r'\bconsole\s*\.\s*warn\s*\(', 'console.warn()'),
                (r'\bconsole\s*\.\s*error\s*\(', 'console.error()'),
                (r'\bconsole\s*\.\s*trace\s*\(', 'console.trace()'),
                (r'\bconsole\s*\.\s*dir\s*\(', 'console.dir()'),
                (r'\bconsole\s*\.\s*table\s*\(', 'console.table()'),
                (r'\bconsole\s*\.\s*time\s*\(', 'console.time()'),
                (r'\bconsole\s*\.\s*timeEnd\s*\(', 'console.timeEnd()'),
                (r'\balert\s*\(', 'alert()'),
                (r'\bdebugger\b', 'debugger'),
            ]
        }

    def add_language(self, extension: str, language: str) -> None:
        """Add a new language mapping without modifying the class."""
        self.language_map[extension] = language

    def add_pattern(self, language: str, pattern: str, description: str) -> None:
        """Add a new pattern for a language without modifying the class."""
        if language not in self.print_patterns:
            self.print_patterns[language] = []
        self.print_patterns[language].append((pattern, description))

    def get_language(self, extension: str) -> Optional[str]:
        """Get the language for a file extension."""
        return self.language_map.get(extension)

    def get_patterns(self, language: str) -> List[Tuple[str, str]]:
        """Get patterns for a language."""
        return self.print_patterns.get(language, [])


class PrintStatementLinter:
    """Linter to detect print statements in code."""

    # Directories to skip (excluding test directories - they should also use logging)
    SKIP_DIRS = {
        'node_modules', '__pycache__', '.git', '.venv', 'venv',
        'dist', 'build', 'coverage', '.pytest_cache', '.tox',
        'design_linters'  # Skip linter tools themselves (meta-tools exception)
    }

    # File patterns to skip (excluding test files - they should also use logging)
    SKIP_FILES = {
        '*.min.js', '*.min.css', '*.map', 'setup.py'
    }

    def __init__(self,
                 allow_logging: bool = False,
                 allow_in_tests: bool = True,
                 pattern_registry: Optional[PatternRegistry] = None):
        """Initialize the linter.

        Args:
            allow_logging: If True, allow logging statements (warn/error)
            allow_in_tests: If True, allow print statements in test files
            pattern_registry: Custom pattern registry (defaults to standard patterns)
        """
        self.allow_logging = allow_logging
        self.allow_in_tests = allow_in_tests
        self.pattern_registry = pattern_registry or PatternRegistry()
        self.violations: List[PrintViolation] = []

    def should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        if self._should_skip_by_file_pattern(file_path):
            return True

        if self._should_skip_by_directory(file_path):
            return True

        if self._should_skip_test_file(file_path):
            return True

        if self._should_skip_non_source_file(file_path):
            return True

        return False

    def _should_skip_by_file_pattern(self, file_path: Path) -> bool:
        """Check if file should be skipped based on file patterns.

        Args:
            file_path: Path to check

        Returns:
            True if file matches skip patterns
        """
        for pattern in self.SKIP_FILES:
            if file_path.match(pattern):
                return True
        return False

    def _should_skip_by_directory(self, file_path: Path) -> bool:
        """Check if file should be skipped based on its directory.

        Args:
            file_path: Path to check

        Returns:
            True if file is in a skip directory
        """
        for parent in file_path.parents:
            if parent.name in self.SKIP_DIRS:
                return True
        return False

    def _should_skip_test_file(self, file_path: Path) -> bool:
        """Check if test file should be skipped.

        Args:
            file_path: Path to check

        Returns:
            True if file is a test file and should be skipped
        """
        if not self.allow_in_tests:
            return False

        if self._matches_test_file_pattern(file_path):
            return True

        return self._is_in_test_directory(file_path)

    def _matches_test_file_pattern(self, file_path: Path) -> bool:
        """Check if file matches test file patterns.

        Args:
            file_path: Path to check

        Returns:
            True if file matches test patterns
        """
        test_patterns = [
            '*test*.py', '*test*.js', '*test*.ts', '*.test.*', '*.spec.*',
            'test_*.py', '*_test.py', 'conftest.py'
        ]
        for pattern in test_patterns:
            if file_path.match(pattern):
                return True
        return False

    def _is_in_test_directory(self, file_path: Path) -> bool:
        """Check if file is in a test directory.

        Args:
            file_path: Path to check

        Returns:
            True if file is in a test directory
        """
        test_dirs = {'test', 'tests', '__tests__', 'test_*', '*_test'}
        for parent in file_path.parents:
            if (parent.name in test_dirs or
                parent.match('test_*') or
                parent.match('*_test')):
                return True
        return False

    def _should_skip_non_source_file(self, file_path: Path) -> bool:
        """Check if file should be skipped because it's not a source file.

        Args:
            file_path: Path to check

        Returns:
            True if file is not a supported source file
        """
        return self.pattern_registry.get_language(file_path.suffix) is None

    def detect_language(self, file_path: Path) -> Optional[str]:
        """Detect the programming language of a file."""
        suffix = file_path.suffix.lower()
        return self.pattern_registry.get_language(suffix)

    def lint_python_file(self, file_path: Path, content: str) -> List[PrintViolation]:
        """Lint a Python file using AST parsing."""
        # Check for file-level disable
        if self._is_file_disabled(content, 'python'):
            return []

        try:
            tree = ast.parse(content, filename=str(file_path))
            lines = content.split('\n')
            return self._extract_violations_from_ast(tree, lines, file_path, content)
        except SyntaxError:
            # Fall back to regex if AST parsing fails
            return self.lint_with_regex(file_path, content, 'python')

    def _extract_violations_from_ast(self, tree: ast.AST, lines: List[str],
                                     file_path: Path,
                                     content: str) -> List[PrintViolation]:
        """Extract violations from AST nodes."""
        violations = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            violation = self._check_ast_call_node(node, lines, file_path, content)
            if violation:
                violations.append(violation)

        return violations

    def _check_ast_call_node(self, node: ast.Call, lines: List[str],
                           file_path: Path, content: str) -> Optional[PrintViolation]:
        """Check a single AST call node for print violations."""
        if not isinstance(node.func, ast.Name):
            return None

        # Check if this line is disabled
        if self._is_line_disabled(lines, node.lineno, 'python'):
            return None

        # Check for print/pprint functions
        if node.func.id in ('print', 'pprint'):
            return PrintViolation(
                file_path=file_path,
                line_number=node.lineno,
                column=node.col_offset,
                statement=f"{node.func.id}()",
                context=self._get_line_context(content, node.lineno),
                language='python',
                severity='error'
            )

        # Check for pp (pprint alias)
        if node.func.id == 'pp':
            return PrintViolation(
                file_path=file_path,
                line_number=node.lineno,
                column=node.col_offset,
                statement='pp()',
                context=self._get_line_context(content, node.lineno),
                language='python',
                severity='warning'
            )

        # Check custom patterns from pattern registry
        patterns = self.pattern_registry.get_patterns('python')
        for pattern_str, description in patterns:
            # Check if this function name matches any custom pattern
            # Pattern format is typically: \bFUNCNAME\s*\(
            # So we check if the function name is in the pattern
            if f'\\b{node.func.id}\\s*\\(' in pattern_str:
                return PrintViolation(
                    file_path=file_path,
                    line_number=node.lineno,
                    column=node.col_offset,
                    statement=description,
                    context=self._get_line_context(content, node.lineno),
                    language='python',
                    severity='warning'
                )

        return None

    def lint_with_regex(self, file_path: Path, content: str,
                        language: str) -> List[PrintViolation]:
        """Lint a file using regex patterns.

        Args:
            file_path: Path to the file
            content: File content
            language: Programming language
            custom_only: If True, only check custom patterns
        """
        # Check for file-level disable
        if self._is_file_disabled(content, language):
            return []

        patterns = self.pattern_registry.get_patterns(language)
        lines = content.split('\n')
        violations = []

        for line_num, line in enumerate(lines, 1):
            # Skip comments and disabled lines
            if self._should_skip_line(line, lines, line_num, language):
                continue

            violations.extend(self._check_line_patterns(
                line, line_num, patterns, file_path=file_path, language=language))

        return violations

    def _should_skip_line(self, line: str, lines: List[str], line_num: int,
                          language: str) -> bool:
        """Check if a line should be skipped during regex linting."""
        return (self._is_comment(line, language) or
                self._is_line_disabled(lines, line_num, language))

    def _check_line_patterns(self, line: str, line_num: int,
                             patterns: List[Tuple[str, str]], *,
                             file_path: Path, language: str) -> List[PrintViolation]:
        """Check a line against all patterns and return violations."""
        violations = []

        for pattern, statement_type in patterns:
            violation = self._check_single_pattern(
                line, line_num, pattern, statement_type,
                file_path=file_path, language=language
            )
            if violation:
                violations.append(violation)

        return violations

    def _check_single_pattern(
            self, line: str, line_num: int, pattern: str, statement_type: str, *,
            file_path: Path, language: str
    ) -> Optional[PrintViolation]:
        """Check a line against a single pattern.

        Args:
            line: Line content
            line_num: Line number
            pattern: Regex pattern to match
            statement_type: Type of statement (e.g., 'print()', 'console.log()')
            file_path: Path to the file
            language: Programming language

        Returns:
            PrintViolation if pattern matches and is not allowed, None otherwise
        """
        match = re.search(pattern, line)
        if not match:
            return None

        if self._is_allowed_statement(line, language):
            return None

        return self._create_print_violation(
            file_path, line_num, match,
            statement_type=statement_type, line=line, language=language
        )

    def _is_allowed_statement(self, line: str, language: str) -> bool:
        """Check if the statement in the line is allowed.

        Args:
            line: Line content
            language: Programming language

        Returns:
            True if statement is allowed (e.g., allowed logging)
        """
        return self.allow_logging and self._is_allowed_logging(line, language)

    def _create_print_violation(self, file_path: Path, line_num: int,
                               match: re.Match, *,
                               statement_type: str, line: str,
                               language: str) -> PrintViolation:
        """Create a PrintViolation object.

        Args:
            file_path: Path to the file
            line_num: Line number
            match: Regex match object
            statement_type: Type of statement
            line: Line content
            language: Programming language

        Returns:
            PrintViolation object
        """
        return PrintViolation(
            file_path=file_path,
            line_number=line_num,
            column=line.index(match.group()),
            statement=statement_type,
            context=line.strip(),
            language=language,
            severity=self._determine_severity(statement_type)
        )

    def _determine_severity(self, statement_type: str) -> str:
        """Determine the severity of a violation.

        Args:
            statement_type: Type of statement

        Returns:
            Severity level ('error' or 'warning')
        """
        return 'error' if 'debugger' in statement_type else 'warning'

    def lint_file(self, file_path: Path) -> List[PrintViolation]:
        """Lint a single file."""
        if self.should_skip_file(file_path):
            self.violations = []
            return []

        language = self.detect_language(file_path)
        if not language:
            self.violations = []
            return []

        try:
            content = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, FileNotFoundError):
            self.violations = []
            return []

        # Use AST for Python, regex for others
        if language == 'python':
            violations = self.lint_python_file(file_path, content)
        else:
            violations = self.lint_with_regex(file_path, content,
                                               language)

        self.violations = violations
        return violations

    def lint_directory(self, directory: Path,
                       recursive: bool = True) -> List[PrintViolation]:
        """Lint all files in a directory."""
        violations = []

        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"

        for file_path in directory.glob(pattern):
            if file_path.is_file():
                violations.extend(self.lint_file(file_path))

        self.violations = violations
        return violations

    def _get_line_context(self, content: str, line_number: int) -> str:
        """Get the context of a specific line."""
        lines = content.split('\n')
        if 0 < line_number <= len(lines):
            return lines[line_number - 1].strip()
        return ""

    def _is_comment(self, line: str, language: str) -> bool:
        """Check if a line is a comment."""
        stripped = line.strip()

        if language == 'python':
            return stripped.startswith('#')
        if language in ('javascript', 'typescript'):
            return (stripped.startswith('//') or stripped.startswith('/*') or
                    stripped.startswith('*'))

        return False

    def _is_allowed_logging(self, line: str, language: str) -> bool:
        """Check if a line contains allowed logging statements."""
        if not self.allow_logging:
            return False

        allowed_patterns = {
            'javascript': [r'console\s*\.\s*(warn|error)\s*\('],
            'typescript': [r'console\s*\.\s*(warn|error)\s*\('],
            'python': [r'logging\.(debug|info|warning|error|critical)\s*\(']
        }

        patterns = allowed_patterns.get(language, [])
        for pattern in patterns:
            if re.search(pattern, line):
                return True

        return False

    def _is_file_disabled(self, content: str, language: str) -> bool:
        """Check if the entire file has print linting disabled."""
        # Check first few lines for file-level disable comments
        lines = content.split('\n')[:10]  # Check first 10 lines

        for line in lines:
            if self._has_python_disable_comment(line, language):
                return True
            if self._has_js_disable_comment(line, language):
                return True

        return False

    def _has_python_disable_comment(self, line: str, language: str) -> bool:
        """Check if line has Python disable comment."""
        if language != 'python':
            return False

        python_patterns = [
            r'#\s*print-linter:\s*disable',
            r'#\s*noqa:\s*print',
            r'#\s*type:\s*ignore\[print\]'
        ]

        for pattern in python_patterns:
            flags = re.IGNORECASE if 'type:' not in pattern else 0
            if re.search(pattern, line, flags):
                return True

        return False

    def _has_js_disable_comment(self, line: str, language: str) -> bool:
        """Check if line has JavaScript/TypeScript disable comment."""
        if language not in ('javascript', 'typescript'):
            return False

        js_patterns = [
            r'//\s*print-linter:\s*disable',
            r'/\*\s*print-linter:\s*disable\s*\*/',
            r'//\s*eslint-disable.*console',
            r'/\*\s*eslint-disable.*console\s*\*/'
        ]

        for pattern in js_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True

        return False

    def _is_line_disabled(self, lines: List[str], line_num: int, language: str) -> bool:
        """Check if a specific line has print linting disabled."""
        if line_num < 1 or line_num > len(lines):
            return False

        line = lines[line_num - 1]

        # Check for inline disable comments on current line
        if self._has_inline_disable_comment(line, language):
            return True

        # Check previous line for next-line disable comments
        if line_num > 1:
            prev_line = lines[line_num - 2]
            return self._has_next_line_disable_comment(prev_line, language)

        return False

    def _has_inline_disable_comment(self, line: str, language: str) -> bool:
        """Check if line has inline disable comments."""
        if language == 'python':
            return self._has_python_inline_disable(line)
        if language in ('javascript', 'typescript'):
            return self._has_js_inline_disable(line)
        return False

    def _has_python_inline_disable(self, line: str) -> bool:
        """Check for Python inline disable patterns."""
        patterns = [
            r'#\s*noqa(?:\s|:|$)',
            r'#\s*type:\s*ignore',
            r'#\s*pylint:\s*disable',
            r'#\s*print-linter:\s*ignore'
        ]

        for pattern in patterns:
            flags = re.IGNORECASE if 'print-linter' in pattern else 0
            if re.search(pattern, line, flags):
                return True
        return False

    def _has_js_inline_disable(self, line: str) -> bool:
        """Check for JavaScript/TypeScript inline disable patterns."""
        patterns = [
            r'//\s*eslint-disable-line',
            r'//\s*print-linter:\s*ignore',
            r'/\*\s*eslint-disable-line\s*\*/'
        ]

        for pattern in patterns:
            flags = re.IGNORECASE if 'print-linter' in pattern else 0
            if re.search(pattern, line, flags):
                return True
        return False

    def _has_next_line_disable_comment(self, prev_line: str, language: str) -> bool:
        """Check if previous line has next-line disable comments."""
        if language == 'python':
            return self._has_python_next_line_disable(prev_line)
        if language in ('javascript', 'typescript'):
            return self._has_js_next_line_disable(prev_line)
        return False

    def _has_python_next_line_disable(self, line: str) -> bool:
        """Check for Python next-line disable patterns."""
        patterns = [
            (r'#\s*noqa:\s*next', re.IGNORECASE),
            (r'#\s*pylint:\s*disable-next', 0),
            (r'#\s*print-linter:\s*ignore-next', re.IGNORECASE)
        ]

        for pattern, flags in patterns:
            if re.search(pattern, line, flags):
                return True
        return False

    def _has_js_next_line_disable(self, line: str) -> bool:
        """Check for JavaScript/TypeScript next-line disable patterns."""
        patterns = [
            r'//\s*eslint-disable-next-line',
            r'//\s*print-linter:\s*ignore-next',
            r'/\*\s*eslint-disable-next-line\s*\*/'
        ]

        for pattern in patterns:
            flags = re.IGNORECASE if 'print-linter' in pattern else 0
            if re.search(pattern, line, flags):
                return True
        return False

    def generate_report(self, output_format: str = 'text') -> str:
        """Generate a report of violations.

        Args:
            output_format: Output format ('text', 'json', 'github')
        """
        if output_format == 'json':
            return self._generate_json_report()
        if output_format == 'github':
            return self._generate_github_report()
        return self._generate_text_report()

    def _generate_text_report(self) -> str:
        """Generate a text report."""
        if not self.violations:
            return "✅ No print statements found!"

        report = self._create_report_header()
        report.extend(self._create_report_body())
        report.append("\n" + "=" * 60)
        return "\n".join(report)

    def _create_report_header(self) -> List[str]:
        """Create the header section of the report.

        Returns:
            List of header lines
        """
        return [
            "=" * 60,
            "PRINT STATEMENT LINTING REPORT",
            "=" * 60,
            f"Total violations: {len(self.violations)}",
            ""
        ]

    def _create_report_body(self) -> List[str]:
        """Create the body section of the report with violations.

        Returns:
            List of body lines
        """
        by_file = self._group_violations_by_file()
        report_lines = []

        for file_path, file_violations in by_file.items():
            report_lines.extend(self._create_file_section(file_path, file_violations))

        return report_lines

    def _group_violations_by_file(self) -> Dict[Path, List[PrintViolation]]:
        """Group violations by file path.

        Returns:
            Dictionary mapping file paths to lists of violations
        """
        by_file: Dict[Path, List[PrintViolation]] = {}
        for violation in self.violations:
            if violation.file_path not in by_file:
                by_file[violation.file_path] = []
            by_file[violation.file_path].append(violation)
        return by_file

    def _create_file_section(self, file_path: Path,
                            file_violations: List[PrintViolation]) -> List[str]:
        """Create a section for a single file's violations.

        Args:
            file_path: Path to the file
            file_violations: List of violations in the file

        Returns:
            List of lines for this file's section
        """
        lines = [f"\n📄 {file_path}"]

        for violation in file_violations:
            lines.extend(self._create_violation_lines(violation))

        return lines

    def _create_violation_lines(self, violation: PrintViolation) -> List[str]:
        """Create lines for a single violation.

        Args:
            violation: The violation to format

        Returns:
            List of lines for this violation
        """
        severity_icon = "❌" if violation.severity == 'error' else "⚠️"
        return [
            f"  {severity_icon} Line {violation.line_number}: {violation.statement}",
            f"     {violation.context}"
        ]

    def _generate_json_report(self) -> str:
        """Generate a JSON report."""
        data = {
            'total_violations': len(self.violations),
            'violations': [
                {
                    'file': str(v.file_path),
                    'line': v.line_number,
                    'column': v.column,
                    'statement': v.statement,
                    'context': v.context,
                    'language': v.language,
                    'severity': v.severity
                }
                for v in self.violations
            ]
        }
        return json.dumps(data, indent=2)

    def _generate_github_report(self) -> str:
        """Generate GitHub Actions annotation format."""
        annotations = []
        for v in self.violations:
            level = 'error' if v.severity == 'error' else 'warning'
            annotations.append(
                f"::{level} file={v.file_path},line={v.line_number},col={v.column}"
                f"::Found {v.statement} statement"
            )
        return "\n".join(annotations)


def main() -> int:
    """Main entry point."""
    args = _parse_main_arguments()
    linter = _create_linter(args)
    violations = _run_linting(args, linter)
    _output_report(linter, args)
    return _determine_main_exit_code(violations, args)


def _parse_main_arguments() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = _create_argument_parser()
    _add_main_arguments(parser)
    return parser.parse_args()


def _create_argument_parser() -> argparse.ArgumentParser:
    """Create the argument parser.

    Returns:
        Configured ArgumentParser
    """
    return argparse.ArgumentParser(
        description="Detect print statements in production code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python print_statement_linter.py --path src/
  python print_statement_linter.py --path . --recursive
  python print_statement_linter.py --file app.py --format json
        """
    )


def _add_main_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments to the parser.

    Args:
        parser: ArgumentParser to add arguments to
    """
    _add_input_arguments(parser)
    _add_behavior_arguments(parser)
    _add_output_arguments(parser)


def _add_input_arguments(parser: argparse.ArgumentParser) -> None:
    """Add input-related arguments.

    Args:
        parser: ArgumentParser to add arguments to
    """
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--path', type=Path, help='Directory to lint')
    group.add_argument('--file', type=Path, help='Single file to lint')

    parser.add_argument(
        '--recursive',
        action='store_true',
        default=True,
        help='Recursively scan directories (default: True)'
    )


def _add_behavior_arguments(parser: argparse.ArgumentParser) -> None:
    """Add behavior-related arguments.

    Args:
        parser: ArgumentParser to add arguments to
    """
    parser.add_argument(
        '--allow-logging',
        action='store_true',
        help='Allow warn/error logging statements'
    )

    parser.add_argument(
        '--no-skip-tests',
        action='store_true',
        help='Do not skip test files'
    )

    parser.add_argument(
        '--strict',
        action='store_true',
        help='Treat warnings as errors'
    )


def _add_output_arguments(parser: argparse.ArgumentParser) -> None:
    """Add output-related arguments.

    Args:
        parser: ArgumentParser to add arguments to
    """
    parser.add_argument(
        '--format',
        choices=['text', 'json', 'github'],
        default='text',
        help='Output format (default: text)'
    )


def _create_linter(args: argparse.Namespace) -> PrintStatementLinter:
    """Create a linter instance based on arguments.

    Args:
        args: Parsed arguments

    Returns:
        Configured PrintStatementLinter
    """
    return PrintStatementLinter(
        allow_logging=args.allow_logging,
        allow_in_tests=not args.no_skip_tests
    )


def _run_linting(args: argparse.Namespace,
                 linter: PrintStatementLinter) -> List[PrintViolation]:
    """Run the linting process.

    Args:
        args: Parsed arguments
        linter: Linter instance

    Returns:
        List of violations found
    """
    if args.file:
        return linter.lint_file(args.file)
    return linter.lint_directory(args.path, recursive=args.recursive)


def _output_report(linter: PrintStatementLinter, args: argparse.Namespace) -> None:
    """Output the linting report.

    Args:
        linter: Linter instance
        args: Parsed arguments
    """
    report = linter.generate_report(output_format=args.format)
    sys.stdout.write(report + '\n')
    sys.stdout.flush()


def _determine_main_exit_code(violations: List[PrintViolation],
                              args: argparse.Namespace) -> int:
    """Determine the exit code based on violations.

    Args:
        violations: List of violations
        args: Parsed arguments

    Returns:
        Exit code
    """
    if not violations:
        return 0

    if args.strict or any(v.severity == 'error' for v in violations):
        return 2

    return 1


if __name__ == '__main__':
    sys.exit(main())
