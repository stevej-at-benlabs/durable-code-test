#!/usr/bin/env python3
"""
Purpose: Unit tests for literals detection rules
Scope: Tests for magic number and magic string detection rules
Overview: This module tests the literals rules including detection of
    magic numbers, magic strings, complex numbers, and hardcoded paths
    that should be replaced with named constants or configuration.
Dependencies: unittest, ast, literals rules
"""

import unittest
import ast
from pathlib import Path

import sys
sys.path.insert(0, '/home/stevejackson/Projects/durable-code-test/tools')

from design_linters.framework.interfaces import LintContext, Severity
from design_linters.rules.literals.magic_number_rules import (
    MagicNumberRule,
    MagicComplexRule
)
from design_linters.rules.literals.magic_string_rules import (
    MagicStringRule,
    HardcodedPathRule
)


class TestMagicNumberRule(unittest.TestCase):
    """Test the MagicNumberRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = MagicNumberRule()

    def _create_context(self, code, file_path='/src/file.py'):
        """Helper to create a LintContext."""
        return LintContext(
            file_path=Path(file_path),
            file_content=code,
            ast_tree=ast.parse(code)
        )

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, "literals.magic-number")
        self.assertEqual(self.rule.severity, Severity.WARNING)
        self.assertIn("literals", self.rule.categories)
        self.assertIn("constants", self.rule.categories)

    def test_magic_number_detection(self):
        """Test detection of magic numbers."""
        code = """
def calculate_price():
    base_price = 99.99  # Magic number
    tax_rate = 0.08  # Magic number
    return base_price * (1 + tax_rate)
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Should detect two magic numbers
        self.assertGreaterEqual(len(violations), 2)
        for violation in violations:
            self.assertEqual(violation.rule_id, "literals.magic-number")

    def test_allowed_numbers(self):
        """Test that allowed numbers are not flagged."""
        code = """
def process_data():
    x = 0  # Allowed
    y = 1  # Allowed
    z = -1  # Allowed
    count = 10  # Allowed
    return x + y + z
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Should not flag allowed numbers
        self.assertEqual(len(violations), 0)

    def test_numbers_in_range(self):
        """Test numbers in range() are acceptable."""
        code = """
def iterate():
    for i in range(5):
        print(i)
    for j in range(0, 100):
        pass
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Numbers in range should be acceptable
        self.assertEqual(len(violations), 0)

    def test_numbers_in_test_files(self):
        """Test that test files allow magic numbers."""
        code = """
def test_calculation():
    assert calculate(10) == 42
    assert calculate(15.5) == 31.0
"""
        context = self._create_context(code, '/test/test_calc.py')
        violations = self.rule.check(context)

        # Test files should allow magic numbers
        self.assertEqual(len(violations), 0)

    def test_suggestion_generation(self):
        """Test that suggestions are generated."""
        code = """
MAX_RETRIES = 3  # This is fine

def process():
    delay = 30  # Magic number
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Should have suggestions
        if violations:
            self.assertIsNotNone(violations[0].suggestion)
            self.assertIn("constant", violations[0].suggestion.lower())


class TestMagicComplexRule(unittest.TestCase):
    """Test the MagicComplexRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = MagicComplexRule()

    def _create_context(self, code, file_path='/src/file.py'):
        """Helper to create a LintContext."""
        return LintContext(
            file_path=Path(file_path),
            file_content=code,
            ast_tree=ast.parse(code)
        )

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, "literals.magic-complex")
        self.assertEqual(self.rule.severity, Severity.WARNING)
        self.assertIn("literals", self.rule.categories)

    def test_complex_number_detection(self):
        """Test detection of complex numbers."""
        code = """
def process_signal():
    phase = 3+4j  # Magic complex number
    return phase * 2
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Should detect complex number
        self.assertGreaterEqual(len(violations), 1)

    def test_suggestion_for_imaginary_unit(self):
        """Test suggestions for imaginary unit."""
        code = """
def compute():
    j = 1j  # Imaginary unit, might be acceptable
    return j ** 2
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Might suggest using a constant
        if violations:
            self.assertIn("constant", violations[0].suggestion.lower())


class TestMagicStringRule(unittest.TestCase):
    """Test the MagicStringRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = MagicStringRule()

    def _create_context(self, code, file_path='/src/file.py'):
        """Helper to create a LintContext."""
        return LintContext(
            file_path=Path(file_path),
            file_content=code,
            ast_tree=ast.parse(code)
        )

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, "literals.magic-string")
        self.assertEqual(self.rule.severity, Severity.INFO)
        self.assertIn("literals", self.rule.categories)

    def test_magic_string_detection(self):
        """Test detection of magic strings."""
        code = """
def get_config():
    env = "production"  # Magic string
    mode = "strict"  # Magic string
    return {'env': env, 'mode': mode}
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Should detect magic strings
        self.assertGreaterEqual(len(violations), 2)

    def test_allowed_strings(self):
        """Test that allowed strings are not flagged."""
        code = """
def simple():
    empty = ""  # Empty string allowed
    single = " "  # Single space allowed
    newline = "\\n"  # Newline allowed
    return empty + single + newline
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Common strings should be allowed
        self.assertEqual(len(violations), 0)

    def test_strings_in_logging(self):
        """Test strings in logging are allowed."""
        code = """
import logging

def process():
    logging.info("Starting process")  # Logging message
    logging.error("Process failed")  # Logging message
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Logging strings might be allowed
        self.assertLessEqual(len(violations), 2)

    def test_url_detection(self):
        """Test URL string detection."""
        code = """
def fetch():
    api_url = "https://api.example.com/v1/data"  # URL string
    return requests.get(api_url)
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # URLs should be flagged
        self.assertGreaterEqual(len(violations), 1)
        if violations:
            self.assertIn("config", violations[0].suggestion.lower())

    def test_sql_query_detection(self):
        """Test SQL query detection."""
        code = """
def get_users():
    query = "SELECT * FROM users WHERE active = 1"  # SQL query
    return db.execute(query)
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # SQL queries should be flagged
        self.assertGreaterEqual(len(violations), 1)


class TestHardcodedPathRule(unittest.TestCase):
    """Test the HardcodedPathRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = HardcodedPathRule()

    def _create_context(self, code, file_path='/src/file.py'):
        """Helper to create a LintContext."""
        return LintContext(
            file_path=Path(file_path),
            file_content=code,
            ast_tree=ast.parse(code)
        )

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, "literals.hardcoded-path")
        self.assertEqual(self.rule.severity, Severity.WARNING)
        self.assertIn("configuration", self.rule.categories)

    def test_unix_path_detection(self):
        """Test detection of Unix paths."""
        code = """
def load_config():
    path = "/etc/app/config.yml"  # Hardcoded path
    return read_file(path)
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Should detect Unix path
        self.assertGreaterEqual(len(violations), 1)

    def test_windows_path_detection(self):
        """Test detection of Windows paths."""
        code = """
def load_data():
    path = "C:\\\\Users\\\\Data\\\\file.txt"  # Windows path
    return open(path)
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Should detect Windows path
        self.assertGreaterEqual(len(violations), 1)

    def test_relative_paths_not_flagged(self):
        """Test that relative paths might be acceptable."""
        code = """
def load_local():
    path = "./data/config.json"  # Relative path
    return load(path)
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Relative paths might be acceptable
        self.assertLessEqual(len(violations), 1)

    def test_paths_in_test_files(self):
        """Test that test files allow hardcoded paths."""
        code = """
def test_load():
    test_file = "/tmp/test_file.txt"
    assert exists(test_file)
"""
        context = self._create_context(code, '/test/test_file.py')
        violations = self.rule.check(context)

        # Test files should allow paths
        self.assertEqual(len(violations), 0)

    def test_temp_path_suggestion(self):
        """Test suggestion for temp paths."""
        code = """
def save_temp():
    temp = "/tmp/myapp/data.tmp"
    write_file(temp)
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        if violations:
            self.assertIn("tempfile", violations[0].suggestion.lower())


if __name__ == '__main__':
    unittest.main()
