#!/usr/bin/env python3
"""
Purpose: Tests for framework components
Scope: Test analyzer, registry, and other framework components
Overview: This module tests the core framework components.
Dependencies: unittest, framework components
"""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, '/home/stevejackson/Projects/durable-code-test/tools')

from design_linters.framework.interfaces import LintViolation, Severity, LintContext
from design_linters.framework.rule_registry import DefaultRuleRegistry
from design_linters.framework.analyzer import DefaultLintOrchestrator
from design_linters.framework.reporters import TextReporter
from design_linters.rules.literals.magic_number_rules import MagicNumberRule


class TestDefaultRuleRegistry(unittest.TestCase):
    """Test DefaultRuleRegistry implementation."""

    def setUp(self):
        self.registry = DefaultRuleRegistry()

    def test_registry_creation(self):
        """Test registry creation."""
        self.assertIsNotNone(self.registry)
        self.assertEqual(self.registry.get_rule_count(), 0)

    def test_register_rule(self):
        """Test rule registration."""
        rule = MagicNumberRule()
        self.registry.register_rule(rule)

        self.assertEqual(self.registry.get_rule_count(), 1)
        self.assertEqual(self.registry.get_rule(rule.rule_id), rule)

    def test_unregister_rule(self):
        """Test rule unregistration."""
        rule = MagicNumberRule()
        self.registry.register_rule(rule)
        self.assertEqual(self.registry.get_rule_count(), 1)

        self.registry.unregister_rule(rule.rule_id)
        self.assertEqual(self.registry.get_rule_count(), 0)
        self.assertIsNone(self.registry.get_rule(rule.rule_id))

    def test_get_all_rules(self):
        """Test getting all rules."""
        rule1 = MagicNumberRule()
        rule2 = Mock()
        rule2.rule_id = 'test.rule'
        rule2.categories = {'test'}

        self.registry.register_rule(rule1)
        self.registry.register_rule(rule2)

        all_rules = self.registry.get_all_rules()
        self.assertEqual(len(all_rules), 2)
        self.assertIn(rule1, all_rules)
        self.assertIn(rule2, all_rules)

    def test_get_rules_by_category(self):
        """Test getting rules by category."""
        rule1 = MagicNumberRule()  # Has 'literals' category
        rule2 = Mock()
        rule2.rule_id = 'test.rule'
        rule2.categories = {'test', 'example'}

        self.registry.register_rule(rule1)
        self.registry.register_rule(rule2)

        literals_rules = self.registry.get_rules_by_category('literals')
        self.assertEqual(len(literals_rules), 1)
        self.assertIn(rule1, literals_rules)

        test_rules = self.registry.get_rules_by_category('test')
        self.assertEqual(len(test_rules), 1)
        self.assertIn(rule2, test_rules)

    def test_get_categories(self):
        """Test getting all categories."""
        rule1 = MagicNumberRule()  # Has 'literals' category
        rule2 = Mock()
        rule2.rule_id = 'test.rule'
        rule2.categories = {'test', 'example'}

        self.registry.register_rule(rule1)
        self.registry.register_rule(rule2)

        categories = self.registry.get_categories()
        self.assertIn('literals', categories)
        self.assertIn('test', categories)
        self.assertIn('example', categories)

    def test_discover_rules_empty_paths(self):
        """Test discovery with empty paths."""
        count = self.registry.discover_rules([])
        self.assertEqual(count, 0)


class TestDefaultLintOrchestrator(unittest.TestCase):
    """Test DefaultLintOrchestrator implementation."""

    def setUp(self):
        self.orchestrator = DefaultLintOrchestrator()

    def test_orchestrator_creation(self):
        """Test orchestrator creation."""
        self.assertIsNotNone(self.orchestrator)
        self.assertIsNotNone(self.orchestrator.registry)

    def test_lint_file_nonexistent(self):
        """Test linting nonexistent file."""
        violations = self.orchestrator.lint_file('/nonexistent/file.py')
        self.assertEqual(violations, [])

    def test_lint_file_non_python(self):
        """Test linting non-Python file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is not Python code")
            f.flush()

            violations = self.orchestrator.lint_file(f.name)
            self.assertEqual(violations, [])

            Path(f.name).unlink()

    def test_lint_python_file(self):
        """Test linting Python file."""
        code = """
def test_function():
    x = 42
    return x
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()

            # Register a rule
            self.orchestrator.registry.register_rule(MagicNumberRule())

            violations = self.orchestrator.lint_file(f.name)
            self.assertIsInstance(violations, list)

            Path(f.name).unlink()

    def test_lint_directory(self):
        """Test linting directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some Python files
            test_file1 = Path(temp_dir) / 'test1.py'
            test_file2 = Path(temp_dir) / 'test2.py'

            test_file1.write_text('x = 42')
            test_file2.write_text('print("hello")')

            violations = self.orchestrator.lint_directory(temp_dir)
            self.assertIsInstance(violations, list)

    def test_get_available_rules(self):
        """Test getting available rules."""
        rule = MagicNumberRule()
        self.orchestrator.registry.register_rule(rule)

        rules = self.orchestrator.get_available_rules()
        self.assertIn(rule, rules)

    def test_generate_report_text(self):
        """Test generating text report."""
        violations = [
            LintViolation(
                rule_id='test.rule',
                file_path='/test.py',
                line=1,
                column=0,
                severity=Severity.WARNING,
                message='Test violation',
                description='Description',
                suggestion='Suggestion'
            )
        ]

        report = self.orchestrator.generate_report(violations, format='text')
        self.assertIsInstance(report, str)
        self.assertIn('Test violation', report)

    def test_generate_report_json(self):
        """Test generating JSON report."""
        violations = [
            LintViolation(
                rule_id='test.rule',
                file_path='/test.py',
                line=1,
                column=0,
                severity=Severity.WARNING,
                message='Test violation',
                description='Description',
                suggestion='Suggestion'
            )
        ]

        report = self.orchestrator.generate_report(violations, format='json')
        self.assertIsInstance(report, str)
        # Should be valid JSON
        import json
        data = json.loads(report)
        self.assertIn('total_violations', data)

    def test_filter_enabled_rules(self):
        """Test filtering enabled rules."""
        rule = Mock()
        rule.rule_id = 'test.rule'
        rule.is_enabled.return_value = True

        self.orchestrator.registry.register_rule(rule)
        enabled_rules = self.orchestrator._filter_enabled_rules({})
        self.assertIn(rule, enabled_rules)

    def test_create_context(self):
        """Test creating lint context."""
        file_path = Path('/test.py')
        content = 'x = 42'
        metadata = {'key': 'value'}

        context = self.orchestrator._create_context(file_path, content, metadata)

        self.assertEqual(context.file_path, file_path)
        self.assertEqual(context.file_content, content)
        self.assertEqual(context.metadata, metadata)
        self.assertIsNotNone(context.ast_tree)


if __name__ == '__main__':
    unittest.main()
