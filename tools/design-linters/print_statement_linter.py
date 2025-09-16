#!/usr/bin/env python3
"""
Purpose: Detects and reports print statements, console.log, alert, and debugger statements
Scope: Python, JavaScript, TypeScript source files across the entire project
Overview: This linter enforces proper logging standards by detecting print statements,
    console.log, alert, and debugger statements in production code. It analyzes Python,
    JavaScript, and TypeScript files to ensure developers use proper logging libraries
    (like loguru for Python) instead of debug statements that can leak sensitive information
    or degrade performance. The tool helps maintain clean, production-ready code.
Dependencies: ast for Python AST parsing, pathlib for file operations, re for pattern matching
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
from typing import Dict, List, NamedTuple, Optional, Set, Tuple


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

    def __init__(self):
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

    def add_language(self, extension: str, language: str):
        """Add a new language mapping without modifying the class."""
        self.language_map[extension] = language

    def add_pattern(self, language: str, pattern: str, description: str):
        """Add a new pattern for a language without modifying the class."""
        if language not in self.print_patterns:
            self.print_patterns[language] = []
        self.print_patterns[language].append((pattern, description))

    def get_language(self, extension: str) -> str:
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
        'design-linters'  # Skip linter tools themselves (meta-tools exception)
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
        # Always skip certain directories and files
        for pattern in self.SKIP_FILES:
            if file_path.match(pattern):
                return True

        # Check if in skip directory
        for parent in file_path.parents:
            if parent.name in self.SKIP_DIRS:
                return True

        # Skip test files only if allow_in_tests is True
        if self.allow_in_tests:
            test_patterns = [
                '*test*.py', '*test*.js', '*test*.ts', '*.test.*', '*.spec.*',
                'test_*.py', '*_test.py', 'conftest.py'
            ]
            for pattern in test_patterns:
                if file_path.match(pattern):
                    return True

            # Check if in test directory
            test_dirs = {'test', 'tests', '__tests__', 'test_*', '*_test'}
            for parent in file_path.parents:
                if parent.name in test_dirs or parent.match('test_*') or parent.match('*_test'):
                    return True

        # Skip non-source files
        if self.pattern_registry.get_language(file_path.suffix) is None:
            return True

        return False

    def detect_language(self, file_path: Path) -> Optional[str]:
        """Detect the programming language of a file."""
        suffix = file_path.suffix.lower()
        return self.pattern_registry.get_language(suffix)

    def lint_python_file(self, file_path: Path, content: str) -> List[PrintViolation]:
        """Lint a Python file using AST parsing."""
        violations = []

        # Check for file-level disable
        if self._is_file_disabled(content, 'python'):
            return []

        try:
            tree = ast.parse(content, filename=str(file_path))
            lines = content.split('\n')

            for node in ast.walk(tree):
                # Check for print function calls
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in ('print', 'pprint'):
                        # Check if this line is disabled
                        if self._is_line_disabled(lines, node.lineno, 'python'):
                            continue

                        violations.append(PrintViolation(
                            file_path=file_path,
                            line_number=node.lineno,
                            column=node.col_offset,
                            statement=f"{node.func.id}()",
                            context=self._get_line_context(content, node.lineno),
                            language='python',
                            severity='error'
                        ))

                    # Check for pp (pprint alias)
                    elif isinstance(node.func, ast.Name) and node.func.id == 'pp':
                        # Check if this line is disabled
                        if self._is_line_disabled(lines, node.lineno, 'python'):
                            continue

                        violations.append(PrintViolation(
                            file_path=file_path,
                            line_number=node.lineno,
                            column=node.col_offset,
                            statement='pp()',
                            context=self._get_line_context(content, node.lineno),
                            language='python',
                            severity='warning'
                        ))

        except SyntaxError:
            # Fall back to regex if AST parsing fails
            violations.extend(self.lint_with_regex(file_path, content, 'python'))

        # The pattern registry already handles all patterns

        return violations

    def lint_with_regex(self, file_path: Path, content: str, language: str) -> List[PrintViolation]:
        """Lint a file using regex patterns.

        Args:
            file_path: Path to the file
            content: File content
            language: Programming language
            custom_only: If True, only check custom patterns
        """
        violations = []

        # Check for file-level disable
        if self._is_file_disabled(content, language):
            return []

        # Use patterns from registry
        patterns = self.pattern_registry.get_patterns(language)

        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Skip comments
            if self._is_comment(line, language):
                continue

            # Check if this line is disabled
            if self._is_line_disabled(lines, line_num, language):
                continue

            for pattern, statement_type in patterns:
                if re.search(pattern, line):
                    # Check if it's a logging statement we allow
                    if self.allow_logging and self._is_allowed_logging(line, language):
                        continue

                    violations.append(PrintViolation(
                        file_path=file_path,
                        line_number=line_num,
                        column=line.index(re.search(pattern, line).group()),
                        statement=statement_type,
                        context=line.strip(),
                        language=language,
                        severity='error' if 'debugger' in statement_type else 'warning'
                    ))

        return violations

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
            violations = self.lint_with_regex(file_path, content, language)

        self.violations = violations
        return violations

    def lint_directory(self, directory: Path, recursive: bool = True) -> List[PrintViolation]:
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
        elif language in ('javascript', 'typescript'):
            return stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*')

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
            if language == 'python':
                # Python disable comments
                if re.search(r'#\s*print-linter:\s*disable', line, re.IGNORECASE):
                    return True
                if re.search(r'#\s*noqa:\s*print', line, re.IGNORECASE):
                    return True
                if re.search(r'#\s*type:\s*ignore\[print\]', line):
                    return True
            elif language in ('javascript', 'typescript'):
                # JavaScript/TypeScript disable comments
                if re.search(r'//\s*print-linter:\s*disable', line, re.IGNORECASE):
                    return True
                if re.search(r'/\*\s*print-linter:\s*disable\s*\*/', line, re.IGNORECASE):
                    return True
                if re.search(r'//\s*eslint-disable.*console', line):
                    return True
                if re.search(r'/\*\s*eslint-disable.*console\s*\*/', line):
                    return True

        return False

    def _is_line_disabled(self, lines: List[str], line_num: int, language: str) -> bool:
        """Check if a specific line has print linting disabled."""
        if line_num < 1 or line_num > len(lines):
            return False

        line = lines[line_num - 1]

        # Check for inline disable comments
        if language == 'python':
            # Python inline disable comments
            if re.search(r'#\s*noqa(?:\s|:|$)', line):
                return True
            if re.search(r'#\s*type:\s*ignore', line):
                return True
            if re.search(r'#\s*pylint:\s*disable', line):
                return True
            if re.search(r'#\s*print-linter:\s*ignore', line, re.IGNORECASE):
                return True
        elif language in ('javascript', 'typescript'):
            # JavaScript/TypeScript inline disable comments
            if re.search(r'//\s*eslint-disable-line', line):
                return True
            if re.search(r'//\s*print-linter:\s*ignore', line, re.IGNORECASE):
                return True
            if re.search(r'/\*\s*eslint-disable-line\s*\*/', line):
                return True

        # Check previous line for next-line disable comments
        if line_num > 1:
            prev_line = lines[line_num - 2]
            if language == 'python':
                if re.search(r'#\s*noqa:\s*next', prev_line, re.IGNORECASE):
                    return True
                if re.search(r'#\s*pylint:\s*disable-next', prev_line):
                    return True
                if re.search(r'#\s*print-linter:\s*ignore-next', prev_line, re.IGNORECASE):
                    return True
            elif language in ('javascript', 'typescript'):
                if re.search(r'//\s*eslint-disable-next-line', prev_line):
                    return True
                if re.search(r'//\s*print-linter:\s*ignore-next', prev_line, re.IGNORECASE):
                    return True
                if re.search(r'/\*\s*eslint-disable-next-line\s*\*/', prev_line):
                    return True

        return False

    def generate_report(self, format: str = 'text') -> str:
        """Generate a report of violations.

        Args:
            format: Output format ('text', 'json', 'github')
        """
        if format == 'json':
            return self._generate_json_report()
        elif format == 'github':
            return self._generate_github_report()
        else:
            return self._generate_text_report()

    def _generate_text_report(self) -> str:
        """Generate a text report."""
        if not self.violations:
            return "✅ No print statements found!"

        report = ["=" * 60]
        report.append("PRINT STATEMENT LINTING REPORT")
        report.append("=" * 60)
        report.append(f"Total violations: {len(self.violations)}")
        report.append("")

        # Group by file
        by_file: Dict[Path, List[PrintViolation]] = {}
        for violation in self.violations:
            if violation.file_path not in by_file:
                by_file[violation.file_path] = []
            by_file[violation.file_path].append(violation)

        for file_path, file_violations in by_file.items():
            report.append(f"\n📄 {file_path}")
            for v in file_violations:
                severity_icon = "❌" if v.severity == 'error' else "⚠️"
                report.append(f"  {severity_icon} Line {v.line_number}: {v.statement}")
                report.append(f"     {v.context}")

        report.append("\n" + "=" * 60)
        return "\n".join(report)

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


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Detect print statements in production code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python print_statement_linter.py --path src/
  python print_statement_linter.py --path . --recursive
  python print_statement_linter.py --file app.py --format json
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--path', type=Path, help='Directory to lint')
    group.add_argument('--file', type=Path, help='Single file to lint')

    parser.add_argument(
        '--recursive',
        action='store_true',
        default=True,
        help='Recursively scan directories (default: True)'
    )

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
        '--format',
        choices=['text', 'json', 'github'],
        default='text',
        help='Output format (default: text)'
    )

    parser.add_argument(
        '--strict',
        action='store_true',
        help='Treat warnings as errors'
    )

    args = parser.parse_args()

    linter = PrintStatementLinter(
        allow_logging=args.allow_logging,
        allow_in_tests=not args.no_skip_tests
    )

    if args.file:
        violations = linter.lint_file(args.file)
    else:
        violations = linter.lint_directory(args.path, recursive=args.recursive)

    # Generate report - using logger for structured output
    report = linter.generate_report(format=args.format)
    # For CLI tools, the report itself is the output, not a log message
    # We write directly to stdout for piping/redirection compatibility
    sys.stdout.write(report + '\n')
    sys.stdout.flush()

    # Exit code
    if violations:
        if args.strict or any(v.severity == 'error' for v in violations):
            return 2
        else:
            return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
