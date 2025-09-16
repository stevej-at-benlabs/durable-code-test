#!/usr/bin/env python3
"""
Purpose: Validates file placement according to project structure standards
Scope: Project-wide file organization enforcement across all directories
Overview: This comprehensive linter analyzes Python, HTML, TypeScript, and configuration
    files to ensure they are located in appropriate directories as defined in
    STANDARDS.md.
    It enforces project organization rules by checking files against configurable
    placement
    rules, detecting violations, and providing suggested corrections with clear
    explanations.
    The linter supports multiple file types, handles complex directory patterns
    with wildcards,
    and can be integrated into CI/CD pipelines to maintain consistent project structure.
    It helps prevent misplaced files that could break builds or violate
    architectural principles.
Dependencies: pathlib for file operations, fnmatch for pattern matching,
    argparse for CLI interface
Exports: FilePlacementLinter class, ViolationType enum, PlacementRule dataclass
Interfaces: main() CLI function, analyze_project() returns List[FilePlacementViolation]
Implementation: Uses rule-based pattern matching with configurable directory
    allowlists/blocklists
"""

import sys
import argparse
import json
import fnmatch
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
try:
    from .constants import EXCLUDED_PATTERNS
except ImportError:
    # For direct script execution
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from constants import EXCLUDED_PATTERNS  # type: ignore[import-not-found,no-redef]


class ViolationType(Enum):
    """Types of file placement violations."""
    PYTHON_MISPLACED = "python_misplaced"
    HTML_MISPLACED = "html_misplaced"
    TEST_MISPLACED = "test_misplaced"
    CONFIG_MISPLACED = "config_misplaced"
    FRONTEND_MISPLACED = "frontend_misplaced"
    ROOT_VIOLATION = "root_violation"
    BUILD_ARTIFACT = "build_artifact"


@dataclass
class PlacementRule:
    """Defines a file placement rule."""
    file_patterns: List[str]
    allowed_directories: List[str]
    prohibited_directories: List[str]
    description: str
    violation_type: ViolationType
    exceptions: Optional[List[str]] = None

    def __post_init__(self) -> None:
        if self.exceptions is None:
            self.exceptions = []


class FilePlacementViolation:
    """Represents a file placement violation."""

    def __init__(
        self,
        file_path: str,
        violation_type: ViolationType,
        *,
        current_location: str,
        expected_locations: List[str],
        description: str,
        severity: str = "error"
    ):
        self.file_path = file_path
        self.violation_type = violation_type
        self.current_location = current_location
        self.expected_locations = expected_locations
        self.description = description
        self.severity = severity

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON output."""
        return {
            'file': self.file_path,
            'violation_type': self.violation_type.value,
            'current_location': self.current_location,
            'expected_locations': self.expected_locations,
            'description': self.description,
            'severity': self.severity
        }


class FilePlacementLinter:
    """Analyzes project structure for file placement violations."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.violations: List[FilePlacementViolation] = []
        self.rules = self._init_placement_rules()

    def _init_placement_rules(self) -> List[PlacementRule]:
        """Initialize file placement rules based on project standards."""
        return [
            # Python source files
            PlacementRule(
                file_patterns=["*.py"],
                allowed_directories=[
                    "durable-code-app/backend/app",
                    "durable-code-app/backend/app/**",
                    "tools",
                    "tools/**",
                    "test",
                    "test/**"
                ],
                prohibited_directories=[
                    ".",  # Root directory
                    "docs",
                    "durable-code-app/frontend",
                    "durable-code-app/frontend/**",
                    "durable-code-app/backend/tests",  # Backend tests not allowed
                    "durable-code-app/backend/tests/**"
                ],
                description=("Python files must be in backend app/, tools/, "
                           "or root test/ directories"),
                violation_type=ViolationType.PYTHON_MISPLACED,
                exceptions=["__init__.py", "setup.py", "conftest.py"]
            ),

            # HTML files - Restrict standalone HTML pages, encourage React components
            PlacementRule(
                file_patterns=["*.html"],
                allowed_directories=[
                    "durable-code-app/frontend",      # Allow index.html (Vite)
                    "durable-code-app/frontend/dist", # Built files only
                    "durable-code-app/frontend/dist/**",
                    "docs"                            # Documentation only
                ],
                prohibited_directories=[
                    ".",  # Root directory
                    "durable-code-app/backend",
                    "durable-code-app/backend/**",
                    "durable-code-app/frontend/src",
                    "durable-code-app/frontend/public",  # Discourage HTML here
                    "tools"
                ],
                description=("HTML files should be React components, not "
                           "standalone pages. Only index.html, docs, and "
                           "build artifacts allowed."),
                violation_type=ViolationType.HTML_MISPLACED,
                exceptions=[
                    "index.html",                     # Vite entry point
                    "diagrams/*.html"  # Allow diagram files (to be migrated)
                ]
            ),

            # TypeScript/React files
            PlacementRule(
                file_patterns=["*.ts", "*.tsx"],
                allowed_directories=[
                    "durable-code-app/frontend/src",
                    "durable-code-app/frontend/src/**",
                    "durable-code-app/frontend/tests",
                    "durable-code-app/frontend/tests/**"
                ],
                prohibited_directories=[
                    ".",  # Root directory
                    "durable-code-app/backend",
                    "durable-code-app/backend/**",
                    "tools",
                    "test"
                ],
                description=("TypeScript/React files must be in "
                           "frontend/src/ or frontend/tests/"),
                violation_type=ViolationType.FRONTEND_MISPLACED,
                exceptions=["vite.config.ts", "vitest.config.ts",
                          "tsconfig*.json"]
            ),

            # CSS files
            PlacementRule(
                file_patterns=["*.css"],
                allowed_directories=[
                    "durable-code-app/frontend/src",
                    "durable-code-app/frontend/src/**",
                    "durable-code-app/frontend/public",
                    "durable-code-app/frontend/dist",
                    "durable-code-app/frontend/dist/**"
                ],
                prohibited_directories=[
                    ".",  # Root directory
                    "durable-code-app/backend",
                    "durable-code-app/backend/**",
                    "tools",
                    "test"
                ],
                description="CSS files must be in frontend/src/ or frontend/public/",
                violation_type=ViolationType.FRONTEND_MISPLACED
            ),

            # Test files - Python tests in root test/, Frontend tests
            # can be co-located or in tests/
            PlacementRule(
                file_patterns=["test_*.py", "*_test.py"],  # Python test files only
                allowed_directories=[
                    "test",
                    "test/**"
                ],
                prohibited_directories=[
                    ".",  # Root directory
                    "docs",
                    "tools",
                    "durable-code-app/backend/tests",  # Backend tests prohibited
                    "durable-code-app/backend/tests/**",
                    "durable-code-app/frontend",
                    "durable-code-app/frontend/**"
                ],
                description="Python test files must be in root test/ directory",
                violation_type=ViolationType.TEST_MISPLACED
            ),

            # Frontend test files - allow co-location with source or in tests/
            PlacementRule(
                file_patterns=["*.test.js", "*.test.ts", "*.test.tsx",
                              "*.spec.js", "*.spec.ts", "*.spec.tsx"],
                allowed_directories=[
                    "durable-code-app/frontend/src",      # Co-located with source
                    "durable-code-app/frontend/src/**",   # Co-located in subdirs
                    "durable-code-app/frontend/tests",    # Centralized test directory
                    "durable-code-app/frontend/tests/**"  # All subdirs in tests
                ],
                prohibited_directories=[
                    ".",  # Root directory
                    "docs",
                    "tools",
                    "durable-code-app/backend",
                    "durable-code-app/backend/**",
                    "test",  # Root test/ is for Python tests only
                    "test/**"
                ],
                description=("Frontend test files can be co-located with source "
                           "files or in frontend/tests/"),
                violation_type=ViolationType.TEST_MISPLACED
            ),

            # Build artifacts that shouldn't be in root
            PlacementRule(
                file_patterns=["*.js", "*.css", "*.map"],
                allowed_directories=[
                    "durable-code-app/frontend/src",
                    "durable-code-app/frontend/src/**",
                    "durable-code-app/frontend/dist",
                    "durable-code-app/frontend/dist/**",
                    "durable-code-app/frontend/node_modules",
                    "durable-code-app/frontend/node_modules/**"
                ],
                prohibited_directories=[
                    ".",  # Root directory
                ],
                description="Build artifacts should not be in root directory",
                violation_type=ViolationType.BUILD_ARTIFACT,
                exceptions=["eslint.config.js", "vite.config.js"]
            )
        ]

    def _matches_pattern(self, file_path: Path, pattern: str) -> bool:
        """Check if file matches a glob pattern."""
        return fnmatch.fnmatch(file_path.name, pattern)

    def _is_in_allowed_directory(self, file_path: Path,
                                  allowed_dirs: List[str]) -> bool:
        """Check if file is in an allowed directory."""
        relative_path = file_path.relative_to(self.project_root)
        parent_dir = str(relative_path.parent)

        for allowed in allowed_dirs:
            if self._check_directory_match(allowed, parent_dir, relative_path):
                return True

        return False

    def _check_directory_match(self, allowed: str, parent_dir: str,
                                relative_path: Path) -> bool:
        """Helper method to check if a directory matches the allowed pattern."""
        if allowed == ".":
            # Allow root directory
            return relative_path.parent == Path(".")

        if allowed.endswith("/**"):
            # Allow directory and all subdirectories
            base_dir = allowed[:-3]
            return (parent_dir == base_dir or
                    parent_dir.startswith(base_dir + "/"))

        # Exact directory match
        return parent_dir == allowed

    def _is_in_prohibited_directory(self, file_path: Path,
                                     prohibited_dirs: List[str]) -> bool:
        """Check if file is in a prohibited directory."""
        relative_path = file_path.relative_to(self.project_root)
        parent_dir = str(relative_path.parent)

        for prohibited in prohibited_dirs:
            if self._check_directory_match(prohibited, parent_dir, relative_path):
                return True

        return False

    def _is_exception(self, file_path: Path, exceptions: Optional[List[str]]) -> bool:
        """Check if file is in the exceptions list."""
        if exceptions is None:
            return False
        for exception in exceptions:
            if self._matches_pattern(file_path, exception):
                return True
        return False

    def _get_excluded_patterns(self) -> List[str]:
        """Get patterns for files/directories to exclude from analysis."""
        # Base exclusion patterns - common across all projects
        base_patterns = list(EXCLUDED_PATTERNS)

        # Additional exclusions for this project
        project_specific_patterns = [
            'coverage',  # Test coverage reports
            'htmlcov',  # Coverage HTML reports
        ]

        return base_patterns + project_specific_patterns

    def _should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from analysis."""
        excluded_patterns = self._get_excluded_patterns()
        relative_path = str(file_path.relative_to(self.project_root))

        for pattern in excluded_patterns:
            if pattern in relative_path:
                return True

            if fnmatch.fnmatch(relative_path, pattern):
                return True

        return False

    def analyze_project(self) -> List[FilePlacementViolation]:
        """Analyze the entire project for file placement violations."""
        self.violations = []

        # Walk through all files in the project
        for file_path in self.project_root.rglob('*'):
            if not file_path.is_file():
                continue

            if self._should_exclude_file(file_path):
                continue

            # Check each rule
            for rule in self.rules:
                self._check_file_against_rule(file_path, rule)

        return self.violations

    def _check_file_against_rule(self, file_path: Path, rule: PlacementRule) -> None:
        """Check a single file against a single placement rule."""
        # Check if file matches any pattern in this rule
        if not self._file_matches_rule_patterns(file_path, rule.file_patterns):
            return

        # Check if file is an exception
        if self._is_exception(file_path, rule.exceptions):
            return

        # Create violation if placement is invalid
        self._create_violation_if_needed(file_path, rule)

    def _file_matches_rule_patterns(self, file_path: Path,
                                     patterns: List[str]) -> bool:
        """Check if file matches any pattern in the given list."""
        for pattern in patterns:
            if self._matches_pattern(file_path, pattern):
                return True
        return False

    def _create_violation_if_needed(self, file_path: Path,
                                     rule: PlacementRule) -> None:
        """Create a violation if file placement is invalid."""
        # Check if file is in prohibited directory
        if self._is_in_prohibited_directory(file_path,
                                             rule.prohibited_directories):
            self._add_violation(file_path, rule, "error")
            return

        # Check if file is not in any allowed directory
        if not self._is_in_allowed_directory(file_path,
                                              rule.allowed_directories):
            self._add_violation(file_path, rule, "warning")

    def _add_violation(self, file_path: Path, rule: PlacementRule,
                        severity: str) -> None:
        """Add a violation to the violations list."""
        relative_path = str(file_path.relative_to(self.project_root))
        violation = FilePlacementViolation(
            file_path=relative_path,
            violation_type=rule.violation_type,
            current_location=str(file_path.parent.relative_to(self.project_root)),
            expected_locations=rule.allowed_directories,
            description=rule.description,
            severity=severity
        )
        self.violations.append(violation)


def main() -> None:
    """Main entry point."""
    args = _parse_placement_arguments()
    project_path = _validate_project_path(args.path)
    violations = _run_placement_analysis(project_path)
    filtered_violations = _filter_violations_by_severity(violations, args.severity)
    _output_placement_results(project_path, filtered_violations, args.json)
    _handle_placement_exit_code(filtered_violations, args)


def _parse_placement_arguments() -> argparse.Namespace:
    """Parse command line arguments for file placement linter.

    Returns:
        Parsed arguments namespace
    """
    parser = _create_placement_parser()
    _add_placement_arguments(parser)
    return parser.parse_args()


def _create_placement_parser() -> argparse.ArgumentParser:
    """Create the argument parser for file placement linter.

    Returns:
        Configured ArgumentParser
    """
    return argparse.ArgumentParser(
        description='Lint file placement according to project standards'
    )


def _add_placement_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments to the placement parser.

    Args:
        parser: ArgumentParser to add arguments to
    """
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Project root directory to analyze (default: current directory)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    parser.add_argument(
        '--fail-on-violation',
        action='store_true',
        help='Exit with non-zero code if violations found'
    )
    parser.add_argument(
        '--severity',
        choices=['error', 'warning', 'all'],
        default='all',
        help='Minimum severity level to report (default: all)'
    )


def _validate_project_path(path_arg: str) -> Path:
    """Validate the project path argument.

    Args:
        path_arg: Path argument from command line

    Returns:
        Validated Path object

    Raises:
        SystemExit: If path is invalid
    """
    project_path = Path(path_arg).resolve()
    if not project_path.exists() or not project_path.is_dir():
        print(f"Error: {path_arg} is not a valid directory", file=sys.stderr)
        sys.exit(1)
    return project_path


def _run_placement_analysis(project_path: Path) -> List[FilePlacementViolation]:
    """Run the file placement analysis.

    Args:
        project_path: Path to the project directory

    Returns:
        List of violations found
    """
    linter = FilePlacementLinter(str(project_path))
    return linter.analyze_project()


def _filter_violations_by_severity(violations: List[FilePlacementViolation],
                                   severity: str) -> List[FilePlacementViolation]:
    """Filter violations by severity level.

    Args:
        violations: List of all violations
        severity: Severity filter ('error', 'warning', 'all')

    Returns:
        Filtered list of violations
    """
    if severity == 'all':
        return violations
    return [v for v in violations if v.severity == severity]


def _output_placement_results(project_path: Path,
                             violations: List[FilePlacementViolation],
                             json_output: bool) -> None:
    """Output the analysis results.

    Args:
        project_path: Path to the project directory
        violations: List of violations to output
        json_output: Whether to use JSON format
    """
    if json_output:
        _output_json_results(project_path, violations)
    else:
        _output_text_results(violations)


def _handle_placement_exit_code(violations: List[FilePlacementViolation],
                                args: argparse.Namespace) -> None:
    """Handle the exit code based on violations and arguments.

    Args:
        violations: List of violations found
        args: Parsed arguments
    """
    if not _should_exit_on_violations(violations, args):
        return

    if _has_exit_worthy_violations(violations, args):
        sys.exit(1)


def _should_exit_on_violations(violations: List[FilePlacementViolation],
                              args: argparse.Namespace) -> bool:
    """Check if we should consider exiting on violations.

    Args:
        violations: List of violations found
        args: Parsed arguments

    Returns:
        True if we should consider exiting
    """
    return bool(args.fail_on_violation and violations)


def _has_exit_worthy_violations(violations: List[FilePlacementViolation],
                               args: argparse.Namespace) -> bool:
    """Check if violations warrant exiting with error code.

    Args:
        violations: List of violations found
        args: Parsed arguments

    Returns:
        True if should exit with error code
    """
    error_count = sum(1 for v in violations if v.severity == "error")
    return error_count > 0 or args.severity == 'warning'

def _output_json_results(project_path: Path,
                         violations: List[FilePlacementViolation]) -> None:
    """Output results in JSON format."""
    result = {
        'project_root': str(project_path),
        'total_violations': len(violations),
        'violations': [v.to_dict() for v in violations]
    }
    print(json.dumps(result, indent=2))

def _output_text_results(violations: List[FilePlacementViolation]) -> None:
    """Output results in text format."""
    if not violations:
        print("✅ All files are properly placed!")
        return

    print(f"Found {len(violations)} file placement violations:\n")

    # Group violations by type and display
    violation_groups = _group_violations_by_type(violations)
    _display_violation_groups(violation_groups)

def _group_violations_by_type(
        violations: List[FilePlacementViolation]
) -> Dict[ViolationType, List[FilePlacementViolation]]:
    """Group violations by their type."""
    violation_groups: Dict[ViolationType,
                           List[FilePlacementViolation]] = {}
    for violation in violations:
        if violation.violation_type not in violation_groups:
            violation_groups[violation.violation_type] = []
        violation_groups[violation.violation_type].append(violation)
    return violation_groups

def _display_violation_groups(
        violation_groups: Dict[ViolationType, List[FilePlacementViolation]]
) -> None:
    """Display violations grouped by type."""
    for violation_type, group_violations in violation_groups.items():
        title = violation_type.value.replace('_', ' ').title()
        print(f"📁 {title} ({len(group_violations)} files):")
        for violation in group_violations:
            severity_icon = "❌" if violation.severity == "error" else "⚠️"
            print(f"  {severity_icon} {violation.file_path}")
            print(f"     Current: {violation.current_location}")
            print(f"     Expected: {', '.join(violation.expected_locations)}")
            print(f"     {violation.description}")
        print()


if __name__ == '__main__':
    main()
