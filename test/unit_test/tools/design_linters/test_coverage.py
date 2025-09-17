#!/usr/bin/env python3
"""
Purpose: Coverage-focused tests for design linters
Scope: Test coverage for all modules
Overview: This module provides tests that focus on achieving high code coverage
    by exercising as many code paths as possible with simple, working tests.
Dependencies: unittest, all modules
"""

import unittest
import ast
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import sys
sys.path.insert(0, '/home/stevejackson/Projects/durable-code-test/tools')


class TestInterfacesCoverage(unittest.TestCase):
    """Test interfaces module for coverage."""

    def test_severity_enum(self):
        """Test Severity enum methods."""
        from design_linters.framework.interfaces import Severity

        # Test all enum values
        self.assertEqual(Severity.ERROR.value, 'error')
        self.assertEqual(Severity.WARNING.value, 'warning')
        self.assertEqual(Severity.INFO.value, 'info')

        # Test from_string method
        self.assertEqual(Severity.from_string('error'), Severity.ERROR)
        self.assertEqual(Severity.from_string('warning'), Severity.WARNING)
        self.assertEqual(Severity.from_string('info'), Severity.INFO)
        self.assertEqual(Severity.from_string('invalid'), Severity.WARNING)

    def test_lint_violation(self):
        """Test LintViolation creation."""
        from design_linters.framework.interfaces import LintViolation, Severity

        violation = LintViolation(
            rule_id='test.rule',
            file_path='/test.py',
            line=1,
            column=0,
            severity=Severity.ERROR,
            message='Test',
            description='Test',
            suggestion='Test'
        )
        self.assertEqual(violation.rule_id, 'test.rule')

    def test_lint_context(self):
        """Test LintContext creation."""
        from design_linters.framework.interfaces import LintContext

        context = LintContext(file_path=Path('/test.py'))
        self.assertEqual(context.file_path, Path('/test.py'))

    def test_abstract_classes(self):
        """Test abstract class instantiation fails."""
        from design_linters.framework.interfaces import LintRule, ASTLintRule, LintReporter, LintAnalyzer, RuleRegistry

        with self.assertRaises(TypeError):
            LintRule()
        with self.assertRaises(TypeError):
            ASTLintRule()
        with self.assertRaises(TypeError):
            LintReporter()
        with self.assertRaises(TypeError):
            LintAnalyzer()
        with self.assertRaises(TypeError):
            RuleRegistry()


class TestReportersCoverage(unittest.TestCase):
    """Test reporters module for coverage."""

    def test_text_reporter(self):
        """Test TextReporter methods."""
        from design_linters.framework.reporters import TextReporter
        from design_linters.framework.interfaces import LintViolation, Severity

        reporter = TextReporter()

        # Test empty report
        report = reporter.generate_report([])
        self.assertIn("No linting violations found", report)

        # Test with violations
        violation = LintViolation(
            rule_id='test.rule',
            file_path='/test.py',
            line=1,
            column=0,
            severity=Severity.ERROR,
            message='Test',
            description='Test',
            suggestion='Test'
        )

        report = reporter.generate_report([violation])
        self.assertIn('test.py', report)

        # Test format_violation
        formatted = reporter.format_violation(violation)
        self.assertIn('ERROR', formatted)

        # Test _group_by_file
        grouped = reporter._group_by_file([violation])
        self.assertIn('/test.py', grouped)

    def test_json_reporter(self):
        """Test JSONReporter methods."""
        from design_linters.framework.reporters import JSONReporter
        from design_linters.framework.interfaces import LintViolation, Severity
        import json

        reporter = JSONReporter()

        # Test empty report
        report = reporter.generate_report([])
        data = json.loads(report)
        self.assertEqual(data['total_violations'], 0)

        # Test with violation
        violation = LintViolation(
            rule_id='test.rule',
            file_path='/test.py',
            line=1,
            column=0,
            severity=Severity.ERROR,
            message='Test',
            description='Test',
            suggestion='Test'
        )

        report = reporter.generate_report([violation])
        data = json.loads(report)
        self.assertEqual(data['total_violations'], 1)

        # Test format_violation
        formatted = reporter.format_violation(violation)
        self.assertEqual(formatted['rule_id'], 'test.rule')

    def test_sarif_reporter(self):
        """Test SARIFReporter methods."""
        from design_linters.framework.reporters import SARIFReporter
        from design_linters.framework.interfaces import LintViolation, Severity
        import json

        reporter = SARIFReporter()

        violation = LintViolation(
            rule_id='test.rule',
            file_path='/test.py',
            line=1,
            column=0,
            severity=Severity.ERROR,
            message='Test',
            description='Test',
            suggestion='Test'
        )

        report = reporter.generate_report([violation])
        data = json.loads(report)
        self.assertIn('$schema', data)

    def test_github_actions_reporter(self):
        """Test GitHubActionsReporter methods."""
        from design_linters.framework.reporters import GitHubActionsReporter
        from design_linters.framework.interfaces import LintViolation, Severity

        reporter = GitHubActionsReporter()

        violation = LintViolation(
            rule_id='test.rule',
            file_path='/test.py',
            line=1,
            column=0,
            severity=Severity.ERROR,
            message='Test',
            description='Test',
            suggestion='Test'
        )

        report = reporter.generate_report([violation])
        self.assertIn('::error', report)

        # Test format_violation
        formatted = reporter.format_violation(violation)
        self.assertIn('::error', formatted)

    def test_reporter_factory(self):
        """Test ReporterFactory methods."""
        from design_linters.framework.reporters import ReporterFactory, TextReporter

        reporter = ReporterFactory.create_reporter('text')
        self.assertIsInstance(reporter, TextReporter)

        # Test invalid format
        reporter = ReporterFactory.create_reporter('invalid')
        self.assertIsInstance(reporter, TextReporter)


class TestRegistryCoverage(unittest.TestCase):
    """Test registry module for coverage."""

    def test_default_rule_registry(self):
        """Test DefaultRuleRegistry methods."""
        from design_linters.framework.rule_registry import DefaultRuleRegistry
        from design_linters.rules.literals.magic_number_rules import MagicNumberRule

        registry = DefaultRuleRegistry()

        # Test initial state
        self.assertEqual(registry.get_rule_count(), 0)
        self.assertEqual(registry.get_all_rules(), [])
        self.assertEqual(registry.get_categories(), set())

        # Test rule registration
        rule = MagicNumberRule()
        registry.register_rule(rule)
        self.assertEqual(registry.get_rule_count(), 1)
        self.assertEqual(registry.get_rule(rule.rule_id), rule)

        # Test get_all_rules
        all_rules = registry.get_all_rules()
        self.assertIn(rule, all_rules)

        # Test get_rules_by_category
        literals_rules = registry.get_rules_by_category('literals')
        self.assertIn(rule, literals_rules)

        # Test get_categories
        categories = registry.get_categories()
        self.assertIn('literals', categories)

        # Test unregister
        registry.unregister_rule(rule.rule_id)
        self.assertEqual(registry.get_rule_count(), 0)

        # Test discover_rules with empty paths
        count = registry.discover_rules([])
        self.assertEqual(count, 0)


class TestAnalyzerCoverage(unittest.TestCase):
    """Test analyzer module for coverage."""

    def test_default_lint_orchestrator(self):
        """Test DefaultLintOrchestrator methods."""
        from design_linters.framework.analyzer import DefaultLintOrchestrator
        from design_linters.framework.interfaces import LintViolation, Severity

        orchestrator = DefaultLintOrchestrator()

        # Test initialization
        self.assertIsNotNone(orchestrator.registry)

        # Test get_available_rules
        rules = orchestrator.get_available_rules()
        self.assertIsInstance(rules, list)

        # Test lint_file with non-existent file
        violations = orchestrator.lint_file('/nonexistent.py')
        self.assertEqual(violations, [])

        # Test lint_directory with non-existent directory
        violations = orchestrator.lint_directory('/nonexistent')
        self.assertEqual(violations, [])

        # Test generate_report
        violation = LintViolation(
            rule_id='test.rule',
            file_path='/test.py',
            line=1,
            column=0,
            severity=Severity.ERROR,
            message='Test',
            description='Test',
            suggestion='Test'
        )

        # Test text report
        report = orchestrator.generate_report([violation], format='text')
        self.assertIsInstance(report, str)

        # Test JSON report
        report = orchestrator.generate_report([violation], format='json')
        self.assertIsInstance(report, str)

        # Test invalid format (should default to text)
        report = orchestrator.generate_report([violation], format='invalid')
        self.assertIsInstance(report, str)


class TestRulesCoverage(unittest.TestCase):
    """Test rules modules for coverage."""

    def test_magic_number_rule(self):
        """Test MagicNumberRule methods."""
        from design_linters.rules.literals.magic_number_rules import MagicNumberRule
        from design_linters.framework.interfaces import LintContext

        rule = MagicNumberRule()

        # Test properties
        self.assertEqual(rule.rule_id, 'literals.magic-number')
        self.assertIn('literals', rule.categories)

        # Test configuration
        config = rule.get_configuration(None)
        self.assertEqual(config, {})

        # Test is_enabled
        self.assertTrue(rule.is_enabled(None))

        # Test should_check_node
        const_node = ast.Constant(value=42)
        context = LintContext(file_path=Path('/test.py'))
        self.assertTrue(rule.should_check_node(const_node, context))

    def test_magic_string_rule(self):
        """Test MagicStringRule methods."""
        from design_linters.rules.literals.magic_string_rules import MagicStringRule

        rule = MagicStringRule()
        self.assertEqual(rule.rule_id, 'literals.magic-string')
        self.assertIn('literals', rule.categories)

    def test_print_statement_rule(self):
        """Test PrintStatementRule methods."""
        from design_linters.rules.style.print_statement_rules import PrintStatementRule

        rule = PrintStatementRule()
        self.assertEqual(rule.rule_id, 'style.print-statement')
        self.assertIn('style', rule.categories)

    def test_nesting_rules(self):
        """Test nesting rules methods."""
        from design_linters.rules.style.nesting_rules import ExcessiveNestingRule

        rule = ExcessiveNestingRule()
        self.assertEqual(rule.rule_id, 'style.excessive-nesting')
        self.assertIn('readability', rule.categories)

    def test_srp_rules(self):
        """Test SRP rules methods."""
        from design_linters.rules.solid.srp_rules import TooManyMethodsRule

        rule = TooManyMethodsRule()
        self.assertEqual(rule.rule_id, 'solid.srp.too-many-methods')
        self.assertIn('solid', rule.categories)

    def test_logging_rules(self):
        """Test logging rules methods."""
        from design_linters.rules.logging.general_logging_rules import NoPlainPrintRule

        rule = NoPlainPrintRule()
        self.assertEqual(rule.rule_id, 'logging.no-print')
        self.assertIn('logging', rule.categories)


class TestCLICoverage(unittest.TestCase):
    """Test CLI module for coverage."""

    def test_cli_creation(self):
        """Test CLI creation."""
        from design_linters.cli import DesignLinterCLI

        cli = DesignLinterCLI()
        self.assertIsNotNone(cli)
        self.assertIsNone(cli.orchestrator)

    @patch('design_linters.cli.create_orchestrator')
    def test_create_orchestrator(self, mock_create):
        """Test orchestrator creation."""
        from design_linters.cli import DesignLinterCLI

        mock_create.return_value = Mock()
        cli = DesignLinterCLI()

        args = Mock()
        args.rules = None
        args.exclude_rules = None
        args.config = None
        args.strict = False
        args.lenient = False
        args.legacy = None
        args.list_rules = False
        args.list_categories = False

        result = cli._create_orchestrator(args)
        self.assertIsNotNone(result)

    def test_load_configuration(self):
        """Test configuration loading."""
        from design_linters.cli import DesignLinterCLI

        cli = DesignLinterCLI()

        args = Mock()
        args.config = None
        args.strict = False
        args.lenient = False
        args.legacy = None
        args.rules = None
        args.exclude_rules = None

        config = cli._load_configuration(args)
        self.assertIn('rules', config)

    def test_helper_methods(self):
        """Test CLI helper methods."""
        from design_linters.cli import DesignLinterCLI

        cli = DesignLinterCLI()

        # Test config file loading
        config = cli._load_config_file('/nonexistent.yml')
        self.assertEqual(config, {})

        # Test config methods
        strict_config = cli._get_strict_config()
        self.assertIsInstance(strict_config, dict)

        lenient_config = cli._get_lenient_config()
        self.assertIsInstance(lenient_config, dict)

        legacy_config = cli._get_legacy_config('srp')
        self.assertIsInstance(legacy_config, dict)


class TestFrameworkCoverage(unittest.TestCase):
    """Test framework module for coverage."""

    def test_framework_imports(self):
        """Test framework module imports."""
        from design_linters.framework import (
            create_orchestrator, create_rule_registry,
            LintViolation, Severity, ReporterFactory
        )

        self.assertIsNotNone(create_orchestrator)
        self.assertIsNotNone(create_rule_registry)
        self.assertIsNotNone(LintViolation)
        self.assertIsNotNone(Severity)
        self.assertIsNotNone(ReporterFactory)

    @patch('design_linters.framework.DefaultRuleRegistry')
    @patch('design_linters.framework.DefaultLintOrchestrator')
    def test_create_orchestrator(self, mock_orchestrator, mock_registry):
        """Test create_orchestrator function."""
        from design_linters.framework import create_orchestrator

        mock_orch = Mock()
        mock_orchestrator.return_value = mock_orch

        result = create_orchestrator(['package'], {})
        self.assertEqual(result, mock_orch)

    @patch('design_linters.framework.DefaultRuleRegistry')
    def test_create_rule_registry(self, mock_registry):
        """Test create_rule_registry function."""
        from design_linters.framework import create_rule_registry

        mock_reg = Mock()
        mock_registry.return_value = mock_reg

        result = create_rule_registry(['package'])
        self.assertEqual(result, mock_reg)


if __name__ == '__main__':
    unittest.main()
