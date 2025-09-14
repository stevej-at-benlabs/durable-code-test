#!/usr/bin/env python3
"""Unit tests for the Magic Number Detector."""

import ast
import os
import tempfile
from pathlib import Path

import pytest
from magic_number_detector import (
    MagicNumberDetector,
    MagicNumberViolation,
    add_parent_refs,
    analyze_directory,
    analyze_file,
)


class TestMagicNumberDetector:
    """Test suite for magic number detection."""

    def test_detects_numeric_magic_numbers(self):
        """Test detection of numeric magic numbers."""
        code = """
def calculate_price(quantity):
    return quantity * 42.5  # Magic number!
        """
        tree = ast.parse(code)
        add_parent_refs(tree)
        detector = MagicNumberDetector("test.py", ignore_tests=False)
        detector.visit(tree)

        assert len(detector.violations) == 1
        assert detector.violations[0].value == 42.5
        assert "calculate_price" in detector.violations[0].context

    def test_allows_common_numbers(self):
        """Test that common numbers are allowed."""
        code = """
def init_values():
    x = 0
    y = 1
    z = -1
    percentage = 100
    binary = 1024
    return x + y + z
        """
        tree = ast.parse(code)
        add_parent_refs(tree)
        detector = MagicNumberDetector("test.py")
        detector.visit(tree)

        assert len(detector.violations) == 0

    def test_detects_string_magic_literals(self):
        """Test detection of magic string literals."""
        code = """
def get_status():
    return "ACTIVE_STATUS"  # Magic string!
        """
        tree = ast.parse(code)
        add_parent_refs(tree)
        detector = MagicNumberDetector("test.py", ignore_tests=False)
        detector.visit(tree)

        assert len(detector.violations) == 1
        assert detector.violations[0].value == "ACTIVE_STATUS"

    def test_allows_common_strings(self):
        """Test that common strings are allowed."""
        code = """
def open_file():
    with open("file.txt", "r") as f:
        content = f.read()
    return content.split(",")
        """
        tree = ast.parse(code)
        add_parent_refs(tree)
        detector = MagicNumberDetector("test.py", ignore_tests=False)
        detector.visit(tree)

        # Should only detect "file.txt", not "r" or ","
        violations = [v for v in detector.violations if v.value in ["r", ","]]
        assert len(violations) == 0

    def test_ignores_constants(self):
        """Test that constant definitions are ignored."""
        code = """
MAX_RETRIES = 5
DEFAULT_TIMEOUT = 30
API_KEY = "secret-key-123"

def retry():
    return MAX_RETRIES
        """
        tree = ast.parse(code)
        add_parent_refs(tree)
        detector = MagicNumberDetector("test.py")
        detector.visit(tree)

        # Constants definitions should not be violations
        violations = [
            v for v in detector.violations if v.value in [5, 30, "secret-key-123"]
        ]
        assert len(violations) == 0

    def test_acceptable_contexts(self):
        """Test that certain contexts are acceptable for numbers."""
        code = """
def process_list(items):
    # Array indexing is OK
    first = items[0]
    last = items[-1]

    # Range is OK
    for i in range(10):
        pass

    # Slicing is OK
    subset = items[1:5]

    return first, last
        """
        tree = ast.parse(code)
        add_parent_refs(tree)
        detector = MagicNumberDetector("test.py", ignore_tests=False)
        detector.visit(tree)

        # The 5 in slice might be detected, but indices and range should not
        for v in detector.violations:
            assert v.value not in [0, -1, 1]  # indices
            assert v.value != 10  # range argument

    def test_string_keys_ignored(self):
        """Test that dictionary keys are generally ignored."""
        code = """
def get_config():
    config = {
        "database": "postgres",
        "port": 5432,
        "timeout": 30
    }
    return config["database"]
        """
        tree = ast.parse(code)
        add_parent_refs(tree)
        detector = MagicNumberDetector("test.py", ignore_tests=False)
        detector.visit(tree)

        # Dictionary string keys should not be violations
        string_violations = [
            v for v in detector.violations if v.value in ["database", "port", "timeout"]
        ]
        assert len(string_violations) == 0

        # But numeric values should be detected
        numeric_violations = [v for v in detector.violations if v.value in [5432, 30]]
        assert len(numeric_violations) == 2

    def test_ignore_test_files(self):
        """Test that test files can be ignored."""
        code = """
def calculation():
    assert calculate(5) == 25
    assert calculate(10) == 100
        """

        # Test file (should be ignored by default)
        tree = ast.parse(code)
        add_parent_refs(tree)
        detector = MagicNumberDetector("test_calc.py", ignore_tests=True)
        detector.visit(tree)
        assert len(detector.violations) == 0

        # Non-test file (should detect violations)
        detector = MagicNumberDetector("calc.py", ignore_tests=True)
        detector.visit(tree)
        assert len(detector.violations) > 0


class TestMagicNumberViolation:
    """Test the MagicNumberViolation class."""

    def test_suggestion_generation_for_numbers(self):
        """Test constant name suggestions for numbers."""
        violation = MagicNumberViolation("test.py", 10, 5, 42, "in main")
        assert "THRESHOLD_42" in violation.suggestion

        violation = MagicNumberViolation("test.py", 10, 5, 3.14, "in main")
        assert "THRESHOLD_3_14" in violation.suggestion

        violation = MagicNumberViolation("test.py", 10, 5, -5, "in main")
        assert "NEG_5" in violation.suggestion

    def test_suggestion_generation_for_strings(self):
        """Test constant name suggestions for strings."""
        violation = MagicNumberViolation("test.py", 10, 5, "active-status", "in main")
        assert "ACTIVE_STATUS" in violation.suggestion

        violation = MagicNumberViolation(
            "test.py", 10, 5, "very long string that should be truncated", "in main"
        )
        assert len(violation.suggestion) <= 40  # Should be truncated

    def test_to_dict(self):
        """Test conversion to dictionary."""
        violation = MagicNumberViolation("test.py", 10, 5, 42, "in calculate")
        result = violation.to_dict()

        assert result["file"] == "test.py"
        assert result["line"] == 10
        assert result["column"] == 5
        assert result["value"] == "42"
        assert result["type"] == "int"
        assert result["context"] == "in calculate"
        assert "suggestion" in result


class TestFileAnalysis:
    """Test file and directory analysis functions."""

    def test_analyze_file(self):
        """Test analyzing a single file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
def calculate_tax(amount):
    return amount * 0.15  # 15% tax - magic number!

MAX_AMOUNT = 10000  # This is OK - constant
            """
            )
            f.flush()

            violations = analyze_file(f.name)

            # Clean up
            os.unlink(f.name)

            assert len(violations) == 1
            assert violations[0].value == 0.15

    def test_analyze_directory(self):
        """Test analyzing a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            file1 = Path(tmpdir) / "module1.py"
            file1.write_text(
                """
def process():
    return 42  # Magic number
            """
            )

            file2 = Path(tmpdir) / "module2.py"
            file2.write_text(
                """
CONSTANT = 100  # OK

def calculate():
    return CONSTANT * 0.5  # Magic number
            """
            )

            # Excluded file
            test_file = Path(tmpdir) / "test_module.py"
            test_file.write_text(
                """
def test_something():
    assert 1 + 1 == 2  # Should be excluded
            """
            )

            violations = analyze_directory(tmpdir)

            # Should find violations in module1 and module2, but not test_module
            assert len(violations) >= 2
            values = [v.value for v in violations]
            assert 42 in values
            assert 0.5 in values


class TestSpecialNumbers:
    """Test special number detection."""

    def test_special_number_suggestions(self):
        """Test that special numbers get appropriate suggestions."""
        test_cases = [
            (0, "ZERO_VALUE"),
            (1, "SINGLE_ITEM"),
            (100, "PERCENTAGE_MAX"),
            (60, "SECONDS_PER_MINUTE"),
            (3600, "SECONDS_PER_HOUR"),
        ]

        for value, expected in test_cases:
            violation = MagicNumberViolation("test.py", 1, 1, value, "test")
            assert expected in violation.suggestion


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
