#!/usr/bin/env python3
"""
Purpose: Unit tests for the file header validation linting rule
Scope: Testing header field detection, validation, and quality checks across file types
Overview: This comprehensive test suite validates the FileHeaderRule implementation, ensuring
    it correctly identifies missing headers, validates required fields, checks content quality,
    and supports multiple file types. Tests cover Python, TypeScript, JavaScript, HTML, YAML,
    and Markdown files with various header formats. The suite verifies field parsing logic,
    multi-line field handling, Overview word count validation, and proper error reporting.
    It also tests edge cases like files without headers, headers with placeholder text, and
    files that should be skipped. The tests ensure the rule provides helpful suggestions and
    maintains consistent behavior across all supported file types.
Dependencies: pytest, ast, pathlib, design_linters framework
Exports: Test classes and fixtures for FileHeaderRule validation
Interfaces: pytest test cases following standard test patterns
Implementation: Uses pytest fixtures and parameterized tests for comprehensive coverage
"""

import ast

import pytest
from design_linters.framework.interfaces import LintContext, Severity
from design_linters.rules.style.file_header_rules import FileHeaderRule


class TestFileHeaderRule:
    """Test suite for FileHeaderRule."""

    @pytest.fixture
    def rule(self):
        """Create a FileHeaderRule instance."""
        return FileHeaderRule()

    @pytest.fixture
    def context(self):
        """Create a basic lint context."""
        ctx = LintContext()
        ctx.file_path = "test_file.py"  # Test files should have headers too
        ctx.file_content = ""
        ctx.ast_tree = ast.parse("")
        return ctx

    def test_python_file_with_complete_header(self, rule, context):
        """Test Python file with all required fields."""
        content = '''"""
Purpose: Test module for validating header compliance in Python files
Scope: Unit testing of header validation logic for Python modules
Overview: This test module provides comprehensive validation of the header checking
    logic for Python files. It ensures that all required fields are present and properly
    formatted, validates content quality requirements, and checks that multi-line fields
    are correctly parsed. The module tests both positive cases with complete headers
    and negative cases with missing or inadequate fields.
Dependencies: pytest framework, ast module for parsing, design_linters for rule implementation
Exports: TestFileHeaderRule class with comprehensive test cases
Interfaces: Standard pytest test methods for validation scenarios
Implementation: Uses fixtures and parameterized tests for thorough coverage
"""

def test_function():
    pass
'''
        context.file_content = content
        context.ast_tree = ast.parse(content)

        violations = rule.check(context)

        # Should have no violations for a complete header
        assert len(violations) == 0

    def test_python_file_missing_header(self, rule, context):
        """Test Python file with no header."""
        content = """def test_function():
    pass
"""
        context.file_content = content
        context.ast_tree = ast.parse(content)

        violations = rule.check(context)

        # Should have violations for missing header
        assert len(violations) > 0
        assert any("Missing file header" in v.message for v in violations)

    def test_python_file_missing_required_fields(self, rule, context):
        """Test Python file with incomplete header."""
        content = '''"""
This is a simple module description without proper fields.
"""

def test_function():
    pass
'''
        context.file_content = content
        context.ast_tree = ast.parse(content)

        violations = rule.check(context)

        # Should have violations for missing required fields
        assert len(violations) > 0
        assert any("Missing required header fields" in v.message for v in violations)

    def test_overview_word_count_validation(self, rule, context):
        """Test Overview field word count requirement."""
        content = '''"""
Purpose: Test module for validation
Scope: Testing header validation
Overview: Short overview text
Dependencies: pytest
Exports: Test class
Interfaces: Test methods
Implementation: Test patterns
"""

def test_function():
    pass
'''
        context.file_content = content
        context.ast_tree = ast.parse(content)

        violations = rule.check(context)

        # Should have violation for brief Overview
        assert any("Overview field too brief" in v.message for v in violations)

    def test_multiline_overview_parsing(self, rule, context):
        """Test that multi-line Overview fields are correctly parsed."""
        content = '''"""
Purpose: Test module for validating multi-line overview field parsing capability
Scope: Testing multi-line field parsing in Python docstring headers
Overview: This is a comprehensive overview that spans multiple lines to ensure
    the parser correctly handles continuation lines in header fields. It contains
    enough words to satisfy the minimum word count requirement. The parser should
    collect all these lines and count the total words correctly, not just the first
    line of the overview field.
Dependencies: pytest, ast module, design_linters framework
Exports: Test functions for validation
Interfaces: Standard test interfaces
Implementation: Comprehensive test coverage patterns
"""

def test_function():
    pass
'''
        context.file_content = content
        context.ast_tree = ast.parse(content)

        violations = rule.check(context)

        # Should have no Overview word count violation
        assert not any("Overview field too brief" in v.message for v in violations)

    def test_typescript_file_header(self, rule, context):
        """Test TypeScript file header validation."""
        content = """/**
 * Purpose: React component for displaying user profile information
 * Scope: User interface components for profile management
 * Overview: This component renders user profile data including avatar, name, bio,
 *     and social links. It handles loading states, error conditions, and provides
 *     edit functionality for authenticated users. The component uses React hooks for
 *     state management and integrates with the user API service for data fetching.
 * Dependencies: React, user API service, styling utilities
 * Exports: UserProfile component as default export
 * Interfaces: UserProfileProps interface with user data
 * Implementation: State management with React hooks
 */

export default function UserProfile() {
    return null;
}
"""
        context.file_path = "test_file.tsx"
        context.file_content = content
        # For TypeScript files, we still need an AST (even if minimal)
        context.ast_tree = ast.parse("")

        violations = rule.check(context)

        # Should have no violations for complete TypeScript header
        assert len(violations) == 0

    def test_markdown_file_header(self, rule, context):
        """Test Markdown file header validation."""
        content = """# Documentation Title

**Purpose**: Comprehensive guide for using the application features
**Scope**: End-user documentation for all application modules

---

## Overview
Content starts here...
"""
        context.file_path = "test_file.md"
        context.file_content = content
        context.ast_tree = ast.parse("")

        violations = rule.check(context)

        # Should have violation for missing Overview in header section
        assert any("Missing required Overview field" in v.message for v in violations)

    def test_skip_test_files(self):
        """Test that test files can be skipped when configured."""
        rule = FileHeaderRule(
            config={"skip_test_files": True}
        )  # Changed from check_test_files
        context = LintContext()
        context.file_path = "test_something.py"
        context.file_content = "# No header needed for test files"
        context.ast_tree = ast.parse("")

        violations = rule.check(context)

        # Should have no violations for test files when check_test_files is False
        assert len(violations) == 0

    def test_skip_init_files(self, rule, context):
        """Test that __init__.py files are skipped."""
        context.file_path = "__init__.py"
        context.file_content = "# Empty init file"

        violations = rule.check(context)

        # Should have no violations for __init__.py files
        assert len(violations) == 0

    def test_html_file_header(self, rule, context):
        """Test HTML file header validation."""
        content = """<!DOCTYPE html>
<!--
Purpose: Main application template for the web interface
Scope: HTML structure for single-page application
Dependencies: Bootstrap CSS, Vue.js framework
-->
<html lang="en">
<head>
    <title>Test</title>
</head>
<body>
</body>
</html>
"""
        context.file_path = "test_file.html"
        context.file_content = content
        context.ast_tree = ast.parse("")

        violations = rule.check(context)

        # Should have violations for missing Overview and other fields
        assert len(violations) > 0

    def test_yaml_file_header(self, rule, context):
        """Test YAML file header validation."""
        content = """# Purpose: Configuration for CI/CD pipeline
# Scope: GitHub Actions workflow configuration
# Dependencies: Node.js, Python, Docker

name: CI Pipeline
on: [push, pull_request]
"""
        context.file_path = "test_file.yml"
        context.file_content = content
        context.ast_tree = ast.parse("")

        violations = rule.check(context)

        # Should have violation for missing Overview
        assert any("Missing required Overview field" in v.message for v in violations)

    def test_placeholder_text_detection(self, rule, context):
        """Test detection of placeholder text in fields."""
        content = '''"""
Purpose: TODO
Scope: TBD
Overview: This is a placeholder overview that needs to be filled in later
Dependencies: TODO
Exports: TODO
Interfaces: TODO
Implementation: TODO
"""

def test_function():
    pass
'''
        context.file_content = content
        context.ast_tree = ast.parse(content)

        violations = rule.check(context)

        # Should have violations for placeholder text
        assert any("placeholder text" in v.message for v in violations)

    def test_field_parsing_with_colons(self, rule, context):
        """Test that fields with colons in values are parsed correctly."""
        content = '''"""
Purpose: Module for parsing URLs like http://example.com
Scope: URL validation and parsing utilities
Overview: This module provides comprehensive URL parsing functionality including
    validation of protocols like http:// and https://, extraction of components,
    and normalization of URLs. It handles various URL formats and edge cases to
    ensure reliable URL processing throughout the application.
Dependencies: urllib.parse, validators library
Exports: parse_url(), validate_url(), normalize_url() functions
Interfaces: URL parsing and validation functions
Implementation: Uses urllib.parse with custom validation logic
"""

def test_function():
    pass
'''
        context.file_content = content
        context.ast_tree = ast.parse(content)

        violations = rule.check(context)

        # Should handle colons in field values correctly
        assert len(violations) == 0

    def test_recommended_field_warnings(self, rule, context):
        """Test that missing recommended fields generate warnings."""
        content = '''"""
Purpose: Basic module for testing recommended field warnings
Scope: Testing the detection of missing recommended fields
Overview: This module has all required fields but is missing the recommended
    Implementation field. The linter should generate a warning for this missing
    field when running in strict mode to encourage comprehensive documentation.
Dependencies: Standard library only
Exports: Basic test functions
Interfaces: Simple function interfaces
"""

def test_function():
    pass
'''
        context.file_content = content
        context.ast_tree = ast.parse(content)

        violations = rule.check(context)

        # Should have warning for missing Implementation field
        assert any("Missing recommended header field" in v.message for v in violations)
        assert any(v.severity == Severity.WARNING for v in violations)

    @pytest.mark.parametrize(
        "file_ext,header_start",
        [
            (".py", '"""'),
            (".ts", "/**"),
            (".tsx", "/**"),
            (".js", "/**"),
            (".jsx", "/**"),
        ],
    )
    def test_file_type_detection(self, rule, file_ext, header_start):
        """Test that different file types are detected correctly."""
        context = LintContext()
        context.file_path = f"test_file{file_ext}"
        context.file_content = f"{header_start}\nPurpose: Test\n"
        context.ast_tree = ast.parse("")

        violations = rule.check(context)

        # Should detect the file type and check for violations
        assert len(violations) > 0  # Missing required fields


class TestFileHeaderFieldParsing:
    """Test the field parsing logic specifically."""

    @pytest.fixture
    def rule(self):
        """Create a FileHeaderRule instance."""
        return FileHeaderRule()

    def test_parse_python_header_fields(self, rule):
        """Test parsing of Python docstring header fields."""
        header_content = '''"""
Purpose: Test module for validation
Scope: Unit testing
Overview: This is a comprehensive overview spanning
    multiple lines with continuation
    and more text here.
Dependencies: pytest, unittest
Exports: TestClass, test_function
"""'''

        pattern = rule.FILE_CONFIGS[".py"]["field_pattern"]
        fields = rule._parse_header_fields(header_content, pattern)

        assert "purpose" in fields
        assert fields["purpose"] == "Test module for validation"
        assert "scope" in fields
        assert fields["scope"] == "Unit testing"
        assert "overview" in fields
        # Check that multi-line Overview is fully captured
        assert "multiple lines" in fields["overview"]
        assert "more text here" in fields["overview"]

    def test_parse_typescript_header_fields(self, rule):
        """Test parsing of TypeScript comment header fields."""
        header_content = """/**
 * Purpose: Component for user interface
 * Scope: UI components
 * Overview: A detailed overview that
 *     continues on multiple lines
 *     with proper indentation.
 * Dependencies: React, Redux
 */"""

        pattern = rule.FILE_CONFIGS[".ts"]["field_pattern"]
        fields = rule._parse_header_fields(header_content, pattern)

        assert "purpose" in fields
        assert "overview" in fields
        assert "multiple lines" in fields["overview"]
        assert "proper indentation" in fields["overview"]

    def test_parse_markdown_header_fields(self, rule):
        """Test parsing of Markdown header fields."""
        header_content = """# Title

**Purpose**: Documentation for the system
**Scope**: All system components

---"""

        pattern = rule.FILE_CONFIGS[".md"]["field_pattern"]
        fields = rule._parse_header_fields(header_content, pattern)

        assert "purpose" in fields
        assert fields["purpose"] == "Documentation for the system"
        assert "scope" in fields
