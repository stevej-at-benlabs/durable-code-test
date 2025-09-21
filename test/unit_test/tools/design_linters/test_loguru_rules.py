#!/usr/bin/env python3
"""
Purpose: Comprehensive unit tests for loguru rules
Scope: Tests all loguru rule classes and their methods
Overview: This module provides comprehensive tests for all loguru-specific
    linting rules, covering property access, node checking, violation creation,
    and edge cases. Tests verify proper implementation of the ASTLintRule
    interface and correct violation reporting.
Dependencies: unittest, ast, framework interfaces, loguru rules
Exports: Test classes for all loguru rule implementations including UseLoguruRule, LoguruImportRule, StructuredLoggingRule, LogLevelConsistencyRule, and LoguruConfigurationRule
Interfaces: Standard unittest test methods with setUp fixtures and parameterized test cases
Implementation: Uses unittest with AST parsing, mock objects, and comprehensive test coverage patterns
"""

import unittest
import ast
from pathlib import Path
from unittest.mock import Mock, patch

import sys
sys.path.insert(0, '/home/stevejackson/Projects/durable-code-test/tools')

from design_linters.framework.interfaces import LintContext, LintViolation, Severity
from design_linters.rules.logging.loguru_rules import (
    UseLoguruRule,
    LoguruImportRule,
    StructuredLoggingRule,
    LogLevelConsistencyRule,
    LoguruConfigurationRule
)


class TestUseLoguruRule(unittest.TestCase):
    """Test UseLoguruRule implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = UseLoguruRule()
        self.context = LintContext(file_path=Path('/test.py'))

    def test_rule_properties(self):
        """Test rule properties are correctly defined."""
        self.assertEqual(self.rule.rule_id, "logging.use-loguru")
        self.assertEqual(self.rule.rule_name, "Use Loguru for Logging")
        self.assertIn("loguru over standard logging", self.rule.description)
        self.assertEqual(self.rule.severity, Severity.INFO)
        self.assertEqual(self.rule.categories, {"logging", "loguru", "best-practices"})

    def test_should_check_node_import(self):
        """Test should_check_node for import statements."""
        import_node = ast.parse("import logging").body[0]
        from_import_node = ast.parse("from logging import getLogger").body[0]
        assign_node = ast.parse("x = 1").body[0]

        self.assertTrue(self.rule.should_check_node(import_node, self.context))
        self.assertTrue(self.rule.should_check_node(from_import_node, self.context))
        self.assertFalse(self.rule.should_check_node(assign_node, self.context))

    def test_check_node_import_logging(self):
        """Test detection of standard logging import."""
        node = ast.parse("import logging").body[0]
        violations = self.rule.check_node(node, self.context)

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation.rule_id, "logging.use-loguru")
        self.assertIn("Consider using loguru instead", violation.message)
        self.assertIn("logging", violation.message)
        self.assertEqual(violation.context['logging_type'], 'logging')

    def test_check_node_import_logging_with_alias(self):
        """Test detection of aliased logging import."""
        node = ast.parse("import logging as log").body[0]
        violations = self.rule.check_node(node, self.context)

        self.assertEqual(len(violations), 1)
        self.assertIn("logging", violations[0].message)

    def test_check_node_from_import_logging(self):
        """Test detection of from logging import."""
        node = ast.parse("from logging import getLogger").body[0]
        violations = self.rule.check_node(node, self.context)

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertIn("Consider using loguru instead", violation.message)
        self.assertEqual(violation.context['logging_type'], 'logging')

    def test_check_node_non_logging_import(self):
        """Test that non-logging imports are ignored."""
        node = ast.parse("import os").body[0]
        violations = self.rule.check_node(node, self.context)
        self.assertEqual(len(violations), 0)

        node = ast.parse("from collections import defaultdict").body[0]
        violations = self.rule.check_node(node, self.context)
        self.assertEqual(len(violations), 0)

    def test_check_node_loguru_import(self):
        """Test that loguru imports are not flagged."""
        node = ast.parse("from loguru import logger").body[0]
        violations = self.rule.check_node(node, self.context)
        self.assertEqual(len(violations), 0)

    def test_create_violation(self):
        """Test _create_violation method."""
        node = ast.parse("import logging").body[0]
        violation = self.rule._create_violation(node, self.context, 'logging')

        self.assertEqual(violation.rule_id, "logging.use-loguru")
        self.assertEqual(violation.severity, Severity.INFO)
        self.assertIn("Consider using loguru instead", violation.message)
        self.assertIn("Replace with: from loguru import logger", violation.suggestion)
        self.assertEqual(violation.context['logging_type'], 'logging')


class TestLoguruImportRule(unittest.TestCase):
    """Test LoguruImportRule implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = LoguruImportRule()
        self.context = LintContext(file_path=Path('/test.py'))

    def test_rule_properties(self):
        """Test rule properties are correctly defined."""
        self.assertEqual(self.rule.rule_id, "logging.loguru-import")
        self.assertEqual(self.rule.rule_name, "Proper Loguru Import")
        self.assertIn("recommended pattern", self.rule.description)
        self.assertEqual(self.rule.severity, Severity.WARNING)
        self.assertEqual(self.rule.categories, {"logging", "loguru", "imports"})

    def test_should_check_node(self):
        """Test should_check_node for import statements."""
        import_node = ast.parse("import loguru").body[0]
        from_import_node = ast.parse("from loguru import logger").body[0]
        assign_node = ast.parse("x = 1").body[0]

        self.assertTrue(self.rule.should_check_node(import_node, self.context))
        self.assertTrue(self.rule.should_check_node(from_import_node, self.context))
        self.assertFalse(self.rule.should_check_node(assign_node, self.context))

    def test_check_node_correct_loguru_import(self):
        """Test that correct loguru import is not flagged."""
        node = ast.parse("from loguru import logger").body[0]
        violations = self.rule.check_node(node, self.context)
        self.assertEqual(len(violations), 0)

    def test_check_node_incorrect_loguru_from_import(self):
        """Test detection of incorrect loguru from import."""
        node = ast.parse("from loguru import Logger").body[0]
        violations = self.rule.check_node(node, self.context)

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertIn("Import loguru.Logger not recommended", violation.message)
        self.assertIn("Use: from loguru import logger", violation.suggestion)
        self.assertEqual(violation.context['imported_name'], 'Logger')

    def test_check_node_multiple_incorrect_imports(self):
        """Test detection of multiple incorrect imports."""
        node = ast.parse("from loguru import Logger, config").body[0]
        violations = self.rule.check_node(node, self.context)

        self.assertEqual(len(violations), 2)
        imported_names = {v.context['imported_name'] for v in violations}
        self.assertEqual(imported_names, {'Logger', 'config'})

    def test_check_node_full_module_import(self):
        """Test detection of full module import."""
        node = ast.parse("import loguru").body[0]
        violations = self.rule.check_node(node, self.context)

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertIn("Use 'from loguru import logger'", violation.message)
        self.assertEqual(violation.context['import_type'], 'full_module')

    def test_check_node_aliased_module_import(self):
        """Test detection of aliased module import."""
        node = ast.parse("import loguru as log").body[0]
        violations = self.rule.check_node(node, self.context)

        self.assertEqual(len(violations), 1)
        self.assertIn("Use 'from loguru import logger'", violations[0].message)

    def test_check_node_non_loguru_import(self):
        """Test that non-loguru imports are ignored."""
        node = ast.parse("import logging").body[0]
        violations = self.rule.check_node(node, self.context)
        self.assertEqual(len(violations), 0)

        node = ast.parse("from collections import defaultdict").body[0]
        violations = self.rule.check_node(node, self.context)
        self.assertEqual(len(violations), 0)


class TestStructuredLoggingRule(unittest.TestCase):
    """Test StructuredLoggingRule implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = StructuredLoggingRule()
        self.context = LintContext(file_path=Path('/test.py'))

    def test_rule_properties(self):
        """Test rule properties are correctly defined."""
        self.assertEqual(self.rule.rule_id, "logging.structured-logging")
        self.assertEqual(self.rule.rule_name, "Structured Logging")
        self.assertIn("structured logging", self.rule.description)
        self.assertEqual(self.rule.severity, Severity.INFO)
        self.assertEqual(self.rule.categories, {"logging", "loguru", "observability"})

    def test_should_check_node(self):
        """Test should_check_node for logger calls."""
        logger_call = ast.parse("logger.info('test')").body[0].value
        other_call = ast.parse("print('test')").body[0].value
        assignment = ast.parse("x = 1").body[0]

        self.assertTrue(self.rule.should_check_node(logger_call, self.context))
        self.assertFalse(self.rule.should_check_node(other_call, self.context))
        self.assertFalse(self.rule.should_check_node(assignment, self.context))

    def test_check_node_non_call_raises_error(self):
        """Test that non-Call nodes raise TypeError."""
        node = ast.parse("x = 1").body[0]
        with self.assertRaises(TypeError):
            self.rule.check_node(node, self.context)

    def test_check_node_non_logger_call(self):
        """Test that non-logger calls return empty violations."""
        node = ast.parse("print('test')").body[0].value
        violations = self.rule.check_node(node, self.context)
        self.assertEqual(len(violations), 0)

    def test_check_node_f_string_logging(self):
        """Test detection of f-string in logging."""
        code = "logger.info(f'User {user_id} logged in')"
        node = ast.parse(code).body[0].value
        violations = self.rule.check_node(node, self.context)

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertIn("Use structured logging instead", violation.message)
        self.assertIn("string formatting", violation.message)
        self.assertEqual(violation.context['method'], 'info')
        self.assertEqual(violation.context['issue'], 'string_formatting')

    def test_check_node_format_method_logging(self):
        """Test detection of .format() method in logging."""
        code = "logger.error('Error in {}'.format(module))"
        node = ast.parse(code).body[0].value
        violations = self.rule.check_node(node, self.context)

        self.assertEqual(len(violations), 1)
        self.assertIn("Use structured logging instead", violations[0].message)

    def test_check_node_percent_formatting(self):
        """Test detection of % formatting in logging."""
        code = "logger.warning('Value is %s' % value)"
        node = ast.parse(code).body[0].value
        violations = self.rule.check_node(node, self.context)

        self.assertEqual(len(violations), 1)
        self.assertIn("Use structured logging instead", violations[0].message)

    def test_check_node_complex_message_without_context(self):
        """Test detection of complex messages without context variables."""
        code = "logger.info('Operation completed successfully with all validation checks passed')"
        node = ast.parse(code).body[0].value
        violations = self.rule.check_node(node, self.context)

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertIn("Consider adding context variables", violation.message)
        self.assertEqual(violation.context['issue'], 'missing_context')

    def test_check_node_simple_message_no_violation(self):
        """Test that simple messages don't trigger violations."""
        code = "logger.info('OK')"
        node = ast.parse(code).body[0].value
        violations = self.rule.check_node(node, self.context)

        self.assertEqual(len(violations), 0)

    def test_check_node_structured_logging_no_violation(self):
        """Test that proper structured logging doesn't trigger violations."""
        code = "logger.info('User logged in', user_id=user_id, ip=ip)"
        node = ast.parse(code).body[0].value
        violations = self.rule.check_node(node, self.context)

        self.assertEqual(len(violations), 0)

    def test_is_logger_call(self):
        """Test _is_logger_call method."""
        valid_calls = [
            "logger.debug('test')",
            "logger.info('test')",
            "logger.warning('test')",
            "logger.error('test')",
            "logger.critical('test')",
            "logger.success('test')"
        ]

        for code in valid_calls:
            with self.subTest(code=code):
                node = ast.parse(code).body[0].value
                self.assertTrue(self.rule._is_logger_call(node))

        invalid_calls = [
            "logger.add('test')",
            "other.info('test')",
            "print('test')"
        ]

        for code in invalid_calls:
            with self.subTest(code=code):
                node = ast.parse(code).body[0].value
                self.assertFalse(self.rule._is_logger_call(node))

    def test_uses_string_formatting(self):
        """Test _uses_string_formatting method."""
        formatting_cases = [
            "logger.info(f'test {var}')",
            "logger.info('test {}'.format(var))",
            "logger.info('test %s' % var)"
        ]

        for code in formatting_cases:
            with self.subTest(code=code):
                node = ast.parse(code).body[0].value
                self.assertTrue(self.rule._uses_string_formatting(node))

        non_formatting_cases = [
            "logger.info('test')",
            "logger.info('test', var=var)"
        ]

        for code in non_formatting_cases:
            with self.subTest(code=code):
                node = ast.parse(code).body[0].value
                self.assertFalse(self.rule._uses_string_formatting(node))

    def test_has_complex_message(self):
        """Test _has_complex_message method."""
        complex_cases = [
            "logger.info('This is a very long message that exceeds fifty characters')",
            "logger.info('Operation completed successfully')",
            "logger.info('Processing started for user data')",
            "logger.info('Started')"  # Contains 'started' keyword
        ]

        for code in complex_cases:
            with self.subTest(code=code):
                node = ast.parse(code).body[0].value
                self.assertTrue(self.rule._has_complex_message(node))

        simple_cases = [
            "logger.info('OK')",
            "logger.info('Done')",
            "logger.info('Simple message', context=value)"  # Has keywords
        ]

        for code in simple_cases:
            with self.subTest(code=code):
                node = ast.parse(code).body[0].value
                self.assertFalse(self.rule._has_complex_message(node))

    def test_check_node_no_args(self):
        """Test handling of logger calls with no arguments."""
        code = "logger.info()"
        node = ast.parse(code).body[0].value
        violations = self.rule.check_node(node, self.context)

        # Should not crash and return no violations
        self.assertEqual(len(violations), 0)


class TestLogLevelConsistencyRule(unittest.TestCase):
    """Test LogLevelConsistencyRule implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = LogLevelConsistencyRule()
        self.context = LintContext(file_path=Path('/test.py'))

    def test_rule_properties(self):
        """Test rule properties are correctly defined."""
        self.assertEqual(self.rule.rule_id, "logging.log-level-consistency")
        self.assertEqual(self.rule.rule_name, "Log Level Consistency")
        self.assertIn("appropriate log levels", self.rule.description)
        self.assertEqual(self.rule.severity, Severity.INFO)
        self.assertEqual(self.rule.categories, {"logging", "loguru", "consistency"})

    def test_should_check_node(self):
        """Test should_check_node for logger calls."""
        logger_call = ast.parse("logger.info('test')").body[0].value
        other_call = ast.parse("print('test')").body[0].value

        self.assertTrue(self.rule.should_check_node(logger_call, self.context))
        self.assertFalse(self.rule.should_check_node(other_call, self.context))

    def test_check_node_non_call_raises_error(self):
        """Test that non-Call nodes raise TypeError."""
        node = ast.parse("x = 1").body[0]
        with self.assertRaises(TypeError):
            self.rule.check_node(node, self.context)

    def test_check_node_error_message_with_info_level(self):
        """Test detection of error message using info level."""
        code = "logger.info('An error occurred while processing')"
        node = ast.parse(code).body[0].value
        violations = self.rule.check_node(node, self.context)

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertIn("suggests 'error' level", violation.message)
        self.assertIn("using 'info'", violation.message)
        self.assertEqual(violation.context['current_level'], 'info')
        self.assertEqual(violation.context['suggested_level'], 'error')

    def test_check_node_warning_message_with_error_level(self):
        """Test detection of warning message using error level."""
        code = "logger.error('This is deprecated and will be removed')"
        node = ast.parse(code).body[0].value
        violations = self.rule.check_node(node, self.context)

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertIn("suggests 'warning' level", violation.message)
        self.assertEqual(violation.context['suggested_level'], 'warning')

    def test_check_node_success_message_with_info_level(self):
        """Test detection of success message using info level."""
        code = "logger.info('Operation completed successfully')"
        node = ast.parse(code).body[0].value
        violations = self.rule.check_node(node, self.context)

        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].context['suggested_level'], 'success')

    def test_check_node_debug_message_with_info_level(self):
        """Test detection of debug message using info level."""
        code = "logger.info('Debug: variable state is active')"
        node = ast.parse(code).body[0].value
        violations = self.rule.check_node(node, self.context)

        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].context['suggested_level'], 'debug')

    def test_check_node_correct_level_no_violation(self):
        """Test that correct level usage doesn't trigger violations."""
        correct_cases = [
            "logger.error('An error occurred')",
            "logger.warning('This is deprecated')",
            "logger.success('Operation completed successfully')",
            "logger.debug('Debug information')",
            "logger.info('General information')"
        ]

        for code in correct_cases:
            with self.subTest(code=code):
                node = ast.parse(code).body[0].value
                violations = self.rule.check_node(node, self.context)
                self.assertEqual(len(violations), 0)

    def test_check_node_non_string_message(self):
        """Test handling of non-string message arguments."""
        code = "logger.info(123)"
        node = ast.parse(code).body[0].value
        violations = self.rule.check_node(node, self.context)

        # Should not crash and return no violations
        self.assertEqual(len(violations), 0)

    def test_check_node_no_args(self):
        """Test handling of logger calls with no arguments."""
        code = "logger.info()"
        node = ast.parse(code).body[0].value
        violations = self.rule.check_node(node, self.context)

        self.assertEqual(len(violations), 0)

    def test_suggest_log_level(self):
        """Test _suggest_log_level method."""
        test_cases = [
            ("An error occurred", "error"),
            ("Exception caught", "error"),
            ("Failed to process", "error"),
            ("This is deprecated", "warning"),
            ("Fallback used", "warning"),
            ("Operation completed successfully", "success"),
            ("Debug information", "debug"),
            ("Variable state", "debug"),
            ("General message", None)
        ]

        for message, expected in test_cases:
            with self.subTest(message=message):
                result = self.rule._suggest_log_level(message)
                self.assertEqual(result, expected)

    def test_is_logger_call(self):
        """Test _is_logger_call method."""
        valid_calls = [
            "logger.debug('test')",
            "logger.info('test')",
            "logger.warning('test')",
            "logger.error('test')",
            "logger.critical('test')",
            "logger.success('test')"
        ]

        for code in valid_calls:
            with self.subTest(code=code):
                node = ast.parse(code).body[0].value
                self.assertTrue(self.rule._is_logger_call(node))

        invalid_calls = [
            "logger.add('test')",
            "other.info('test')",
            "print('test')"
        ]

        for code in invalid_calls:
            with self.subTest(code=code):
                node = ast.parse(code).body[0].value
                self.assertFalse(self.rule._is_logger_call(node))


class TestLoguruConfigurationRule(unittest.TestCase):
    """Test LoguruConfigurationRule implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = LoguruConfigurationRule()
        self.context = LintContext(file_path=Path('/test.py'))

    def test_rule_properties(self):
        """Test rule properties are correctly defined."""
        self.assertEqual(self.rule.rule_id, "logging.loguru-configuration")
        self.assertEqual(self.rule.rule_name, "Loguru Configuration")
        self.assertIn("proper loguru configuration", self.rule.description)
        self.assertEqual(self.rule.severity, Severity.WARNING)
        self.assertEqual(self.rule.categories, {"logging", "loguru", "configuration"})

    def test_should_check_node(self):
        """Test should_check_node for logger.add calls."""
        add_call = ast.parse("logger.add('file.log')").body[0].value
        info_call = ast.parse("logger.info('test')").body[0].value
        other_call = ast.parse("print('test')").body[0].value

        self.assertTrue(self.rule.should_check_node(add_call, self.context))
        self.assertFalse(self.rule.should_check_node(info_call, self.context))
        self.assertFalse(self.rule.should_check_node(other_call, self.context))

    def test_check_node_non_call_raises_error(self):
        """Test that non-Call nodes raise TypeError."""
        node = ast.parse("x = 1").body[0]
        with self.assertRaises(TypeError):
            self.rule.check_node(node, self.context)

    def test_check_node_no_sink_argument(self):
        """Test detection of logger.add() without sink argument."""
        code = "logger.add()"
        node = ast.parse(code).body[0].value
        violations = self.rule.check_node(node, self.context)

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertIn("called without sink argument", violation.message)
        self.assertEqual(violation.context['issue'], 'missing_sink')

    def test_check_node_file_sink_missing_options(self):
        """Test suggestions for missing configuration options with file sink."""
        code = "logger.add('app.log')"
        node = ast.parse(code).body[0].value
        violations = self.rule.check_node(node, self.context)

        # Should suggest all recommended options for file sinks
        self.assertEqual(len(violations), 4)
        suggested_options = {v.context['missing_option'] for v in violations}
        expected_options = {'level', 'format', 'rotation', 'retention'}
        self.assertEqual(suggested_options, expected_options)

        # All should be INFO severity
        for violation in violations:
            self.assertEqual(violation.severity, Severity.INFO)

    def test_check_node_file_sink_with_some_options(self):
        """Test that existing options are not suggested again."""
        code = "logger.add('app.log', level='INFO', rotation='1 MB')"
        node = ast.parse(code).body[0].value
        violations = self.rule.check_node(node, self.context)

        # Should only suggest missing options
        self.assertEqual(len(violations), 2)
        suggested_options = {v.context['missing_option'] for v in violations}
        expected_options = {'format', 'retention'}
        self.assertEqual(suggested_options, expected_options)

    def test_check_node_stderr_sink_no_suggestions(self):
        """Test that stderr/stdout sinks don't get file-specific suggestions."""
        stderr_cases = [
            "logger.add('<stderr>')",
            "logger.add('<stdout>')",
            "logger.add(sys.stderr)"
        ]

        for code in stderr_cases[:2]:  # Skip sys.stderr as it's more complex to parse
            with self.subTest(code=code):
                node = ast.parse(code).body[0].value
                violations = self.rule.check_node(node, self.context)
                self.assertEqual(len(violations), 0)

    def test_check_node_complete_file_configuration(self):
        """Test that complete file configuration doesn't trigger violations."""
        code = """logger.add('app.log', level='INFO', format='{time} {level} {message}',
                            rotation='1 MB', retention='7 days')"""
        node = ast.parse(code).body[0].value
        violations = self.rule.check_node(node, self.context)

        self.assertEqual(len(violations), 0)

    def test_check_node_variable_sink(self):
        """Test handling of variable as sink argument."""
        code = "logger.add(sink_variable)"
        node = ast.parse(code).body[0].value
        violations = self.rule.check_node(node, self.context)

        # Should not suggest file-specific options for variable sinks
        self.assertEqual(len(violations), 0)

    def test_check_node_function_call_sink(self):
        """Test handling of function call as sink argument."""
        code = "logger.add(get_sink())"
        node = ast.parse(code).body[0].value
        violations = self.rule.check_node(node, self.context)

        # Should not suggest file-specific options for function call sinks
        self.assertEqual(len(violations), 0)


class TestRuleIntegration(unittest.TestCase):
    """Integration tests for loguru rules."""

    def setUp(self):
        """Set up test fixtures."""
        self.context = LintContext(file_path=Path('/test.py'))

    def test_all_rules_implement_interface(self):
        """Test that all rules properly implement ASTLintRule interface."""
        rules = [
            UseLoguruRule(),
            LoguruImportRule(),
            StructuredLoggingRule(),
            LogLevelConsistencyRule(),
            LoguruConfigurationRule()
        ]

        for rule in rules:
            with self.subTest(rule=rule.__class__.__name__):
                # Test required properties exist
                self.assertIsInstance(rule.rule_id, str)
                self.assertIsInstance(rule.rule_name, str)
                self.assertIsInstance(rule.description, str)
                self.assertIsInstance(rule.severity, Severity)
                self.assertIsInstance(rule.categories, set)

                # Test required methods exist and are callable
                self.assertTrue(hasattr(rule, 'should_check_node'))
                self.assertTrue(callable(rule.should_check_node))
                self.assertTrue(hasattr(rule, 'check_node'))
                self.assertTrue(callable(rule.check_node))
                self.assertTrue(hasattr(rule, 'check'))
                self.assertTrue(callable(rule.check))

    def test_rules_unique_ids(self):
        """Test that all rules have unique IDs."""
        rules = [
            UseLoguruRule(),
            LoguruImportRule(),
            StructuredLoggingRule(),
            LogLevelConsistencyRule(),
            LoguruConfigurationRule()
        ]

        rule_ids = [rule.rule_id for rule in rules]
        self.assertEqual(len(rule_ids), len(set(rule_ids)), "Rule IDs must be unique")

    def test_rules_handle_empty_context(self):
        """Test that rules handle empty/minimal context gracefully."""
        rules = [
            UseLoguruRule(),
            LoguruImportRule(),
            StructuredLoggingRule(),
            LogLevelConsistencyRule(),
            LoguruConfigurationRule()
        ]

        empty_context = LintContext()

        for rule in rules:
            with self.subTest(rule=rule.__class__.__name__):
                # Should not crash with empty context
                try:
                    violations = rule.check(empty_context)
                    self.assertIsInstance(violations, list)
                except Exception as e:
                    self.fail(f"Rule {rule.__class__.__name__} failed with empty context: {e}")

    def test_violation_creation_consistency(self):
        """Test that all rules create violations with consistent structure."""
        # Test UseLoguruRule violation creation
        rule = UseLoguruRule()
        node = ast.parse("import logging").body[0]
        violations = rule.check_node(node, self.context)

        if violations:
            violation = violations[0]
            self.assertIsInstance(violation.rule_id, str)
            self.assertIsInstance(violation.file_path, str)
            self.assertIsInstance(violation.line, int)
            self.assertIsInstance(violation.column, int)
            self.assertIsInstance(violation.severity, Severity)
            self.assertIsInstance(violation.message, str)
            self.assertIsInstance(violation.description, str)
            # suggestion and context can be None, but if present should be proper types
            if violation.suggestion is not None:
                self.assertIsInstance(violation.suggestion, str)
            if violation.context is not None:
                self.assertIsInstance(violation.context, dict)


if __name__ == '__main__':
    unittest.main()
