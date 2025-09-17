#!/usr/bin/env python3
"""
Purpose: Basic working tests for design linters
Scope: Simple smoke tests that actually work
Overview: This module provides basic tests that verify the framework loads
    and basic components exist without testing complex functionality.
Dependencies: unittest, framework modules
"""

import unittest
from pathlib import Path

import sys
sys.path.insert(0, '/home/stevejackson/Projects/durable-code-test/tools')


class TestBasicImports(unittest.TestCase):
    """Test that all modules can be imported without errors."""

    def test_framework_imports(self):
        """Test framework module imports."""
        try:
            from design_linters.framework import interfaces
            from design_linters.framework import reporters
            from design_linters.framework import rule_registry
            from design_linters.framework import analyzer
            self.assertTrue(True)  # If we get here, imports worked
        except ImportError as e:
            self.fail(f"Framework import failed: {e}")

    def test_rules_imports(self):
        """Test rules module imports."""
        try:
            from design_linters.rules.literals import magic_number_rules
            from design_linters.rules.literals import magic_string_rules
            from design_linters.rules.style import print_statement_rules
            from design_linters.rules.style import nesting_rules
            from design_linters.rules.solid import srp_rules
            from design_linters.rules.logging import general_logging_rules
            from design_linters.rules.logging import loguru_rules
            self.assertTrue(True)  # If we get here, imports worked
        except ImportError as e:
            self.fail(f"Rules import failed: {e}")

    def test_cli_import(self):
        """Test CLI module import."""
        try:
            from design_linters import cli
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"CLI import failed: {e}")


class TestBasicFunctionality(unittest.TestCase):
    """Test basic functionality without complex scenarios."""

    def test_severity_enum(self):
        """Test Severity enum exists and has expected values."""
        from design_linters.framework.interfaces import Severity

        self.assertEqual(Severity.ERROR.value, 'error')
        self.assertEqual(Severity.WARNING.value, 'warning')
        self.assertEqual(Severity.INFO.value, 'info')

    def test_lint_violation_creation(self):
        """Test basic LintViolation creation."""
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

    def test_lint_context_creation(self):
        """Test basic LintContext creation."""
        from design_linters.framework.interfaces import LintContext

        context = LintContext(file_path=Path('/test.py'))
        self.assertEqual(context.file_path, Path('/test.py'))

    def test_text_reporter_exists(self):
        """Test TextReporter can be created."""
        from design_linters.framework.reporters import TextReporter

        reporter = TextReporter()
        self.assertIsNotNone(reporter)

    def test_json_reporter_exists(self):
        """Test JSONReporter can be created."""
        from design_linters.framework.reporters import JSONReporter

        reporter = JSONReporter()
        self.assertIsNotNone(reporter)

    def test_rule_registry_exists(self):
        """Test DefaultRuleRegistry can be created."""
        from design_linters.framework.rule_registry import DefaultRuleRegistry

        registry = DefaultRuleRegistry()
        self.assertIsNotNone(registry)

    def test_orchestrator_exists(self):
        """Test DefaultLintOrchestrator can be created."""
        from design_linters.framework.analyzer import DefaultLintOrchestrator
        from design_linters.framework.rule_registry import DefaultRuleRegistry

        registry = DefaultRuleRegistry()
        orchestrator = DefaultLintOrchestrator(registry)
        self.assertIsNotNone(orchestrator)

    def test_cli_exists(self):
        """Test DesignLinterCLI can be created."""
        from design_linters.cli import DesignLinterCLI

        cli = DesignLinterCLI()
        self.assertIsNotNone(cli)

    def test_magic_number_rule_exists(self):
        """Test MagicNumberRule can be created."""
        from design_linters.rules.literals.magic_number_rules import MagicNumberRule

        rule = MagicNumberRule()
        self.assertEqual(rule.rule_id, 'literals.magic-number')

    def test_print_statement_rule_exists(self):
        """Test PrintStatementRule can be created."""
        from design_linters.rules.style.print_statement_rules import PrintStatementRule

        rule = PrintStatementRule()
        self.assertEqual(rule.rule_id, 'style.print-statement')


if __name__ == '__main__':
    unittest.main()
