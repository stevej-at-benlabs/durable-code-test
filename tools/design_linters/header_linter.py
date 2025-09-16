#!/usr/bin/env python3
"""
Purpose: Validates file headers according to comprehensive header standards
Scope: All code files (Python, TypeScript, JavaScript) and documentation files
Overview: This comprehensive linter ensures all files have proper headers with
    required fields including Purpose, Scope, Overview, Dependencies, Exports, and
    Interfaces as defined in FILE_HEADER_STANDARDS.md. It validates header structure,
    field presence, and content quality to ensure headers provide sufficient
    information for understanding files without reading the implementation. The linter
    supports different header formats for different file types (Python docstrings,
    TypeScript block comments, Markdown metadata) and enforces content quality
    standards including minimum word counts and descriptiveness requirements.
Dependencies: pathlib for file operations, re for regex parsing, argparse for CLI
Exports: FileHeaderLinter class, HeaderField class, ValidationResult class
Interfaces: main() CLI function, lint_file() returns ValidationResult
Implementation: Uses regex parsing to extract header blocks and validate required fields
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Any, Tuple


class HeaderField(NamedTuple):
    """Represents a header field with its value and line number."""
    name: str
    value: str
    line_number: int


class ValidationResult(NamedTuple):
    """Result of header validation."""
    passed: bool
    errors: List[str]
    warnings: List[str]
    header_fields: List[HeaderField]


class FileHeaderLinter:
    """Lints file headers according to project standards."""

    # Required fields for all files
    REQUIRED_FIELDS = {'purpose', 'scope', 'overview'}

    # Recommended fields for code files (generate warnings if missing)
    RECOMMENDED_CODE_FIELDS = {'dependencies', 'exports'}

    # Optional fields that can be present
    OPTIONAL_FIELDS = {
        'interfaces', 'props/interfaces', 'implementation',
        'state/behavior', 'notes', 'related', 'configuration'
    }

    # Valid date format pattern
    DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')

    # File type configurations
    FILE_CONFIGS = {
        '.md': {
            'header_pattern': re.compile(
                r'^# .+?\n\n(\*\*\w+\*\*:.+?\n)+\n---\n',
                re.MULTILINE | re.DOTALL
            ),
            'field_pattern': re.compile(r'^\*\*(\w+)\*\*:\s*(.+)$'),
            'comment_prefix': '',
            'header_end_marker': '---'
        },
        '.py': {
            'header_pattern': re.compile(
                r'^"""[\s\S]*?"""',
                re.MULTILINE
            ),
            'field_pattern': re.compile(r'^(\w+):\s*(.+)$'),
            'comment_prefix': '"""',
            'header_end_marker': '"""'
        },
        '.ts': {
            'header_pattern': re.compile(
                r'^/\*\*[\s\S]*?\*/',
                re.MULTILINE
            ),
            'field_pattern': re.compile(r'^\s\*\s([A-Za-z][A-Za-z0-9 /_-]*?):\s*(.+)$'),
            'comment_prefix': '/**',
            'header_end_marker': '*/'
        },
        '.tsx': {
            'header_pattern': re.compile(
                r'^/\*\*[\s\S]*?\*/',
                re.MULTILINE
            ),
            'field_pattern': re.compile(r'^\s\*\s([A-Za-z][A-Za-z0-9 /_-]*?):\s*(.+)$'),
            'comment_prefix': '/**',
            'header_end_marker': '*/'
        },
        '.js': {
            'header_pattern': re.compile(
                r'^/\*\*[\s\S]*?\*/',
                re.MULTILINE
            ),
            'field_pattern': re.compile(r'^\s\*\s([A-Za-z][A-Za-z0-9 /_-]*?):\s*(.+)$'),
            'comment_prefix': '/**',
            'header_end_marker': '*/'
        },
        '.jsx': {
            'header_pattern': re.compile(
                r'^/\*\*[\s\S]*?\*/',
                re.MULTILINE
            ),
            'field_pattern': re.compile(r'^\s\*\s([A-Za-z][A-Za-z0-9 /_-]*?):\s*(.+)$'),
            'comment_prefix': '/**',
            'header_end_marker': '*/'
        },
        '.html': {
            'header_pattern': re.compile(
                r'<!--[\s\S]*?-->',
                re.MULTILINE
            ),
            'field_pattern': re.compile(r'^(\w+):\s*(.+)$'),
            'comment_prefix': '<!--',
            'header_end_marker': '-->'
        },
        '.yml': {
            'header_pattern': re.compile(
                r'^(#[\s\S]*?)(?=\n[^#]|\n$)',
                re.MULTILINE
            ),
            'field_pattern': re.compile(r'^#\s(\w+):\s*(.+)$'),
            'comment_prefix': '#',
            'header_end_marker': None
        },
        '.yaml': {
            'header_pattern': re.compile(
                r'^(#[\s\S]*?)(?=\n[^#]|\n$)',
                re.MULTILINE
            ),
            'field_pattern': re.compile(r'^#\s(\w+):\s*(.+)$'),
            'comment_prefix': '#',
            'header_end_marker': None
        }
    }

    def __init__(self, strict_mode: bool = False):
        """Initialize the linter.

        Args:
            strict_mode: If True, treat warnings as errors
        """
        self.strict_mode = strict_mode

    def lint_file(self, file_path: Path) -> ValidationResult:
        """Lint a single file's header.

        Args:
            file_path: Path to the file to lint

        Returns:
            ValidationResult with pass/fail status and details
        """
        if not file_path.exists():
            return ValidationResult(
                passed=False,
                errors=[f"File does not exist: {file_path}"],
                warnings=[],
                header_fields=[]
            )

        # Skip README files
        if file_path.name.lower().startswith('readme'):
            return ValidationResult(
                passed=True,
                errors=[],
                warnings=[],
                header_fields=[]
            )

        # Check if file type is supported
        suffix = file_path.suffix.lower()
        if suffix not in self.FILE_CONFIGS:
            return ValidationResult(
                passed=True,
                errors=[],
                warnings=[f"File type {suffix} not configured for header linting"],
                header_fields=[]
            )

        try:
            content = file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            return ValidationResult(
                passed=False,
                errors=[f"Could not read file (encoding issue): {file_path}"],
                warnings=[],
                header_fields=[]
            )

        return self._validate_header(content, suffix)

    def _validate_header(self, content: str,
                         suffix: str) -> ValidationResult:
        """Validate the header in file content.

        Args:
            content: File content as string
            suffix: File extension

        Returns:
            ValidationResult with validation details
        """
        config: Dict[str, Any] = self.FILE_CONFIGS[suffix]
        errors: List[str] = []
        warnings: List[str] = []

        # Find and extract header
        header_fields = self._extract_and_validate_header_structure(
            content, config, errors
        )
        if not header_fields:
            return self._create_validation_result(False, errors, warnings, [])

        # Validate field requirements
        self._check_required_fields(header_fields, errors)
        self._check_recommended_fields(header_fields, warnings, suffix)

        # Validate field content
        self._validate_field_content(header_fields, warnings, suffix)

        # Determine final result
        passed = self._determine_validation_result(errors, warnings)
        return self._create_validation_result(passed, errors, warnings, header_fields)

    def _extract_and_validate_header_structure(
            self, content: str, config: Dict[str, Any], errors: List[str]
    ) -> List[HeaderField]:
        """Extract header structure and validate it exists.

        Args:
            content: File content as string
            config: File type configuration
            errors: List to append errors to

        Returns:
            List of header fields if header found, empty list otherwise
        """
        header_match = config['header_pattern'].search(content)
        if not header_match:
            errors.append("No header found in file")
            return []

        header_content = header_match.group(0)
        return self._extract_header_fields(header_content, config)

    def _check_required_fields(self, header_fields: List[HeaderField],
                              errors: List[str]) -> None:
        """Check for presence of required fields.

        Args:
            header_fields: List of header fields
            errors: List to append errors to
        """
        field_names = {field.name.lower() for field in header_fields}
        for required_field in self.REQUIRED_FIELDS:
            if required_field not in field_names:
                errors.append(f"Missing required field: {required_field}")

    def _check_recommended_fields(self, header_fields: List[HeaderField],
                                 warnings: List[str], suffix: str) -> None:
        """Check for presence of recommended fields in code files.

        Args:
            header_fields: List of header fields
            warnings: List to append warnings to
            suffix: File extension
        """
        if not self._is_code_file(suffix):
            return

        field_names = {field.name.lower() for field in header_fields}
        for recommended_field in self.RECOMMENDED_CODE_FIELDS:
            if recommended_field not in field_names:
                warnings.append(
                    f"Missing recommended field for code files: "
                    f"{recommended_field}"
                )

    def _determine_validation_result(self, errors: List[str],
                                   warnings: List[str]) -> bool:
        """Determine if validation passed based on errors and warnings.

        Args:
            errors: List of errors
            warnings: List of warnings

        Returns:
            True if validation passed, False otherwise
        """
        passed = len(errors) == 0
        if self.strict_mode and warnings:
            passed = False
            errors.extend([f"WARNING (strict mode): {w}" for w in warnings])
            warnings.clear()
        return passed

    def _create_validation_result(self, passed: bool, errors: List[str],
                                 warnings: List[str],
                                 header_fields: List[HeaderField]) -> ValidationResult:
        """Create a ValidationResult object.

        Args:
            passed: Whether validation passed
            errors: List of errors
            warnings: List of warnings
            header_fields: List of header fields

        Returns:
            ValidationResult object
        """
        return ValidationResult(
            passed=passed,
            errors=errors,
            warnings=warnings,
            header_fields=header_fields
        )

    def _extract_header_fields(self, header_content: str,
                               config: Dict[str, Any]) -> List[HeaderField]:
        """Extract header fields from header content.

        Args:
            header_content: The header section content
            config: File type configuration

        Returns:
            List of HeaderField objects
        """
        fields = []
        lines = header_content.split('\n')
        current_field = None
        current_value = []

        for line_num, line in enumerate(lines, 1):
            # Check if this line starts a new field
            match = config['field_pattern'].search(line.strip())
            if match:
                # Save the previous field if exists
                if current_field is not None:
                    field_name, field_line_num = current_field
                    fields.append(HeaderField(
                        name=field_name,
                        value=' '.join(current_value),
                        line_number=field_line_num
                    ))
                # Start new field
                current_field = (match.group(1).lower(), line_num)
                current_value = [match.group(2).strip()]
                continue

            # Process continuation lines
            self._process_continuation_line(line, config, current_field, current_value)

        # Don't forget the last field
        if current_field is not None:
            field_name, field_line_num = current_field
            fields.append(HeaderField(
                name=field_name,
                value=' '.join(current_value),
                line_number=field_line_num
            ))

        return fields

    def _process_continuation_line(
            self, line: str, config: Dict[str, Any],
            current_field: Optional[Tuple[str, int]],
            current_value: List[str]
    ) -> None:
        """Process a potential continuation line for multi-line field values.

        Args:
            line: The current line being processed
            config: File type configuration
            current_field: The current field being built (tuple of name and line number)
            current_value: List of value parts for the current field
        """
        if not self._should_process_continuation(current_field, config):
            return

        stripped = line.strip()
        self._handle_yaml_continuation(stripped, config, current_value)
        self._handle_html_continuation(line, stripped, config, current_value)

    def _should_process_continuation(self, current_field: Optional[Tuple[str, int]],
                                   config: Dict[str, Any]) -> bool:
        """Check if we should process this line as a continuation.

        Args:
            current_field: The current field being built
            config: File type configuration

        Returns:
            True if line should be processed as continuation
        """
        return (current_field is not None and
                config['comment_prefix'] in ['#', '<!--'])

    def _handle_yaml_continuation(self, stripped: str, config: Dict[str, Any],
                                 current_value: List[str]) -> None:
        """Handle YAML-style continuation lines.

        Args:
            stripped: Stripped line content
            config: File type configuration
            current_value: List of value parts for the current field
        """
        if config['comment_prefix'] != '#' or not stripped.startswith('#'):
            return

        continuation = stripped[1:].strip()
        if continuation:
            current_value.append(continuation)

    def _handle_html_continuation(self, line: str, stripped: str,
                                 config: Dict[str, Any],
                                 current_value: List[str]) -> None:
        """Handle HTML-style continuation lines.

        Args:
            line: Original line content
            stripped: Stripped line content
            config: File type configuration
            current_value: List of value parts for the current field
        """
        if (config['comment_prefix'] == '<!--' and
                '-->' not in line and stripped):
            current_value.append(stripped)

    def _validate_field_content(self, fields: List[HeaderField],
                                warnings: List[str],
                                suffix: str) -> None:
        """Validate the content of header fields.

        Args:
            fields: List of header fields to validate
            warnings: List to append warnings to
            suffix: File extension to determine validation rules
        """
        field_dict = {field.name: field.value for field in fields}

        # Validate required fields
        self._validate_purpose_field(field_dict, warnings)
        self._validate_scope_field(field_dict, warnings)
        self._validate_overview_field(field_dict, warnings, suffix)

        # Validate code-specific fields
        if self._is_code_file(suffix):
            self._validate_dependencies_field(field_dict, warnings)
            self._validate_exports_field(field_dict, warnings)

    def _validate_purpose_field(self, field_dict: Dict[str, str],
                               warnings: List[str]) -> None:
        """Validate the purpose field content.

        Args:
            field_dict: Dictionary of field names to values
            warnings: List to append warnings to
        """
        if 'purpose' not in field_dict:
            return

        purpose = field_dict['purpose'].strip()
        if len(purpose) < 20:
            warnings.append(
                "Purpose field is too brief (should be 1-2 descriptive lines)"
            )
        elif len(purpose.split()) < 5:
            warnings.append("Purpose field should be more descriptive")

    def _validate_scope_field(self, field_dict: Dict[str, str],
                             warnings: List[str]) -> None:
        """Validate the scope field content.

        Args:
            field_dict: Dictionary of field names to values
            warnings: List to append warnings to
        """
        if 'scope' not in field_dict:
            return

        scope = field_dict['scope'].strip()
        if len(scope) < 10:
            warnings.append(
                "Scope field is too brief (should describe what areas "
                "this file covers)"
            )

    def _validate_overview_field(self, field_dict: Dict[str, str],
                                warnings: List[str], suffix: str) -> None:
        """Validate the overview field content.

        Args:
            field_dict: Dictionary of field names to values
            warnings: List to append warnings to
            suffix: File extension to determine validation rules
        """
        if 'overview' not in field_dict:
            return

        overview = field_dict['overview'].strip()
        word_count = len(overview.split())

        if word_count < 15:
            warnings.append(
                "Overview field is too brief (should provide comprehensive "
                "summary)"
            )
        elif word_count < 25 and self._is_code_file(suffix):
            warnings.append(
                "Overview field should be more comprehensive for code files"
            )

    def _validate_dependencies_field(self, field_dict: Dict[str, str],
                                    warnings: List[str]) -> None:
        """Validate the dependencies field content.

        Args:
            field_dict: Dictionary of field names to values
            warnings: List to append warnings to
        """
        if 'dependencies' not in field_dict:
            return

        dependencies = field_dict['dependencies'].strip()
        if len(dependencies) < 10:
            warnings.append(
                "Dependencies field should list key dependencies and libraries"
            )

    def _validate_exports_field(self, field_dict: Dict[str, str],
                               warnings: List[str]) -> None:
        """Validate the exports field content.

        Args:
            field_dict: Dictionary of field names to values
            warnings: List to append warnings to
        """
        if 'exports' not in field_dict:
            return

        exports = field_dict['exports'].strip()
        if len(exports) < 10:
            warnings.append(
                "Exports field should list main classes, functions, or "
                "components"
            )

    def _is_code_file(self, suffix: str) -> bool:
        """Check if the file is a code file based on its extension.

        Args:
            suffix: File extension

        Returns:
            True if it's a code file, False otherwise
        """
        return suffix in ['.py', '.ts', '.tsx', '.js', '.jsx']

    def lint_directory(self, directory: Path,
                       recursive: bool = True) -> Dict[Path, ValidationResult]:
        """Lint all supported files in a directory.

        Args:
            directory: Directory to scan
            recursive: Whether to scan subdirectories

        Returns:
            Dictionary mapping file paths to validation results
        """
        if not self._is_valid_directory(directory):
            return {}

        file_paths = self._find_lintable_files(directory, recursive)
        return self._lint_file_collection(file_paths)

    def _is_valid_directory(self, directory: Path) -> bool:
        """Check if directory is valid for linting.

        Args:
            directory: Directory to check

        Returns:
            True if directory is valid, False otherwise
        """
        return directory.exists() and directory.is_dir()

    def _find_lintable_files(self, directory: Path, recursive: bool) -> List[Path]:
        """Find all files that can be linted in the directory.

        Args:
            directory: Directory to scan
            recursive: Whether to scan subdirectories

        Returns:
            List of file paths that can be linted
        """
        pattern = "**/*" if recursive else "*"
        lintable_files = []

        for file_path in directory.glob(pattern):
            if self._is_lintable_file(file_path):
                lintable_files.append(file_path)

        return lintable_files

    def _is_lintable_file(self, file_path: Path) -> bool:
        """Check if a file can be linted.

        Args:
            file_path: Path to check

        Returns:
            True if file can be linted, False otherwise
        """
        return (file_path.is_file() and
                file_path.suffix.lower() in self.FILE_CONFIGS)

    def _lint_file_collection(
            self, file_paths: List[Path]
    ) -> Dict[Path, ValidationResult]:
        """Lint a collection of files.

        Args:
            file_paths: List of file paths to lint

        Returns:
            Dictionary mapping file paths to validation results
        """
        results = {}
        for file_path in file_paths:
            results[file_path] = self.lint_file(file_path)
        return results

    def generate_report(self,
                        results: Dict[Path, ValidationResult]) -> str:
        """Generate a formatted report from validation results.

        Args:
            results: Dictionary of file paths to validation results

        Returns:
            Formatted report string
        """
        total_files = len(results)
        passed_files = sum(1 for r in results.values() if r.passed)
        failed_files = total_files - passed_files

        report = []
        report.append("=" * 60)
        report.append("FILE HEADER LINTING REPORT")
        report.append("=" * 60)
        report.append(f"Total files checked: {total_files}")
        report.append(f"Passed: {passed_files}")
        report.append(f"Failed: {failed_files}")
        report.append("")

        # Add failed files section
        self._add_failed_files_section(report, results)

        # Add warning files section
        self._add_warning_files_section(report, results)

        report.append("\n" + "=" * 60)
        return "\n".join(report)

    def _add_failed_files_section(self, report: List[str],
                                  results: Dict[Path, ValidationResult]) -> None:
        """Add failed files section to report.

        Args:
            report: Report lines list to append to
            results: Validation results
        """
        failed_results = self._get_failed_results(results)
        if not failed_results:
            return

        self._add_section_header(report, "FAILED FILES:")
        self._add_failed_file_details(report, failed_results)

    def _get_failed_results(
            self, results: Dict[Path, ValidationResult]
    ) -> List[Tuple[Path, ValidationResult]]:
        """Get list of failed validation results.

        Args:
            results: Validation results

        Returns:
            List of tuples of file paths and failed results
        """
        return [(fp, r) for fp, r in results.items() if not r.passed]

    def _add_section_header(self, report: List[str], title: str) -> None:
        """Add a section header to the report.

        Args:
            report: Report lines list to append to
            title: Section title
        """
        report.append(title)
        report.append("-" * 40)

    def _add_failed_file_details(
            self, report: List[str],
            failed_results: List[Tuple[Path, ValidationResult]]
    ) -> None:
        """Add details for failed files to the report.

        Args:
            report: Report lines list to append to
            failed_results: List of failed validation results
        """
        for file_path, result in failed_results:
            self._add_file_details(
                report, file_path, result.errors, result.warnings
            )

    def _add_warning_files_section(
            self, report: List[str],
            results: Dict[Path, ValidationResult]
    ) -> None:
        """Add warning files section to report.

        Args:
            report: Report lines list to append to
            results: Validation results
        """
        warning_results = self._get_warning_results(results)
        if not warning_results:
            return

        self._add_warning_section_header(report)
        self._add_warning_file_details(report, warning_results)

    def _get_warning_results(
            self, results: Dict[Path, ValidationResult]
    ) -> List[Tuple[Path, ValidationResult]]:
        """Get list of results with warnings.

        Args:
            results: Validation results

        Returns:
            List of tuples of file paths and results with warnings
        """
        return [
            (fp, r) for fp, r in results.items()
            if r.passed and r.warnings
        ]

    def _add_warning_section_header(self, report: List[str]) -> None:
        """Add warning section header to report.

        Args:
            report: Report lines list to append to
        """
        report.append("\n\nFILES WITH WARNINGS:")
        report.append("-" * 40)

    def _add_warning_file_details(
            self, report: List[str],
            warning_results: List[Tuple[Path, ValidationResult]]
    ) -> None:
        """Add details for files with warnings to the report.

        Args:
            report: Report lines list to append to
            warning_results: List of results with warnings
        """
        for file_path, result in warning_results:
            self._add_file_details(report, file_path, [], result.warnings)

    def _add_file_details(self, report: List[str], file_path: Path,
                          errors: List[str], warnings: List[str]) -> None:
        """Add file details with errors and warnings to report.

        Args:
            report: Report lines list to append to
            file_path: Path to the file
            errors: List of error messages
            warnings: List of warning messages
        """
        report.append(f"\n📄 {file_path}")

        for error in errors:
            report.append(f"   ❌ {error}")

        for warning in warnings:
            report.append(f"   ⚠️  {warning}")


def main() -> int:
    """Main entry point for the header linter."""
    args = _parse_arguments()
    linter = FileHeaderLinter(strict_mode=args.strict)

    results = _get_lint_results(args, linter)

    if not results:
        print("No files found to lint")
        return 0

    # Generate and print report
    if not args.quiet:
        print(linter.generate_report(results))

    return _determine_exit_code(results, args)


def _parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Lint file headers for compliance with project standards",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python header_linter.py --path docs/
  python header_linter.py --path src/ --recursive --strict
  python header_linter.py --file README.md
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--path',
        type=Path,
        help='Directory path to lint'
    )
    group.add_argument(
        '--file',
        type=Path,
        help='Single file to lint'
    )

    parser.add_argument(
        '--recursive',
        action='store_true',
        help='Recursively scan subdirectories (default: True for --path)'
    )

    parser.add_argument(
        '--strict',
        action='store_true',
        help='Treat warnings as errors'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Only output errors, suppress warnings and summary'
    )

    return parser.parse_args()


def _get_lint_results(
        args: argparse.Namespace, linter: 'FileHeaderLinter'
) -> Dict[Path, ValidationResult]:
    """Get linting results based on arguments.

    Args:
        args: Parsed arguments
        linter: FileHeaderLinter instance

    Returns:
        Dictionary of validation results
    """
    if args.file:
        # Lint single file
        result = linter.lint_file(args.file)
        return {args.file: result}

    # Lint directory
    recursive = args.recursive if args.path else True
    return linter.lint_directory(args.path, recursive=recursive)


def _determine_exit_code(
        results: Dict[Path, ValidationResult], args: argparse.Namespace
) -> int:
    """Determine appropriate exit code based on results.

    Args:
        results: Dictionary of validation results
        args: Parsed arguments

    Returns:
        Exit code integer
    """
    failed_count = _count_failed_files(results)
    if failed_count > 0:
        _print_quiet_failures(results, args.quiet)
        return 2  # Failures found

    warning_count = _count_warning_files(results)
    if warning_count > 0 and not args.strict:
        return 1  # Warnings found

    return 0  # All good


def _count_failed_files(results: Dict[Path, ValidationResult]) -> int:
    """Count the number of failed files.

    Args:
        results: Dictionary of validation results

    Returns:
        Number of failed files
    """
    return sum(1 for r in results.values() if not r.passed)


def _count_warning_files(results: Dict[Path, ValidationResult]) -> int:
    """Count the number of files with warnings.

    Args:
        results: Dictionary of validation results

    Returns:
        Number of files with warnings
    """
    return sum(1 for r in results.values() if r.warnings)


def _print_quiet_failures(
        results: Dict[Path, ValidationResult], is_quiet: bool
) -> None:
    """Print failures in quiet mode if needed.

    Args:
        results: Dictionary of validation results
        is_quiet: Whether quiet mode is enabled
    """
    if not is_quiet:
        return

    for file_path, result in results.items():
        if result.passed:
            continue

        print(f"{file_path}: FAILED")
        for error in result.errors:
            print(f"  {error}")


if __name__ == '__main__':
    sys.exit(main())
