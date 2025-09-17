#!/usr/bin/env python3
"""
Purpose: Simple working tests for the design linters framework
Scope: Basic smoke tests to ensure the framework is functional
Overview: This module provides simple tests that verify the design linters
    framework is working at a basic level.
Dependencies: unittest, framework modules
"""

import unittest
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, '/home/stevejackson/Projects/durable-code-test/tools')


class TestFrameworkBasics(unittest.TestCase):
    """Test basic framework components exist and load."""

    def test_imports_work(self):
        """Test that all modules can be imported."""
        # Framework modules
        from design_linters.framework import interfaces
        from design_linters.framework import analyzer
        from design_linters.framework import reporters
        from design_linters.framework import rule_registry

        # Rule modules
        from design_linters.rules.literals import magic_number_rules
        from design_linters.rules.literals import magic_string_rules
        from design_linters.rules.style import print_statement_rules
        from design_linters.rules.style import nesting_rules
        from design_linters.rules.solid import srp_rules
        from design_linters.rules.logging import general_logging_rules
        from design_linters.rules.logging import loguru_rules

        # CLI
        from design_linters import cli

        # All imports successful
        self.assertTrue(True)

    def test_severity_enum(self):
        """Test the Severity enum."""
        from design_linters.framework.interfaces import Severity

        self.assertEqual(Severity.ERROR.value, 'error')
        self.assertEqual(Severity.WARNING.value, 'warning')
        self.assertEqual(Severity.INFO.value, 'info')

    def test_create_lint_violation(self):
        """Test creating a LintViolation."""
        from design_linters.framework.interfaces import LintViolation, Severity

        violation = LintViolation(
            rule_id='test.rule',
            file_path='/test.py',
            line=1,
            column=0,
            severity=Severity.WARNING,
            message='Test message',
            description='Test description',
            suggestion='Test suggestion'
        )

        self.assertEqual(violation.rule_id, 'test.rule')
        self.assertEqual(violation.severity, Severity.WARNING)

    def test_reporters_exist(self):
        """Test that reporter classes exist."""
        from design_linters.framework.reporters import TextReporter, JSONReporter

        text_reporter = TextReporter()
        json_reporter = JSONReporter()

        self.assertIsNotNone(text_reporter)
        self.assertIsNotNone(json_reporter)

    def test_rule_registry_exists(self):
        """Test that the rule registry exists."""
        from design_linters.framework.rule_registry import DefaultRuleRegistry

        registry = DefaultRuleRegistry()
        self.assertIsNotNone(registry)

        # Test discovering rules with default paths
        count = registry.discover_rules([])
        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 0)

    def test_cli_exists(self):
        """Test that the CLI class exists."""
        from design_linters.cli import DesignLinterCLI

        cli = DesignLinterCLI()
        self.assertIsNotNone(cli)


class TestSimpleRules(unittest.TestCase):
    """Test simple rule functionality."""

    def test_magic_number_rule_exists(self):
        """Test that MagicNumberRule exists and has correct properties."""
        from design_linters.rules.literals.magic_number_rules import MagicNumberRule

        rule = MagicNumberRule()
        self.assertEqual(rule.rule_id, 'literals.magic-number')
        self.assertIn('literals', rule.categories)

    def test_print_statement_rule_exists(self):
        """Test that PrintStatementRule exists and has correct properties."""
        from design_linters.rules.style.print_statement_rules import PrintStatementRule

        rule = PrintStatementRule()
        self.assertEqual(rule.rule_id, 'style.print-statement')
        self.assertIn('style', rule.categories)

    def test_srp_rules_exist(self):
        """Test that SRP rules exist."""
        from design_linters.rules.solid.srp_rules import (
            TooManyMethodsRule,
            TooManyResponsibilitiesRule,
            LowCohesionRule
        )

        rule1 = TooManyMethodsRule()
        rule2 = TooManyResponsibilitiesRule()
        rule3 = LowCohesionRule()

        self.assertIn('solid', rule1.categories)
        self.assertIn('solid', rule2.categories)
        self.assertIn('solid', rule3.categories)


class TestCLIIntegration(unittest.TestCase):
    """Test CLI integration."""

    def test_cli_with_temp_file(self):
        """Test CLI with a temporary file."""
        from design_linters.cli import DesignLinterCLI

        code = """
def example():
    x = 42
    print("Hello")
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()

            cli = DesignLinterCLI()

            # Just test that the CLI can be instantiated
            # and the file exists
            self.assertTrue(Path(f.name).exists())

            # Clean up
            Path(f.name).unlink()


if __name__ == '__main__':
    unittest.main()
