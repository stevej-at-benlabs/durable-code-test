#!/usr/bin/env python3
"""
Purpose: Tests for all rule modules
Scope: Test all implemented rules
Overview: This module tests all rule implementations.
Dependencies: unittest, all rule modules
"""

import unittest
import ast
from pathlib import Path

import sys
sys.path.insert(0, '/home/stevejackson/Projects/durable-code-test/tools')

from design_linters.framework.interfaces import LintContext
from design_linters.rules.literals.magic_number_rules import MagicNumberRule, MagicComplexRule
from design_linters.rules.literals.magic_string_rules import MagicStringRule, HardcodedPathRule
from design_linters.rules.style.print_statement_rules import PrintStatementRule, ConsoleOutputRule
from design_linters.rules.style.nesting_rules import ExcessiveNestingRule, DeepFunctionRule
from design_linters.rules.solid.srp_rules import (
    TooManyMethodsRule, TooManyResponsibilitiesRule,
    LowCohesionRule, ClassTooBigRule, TooManyDependenciesRule
)
from design_linters.rules.logging.general_logging_rules import (
    NoPlainPrintRule, ProperLogLevelsRule, LoggingInExceptionsRule
)
from design_linters.rules.logging.loguru_rules import (
    UseLoguruRule, LoguruImportRule, StructuredLoggingRule,
    LogLevelConsistencyRule, LoguruConfigurationRule
)


class TestMagicNumberRules(unittest.TestCase):
    """Test magic number detection rules."""

    def setUp(self):
        self.rule = MagicNumberRule()

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, 'literals.magic-number')
        self.assertIn('literals', self.rule.categories)

    def test_should_check_node(self):
        """Test node checking logic."""
        const_node = ast.Constant(value=42)
        name_node = ast.Name(id='x')
        context = LintContext(file_path=Path('/src/test.py'))

        self.assertTrue(self.rule.should_check_node(const_node, context))
        self.assertFalse(self.rule.should_check_node(name_node, context))

    def test_allowed_numbers(self):
        """Test that allowed numbers are not flagged."""
        code = "x = 0\ny = 1\nz = -1"
        context = LintContext(
            file_path=Path('/src/test.py'),
            file_content=code,
            ast_tree=ast.parse(code)
        )

        violations = self.rule.check(context)
        # Should not flag 0, 1, -1
        self.assertEqual(len(violations), 0)

    def test_configuration_handling(self):
        """Test configuration handling."""
        config = self.rule.get_configuration(None)
        self.assertEqual(config, {})

        metadata = {
            'rules': {
                'literals.magic-number': {
                    'config': {'allowed_numbers': [0, 1, 42]}
                }
            }
        }
        config = self.rule.get_configuration(metadata)
        self.assertEqual(config['allowed_numbers'], [0, 1, 42])


class TestMagicComplexRule(unittest.TestCase):
    """Test magic complex number rule."""

    def setUp(self):
        self.rule = MagicComplexRule()

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, 'literals.magic-complex')
        self.assertIn('literals', self.rule.categories)

    def test_should_check_node(self):
        """Test complex number detection."""
        complex_node = ast.Constant(value=3+4j)
        int_node = ast.Constant(value=42)
        context = LintContext(file_path=Path('/src/test.py'))

        self.assertTrue(self.rule.should_check_node(complex_node, context))
        self.assertFalse(self.rule.should_check_node(int_node, context))


class TestMagicStringRules(unittest.TestCase):
    """Test magic string detection rules."""

    def setUp(self):
        self.rule = MagicStringRule()

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, 'literals.magic-string')
        self.assertIn('literals', self.rule.categories)

    def test_should_check_node(self):
        """Test string node checking."""
        string_node = ast.Constant(value="test string")
        int_node = ast.Constant(value=42)
        context = LintContext(file_path=Path('/src/test.py'))

        self.assertTrue(self.rule.should_check_node(string_node, context))
        self.assertFalse(self.rule.should_check_node(int_node, context))

    def test_allowed_strings(self):
        """Test that simple strings are allowed."""
        code = 'x = ""\ny = " "'
        context = LintContext(
            file_path=Path('/src/test.py'),
            file_content=code,
            ast_tree=ast.parse(code)
        )

        violations = self.rule.check(context)
        # Empty strings should not be flagged
        self.assertEqual(len(violations), 0)


class TestHardcodedPathRule(unittest.TestCase):
    """Test hardcoded path detection."""

    def setUp(self):
        self.rule = HardcodedPathRule()

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, 'literals.hardcoded-path')
        self.assertIn('paths', self.rule.categories)

    def test_should_check_node(self):
        """Test path detection logic."""
        path_node = ast.Constant(value="/var/log/app.log")
        string_node = ast.Constant(value="hello")
        context = LintContext(file_path=Path('/src/test.py'))

        self.assertTrue(self.rule.should_check_node(path_node, context))
        self.assertFalse(self.rule.should_check_node(string_node, context))


class TestPrintStatementRules(unittest.TestCase):
    """Test print statement detection rules."""

    def setUp(self):
        self.rule = PrintStatementRule()

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, 'style.print-statement')
        self.assertIn('style', self.rule.categories)

    def test_should_check_node(self):
        """Test print call detection."""
        print_call = ast.Call(func=ast.Name(id='print'), args=[], keywords=[])
        other_call = ast.Call(func=ast.Name(id='foo'), args=[], keywords=[])
        context = LintContext(file_path=Path('/src/test.py'))

        self.assertTrue(self.rule.should_check_node(print_call, context))
        self.assertFalse(self.rule.should_check_node(other_call, context))


class TestConsoleOutputRule(unittest.TestCase):
    """Test console output rule."""

    def setUp(self):
        self.rule = ConsoleOutputRule()

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, 'style.console-output')
        self.assertIn('console', self.rule.categories)


class TestNestingRules(unittest.TestCase):
    """Test nesting depth rules."""

    def setUp(self):
        self.rule = ExcessiveNestingRule()

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, 'style.excessive-nesting')
        self.assertIn('readability', self.rule.categories)

    def test_should_check_node(self):
        """Test function node checking."""
        func_node = ast.FunctionDef(name='test', args=ast.arguments(
            posonlyargs=[], args=[], defaults=[], kwonlyargs=[], kw_defaults=[]
        ), body=[], decorator_list=[])
        other_node = ast.Name(id='x')
        context = LintContext(file_path=Path('/src/test.py'))

        self.assertTrue(self.rule.should_check_node(func_node, context))
        self.assertFalse(self.rule.should_check_node(other_node, context))


class TestSRPRules(unittest.TestCase):
    """Test SOLID SRP rules."""

    def test_too_many_methods_rule(self):
        """Test too many methods detection."""
        rule = TooManyMethodsRule()
        self.assertEqual(rule.rule_id, 'solid.srp.too-many-methods')
        self.assertIn('solid', rule.categories)

    def test_too_many_responsibilities_rule(self):
        """Test multiple responsibilities detection."""
        rule = TooManyResponsibilitiesRule()
        self.assertEqual(rule.rule_id, 'solid.srp.multiple-responsibilities')
        self.assertIn('solid', rule.categories)

    def test_low_cohesion_rule(self):
        """Test low cohesion detection."""
        rule = LowCohesionRule()
        self.assertEqual(rule.rule_id, 'solid.srp.low-cohesion')
        self.assertIn('cohesion', rule.categories)

    def test_class_too_big_rule(self):
        """Test class size detection."""
        rule = ClassTooBigRule()
        self.assertEqual(rule.rule_id, 'solid.srp.class-too-big')
        self.assertIn('size', rule.categories)

    def test_too_many_dependencies_rule(self):
        """Test dependency count detection."""
        rule = TooManyDependenciesRule()
        self.assertEqual(rule.rule_id, 'solid.srp.too-many-dependencies')
        self.assertIn('dependencies', rule.categories)


class TestLoggingRules(unittest.TestCase):
    """Test logging rules."""

    def test_no_plain_print_rule(self):
        """Test no print rule."""
        rule = NoPlainPrintRule()
        self.assertEqual(rule.rule_id, 'logging.no-print')
        self.assertIn('logging', rule.categories)

    def test_use_loguru_rule(self):
        """Test use loguru rule."""
        rule = UseLoguruRule()
        self.assertEqual(rule.rule_id, 'logging.use-loguru')
        self.assertIn('loguru', rule.categories)

    def test_loguru_import_rule(self):
        """Test loguru import pattern."""
        rule = LoguruImportRule()
        self.assertEqual(rule.rule_id, 'logging.loguru-import')
        self.assertIn('loguru', rule.categories)

    def test_structured_logging_rule(self):
        """Test structured logging."""
        rule = StructuredLoggingRule()
        self.assertEqual(rule.rule_id, 'logging.structured-logging')
        self.assertIn('logging', rule.categories)

    def test_log_level_consistency_rule(self):
        """Test log level consistency."""
        rule = LogLevelConsistencyRule()
        self.assertEqual(rule.rule_id, 'logging.log-level-consistency')
        self.assertIn('logging', rule.categories)

    def test_loguru_configuration_rule(self):
        """Test loguru configuration."""
        rule = LoguruConfigurationRule()
        self.assertEqual(rule.rule_id, 'logging.loguru-configuration')
        self.assertIn('loguru', rule.categories)

    def test_logging_in_exceptions_rule(self):
        """Test logging in exception handlers."""
        rule = LoggingInExceptionsRule()
        self.assertEqual(rule.rule_id, 'logging.exception-logging')
        self.assertIn('error-handling', rule.categories)


if __name__ == '__main__':
    unittest.main()
