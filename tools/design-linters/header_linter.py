#!/usr/bin/env python3
"""
Purpose: Lint file headers to ensure compliance with project standards
Scope: All documentation and source code files in the project
Created: 2025-09-12
Updated: 2025-09-12
Author: Development Team
Version: 1.0
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Set


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
    REQUIRED_FIELDS = {'purpose', 'created', 'author'}

    # Recommended fields (generate warnings if missing)
    RECOMMENDED_FIELDS = {'scope', 'updated', 'version'}

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
            'field_pattern': re.compile(r'^\s\*\s(\w+):\s*(.+)$'),
            'comment_prefix': '/**',
            'header_end_marker': '*/'
        },
        '.tsx': {
            'header_pattern': re.compile(
                r'^/\*\*[\s\S]*?\*/',
                re.MULTILINE
            ),
            'field_pattern': re.compile(r'^\s\*\s(\w+):\s*(.+)$'),
            'comment_prefix': '/**',
            'header_end_marker': '*/'
        },
        '.js': {
            'header_pattern': re.compile(
                r'^/\*\*[\s\S]*?\*/',
                re.MULTILINE
            ),
            'field_pattern': re.compile(r'^\s\*\s(\w+):\s*(.+)$'),
            'comment_prefix': '/**',
            'header_end_marker': '*/'
        },
        '.jsx': {
            'header_pattern': re.compile(
                r'^/\*\*[\s\S]*?\*/',
                re.MULTILINE
            ),
            'field_pattern': re.compile(r'^\s\*\s(\w+):\s*(.+)$'),
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

        return self._validate_header(file_path, content, suffix)

    def _validate_header(self, file_path: Path, content: str, suffix: str) -> ValidationResult:
        """Validate the header in file content.

        Args:
            file_path: Path to the file being validated
            content: File content as string
            suffix: File extension

        Returns:
            ValidationResult with validation details
        """
        config = self.FILE_CONFIGS[suffix]
        errors = []
        warnings = []

        # Find header section
        header_match = config['header_pattern'].search(content)
        if not header_match:
            errors.append("No header found in file")
            return ValidationResult(
                passed=False,
                errors=errors,
                warnings=warnings,
                header_fields=[]
            )

        header_content = header_match.group(0)
        header_fields = self._extract_header_fields(header_content, config)

        # Check for required fields
        field_names = {field.name.lower() for field in header_fields}

        for required_field in self.REQUIRED_FIELDS:
            if required_field not in field_names:
                errors.append(f"Missing required field: {required_field}")

        # Check for recommended fields
        for recommended_field in self.RECOMMENDED_FIELDS:
            if recommended_field not in field_names:
                warnings.append(f"Missing recommended field: {recommended_field}")

        # Validate field content
        self._validate_field_content(header_fields, errors, warnings)

        # Determine pass/fail
        passed = len(errors) == 0
        if self.strict_mode and warnings:
            passed = False
            errors.extend([f"WARNING (strict mode): {w}" for w in warnings])
            warnings = []

        return ValidationResult(
            passed=passed,
            errors=errors,
            warnings=warnings,
            header_fields=header_fields
        )

    def _extract_header_fields(self, header_content: str, config: Dict) -> List[HeaderField]:
        """Extract header fields from header content.

        Args:
            header_content: The header section content
            config: File type configuration

        Returns:
            List of HeaderField objects
        """
        fields = []
        lines = header_content.split('\n')

        for line_num, line in enumerate(lines, 1):
            match = config['field_pattern'].search(line.strip())
            if match:
                field_name = match.group(1).lower()
                field_value = match.group(2).strip()
                fields.append(HeaderField(
                    name=field_name,
                    value=field_value,
                    line_number=line_num
                ))

        return fields

    def _validate_field_content(self, fields: List[HeaderField], errors: List[str], warnings: List[str]) -> None:
        """Validate the content of header fields.

        Args:
            fields: List of header fields to validate
            errors: List to append errors to
            warnings: List to append warnings to
        """
        field_dict = {field.name: field.value for field in fields}

        # Validate date fields
        for date_field in ['created', 'updated']:
            if date_field in field_dict:
                if not self.DATE_PATTERN.match(field_dict[date_field]):
                    errors.append(f"Invalid date format for {date_field} (expected YYYY-MM-DD)")
                else:
                    # Check if date is reasonable
                    try:
                        date_obj = datetime.strptime(field_dict[date_field], '%Y-%m-%d')
                        if date_obj.year < 2020 or date_obj > datetime.now():
                            warnings.append(f"Unusual date for {date_field}: {field_dict[date_field]}")
                    except ValueError:
                        errors.append(f"Invalid date value for {date_field}: {field_dict[date_field]}")

        # Validate purpose field
        if 'purpose' in field_dict:
            purpose = field_dict['purpose']
            if len(purpose) < 10:
                warnings.append("Purpose field is very short (less than 10 characters)")
            elif len(purpose) > 200:
                warnings.append("Purpose field is very long (more than 200 characters)")

        # Validate version field
        if 'version' in field_dict:
            version = field_dict['version']
            version_pattern = re.compile(r'^\d+\.\d+(\.\d+)?(-\w+)?$')
            if not version_pattern.match(version):
                warnings.append(f"Version format may not follow semantic versioning: {version}")

    def lint_directory(self, directory: Path, recursive: bool = True) -> Dict[Path, ValidationResult]:
        """Lint all supported files in a directory.

        Args:
            directory: Directory to scan
            recursive: Whether to scan subdirectories

        Returns:
            Dictionary mapping file paths to validation results
        """
        results = {}

        if not directory.exists() or not directory.is_dir():
            return results

        pattern = "**/*" if recursive else "*"
        for file_path in directory.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.FILE_CONFIGS:
                results[file_path] = self.lint_file(file_path)

        return results

    def generate_report(self, results: Dict[Path, ValidationResult]) -> str:
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

        # Failed files
        if failed_files > 0:
            report.append("FAILED FILES:")
            report.append("-" * 40)
            for file_path, result in results.items():
                if not result.passed:
                    report.append(f"\n📄 {file_path}")
                    for error in result.errors:
                        report.append(f"   ❌ {error}")
                    for warning in result.warnings:
                        report.append(f"   ⚠️  {warning}")

        # Files with warnings
        warning_files = [
            (fp, r) for fp, r in results.items()
            if r.passed and r.warnings
        ]
        if warning_files:
            report.append("\n\nFILES WITH WARNINGS:")
            report.append("-" * 40)
            for file_path, result in warning_files:
                report.append(f"\n📄 {file_path}")
                for warning in result.warnings:
                    report.append(f"   ⚠️  {warning}")

        report.append("\n" + "=" * 60)
        return "\n".join(report)


def main():
    """Main entry point for the header linter."""
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

    args = parser.parse_args()

    linter = FileHeaderLinter(strict_mode=args.strict)

    if args.file:
        # Lint single file
        result = linter.lint_file(args.file)
        results = {args.file: result}
    else:
        # Lint directory
        recursive = args.recursive if args.path else True
        results = linter.lint_directory(args.path, recursive=recursive)

    if not results:
        print("No files found to lint")
        return 0

    # Generate and print report
    if not args.quiet:
        print(linter.generate_report(results))

    # Determine exit code
    failed_files = sum(1 for r in results.values() if not r.passed)

    if failed_files > 0:
        if args.quiet:
            for file_path, result in results.items():
                if not result.passed:
                    print(f"{file_path}: FAILED")
                    for error in result.errors:
                        print(f"  {error}")
        return 2  # Failures found

    # Check for warnings in non-strict mode
    warning_files = sum(1 for r in results.values() if r.warnings)
    if warning_files > 0 and not args.strict:
        return 1  # Warnings found

    return 0  # All good


if __name__ == '__main__':
    sys.exit(main())
