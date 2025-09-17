#!/usr/bin/env python3
"""
Purpose: Unit tests for framework interfaces
Scope: Tests for core framework interfaces and base classes
Overview: This module tests the fundamental interfaces of the pluggable
    linter framework including LintRule, LintViolation, LintReporter,
    and other core abstractions to ensure they work as expected.
Dependencies: unittest, framework interfaces
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import ast
from pathlib import Path

import sys
sys.path.insert(0, '/home/stevejackson/Projects/durable-code-test/tools')

from design_linters.framework.interfaces import (
    LintRule, ASTLintRule, LintViolation, LintContext,
    Severity, LintReporter, LintAnalyzer, RuleRegistry
)


class TestSeverity(unittest.TestCase):
    """Test the Severity enum."""

    def test_severity_values(self):
        """Test severity enum values are properly defined."""
        self.assertEqual(Severity.ERROR.value, 'error')
        self.assertEqual(Severity.WARNING.value, 'warning')
        self.assertEqual(Severity.INFO.value, 'info')

    def test_severity_ordering(self):
        """Test severity levels can be compared."""
        severities = [Severity.ERROR, Severity.WARNING, Severity.INFO]
        # Should be sortable by their values
        sorted_severities = sorted(severities, key=lambda s: s.value)
        self.assertEqual(len(sorted_severities), 3)


class TestLintViolation(unittest.TestCase):
    """Test the LintViolation data class."""

    def test_violation_creation(self):
        """Test creating a violation with all required fields."""
        violation = LintViolation(
            rule_id='test.rule',
            file_path='/path/to/file.py',
            line=10,
            column=5,
            severity=Severity.WARNING,
            message='Test violation',
            description='Detailed description',
            suggestion='Fix suggestion'
        )

        self.assertEqual(violation.rule_id, 'test.rule')
        self.assertEqual(violation.file_path, '/path/to/file.py')
        self.assertEqual(violation.line, 10)
        self.assertEqual(violation.column, 5)
        self.assertEqual(violation.severity, Severity.WARNING)
        self.assertEqual(violation.message, 'Test violation')
        self.assertEqual(violation.description, 'Detailed description')
        self.assertEqual(violation.suggestion, 'Fix suggestion')

    def test_violation_with_context(self):
        """Test violation with optional context field."""
        context_data = {'function': 'test_func', 'class': 'TestClass'}
        violation = LintViolation(
            rule_id='test.rule',
            file_path='/path/to/file.py',
            line=10,
            column=5,
            severity=Severity.ERROR,
            message='Test violation',
            description='Description',
            suggestion='Suggestion',
            context=context_data
        )

        self.assertEqual(violation.context, context_data)
        self.assertEqual(violation.context['function'], 'test_func')


class TestLintContext(unittest.TestCase):
    """Test the LintContext data class."""

    def test_context_creation(self):
        """Test creating a lint context."""
        context = LintContext(
            file_path=Path('/path/to/file.py'),
            file_content='print("hello")',
            current_function='my_func',
            current_class='MyClass',
            node_stack=[],
            metadata={'key': 'value'}
        )

        self.assertEqual(context.file_path, Path('/path/to/file.py'))
        self.assertEqual(context.file_content, 'print("hello")')
        self.assertEqual(context.current_function, 'my_func')
        self.assertEqual(context.current_class, 'MyClass')
        self.assertEqual(context.node_stack, [])
        self.assertEqual(context.metadata['key'], 'value')

    def test_context_defaults(self):
        """Test context with default values."""
        context = LintContext(
            file_path=Path('/path/to/file.py')
        )

        self.assertEqual(context.file_path, Path('/path/to/file.py'))
        self.assertIsNone(context.file_content)
        self.assertIsNone(context.current_function)
        self.assertIsNone(context.current_class)
        self.assertIsNone(context.node_stack)  # Default is None, not []
        self.assertIsNone(context.metadata)


class TestLintRule(unittest.TestCase):
    """Test the abstract LintRule base class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a concrete implementation for testing
        class TestRule(LintRule):
            @property
            def rule_id(self) -> str:
                return "test.rule"

            @property
            def rule_name(self) -> str:
                return "Test Rule"

            @property
            def description(self) -> str:
                return "Test rule description"

            @property
            def severity(self) -> Severity:
                return Severity.WARNING

            @property
            def categories(self) -> set:
                return {"test", "sample"}

            def check(self, file_path, file_content, metadata=None):
                return []

        self.TestRule = TestRule

    def test_rule_properties(self):
        """Test rule property accessors."""
        rule = self.TestRule()

        self.assertEqual(rule.rule_id, "test.rule")
        self.assertEqual(rule.rule_name, "Test Rule")
        self.assertEqual(rule.description, "Test rule description")
        self.assertEqual(rule.severity, Severity.WARNING)
        self.assertEqual(rule.categories, {"test", "sample"})

    def test_rule_configuration(self):
        """Test rule configuration handling."""
        rule = self.TestRule()

        # Test with no metadata
        config = rule.get_configuration(None)
        self.assertEqual(config, {})

        # Test with metadata but no rules config
        config = rule.get_configuration({'other': 'data'})
        self.assertEqual(config, {})

        # Test with rules config
        metadata = {
            'rules': {
                'test.rule': {
                    'enabled': True,
                    'config': {
                        'severity': 'error',
                        'custom_param': 'value'
                    }
                }
            }
        }
        config = rule.get_configuration(metadata)
        self.assertEqual(config['severity'], 'error')
        self.assertEqual(config['custom_param'], 'value')

        # Test is_enabled separately
        enabled = rule.is_enabled(metadata)
        self.assertTrue(enabled)


class TestASTLintRule(unittest.TestCase):
    """Test the ASTLintRule base class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a concrete AST rule for testing
        class TestASTRule(ASTLintRule):
            @property
            def rule_id(self) -> str:
                return "test.ast.rule"

            @property
            def rule_name(self) -> str:
                return "Test AST Rule"

            @property
            def description(self) -> str:
                return "Test AST rule description"

            @property
            def severity(self) -> Severity:
                return Severity.INFO

            @property
            def categories(self) -> set:
                return {"ast", "test"}

            def should_check_node(self, node, context):
                return isinstance(node, ast.Call)

            def check_node(self, node, context):
                return [LintViolation(
                    rule_id=self.rule_id,
                    file_path=str(context.file_path),
                    line=node.lineno,
                    column=node.col_offset,
                    severity=self.severity,
                    message="Test violation",
                    description="Test description",
                    suggestion="Test suggestion"
                )]

        self.TestASTRule = TestASTRule

    def test_ast_rule_check(self):
        """Test AST rule checking functionality."""
        rule = self.TestASTRule()

        # Create test code with a function call
        code = """
def test():
    print("hello")
"""

        # Parse the code
        tree = ast.parse(code)

        # Create context
        context = LintContext(
            file_path=Path('/test/file.py'),
            file_content=code
        )

        # Check the rule
        violations = rule.check(context)

        # Should find the print call
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].rule_id, "test.ast.rule")
        self.assertEqual(violations[0].message, "Test violation")


class TestRuleRegistry(unittest.TestCase):
    """Test the RuleRegistry interface."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock registry implementation
        class TestRegistry(RuleRegistry):
            def __init__(self):
                self._rules = {}

            def register_rule(self, rule):
                self._rules[rule.rule_id] = rule

            def unregister_rule(self, rule_id):
                if rule_id in self._rules:
                    del self._rules[rule_id]

            def get_rule(self, rule_id):
                return self._rules.get(rule_id)

            def get_all_rules(self):
                return list(self._rules.values())

            def get_rules_by_category(self, category):
                return [r for r in self._rules.values() if category in r.categories]

            def get_rule_count(self):
                return len(self._rules)

            def get_categories(self):
                categories = set()
                for rule in self._rules.values():
                    categories.update(rule.categories)
                return categories

            def discover_rules(self):
                # Mock implementation for testing
                return []

        self.TestRegistry = TestRegistry

    def test_registry_operations(self):
        """Test registry add/remove/get operations."""
        registry = self.TestRegistry()

        # Create a mock rule
        mock_rule = Mock()
        mock_rule.rule_id = "test.rule"
        mock_rule.categories = {"test"}

        # Test registration
        registry.register_rule(mock_rule)
        self.assertEqual(registry.get_rule_count(), 1)

        # Test retrieval
        retrieved = registry.get_rule("test.rule")
        self.assertEqual(retrieved, mock_rule)

        # Test get all rules
        all_rules = registry.get_all_rules()
        self.assertEqual(len(all_rules), 1)
        self.assertEqual(all_rules[0], mock_rule)

        # Test categories
        categories = registry.get_categories()
        self.assertIn("test", categories)

        # Test unregistration
        registry.unregister_rule("test.rule")
        self.assertEqual(registry.get_rule_count(), 0)


class TestLintReporter(unittest.TestCase):
    """Test the LintReporter interface."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a concrete reporter for testing
        class TestReporter(LintReporter):
            def generate_report(self, violations):
                return f"Found {len(violations)} violations"

            def format_violation(self, violation):
                return f"{violation.rule_id}: {violation.message}"

        self.TestReporter = TestReporter

    def test_reporter_generation(self):
        """Test report generation."""
        reporter = self.TestReporter()

        violations = [
            LintViolation(
                rule_id='test.rule1',
                file_path='/file.py',
                line=1,
                column=0,
                severity=Severity.WARNING,
                message='Test 1',
                description='Desc 1',
                suggestion='Fix 1'
            ),
            LintViolation(
                rule_id='test.rule2',
                file_path='/file.py',
                line=2,
                column=0,
                severity=Severity.ERROR,
                message='Test 2',
                description='Desc 2',
                suggestion='Fix 2'
            )
        ]

        report = reporter.generate_report(violations)
        self.assertEqual(report, "Found 2 violations")

        formatted = reporter.format_violation(violations[0])
        self.assertEqual(formatted, "test.rule1: Test 1")


if __name__ == '__main__':
    unittest.main()
