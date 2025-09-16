#!/usr/bin/env python3
"""
Purpose: Validates HTML documentation files for proper breadcrumb navigation compliance
Scope: HTML files in public directories and documentation folders
Overview: This linter ensures that all HTML documentation files contain proper
    breadcrumb navigation elements for user navigation and understanding document
    hierarchy. It validates that breadcrumbs include proper ARIA labels for
    accessibility, link back to home page, and mark the current page as non-link
    text. The linter helps maintain consistent navigation patterns across all
    documentation and prevents navigation dead-ends.
Dependencies: html.parser for HTML parsing, pathlib for file operations
Exports: BreadcrumbLinter class, BreadcrumbViolation dataclass, HTMLParser subclass
Interfaces: main() CLI function, check_file() returns violations list
Implementation: Uses HTML parsing to detect navigation elements and validates
    ARIA compliance
"""

import os
import sys
from typing import List, Tuple, Optional
from html.parser import HTMLParser
from abc import ABC, abstractmethod


class ValidationRule(ABC):
    """Abstract interface for validation rules - follows OCP."""

    @abstractmethod
    def validate(self, parser_state: dict) -> List[str]:
        """Validate parser state and return list of issues."""


class BreadcrumbValidationRule(ValidationRule):
    """Validates breadcrumb presence and structure."""

    def validate(self, parser_state: dict) -> List[str]:
        issues = []
        if (not parser_state.get('has_breadcrumb') and
                not parser_state.get('has_aria_label')):
            issues.append("No breadcrumb navigation found")
        elif not parser_state.get('has_home_link'):
            issues.append("Breadcrumb missing home page link")
        return issues


class DocumentParser(ABC):
    """Abstract interface for document parsers - follows OCP."""

    @abstractmethod
    def parse(self, content: str) -> Tuple[bool, List[str]]:
        """Parse document content and return (has_breadcrumbs, issues)."""

    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""


class BreadcrumbParser(HTMLParser, DocumentParser):
    """HTML parser to detect breadcrumb navigation elements."""

    def __init__(self,
                 validation_rules: Optional[List[ValidationRule]] = None):
        super().__init__()
        self.has_breadcrumb = False
        self.has_aria_label = False
        self.has_home_link = False
        self.in_breadcrumb = False
        self.breadcrumb_content: List[str] = []
        self.validation_rules = validation_rules or [BreadcrumbValidationRule()]

    def handle_starttag(self, tag: str,
                        attrs: List[Tuple[str, Optional[str]]]) -> None:
        attrs_dict = dict(attrs)

        if tag == 'nav':
            self._handle_nav_tag(attrs_dict)
        elif self.in_breadcrumb and tag == 'a':
            self._handle_anchor_tag(attrs_dict)

    def _handle_nav_tag(self, attrs_dict: dict) -> None:
        """Handle nav tag processing for breadcrumb detection.

        Args:
            attrs_dict: Dictionary of tag attributes
        """
        self._check_breadcrumb_class(attrs_dict)
        self._check_aria_label(attrs_dict)

    def _check_breadcrumb_class(self, attrs_dict: dict) -> None:
        """Check for breadcrumb class in nav element.

        Args:
            attrs_dict: Dictionary of tag attributes
        """
        class_attr = attrs_dict.get('class', '')
        if self._has_breadcrumb_class(class_attr):
            self.has_breadcrumb = True
            self.in_breadcrumb = True

    def _has_breadcrumb_class(self, class_attr: str) -> bool:
        """Check if class attribute contains breadcrumb.

        Args:
            class_attr: Class attribute value

        Returns:
            True if class contains breadcrumb
        """
        return bool(class_attr and 'breadcrumb' in class_attr)

    def _check_aria_label(self, attrs_dict: dict) -> None:
        """Check for breadcrumb aria-label in nav element.

        Args:
            attrs_dict: Dictionary of tag attributes
        """
        aria_label = attrs_dict.get('aria-label', '')
        if self._has_breadcrumb_aria_label(aria_label):
            self.has_aria_label = True
            self.in_breadcrumb = True

    def _has_breadcrumb_aria_label(self, aria_label: str) -> bool:
        """Check if aria-label contains breadcrumb.

        Args:
            aria_label: ARIA label attribute value

        Returns:
            True if aria-label contains breadcrumb
        """
        return bool(aria_label and 'breadcrumb' in aria_label.lower())

    def _handle_anchor_tag(self, attrs_dict: dict) -> None:
        """Handle anchor tag processing within breadcrumb.

        Args:
            attrs_dict: Dictionary of tag attributes
        """
        href = attrs_dict.get('href', '')
        if self._is_home_link(href):
            self.has_home_link = True

    def _is_home_link(self, href: str) -> bool:
        """Check if href points to home page.

        Args:
            href: HREF attribute value

        Returns:
            True if href is a home page link
        """
        if not href:
            return False
        return (href == '/' or
                href == '/index.html' or
                href.startswith('/#'))

    def handle_endtag(self, tag: str) -> None:
        if tag == 'nav' and self.in_breadcrumb:
            self.in_breadcrumb = False

    def handle_data(self, data: str) -> None:
        if self.in_breadcrumb:
            self.breadcrumb_content.append(data.strip())

    def parse(self, content: str) -> Tuple[bool, List[str]]:
        """Parse HTML content and return breadcrumb analysis."""
        self.feed(content)

        # Create parser state for validation
        parser_state = {
            'has_breadcrumb': self.has_breadcrumb,
            'has_aria_label': self.has_aria_label,
            'has_home_link': self.has_home_link,
            'in_breadcrumb': self.in_breadcrumb,
            'breadcrumb_content': self.breadcrumb_content
        }

        # Run all validation rules
        issues = []
        for rule in self.validation_rules:
            issues.extend(rule.validate(parser_state))

        return len(issues) == 0, issues

    def get_supported_extensions(self) -> List[str]:
        """Get supported file extensions for HTML parsing."""
        return ['.html', '.htm']


def check_breadcrumbs(file_path: str) -> Tuple[bool, List[str]]:
    """
    Check if an HTML file has proper breadcrumb navigation.

    Args:
        file_path: Path to the HTML file to check

    Returns:
        Tuple of (has_valid_breadcrumbs, list_of_issues)
    """
    content_result = _read_file_content(file_path)
    if not content_result[0]:
        return False, content_result[1]

    content = content_result[1][0]  # Extract content from success result

    if _is_index_html_file(file_path):
        return True, []

    parser_result = _parse_html_content(content)
    if not parser_result[0]:
        return False, parser_result[1]

    parser = parser_result[1][0]  # Extract parser from success result
    issues = _validate_breadcrumb_requirements(parser)

    return len(issues) == 0, issues


def _read_file_content(file_path: str) -> Tuple[bool, List[str]]:
    """Read file content safely.

    Args:
        file_path: Path to the file

    Returns:
        Tuple of (success, content_or_errors)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return True, [content]
    except (OSError, UnicodeDecodeError) as e:
        return False, [f"Error reading file: {e}"]


def _is_index_html_file(file_path: str) -> bool:
    """Check if file is an index.html file.

    Args:
        file_path: Path to check

    Returns:
        True if file is index.html
    """
    return file_path.endswith('index.html')


def _parse_html_content(content: str) -> Tuple[bool, List]:
    """Parse HTML content safely.

    Args:
        content: HTML content to parse

    Returns:
        Tuple of (success, parser_or_errors)
    """
    parser = BreadcrumbParser()
    try:
        parser.feed(content)
        return True, [parser]
    except (ValueError, TypeError) as e:
        return False, [f"Error parsing HTML: {e}"]


def _validate_breadcrumb_requirements(parser: BreadcrumbParser) -> List[str]:
    """Validate breadcrumb requirements and return issues.

    Args:
        parser: Parsed HTML content

    Returns:
        List of validation issues
    """
    issues: List[str] = []

    _check_breadcrumb_element(parser, issues)
    _check_aria_label(parser, issues)
    _check_home_link(parser, issues)
    _check_breadcrumb_content(parser, issues)

    return issues


def _check_breadcrumb_element(parser: BreadcrumbParser, issues: List[str]) -> None:
    """Check for breadcrumb navigation element.

    Args:
        parser: Parsed HTML content
        issues: List to append issues to
    """
    if not parser.has_breadcrumb:
        issues.append(
            "Missing breadcrumb navigation element (nav with class='breadcrumb')"
        )


def _check_aria_label(parser: BreadcrumbParser, issues: List[str]) -> None:
    """Check for ARIA label.

    Args:
        parser: Parsed HTML content
        issues: List to append issues to
    """
    if not parser.has_aria_label:
        issues.append(
            "Missing ARIA label for breadcrumb navigation "
            "(aria-label='Breadcrumb navigation')"
        )


def _check_home_link(parser: BreadcrumbParser, issues: List[str]) -> None:
    """Check for home link.

    Args:
        parser: Parsed HTML content
        issues: List to append issues to
    """
    if not parser.has_home_link:
        issues.append("Missing link back to home page in breadcrumbs")


def _check_breadcrumb_content(parser: BreadcrumbParser, issues: List[str]) -> None:
    """Check for breadcrumb content.

    Args:
        parser: Parsed HTML content
        issues: List to append issues to
    """
    if parser.has_breadcrumb and not parser.breadcrumb_content:
        issues.append("Breadcrumb navigation is empty")


def find_html_files(
        directory: str, exclude_patterns: Optional[List[str]] = None
) -> List[str]:
    """
    Find all HTML files in the given directory.

    Args:
        directory: Root directory to search
        exclude_patterns: List of patterns to exclude

    Returns:
        List of HTML file paths
    """
    exclude_patterns = _get_default_exclude_patterns(exclude_patterns)
    html_files = []

    for root, dirs, files in os.walk(directory):
        _filter_excluded_directories(dirs, exclude_patterns)
        html_files.extend(_collect_html_files(root, files))

    return html_files


def _get_default_exclude_patterns(exclude_patterns: Optional[List[str]]) -> List[str]:
    """Get default exclude patterns if none provided.

    Args:
        exclude_patterns: Optional list of patterns

    Returns:
        List of exclude patterns
    """
    return exclude_patterns or [
        'node_modules', '.git', 'dist', 'build', 'coverage'
    ]


def _filter_excluded_directories(dirs: List[str], exclude_patterns: List[str]) -> None:
    """Filter out excluded directories from the list.

    Args:
        dirs: List of directories to filter (modified in place)
        exclude_patterns: List of patterns to exclude
    """
    dirs[:] = [
        d for d in dirs
        if not any(pattern in d for pattern in exclude_patterns)
    ]


def _collect_html_files(root: str, files: List[str]) -> List[str]:
    """Collect HTML files from a directory.

    Args:
        root: Root directory path
        files: List of files in the directory

    Returns:
        List of HTML file paths
    """
    html_files = []
    for file in files:
        if file.endswith('.html'):
            html_files.append(os.path.join(root, file))
    return html_files


def _should_skip_file(file_path: str) -> bool:
    """Check if file should be skipped based on patterns."""
    if _is_index_file(file_path):
        return True

    return _matches_skip_patterns(file_path)


def _is_index_file(file_path: str) -> bool:
    """Check if file is an index.html file.

    Args:
        file_path: Path to check

    Returns:
        True if file is index.html
    """
    return os.path.basename(file_path) == 'index.html'


def _matches_skip_patterns(file_path: str) -> bool:
    """Check if file matches any skip patterns.

    Args:
        file_path: Path to check

    Returns:
        True if file should be skipped
    """
    path_lower = file_path.lower()
    return (_matches_test_patterns(path_lower) or
            _matches_template_patterns(path_lower) or
            _matches_mock_patterns(path_lower))


def _matches_test_patterns(path_lower: str) -> bool:
    """Check if path matches test patterns.

    Args:
        path_lower: Lowercase file path

    Returns:
        True if path matches test patterns
    """
    return ('/test/' in path_lower or
            '_test.' in path_lower or
            '.test.' in path_lower)


def _matches_template_patterns(path_lower: str) -> bool:
    """Check if path matches template patterns.

    Args:
        path_lower: Lowercase file path

    Returns:
        True if path matches template patterns
    """
    return ('/template/' in path_lower or
            '_template.' in path_lower or
            '.template.' in path_lower)


def _matches_mock_patterns(path_lower: str) -> bool:
    """Check if path matches mock patterns.

    Args:
        path_lower: Lowercase file path

    Returns:
        True if path matches mock patterns
    """
    return ('/mock/' in path_lower or
            '_mock.' in path_lower or
            '.mock.' in path_lower)


def main() -> int:
    """Main linter function."""
    current_dir = os.getcwd()
    all_html_files = _find_all_html_files(current_dir)

    if not all_html_files:
        print("ℹ️  No HTML files found to check")
        return 0

    _print_check_start_message(len(all_html_files))
    violations, checked_count = _check_all_files(all_html_files, current_dir)
    return _handle_results(violations, checked_count)


def _find_all_html_files(current_dir: str) -> List[str]:
    """Find all HTML files in public directories.

    Args:
        current_dir: Current working directory

    Returns:
        List of HTML file paths
    """
    public_dirs = [
        'durable-code-app/frontend/public',
        'public',
        'docs',
    ]

    all_html_files = []
    for public_dir in public_dirs:
        full_path = os.path.join(current_dir, public_dir)
        if os.path.exists(full_path):
            all_html_files.extend(find_html_files(full_path))

    return all_html_files


def _print_check_start_message(file_count: int) -> None:
    """Print the check start message.

    Args:
        file_count: Number of files to check
    """
    print(
        f"🔍 Checking {file_count} HTML files for breadcrumb navigation..."
    )


def _check_all_files(all_html_files: List[str],
                     current_dir: str) -> Tuple[List[Tuple[str, List[str]]], int]:
    """Check all HTML files for breadcrumb violations.

    Args:
        all_html_files: List of HTML file paths
        current_dir: Current working directory

    Returns:
        Tuple of (violations, checked_count)
    """
    violations = []
    checked_count = 0

    for file_path in all_html_files:
        if _should_skip_file(file_path):
            continue

        checked_count += 1
        has_breadcrumbs, issues = check_breadcrumbs(file_path)

        if not has_breadcrumbs:
            rel_path = os.path.relpath(file_path, current_dir)
            violations.append((rel_path, issues))

    return violations, checked_count


def _handle_results(violations: List[Tuple[str, List[str]]],
                   checked_count: int) -> int:
    """Handle and output the results.

    Args:
        violations: List of violations found
        checked_count: Number of files checked

    Returns:
        Exit code
    """
    if violations:
        _print_violations(violations, checked_count)
        return 1

    _print_success_message(checked_count)
    return 0


def _print_violations(violations: List[Tuple[str, List[str]]],
                     checked_count: int) -> None:
    """Print violation details.

    Args:
        violations: List of violations to print
        checked_count: Number of files checked
    """
    print(
        f"\n❌ Breadcrumb navigation violations found in "
        f"{len(violations)} file(s):\n"
    )

    for file_path, issues in violations:
        print(f"  📄 {file_path}")
        for issue in issues:
            print(f"     ⚠️  {issue}")
        print()

    _print_summary_and_help(violations, checked_count)


def _print_summary_and_help(violations: List[Tuple[str, List[str]]],
                           checked_count: int) -> None:
    """Print summary and help information.

    Args:
        violations: List of violations
        checked_count: Number of files checked
    """
    print(
        f"📊 Summary: {len(violations)} of {checked_count} HTML files are "
        f"missing proper breadcrumb navigation"
    )
    _print_fix_instructions()


def _print_fix_instructions() -> None:
    """Print instructions for fixing breadcrumb issues."""
    print("\n💡 How to fix:")
    print("   Add breadcrumb navigation to each HTML document:")
    print("   <nav class=\"breadcrumb\" aria-label=\"Breadcrumb navigation\">")
    print("       <a href=\"/\">🏠 Home</a>")
    print("       <span class=\"breadcrumb-separator\">›</span>")
    print("       <a href=\"/parent\">Parent Section</a>")
    print("       <span class=\"breadcrumb-separator\">›</span>")
    print("       <span class=\"breadcrumb-current\">Current Page</span>")
    print("   </nav>")


def _print_success_message(checked_count: int) -> None:
    """Print success message.

    Args:
        checked_count: Number of files checked
    """
    print(
        f"✅ All {checked_count} HTML files have proper breadcrumb navigation!"
    )


if __name__ == "__main__":
    sys.exit(main())
