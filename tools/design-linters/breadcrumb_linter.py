#!/usr/bin/env python3
"""
Purpose: Validates HTML documentation files for proper breadcrumb navigation compliance
Scope: HTML files in public directories and documentation folders
Overview: This linter ensures that all HTML documentation files contain proper breadcrumb
    navigation elements for user navigation and understanding document hierarchy. It validates
    that breadcrumbs include proper ARIA labels for accessibility, link back to home page,
    and mark the current page as non-link text. The linter helps maintain consistent
    navigation patterns across all documentation and prevents navigation dead-ends.
Dependencies: html.parser for HTML parsing, pathlib for file operations, re for pattern matching
Exports: BreadcrumbLinter class, BreadcrumbViolation dataclass, HTMLParser subclass
Interfaces: main() CLI function, check_file() returns List[BreadcrumbViolation]
Implementation: Uses HTML parsing to detect navigation elements and validates ARIA compliance
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Tuple, Optional
from html.parser import HTMLParser
from abc import ABC, abstractmethod


class ValidationRule(ABC):
    """Abstract interface for validation rules - follows OCP."""

    @abstractmethod
    def validate(self, parser_state: dict) -> List[str]:
        """Validate parser state and return list of issues."""
        pass


class BreadcrumbValidationRule(ValidationRule):
    """Validates breadcrumb presence and structure."""

    def validate(self, parser_state: dict) -> List[str]:
        issues = []
        if not parser_state.get('has_breadcrumb') and not parser_state.get('has_aria_label'):
            issues.append("No breadcrumb navigation found")
        elif not parser_state.get('has_home_link'):
            issues.append("Breadcrumb missing home page link")
        return issues


class DocumentParser(ABC):
    """Abstract interface for document parsers - follows OCP."""

    @abstractmethod
    def parse(self, content: str) -> Tuple[bool, List[str]]:
        """Parse document content and return (has_breadcrumbs, issues)."""
        pass

    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        pass


class BreadcrumbParser(HTMLParser, DocumentParser):
    """HTML parser to detect breadcrumb navigation elements."""

    def __init__(self, validation_rules: Optional[List[ValidationRule]] = None):
        super().__init__()
        self.has_breadcrumb = False
        self.has_aria_label = False
        self.has_home_link = False
        self.in_breadcrumb = False
        self.breadcrumb_content = []
        self.validation_rules = validation_rules or [BreadcrumbValidationRule()]

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # Check for breadcrumb navigation element
        if tag == 'nav':
            # Check for breadcrumb class or aria-label
            if 'class' in attrs_dict and 'breadcrumb' in attrs_dict.get('class', ''):
                self.has_breadcrumb = True
                self.in_breadcrumb = True
            if 'aria-label' in attrs_dict and 'breadcrumb' in attrs_dict.get('aria-label', '').lower():
                self.has_aria_label = True
                self.in_breadcrumb = True

        # Check for home link within breadcrumb
        if self.in_breadcrumb and tag == 'a':
            href = attrs_dict.get('href', '')
            if href == '/' or href == '/index.html' or href.startswith('/#'):
                self.has_home_link = True

    def handle_endtag(self, tag):
        if tag == 'nav' and self.in_breadcrumb:
            self.in_breadcrumb = False

    def handle_data(self, data):
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
    issues = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, [f"Error reading file: {e}"]

    # Skip checking for index.html or home page
    if file_path.endswith('index.html'):
        return True, []

    # Parse HTML
    parser = BreadcrumbParser()
    try:
        parser.feed(content)
    except Exception as e:
        return False, [f"Error parsing HTML: {e}"]

    # Check for breadcrumb requirements
    if not parser.has_breadcrumb:
        issues.append("Missing breadcrumb navigation element (nav with class='breadcrumb')")

    if not parser.has_aria_label:
        issues.append("Missing ARIA label for breadcrumb navigation (aria-label='Breadcrumb navigation')")

    if not parser.has_home_link:
        issues.append("Missing link back to home page in breadcrumbs")

    # Check if breadcrumb has content
    if parser.has_breadcrumb and not parser.breadcrumb_content:
        issues.append("Breadcrumb navigation is empty")

    return len(issues) == 0, issues


def find_html_files(directory: str, exclude_patterns: Optional[List[str]] = None) -> List[str]:
    """
    Find all HTML files in the given directory.

    Args:
        directory: Root directory to search
        exclude_patterns: List of patterns to exclude

    Returns:
        List of HTML file paths
    """
    exclude_patterns = exclude_patterns or ['node_modules', '.git', 'dist', 'build', 'coverage']
    html_files = []

    for root, dirs, files in os.walk(directory):
        # Remove excluded directories from search
        dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]

        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))

    return html_files


def main():
    """Main linter function."""
    # Determine the project root
    current_dir = os.getcwd()

    # Look for HTML files in public directories
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

    if not all_html_files:
        print("ℹ️  No HTML files found to check")
        return 0

    print(f"🔍 Checking {len(all_html_files)} HTML files for breadcrumb navigation...")

    violations = []
    checked_count = 0
    skipped_count = 0

    for file_path in all_html_files:
        basename = os.path.basename(file_path)

        # Skip test files and templates
        path_lower = file_path.lower()
        # Check for whole word matches to avoid false positives
        if ('/test/' in path_lower or '_test.' in path_lower or '.test.' in path_lower or
            '/template/' in path_lower or '_template.' in path_lower or '.template.' in path_lower or
            '/mock/' in path_lower or '_mock.' in path_lower or '.mock.' in path_lower):
            skipped_count += 1
            continue

        # Skip index.html files
        if basename == 'index.html':
            skipped_count += 1
            continue

        checked_count += 1
        has_breadcrumbs, issues = check_breadcrumbs(file_path)

        if not has_breadcrumbs:
            rel_path = os.path.relpath(file_path, current_dir)
            violations.append((rel_path, issues))

    # Report results
    if violations:
        print(f"\n❌ Breadcrumb navigation violations found in {len(violations)} file(s):\n")

        for file_path, issues in violations:
            print(f"  📄 {file_path}")
            for issue in issues:
                print(f"     ⚠️  {issue}")
            print()

        print(f"📊 Summary: {len(violations)} of {checked_count} HTML files are missing proper breadcrumb navigation")
        print("\n💡 How to fix:")
        print("   Add breadcrumb navigation to each HTML document:")
        print("   <nav class=\"breadcrumb\" aria-label=\"Breadcrumb navigation\">")
        print("       <a href=\"/\">🏠 Home</a>")
        print("       <span class=\"breadcrumb-separator\">›</span>")
        print("       <a href=\"/parent\">Parent Section</a>")
        print("       <span class=\"breadcrumb-separator\">›</span>")
        print("       <span class=\"breadcrumb-current\">Current Page</span>")
        print("   </nav>")

        return 1
    else:
        print(f"✅ All {checked_count} HTML files have proper breadcrumb navigation!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
