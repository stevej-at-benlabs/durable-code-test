#!/usr/bin/env python3
"""
Purpose: Comprehensive tests for framework interfaces
Scope: Test all interface classes and methods
Overview: This module thoroughly tests the framework interfaces to ensure
    they work correctly and achieve high code coverage.
Dependencies: unittest, framework interfaces
"""

import unittest
import ast
from pathlib import Path
from unittest.mock import Mock, MagicMock

import sys
sys.path.insert(0, '/home/stevejackson/Projects/durable-code-test/tools')

from design_linters.framework.interfaces import (
    Severity, LintViolation, LintContext, LintRule, ASTLintRule,
    LintReporter, LintAnalyzer, RuleRegistry
)


class TestSeverity(unittest.TestCase):
    """Test Severity enum."""

    def test_severity_values(self):
        """Test severity values."""
        self.assertEqual(Severity.ERROR.value, 'error')
        self.assertEqual(Severity.WARNING.value, 'warning')
        self.assertEqual(Severity.INFO.value, 'info')

    def test_severity_from_string(self):
        """Test creating severity from string."""
        self.assertEqual(Severity.from_string('error'), Severity.ERROR)
        self.assertEqual(Severity.from_string('warning'), Severity.WARNING)
        self.assertEqual(Severity.from_string('info'), Severity.INFO)
        self.assertEqual(Severity.from_string('invalid'), Severity.WARNING)


class TestLintViolation(unittest.TestCase):
    """Test LintViolation dataclass."""

    def test_violation_creation(self):
        """Test creating a violation with all fields."""
        violation = LintViolation(
            rule_id='test.rule',
            file_path='/test/file.py',
            line=10,
            column=5,
            severity=Severity.ERROR,
            message='Test message',
            description='Test description',
            suggestion='Fix suggestion'
        )

        self.assertEqual(violation.rule_id, 'test.rule')
        self.assertEqual(violation.file_path, '/test/file.py')
        self.assertEqual(violation.line, 10)
        self.assertEqual(violation.column, 5)
        self.assertEqual(violation.severity, Severity.ERROR)
        self.assertEqual(violation.message, 'Test message')
        self.assertEqual(violation.description, 'Test description')
        self.assertEqual(violation.suggestion, 'Fix suggestion')

    def test_violation_with_context(self):
        """Test violation with context data."""
        context_data = {'function': 'test_func', 'value': 42}
        violation = LintViolation(
            rule_id='test.rule',
            file_path='/test.py',
            line=1,
            column=0,
            severity=Severity.INFO,
            message='Message',
            description='Description',
            suggestion='Suggestion',
            context=context_data
        )

        self.assertEqual(violation.context, context_data)
        self.assertEqual(violation.context['function'], 'test_func')


class TestLintContext(unittest.TestCase):
    """Test LintContext dataclass."""

    def test_context_creation(self):
        """Test creating a lint context."""
        code = "x = 42"
        tree = ast.parse(code)

        context = LintContext(
            file_path=Path('/test.py'),
            file_content=code,
            ast_tree=tree,
            current_function='my_func',
            current_class='MyClass',
            node_stack=[],
            metadata={'key': 'value'}
        )

        self.assertEqual(context.file_path, Path('/test.py'))
        self.assertEqual(context.file_content, code)
        self.assertEqual(context.ast_tree, tree)
        self.assertEqual(context.current_function, 'my_func')
        self.assertEqual(context.current_class, 'MyClass')
        self.assertEqual(context.node_stack, [])
        self.assertEqual(context.metadata['key'], 'value')

    def test_context_minimal(self):
        """Test context with minimal fields."""
        context = LintContext(file_path=Path('/test.py'))

        self.assertEqual(context.file_path, Path('/test.py'))
        self.assertIsNone(context.file_content)
        self.assertIsNone(context.ast_tree)
        self.assertIsNone(context.current_function)
        self.assertIsNone(context.current_class)
        self.assertIsNone(context.node_stack)
        self.assertIsNone(context.metadata)


class TestLintRule(unittest.TestCase):
    """Test LintRule abstract base class."""

    def setUp(self):
        """Create a concrete test implementation."""
        class TestRuleImpl(LintRule):
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
                return {"test", "example"}

            def check(self, context):
                return []

        self.TestRuleImpl = TestRuleImpl

    def test_rule_properties(self):
        """Test rule properties."""
        rule = self.TestRuleImpl()

        self.assertEqual(rule.rule_id, "test.rule")
        self.assertEqual(rule.rule_name, "Test Rule")
        self.assertEqual(rule.description, "Test rule description")
        self.assertEqual(rule.severity, Severity.WARNING)
        self.assertEqual(rule.categories, {"test", "example"})

    def test_get_configuration_no_metadata(self):
        """Test get_configuration with no metadata."""
        rule = self.TestRuleImpl()
        config = rule.get_configuration(None)
        self.assertEqual(config, {})

    def test_get_configuration_with_metadata(self):
        """Test get_configuration with metadata."""
        rule = self.TestRuleImpl()
        metadata = {
            'rules': {
                'test.rule': {
                    'config': {
                        'option1': 'value1',
                        'option2': 42
                    }
                }
            }
        }
        config = rule.get_configuration(metadata)
        self.assertEqual(config['option1'], 'value1')
        self.assertEqual(config['option2'], 42)

    def test_is_enabled_default(self):
        """Test is_enabled with default (True)."""
        rule = self.TestRuleImpl()
        self.assertTrue(rule.is_enabled(None))
        self.assertTrue(rule.is_enabled({}))

    def test_is_enabled_disabled(self):
        """Test is_enabled when disabled."""
        rule = self.TestRuleImpl()
        metadata = {
            'rules': {
                'test.rule': {
                    'enabled': False
                }
            }
        }
        self.assertFalse(rule.is_enabled(metadata))


class TestASTLintRule(unittest.TestCase):
    """Test ASTLintRule abstract base class."""

    def setUp(self):
        """Create a concrete test implementation."""
        class TestASTRuleImpl(ASTLintRule):
            @property
            def rule_id(self) -> str:
                return "test.ast.rule"

            @property
            def rule_name(self) -> str:
                return "Test AST Rule"

            @property
            def description(self) -> str:
                return "Test AST rule"

            @property
            def severity(self) -> Severity:
                return Severity.INFO

            @property
            def categories(self) -> set:
                return {"ast", "test"}

            def should_check_node(self, node, context):
                return isinstance(node, ast.Constant)

            def check_node(self, node, context):
                if isinstance(node.value, int) and node.value == 42:
                    return [LintViolation(
                        rule_id=self.rule_id,
                        file_path=str(context.file_path),
                        line=node.lineno,
                        column=node.col_offset,
                        severity=self.severity,
                        message="Found 42",
                        description="Magic number 42",
                        suggestion="Use constant"
                    )]
                return []

        self.TestASTRuleImpl = TestASTRuleImpl

    def test_ast_rule_check(self):
        """Test AST rule checking."""
        rule = self.TestASTRuleImpl()
        code = "x = 42\ny = 10"

        context = LintContext(
            file_path=Path('/test.py'),
            file_content=code,
            ast_tree=ast.parse(code)
        )

        violations = rule.check(context)

        # Should find the 42
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].message, "Found 42")

    def test_should_check_node(self):
        """Test should_check_node method."""
        rule = self.TestASTRuleImpl()
        context = LintContext(file_path=Path('/test.py'))

        const_node = ast.Constant(value=42)
        name_node = ast.Name(id='x')

        self.assertTrue(rule.should_check_node(const_node, context))
        self.assertFalse(rule.should_check_node(name_node, context))


class MockReporter(LintReporter):
    """Mock reporter for testing."""

    def generate_report(self, violations):
        return f"Found {len(violations)} violations"

    def format_violation(self, violation):
        return f"{violation.rule_id}: {violation.message}"


class MockAnalyzer(LintAnalyzer):
    """Mock analyzer for testing."""

    def lint_file(self, file_path):
        return []

    def lint_directory(self, directory_path, recursive=True):
        return []

    def get_available_rules(self):
        return []

    def generate_report(self, violations, format='text'):
        return f"Report: {len(violations)} violations"


class MockRegistry(RuleRegistry):
    """Mock registry for testing."""

    def __init__(self):
        self.rules = {}

    def register_rule(self, rule):
        self.rules[rule.rule_id] = rule

    def unregister_rule(self, rule_id):
        if rule_id in self.rules:
            del self.rules[rule_id]

    def get_rule(self, rule_id):
        return self.rules.get(rule_id)

    def get_all_rules(self):
        return list(self.rules.values())

    def get_rules_by_category(self, category):
        return [r for r in self.rules.values() if category in r.categories]

    def get_rule_count(self):
        return len(self.rules)

    def get_categories(self):
        categories = set()
        for rule in self.rules.values():
            categories.update(rule.categories)
        return categories

    def discover_rules(self, package_paths):
        return 0


class TestInterfaces(unittest.TestCase):
    """Test abstract interfaces."""

    def test_reporter_interface(self):
        """Test LintReporter interface."""
        reporter = MockReporter()

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

        report = reporter.generate_report(violations)
        self.assertEqual(report, "Found 1 violations")

        formatted = reporter.format_violation(violations[0])
        self.assertEqual(formatted, "test.rule: Test")

    def test_analyzer_interface(self):
        """Test LintAnalyzer interface."""
        analyzer = MockAnalyzer()

        violations = analyzer.lint_file('/test.py')
        self.assertEqual(violations, [])

        violations = analyzer.lint_directory('/src')
        self.assertEqual(violations, [])

        rules = analyzer.get_available_rules()
        self.assertEqual(rules, [])

        report = analyzer.generate_report([])
        self.assertEqual(report, "Report: 0 violations")

    def test_registry_interface(self):
        """Test RuleRegistry interface."""
        registry = MockRegistry()

        # Create a mock rule
        rule = Mock()
        rule.rule_id = "test.rule"
        rule.categories = {"test", "mock"}

        # Test registration
        registry.register_rule(rule)
        self.assertEqual(registry.get_rule_count(), 1)

        # Test retrieval
        retrieved = registry.get_rule("test.rule")
        self.assertEqual(retrieved, rule)

        # Test get all
        all_rules = registry.get_all_rules()
        self.assertEqual(len(all_rules), 1)
        self.assertEqual(all_rules[0], rule)

        # Test by category
        test_rules = registry.get_rules_by_category("test")
        self.assertEqual(len(test_rules), 1)

        # Test categories
        categories = registry.get_categories()
        self.assertIn("test", categories)
        self.assertIn("mock", categories)

        # Test unregister
        registry.unregister_rule("test.rule")
        self.assertEqual(registry.get_rule_count(), 0)


if __name__ == '__main__':
    unittest.main()
