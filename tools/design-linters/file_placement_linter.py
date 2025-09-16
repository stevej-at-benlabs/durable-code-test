#!/usr/bin/env python3
"""
File Placement Linter.

Ensures files are placed in appropriate directories according to project standards.
Validates that Python files, HTML files, tests, and other file types follow
the project's organizational structure as defined in STANDARDS.md.
"""

import os
import re
import sys
import argparse
import json
from pathlib import Path
from typing import List, Set, Dict, Optional, Union
from dataclasses import dataclass
from enum import Enum


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
    exceptions: List[str] = None

    def __post_init__(self):
        if self.exceptions is None:
            self.exceptions = []


class FilePlacementViolation:
    """Represents a file placement violation."""

    def __init__(
        self,
        file_path: str,
        violation_type: ViolationType,
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
                    "durable-code-app/backend/tests",  # Backend-specific tests not allowed
                    "durable-code-app/backend/tests/**"
                ],
                description="Python files must be in backend app/, tools/, or root test/ directories",
                violation_type=ViolationType.PYTHON_MISPLACED,
                exceptions=["__init__.py", "setup.py", "conftest.py"]
            ),

            # HTML files - Restrict standalone HTML pages, encourage React components
            PlacementRule(
                file_patterns=["*.html"],
                allowed_directories=[
                    "durable-code-app/frontend",      # Allow index.html in frontend root (Vite requirement)
                    "durable-code-app/frontend/dist", # Built files only
                    "durable-code-app/frontend/dist/**",
                    "docs"                            # Documentation only
                ],
                prohibited_directories=[
                    ".",  # Root directory
                    "durable-code-app/backend",
                    "durable-code-app/backend/**",
                    "durable-code-app/frontend/src",
                    "durable-code-app/frontend/public", # Discourage standalone HTML in public/
                    "tools"
                ],
                description="HTML files should be React components, not standalone pages. Only index.html, docs, and build artifacts allowed.",
                violation_type=ViolationType.HTML_MISPLACED,
                exceptions=[
                    "index.html",                     # Vite entry point
                    "diagrams/*.html"                 # Allow diagram files for now (to be migrated)
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
                description="TypeScript/React files must be in frontend/src/ or frontend/tests/",
                violation_type=ViolationType.FRONTEND_MISPLACED,
                exceptions=["vite.config.ts", "vitest.config.ts", "tsconfig*.json"]
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

            # Test files - Python tests in root test/, Frontend tests can be co-located or in tests/
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
                    "durable-code-app/backend/tests",  # Backend-specific tests prohibited
                    "durable-code-app/backend/tests/**",
                    "durable-code-app/frontend",
                    "durable-code-app/frontend/**"
                ],
                description="Python test files must be in root test/ directory",
                violation_type=ViolationType.TEST_MISPLACED
            ),

            # Frontend test files - allow co-location with source or in tests/ directory
            PlacementRule(
                file_patterns=["*.test.js", "*.test.ts", "*.test.tsx", "*.spec.js", "*.spec.ts", "*.spec.tsx"],
                allowed_directories=[
                    "durable-code-app/frontend/src",      # Co-located with source
                    "durable-code-app/frontend/src/**",   # Co-located with source in subdirs
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
                description="Frontend test files can be co-located with source files or in frontend/tests/",
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
        import fnmatch
        return fnmatch.fnmatch(file_path.name, pattern)

    def _is_in_allowed_directory(self, file_path: Path, allowed_dirs: List[str]) -> bool:
        """Check if file is in an allowed directory."""
        relative_path = file_path.relative_to(self.project_root)
        parent_dir = str(relative_path.parent)

        for allowed in allowed_dirs:
            if allowed == ".":
                # Allow root directory
                if relative_path.parent == Path("."):
                    return True
            elif allowed.endswith("/**"):
                # Allow directory and all subdirectories
                base_dir = allowed[:-3]
                if parent_dir == base_dir or parent_dir.startswith(base_dir + "/"):
                    return True
            else:
                # Exact directory match
                if parent_dir == allowed:
                    return True

        return False

    def _is_in_prohibited_directory(self, file_path: Path, prohibited_dirs: List[str]) -> bool:
        """Check if file is in a prohibited directory."""
        relative_path = file_path.relative_to(self.project_root)
        parent_dir = str(relative_path.parent)

        for prohibited in prohibited_dirs:
            if prohibited == ".":
                # Prohibit root directory
                if relative_path.parent == Path("."):
                    return True
            elif prohibited.endswith("/**"):
                # Prohibit directory and all subdirectories
                base_dir = prohibited[:-3]
                if parent_dir == base_dir or parent_dir.startswith(base_dir + "/"):
                    return True
            else:
                # Exact directory match
                if parent_dir == prohibited:
                    return True

        return False

    def _is_exception(self, file_path: Path, exceptions: List[str]) -> bool:
        """Check if file is in the exceptions list."""
        for exception in exceptions:
            if self._matches_pattern(file_path, exception):
                return True
        return False

    def _get_excluded_patterns(self) -> List[str]:
        """Get patterns for files/directories to exclude from analysis."""
        return [
            '.git',
            '__pycache__',
            '.mypy_cache',
            '.ruff_cache',
            'node_modules',
            '.venv',
            'venv',
            '.pytest_cache',
            '.coverage',
            'htmlcov',  # Coverage HTML reports
            '*.pyc',
            '*.pyo',
            '*.egg-info',
            '.DS_Store',
            'Thumbs.db'
        ]

    def _should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from analysis."""
        excluded_patterns = self._get_excluded_patterns()
        relative_path = str(file_path.relative_to(self.project_root))

        for pattern in excluded_patterns:
            if pattern in relative_path:
                return True

            import fnmatch
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
                # Check if file matches any pattern in this rule
                matches_pattern = False
                for pattern in rule.file_patterns:
                    if self._matches_pattern(file_path, pattern):
                        matches_pattern = True
                        break

                if not matches_pattern:
                    continue

                # Check if file is an exception
                if self._is_exception(file_path, rule.exceptions):
                    continue

                # Check if file is in prohibited directory
                if self._is_in_prohibited_directory(file_path, rule.prohibited_directories):
                    relative_path = str(file_path.relative_to(self.project_root))
                    violation = FilePlacementViolation(
                        file_path=relative_path,
                        violation_type=rule.violation_type,
                        current_location=str(file_path.parent.relative_to(self.project_root)),
                        expected_locations=rule.allowed_directories,
                        description=rule.description,
                        severity="error"
                    )
                    self.violations.append(violation)

                # Check if file is not in any allowed directory
                elif not self._is_in_allowed_directory(file_path, rule.allowed_directories):
                    relative_path = str(file_path.relative_to(self.project_root))
                    violation = FilePlacementViolation(
                        file_path=relative_path,
                        violation_type=rule.violation_type,
                        current_location=str(file_path.parent.relative_to(self.project_root)),
                        expected_locations=rule.allowed_directories,
                        description=rule.description,
                        severity="warning"
                    )
                    self.violations.append(violation)

        return self.violations


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Lint file placement according to project standards'
    )
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

    args = parser.parse_args()

    # Validate project directory
    project_path = Path(args.path).resolve()
    if not project_path.exists() or not project_path.is_dir():
        print(f"Error: {args.path} is not a valid directory", file=sys.stderr)
        sys.exit(1)

    # Run analysis
    linter = FilePlacementLinter(str(project_path))
    violations = linter.analyze_project()

    # Filter by severity
    if args.severity != 'all':
        violations = [v for v in violations if v.severity == args.severity]

    # Output results
    if args.json:
        result = {
            'project_root': str(project_path),
            'total_violations': len(violations),
            'violations': [v.to_dict() for v in violations]
        }
        print(json.dumps(result, indent=2))
    else:
        if not violations:
            print("✅ All files are properly placed!")
        else:
            print(f"Found {len(violations)} file placement violations:\n")

            # Group violations by type
            violation_groups: Dict[ViolationType, List[FilePlacementViolation]] = {}
            for violation in violations:
                if violation.violation_type not in violation_groups:
                    violation_groups[violation.violation_type] = []
                violation_groups[violation.violation_type].append(violation)

            # Display violations by group
            for violation_type, group_violations in violation_groups.items():
                print(f"📁 {violation_type.value.replace('_', ' ').title()} ({len(group_violations)} files):")
                for violation in group_violations:
                    severity_icon = "❌" if violation.severity == "error" else "⚠️"
                    print(f"  {severity_icon} {violation.file_path}")
                    print(f"     Current: {violation.current_location}")
                    print(f"     Expected: {', '.join(violation.expected_locations)}")
                    print(f"     {violation.description}")
                print()

    # Exit code
    if args.fail_on_violation and violations:
        error_count = sum(1 for v in violations if v.severity == "error")
        if error_count > 0 or args.severity == 'warning':
            sys.exit(1)


if __name__ == '__main__':
    main()
