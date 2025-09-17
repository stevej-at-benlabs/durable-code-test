#!/usr/bin/env python3
"""
Purpose: Comprehensive working tests for design linters
Scope: Test all modules to achieve high coverage
Overview: This module provides comprehensive tests that actually work
    with the real implementation to achieve high test coverage.
Dependencies: unittest, all modules
"""

import unittest
import ast
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

import sys
sys.path.insert(0, '/home/stevejackson/Projects/durable-code-test/tools')

from design_linters.framework.interfaces import (
    Severity, LintViolation, LintContext, LintRule, ASTLintRule
)
from design_linters.framework.reporters import TextReporter, JSONReporter, ReporterFactory
from design_linters.framework.rule_registry import DefaultRuleRegistry
from design_linters.framework.analyzer import DefaultLintOrchestrator
from design_linters.cli import DesignLinterCLI
from design_linters.rules.literals.magic_number_rules import MagicNumberRule
from design_linters.rules.style.print_statement_rules import PrintStatementRule


class TestFrameworkInterfaces(unittest.TestCase):
    """Test framework interfaces comprehensively."""

    def test_severity_enum(self):
        """Test Severity enum functionality."""
        self.assertEqual(Severity.ERROR.value, 'error')
        self.assertEqual(Severity.WARNING.value, 'warning')
        self.assertEqual(Severity.INFO.value, 'info')

        # Test from_string method
        self.assertEqual(Severity.from_string('error'), Severity.ERROR)
        self.assertEqual(Severity.from_string('warning'), Severity.WARNING)
        self.assertEqual(Severity.from_string('info'), Severity.INFO)
        self.assertEqual(Severity.from_string('invalid'), Severity.WARNING)

    def test_lint_violation(self):
        """Test LintViolation creation and attributes."""
        violation = LintViolation(
            rule_id='test.rule',
            file_path='/test.py',
            line=10,
            column=5,
            severity=Severity.ERROR,
            message='Test message',
            description='Test description',
            suggestion='Fix suggestion',
            context={'key': 'value'}
        )

        self.assertEqual(violation.rule_id, 'test.rule')
        self.assertEqual(violation.file_path, '/test.py')
        self.assertEqual(violation.line, 10)
        self.assertEqual(violation.column, 5)
        self.assertEqual(violation.severity, Severity.ERROR)
        self.assertEqual(violation.message, 'Test message')
        self.assertEqual(violation.description, 'Test description')
        self.assertEqual(violation.suggestion, 'Fix suggestion')
        self.assertEqual(violation.context['key'], 'value')

    def test_lint_context(self):
        """Test LintContext creation."""
        code = "x = 42"
        tree = ast.parse(code)

        context = LintContext(
            file_path=Path('/test.py'),
            file_content=code,
            ast_tree=tree,
            current_function='test_func',
            current_class='TestClass',
            node_stack=[],
            metadata={'key': 'value'}
        )

        self.assertEqual(context.file_path, Path('/test.py'))
        self.assertEqual(context.file_content, code)
        self.assertEqual(context.ast_tree, tree)
        self.assertEqual(context.current_function, 'test_func')
        self.assertEqual(context.current_class, 'TestClass')
        self.assertEqual(context.node_stack, [])
        self.assertEqual(context.metadata['key'], 'value')


class TestReporters(unittest.TestCase):
    """Test reporter implementations."""

    def test_text_reporter(self):
        """Test TextReporter functionality."""
        reporter = TextReporter()

        # Test with no violations
        report = reporter.generate_report([])
        self.assertIn("No linting violations found", report)

        # Test with violations
        violation = LintViolation(
            rule_id='test.rule',
            file_path='/src/test.py',
            line=10,
            column=5,
            severity=Severity.WARNING,
            message='Test violation',
            description='Test description',
            suggestion='Fix suggestion'
        )

        report = reporter.generate_report([violation])
        self.assertIn('/src/test.py', report)
        self.assertIn('Test violation', report)
        self.assertIn('10:5', report)

        # Test format_violation
        formatted = reporter.format_violation(violation)
        self.assertIn('/src/test.py', formatted)
        self.assertIn('WARNING', formatted)

        # Test _group_by_file
        violations = [violation, violation]
        grouped = reporter._group_by_file(violations)
        self.assertIn('/src/test.py', grouped)
        self.assertEqual(len(grouped['/src/test.py']), 2)

    def test_json_reporter(self):
        """Test JSONReporter functionality."""
        reporter = JSONReporter()

        # Test with no violations
        report = reporter.generate_report([])
        data = json.loads(report)
        self.assertEqual(data['total_violations'], 0)

        # Test with violation
        violation = LintViolation(
            rule_id='test.rule',
            file_path='/src/test.py',
            line=10,
            column=5,
            severity=Severity.WARNING,
            message='Test violation',
            description='Test description',
            suggestion='Fix suggestion'
        )

        report = reporter.generate_report([violation])
        data = json.loads(report)
        self.assertEqual(data['total_violations'], 1)
        self.assertEqual(data['violations'][0]['rule_id'], 'test.rule')

        # Test format_violation
        formatted = reporter.format_violation(violation)
        self.assertEqual(formatted['rule_id'], 'test.rule')
        self.assertEqual(formatted['severity'], 'warning')

    def test_reporter_factory(self):
        """Test ReporterFactory."""
        # Test creating different reporters
        text_reporter = ReporterFactory.create_reporter('text')
        self.assertIsInstance(text_reporter, TextReporter)

        json_reporter = ReporterFactory.create_reporter('json')
        self.assertIsInstance(json_reporter, JSONReporter)

        # Test invalid format defaults to text
        default_reporter = ReporterFactory.create_reporter('invalid')
        self.assertIsInstance(default_reporter, TextReporter)


class TestRuleRegistry(unittest.TestCase):
    """Test rule registry functionality."""

    def setUp(self):
        self.registry = DefaultRuleRegistry()

    def test_registry_operations(self):
        """Test basic registry operations."""
        rule = MagicNumberRule()

        # Test registration
        self.registry.register_rule(rule)
        self.assertEqual(self.registry.get_rule_count(), 1)

        # Test retrieval
        retrieved = self.registry.get_rule(rule.rule_id)
        self.assertEqual(retrieved, rule)

        # Test get all rules
        all_rules = self.registry.get_all_rules()
        self.assertEqual(len(all_rules), 1)
        self.assertIn(rule, all_rules)

        # Test by category
        literals_rules = self.registry.get_rules_by_category('literals')
        self.assertEqual(len(literals_rules), 1)

        # Test categories
        categories = self.registry.get_categories()
        self.assertIn('literals', categories)

        # Test unregistration
        self.registry.unregister_rule(rule.rule_id)
        self.assertEqual(self.registry.get_rule_count(), 0)

    def test_rule_discovery(self):
        """Test rule discovery with empty paths."""
        count = self.registry.discover_rules([])
        self.assertEqual(count, 0)


class TestLintOrchestrator(unittest.TestCase):
    """Test lint orchestrator functionality."""

    def setUp(self):
        self.orchestrator = DefaultLintOrchestrator()

    def test_orchestrator_creation(self):
        """Test orchestrator creation."""
        self.assertIsNotNone(self.orchestrator)
        self.assertIsNotNone(self.orchestrator.registry)

    def test_get_available_rules(self):
        """Test getting available rules."""
        # Register a rule
        rule = MagicNumberRule()
        self.orchestrator.registry.register_rule(rule)

        rules = self.orchestrator.get_available_rules()
        self.assertIn(rule, rules)

    def test_lint_nonexistent_file(self):
        """Test linting nonexistent file."""
        violations = self.orchestrator.lint_file('/nonexistent/file.py')
        self.assertEqual(violations, [])

    def test_lint_non_python_file(self):
        """Test linting non-Python file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Not Python code")
            f.flush()

            violations = self.orchestrator.lint_file(f.name)
            self.assertEqual(violations, [])

            Path(f.name).unlink()

    def test_generate_report(self):
        """Test report generation."""
        violations = [
            LintViolation(
                rule_id='test.rule',
                file_path='/test.py',
                line=1,
                column=0,
                severity=Severity.WARNING,
                message='Test',
                description='Test',
                suggestion='Fix'
            )
        ]

        # Test text report
        text_report = self.orchestrator.generate_report(violations, format='text')
        self.assertIsInstance(text_report, str)
        self.assertIn('Test', text_report)

        # Test JSON report
        json_report = self.orchestrator.generate_report(violations, format='json')
        self.assertIsInstance(json_report, str)
        data = json.loads(json_report)
        self.assertEqual(data['total_violations'], 1)

    def test_filter_enabled_rules(self):
        """Test filtering enabled rules."""
        rule = Mock()
        rule.rule_id = 'test.rule'
        rule.is_enabled.return_value = True

        self.orchestrator.registry.register_rule(rule)
        enabled_rules = self.orchestrator._filter_enabled_rules({})
        self.assertIn(rule, enabled_rules)


class TestRuleImplementations(unittest.TestCase):
    """Test specific rule implementations."""

    def test_magic_number_rule(self):
        """Test MagicNumberRule."""
        rule = MagicNumberRule()

        # Test properties
        self.assertEqual(rule.rule_id, 'literals.magic-number')
        self.assertIn('literals', rule.categories)

        # Test should_check_node
        const_node = ast.Constant(value=42)
        name_node = ast.Name(id='x')
        context = LintContext(file_path=Path('/test.py'))

        self.assertTrue(rule.should_check_node(const_node, context))
        self.assertFalse(rule.should_check_node(name_node, context))

        # Test configuration
        config = rule.get_configuration(None)
        self.assertEqual(config, {})

        # Test is_enabled
        self.assertTrue(rule.is_enabled(None))

    def test_print_statement_rule(self):
        """Test PrintStatementRule."""
        rule = PrintStatementRule()

        # Test properties
        self.assertEqual(rule.rule_id, 'style.print-statement')
        self.assertIn('style', rule.categories)

        # Test should_check_node
        call_node = ast.Call(func=ast.Name(id='print'), args=[], keywords=[])
        other_node = ast.Name(id='x')
        context = LintContext(file_path=Path('/test.py'))

        self.assertTrue(rule.should_check_node(call_node, context))
        self.assertFalse(rule.should_check_node(other_node, context))


class TestCLI(unittest.TestCase):
    """Test CLI functionality."""

    def test_cli_creation(self):
        """Test CLI creation."""
        cli = DesignLinterCLI()
        self.assertIsNotNone(cli)
        self.assertIsNone(cli.orchestrator)  # Not initialized until run()

    @patch('design_linters.cli.sys.argv', ['design-linter', '--help'])
    def test_cli_help(self):
        """Test CLI help."""
        cli = DesignLinterCLI()
        with self.assertRaises(SystemExit):
            cli.run()

    def test_create_orchestrator(self):
        """Test orchestrator creation."""
        cli = DesignLinterCLI()
        args = Mock()
        args.rules_only = []
        args.exclude_rules = []
        args.category = None

        orchestrator = cli._create_orchestrator(args)
        self.assertIsNotNone(orchestrator)

    def test_determine_exit_code(self):
        """Test exit code determination."""
        cli = DesignLinterCLI()

        # No violations
        self.assertEqual(cli._determine_exit_code([], Mock()), 0)

        # With violations but no fail flags
        violations = [Mock()]
        args = Mock()
        args.fail_on_error = False
        args.fail_on_warnings = False
        self.assertEqual(cli._determine_exit_code(violations, args), 0)


class TestEndToEndIntegration(unittest.TestCase):
    """Test end-to-end integration."""

    def test_full_workflow(self):
        """Test complete linting workflow."""
        code = """
def test_function():
    x = 42  # Magic number
    return x
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()

            # Create orchestrator and register rules
            orchestrator = DefaultLintOrchestrator()
            orchestrator.registry.register_rule(MagicNumberRule())

            # Analyze file
            violations = orchestrator.analyze_file(Path(f.name))
            self.assertIsInstance(violations, list)

            # Generate reports
            text_report = orchestrator.generate_report(violations, format='text')
            json_report = orchestrator.generate_report(violations, format='json')

            self.assertIsInstance(text_report, str)
            self.assertIsInstance(json_report, str)

            Path(f.name).unlink()


if __name__ == '__main__':
    unittest.main()
