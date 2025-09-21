#!/usr/bin/env python3
"""
Purpose: Comprehensive unit tests for general logging rules
Scope: Tests all rule classes in general_logging_rules.py
Overview: This module provides comprehensive tests for NoPlainPrintRule,
    ProperLogLevelsRule, and LoggingInExceptionsRule to ensure proper
    logging best practices enforcement and validate rule behavior.
Dependencies: unittest, ast, framework modules
Exports: TestNoPlainPrintRule, TestProperLogLevelsRule, TestLoggingInExceptionsRule
Interfaces: Standard unittest.TestCase interface for test execution
Implementation: Comprehensive test coverage using unittest framework with AST parsing
"""

import unittest
import ast
from pathlib import Path
from typing import Dict, Any

import sys
sys.path.insert(0, '/home/stevejackson/Projects/durable-code-test/tools')

from design_linters.framework.interfaces import LintContext, Severity
from design_linters.rules.logging.general_logging_rules import (
    NoPlainPrintRule,
    ProperLogLevelsRule,
    LoggingInExceptionsRule
)


class TestNoPlainPrintRule(unittest.TestCase):
    """Test NoPlainPrintRule functionality."""

    def setUp(self):
        self.rule = NoPlainPrintRule()
        self.context = LintContext(file_path=Path('/production.py'))

    def test_rule_properties(self):
        """Test rule properties are correctly defined."""
        self.assertEqual(self.rule.rule_id, 'logging.no-print')
        self.assertEqual(self.rule.rule_name, 'No Print Statements')
        self.assertEqual(self.rule.severity, Severity.WARNING)
        self.assertEqual(self.rule.categories, {'logging', 'production', 'anti-patterns'})
        self.assertIn('print statements', self.rule.description.lower())

    def test_should_check_node_print_call(self):
        """Test should_check_node identifies print calls."""
        # Test print() call
        code = "print('hello')"
        tree = ast.parse(code)
        print_node = tree.body[0].value

        self.assertTrue(self.rule.should_check_node(print_node, self.context))

    def test_should_check_node_non_print_call(self):
        """Test should_check_node ignores non-print calls."""
        # Test other function call
        code = "logger.info('hello')"
        tree = ast.parse(code)
        call_node = tree.body[0].value

        self.assertFalse(self.rule.should_check_node(call_node, self.context))

    def test_should_check_node_non_call(self):
        """Test should_check_node ignores non-call nodes."""
        code = "x = 5"
        tree = ast.parse(code)
        assign_node = tree.body[0]

        self.assertFalse(self.rule.should_check_node(assign_node, self.context))

    def test_check_node_simple_print(self):
        """Test check_node creates violation for simple print."""
        code = "print('hello world')"
        tree = ast.parse(code)
        print_node = tree.body[0].value

        violations = self.rule.check_node(print_node, self.context)

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation.rule_id, 'logging.no-print')
        self.assertIn('Print statement found', violation.message)
        self.assertIn('logger.info', violation.suggestion)

    def test_check_node_error_print_suggestion(self):
        """Test check_node suggests error level for error messages."""
        code = "print('Error occurred')"
        tree = ast.parse(code)
        print_node = tree.body[0].value

        violations = self.rule.check_node(print_node, self.context)

        self.assertEqual(len(violations), 1)
        self.assertIn('logger.error', violations[0].suggestion)

    def test_check_node_warning_print_suggestion(self):
        """Test check_node suggests warning level for warning messages."""
        code = "print('Warning: deprecated function')"
        tree = ast.parse(code)
        print_node = tree.body[0].value

        violations = self.rule.check_node(print_node, self.context)

        self.assertEqual(len(violations), 1)
        self.assertIn('logger.warning', violations[0].suggestion)

    def test_check_node_debug_print_suggestion(self):
        """Test check_node suggests debug level for debug messages."""
        code = "print('Debug: variable dump')"
        tree = ast.parse(code)
        print_node = tree.body[0].value

        violations = self.rule.check_node(print_node, self.context)

        self.assertEqual(len(violations), 1)
        self.assertIn('logger.debug', violations[0].suggestion)

    def test_check_node_success_print_suggestion(self):
        """Test check_node suggests success level for success messages."""
        code = "print('Operation completed successfully')"
        tree = ast.parse(code)
        print_node = tree.body[0].value

        violations = self.rule.check_node(print_node, self.context)

        self.assertEqual(len(violations), 1)
        self.assertIn('logger.success', violations[0].suggestion)

    def test_check_node_empty_print(self):
        """Test check_node handles print with no arguments."""
        code = "print()"
        tree = ast.parse(code)
        print_node = tree.body[0].value

        violations = self.rule.check_node(print_node, self.context)

        self.assertEqual(len(violations), 1)
        self.assertIn('logger.info', violations[0].suggestion)

    def test_check_node_non_string_print(self):
        """Test check_node handles print with non-string arguments."""
        code = "print(42)"
        tree = ast.parse(code)
        print_node = tree.body[0].value

        violations = self.rule.check_node(print_node, self.context)

        self.assertEqual(len(violations), 1)
        self.assertIn('logger.info', violations[0].suggestion)

    def test_check_node_wrong_type_raises_error(self):
        """Test check_node raises TypeError for non-Call nodes."""
        code = "x = 5"
        tree = ast.parse(code)
        assign_node = tree.body[0]

        with self.assertRaises(TypeError):
            self.rule.check_node(assign_node, self.context)

    def test_get_logging_suggestion_various_keywords(self):
        """Test _get_logging_suggestion with various keyword patterns."""
        # Test fail keyword
        code = "print('Operation failed')"
        tree = ast.parse(code)
        print_node = tree.body[0].value
        suggestion = self.rule._get_logging_suggestion(print_node)
        self.assertIn('logger.error', suggestion)

        # Test exception keyword
        code = "print('Exception caught')"
        tree = ast.parse(code)
        print_node = tree.body[0].value
        suggestion = self.rule._get_logging_suggestion(print_node)
        self.assertIn('logger.error', suggestion)

        # Test warn keyword
        code = "print('Warn user about issue')"
        tree = ast.parse(code)
        print_node = tree.body[0].value
        suggestion = self.rule._get_logging_suggestion(print_node)
        self.assertIn('logger.warning', suggestion)

        # Test trace keyword
        code = "print('Trace information')"
        tree = ast.parse(code)
        print_node = tree.body[0].value
        suggestion = self.rule._get_logging_suggestion(print_node)
        self.assertIn('logger.debug', suggestion)

        # Test done keyword
        code = "print('Task is done')"
        tree = ast.parse(code)
        print_node = tree.body[0].value
        suggestion = self.rule._get_logging_suggestion(print_node)
        self.assertIn('logger.success', suggestion)

    def test_is_allowed_context_test_file(self):
        """Test _is_allowed_context allows test files."""
        test_context = LintContext(file_path=Path('/test_module.py'))
        config: Dict[str, Any] = {}

        result = self.rule._is_allowed_context(test_context, config)
        self.assertTrue(result)

    def test_is_allowed_context_main_function(self):
        """Test _is_allowed_context allows main function."""
        main_context = LintContext(
            file_path=Path('/script.py'),
            current_function='__main__'
        )
        config: Dict[str, Any] = {}

        result = self.rule._is_allowed_context(main_context, config)
        self.assertTrue(result)

    def test_allowed_context_skips_violation(self):
        """Test that allowed contexts skip violation creation."""
        # Set up a test file context
        test_context = LintContext(file_path=Path('/test_file.py'))

        code = "print('hello')"
        tree = ast.parse(code)
        print_node = tree.body[0].value

        violations = self.rule.check_node(print_node, test_context)
        self.assertEqual(len(violations), 0)


class TestProperLogLevelsRule(unittest.TestCase):
    """Test ProperLogLevelsRule functionality."""

    def setUp(self):
        self.rule = ProperLogLevelsRule()
        self.context = LintContext(file_path=Path('/production.py'))

    def test_rule_properties(self):
        """Test rule properties are correctly defined."""
        self.assertEqual(self.rule.rule_id, 'logging.proper-levels')
        self.assertEqual(self.rule.rule_name, 'Proper Log Levels')
        self.assertEqual(self.rule.severity, Severity.INFO)
        self.assertEqual(self.rule.categories, {'logging', 'best-practices', 'levels'})
        self.assertIn('log levels', self.rule.description.lower())

    def test_should_check_node_logger_call(self):
        """Test should_check_node identifies logger calls."""
        code = "logger.info('message')"
        tree = ast.parse(code)
        call_node = tree.body[0].value

        self.assertTrue(self.rule.should_check_node(call_node, self.context))

    def test_should_check_node_non_logger_call(self):
        """Test should_check_node ignores non-logger calls."""
        code = "print('message')"
        tree = ast.parse(code)
        call_node = tree.body[0].value

        self.assertFalse(self.rule.should_check_node(call_node, self.context))

    def test_should_check_node_non_call(self):
        """Test should_check_node ignores non-call nodes."""
        code = "x = 5"
        tree = ast.parse(code)
        assign_node = tree.body[0]

        self.assertFalse(self.rule.should_check_node(assign_node, self.context))

    def test_is_logging_call_logger_name(self):
        """Test _is_logging_call identifies various logger names."""
        test_cases = [
            "logger.info('test')",
            "log.error('test')",
            "logging.debug('test')"
        ]

        for code in test_cases:
            tree = ast.parse(code)
            call_node = tree.body[0].value
            self.assertTrue(self.rule._is_logging_call(call_node), f"Failed for: {code}")

    def test_is_logging_call_getlogger_pattern(self):
        """Test _is_logging_call identifies getLogger pattern."""
        code = "logging.getLogger().info('test')"
        tree = ast.parse(code)
        call_node = tree.body[0].value

        self.assertTrue(self.rule._is_logging_call(call_node))

    def test_is_logging_call_invalid_method(self):
        """Test _is_logging_call rejects invalid methods."""
        code = "logger.invalid_method('test')"
        tree = ast.parse(code)
        call_node = tree.body[0].value

        self.assertFalse(self.rule._is_logging_call(call_node))

    def test_is_logging_call_non_attribute(self):
        """Test _is_logging_call rejects non-attribute calls."""
        code = "some_function('test')"
        tree = ast.parse(code)
        call_node = tree.body[0].value

        self.assertFalse(self.rule._is_logging_call(call_node))

    def test_check_node_error_in_loop(self):
        """Test check_node detects error logging in loops."""
        code = """
for i in range(10):
    logger.error('Error in loop')
"""
        tree = ast.parse(code)
        for_node = tree.body[0]
        call_node = for_node.body[0].value

        # Set up context with loop in stack
        loop_context = LintContext(
            file_path=Path('/production.py'),
            node_stack=[for_node]
        )

        violations = self.rule.check_node(call_node, loop_context)

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertIn('Error logging inside loop', violation.message)
        self.assertIn('rate limiting', violation.suggestion)

    def test_check_node_debug_for_important_info(self):
        """Test check_node detects debug level for important information."""
        code = "logger.debug('Service started successfully')"
        tree = ast.parse(code)
        call_node = tree.body[0].value

        violations = self.rule.check_node(call_node, self.context)

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertIn('Debug level used for potentially important', violation.message)
        self.assertIn('logger.info', violation.suggestion)

    def test_check_node_normal_debug_no_violation(self):
        """Test check_node doesn't flag normal debug messages."""
        code = "logger.debug('Internal variable state')"
        tree = ast.parse(code)
        call_node = tree.body[0].value

        violations = self.rule.check_node(call_node, self.context)

        self.assertEqual(len(violations), 0)

    def test_check_node_non_call_raises_error(self):
        """Test check_node raises TypeError for non-Call nodes."""
        code = "x = 5"
        tree = ast.parse(code)
        assign_node = tree.body[0]

        with self.assertRaises(TypeError):
            self.rule.check_node(assign_node, self.context)

    def test_check_node_non_logging_call(self):
        """Test check_node returns empty for non-logging calls."""
        code = "print('test')"
        tree = ast.parse(code)
        call_node = tree.body[0].value

        violations = self.rule.check_node(call_node, self.context)

        self.assertEqual(len(violations), 0)

    def test_is_in_loop_for_loop(self):
        """Test _is_in_loop detects for loops."""
        code = """
for i in range(10):
    pass
"""
        tree = ast.parse(code)
        for_node = tree.body[0]

        loop_context = LintContext(
            file_path=Path('/test.py'),
            node_stack=[for_node]
        )

        self.assertTrue(self.rule._is_in_loop(loop_context))

    def test_is_in_loop_while_loop(self):
        """Test _is_in_loop detects while loops."""
        code = """
while True:
    pass
"""
        tree = ast.parse(code)
        while_node = tree.body[0]

        loop_context = LintContext(
            file_path=Path('/production.py'),
            node_stack=[while_node]
        )

        self.assertTrue(self.rule._is_in_loop(loop_context))

    def test_is_in_loop_no_loop(self):
        """Test _is_in_loop returns False when not in loop."""
        context = LintContext(file_path=Path('/production.py'))
        self.assertFalse(self.rule._is_in_loop(context))

    def test_is_in_loop_function_boundary(self):
        """Test _is_in_loop stops at function boundaries."""
        code = """
def func():
    for i in range(10):
        pass
"""
        tree = ast.parse(code)
        func_node = tree.body[0]
        for_node = func_node.body[0]

        # Context inside function but outside loop scope
        context = LintContext(
            file_path=Path('/production.py'),
            node_stack=[func_node]  # Only function in stack
        )

        self.assertFalse(self.rule._is_in_loop(context))

    def test_appears_production_critical_keywords(self):
        """Test _appears_production_critical detects important keywords."""
        important_keywords = [
            'started', 'starting', 'initialized', 'connected', 'loaded',
            'finished', 'completed', 'processed', 'received', 'sent'
        ]

        for keyword in important_keywords:
            code = f"logger.debug('Service {keyword}')"
            tree = ast.parse(code)
            call_node = tree.body[0].value

            result = self.rule._appears_production_critical(call_node, self.context)
            self.assertTrue(result, f"Failed for keyword: {keyword}")

    def test_appears_production_critical_normal_debug(self):
        """Test _appears_production_critical doesn't flag normal debug."""
        code = "logger.debug('Variable x = 42')"
        tree = ast.parse(code)
        call_node = tree.body[0].value

        result = self.rule._appears_production_critical(call_node, self.context)
        self.assertFalse(result)

    def test_appears_production_critical_no_args(self):
        """Test _appears_production_critical handles no arguments."""
        code = "logger.debug()"
        tree = ast.parse(code)
        call_node = tree.body[0].value

        result = self.rule._appears_production_critical(call_node, self.context)
        self.assertFalse(result)

    def test_appears_production_critical_non_string(self):
        """Test _appears_production_critical handles non-string arguments."""
        code = "logger.debug(42)"
        tree = ast.parse(code)
        call_node = tree.body[0].value

        result = self.rule._appears_production_critical(call_node, self.context)
        self.assertFalse(result)


class TestLoggingInExceptionsRule(unittest.TestCase):
    """Test LoggingInExceptionsRule functionality."""

    def setUp(self):
        self.rule = LoggingInExceptionsRule()
        self.context = LintContext(file_path=Path('/production.py'))

    def test_rule_properties(self):
        """Test rule properties are correctly defined."""
        self.assertEqual(self.rule.rule_id, 'logging.exception-logging')
        self.assertEqual(self.rule.rule_name, 'Exception Logging')
        self.assertEqual(self.rule.severity, Severity.WARNING)
        self.assertEqual(self.rule.categories, {'logging', 'exceptions', 'debugging'})
        self.assertIn('exception handlers', self.rule.description.lower())

    def test_should_check_node_except_handler(self):
        """Test should_check_node identifies exception handlers."""
        code = """
try:
    pass
except Exception:
    pass
"""
        tree = ast.parse(code)
        try_node = tree.body[0]
        except_node = try_node.handlers[0]

        self.assertTrue(self.rule.should_check_node(except_node, self.context))

    def test_should_check_node_non_except_handler(self):
        """Test should_check_node ignores non-exception handlers."""
        code = "x = 5"
        tree = ast.parse(code)
        assign_node = tree.body[0]

        self.assertFalse(self.rule.should_check_node(assign_node, self.context))

    def test_check_node_no_logging_no_reraise(self):
        """Test check_node flags exception handler with no logging or re-raise."""
        code = """
try:
    risky_operation()
except Exception:
    x = 1  # No logging or re-raise
"""
        tree = ast.parse(code)
        except_node = tree.body[0].handlers[0]

        violations = self.rule.check_node(except_node, self.context)

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertIn('Exception handler without logging', violation.message)
        self.assertIn('logger.exception', violation.suggestion)

    def test_check_node_with_logging_no_violation(self):
        """Test check_node doesn't flag exception handler with proper logging."""
        code = """
try:
    risky_operation()
except Exception:
    logger.error('Operation failed')
"""
        tree = ast.parse(code)
        except_node = tree.body[0].handlers[0]

        violations = self.rule.check_node(except_node, self.context)

        self.assertEqual(len(violations), 0)

    def test_check_node_with_reraise_no_violation(self):
        """Test check_node doesn't flag exception handler with re-raise."""
        code = """
try:
    risky_operation()
except Exception:
    cleanup()
    raise
"""
        tree = ast.parse(code)
        except_node = tree.body[0].handlers[0]

        violations = self.rule.check_node(except_node, self.context)

        self.assertEqual(len(violations), 0)

    def test_check_node_wrong_log_level(self):
        """Test check_node flags inappropriate log levels in exception handlers."""
        code = """
try:
    risky_operation()
except Exception:
    logger.info('Something went wrong')
"""
        tree = ast.parse(code)
        except_node = tree.body[0].handlers[0]

        violations = self.rule.check_node(except_node, self.context)

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertIn('Using info level for exception', violation.message)
        self.assertEqual(violation.severity, Severity.INFO)

    def test_check_node_proper_exception_logging(self):
        """Test check_node accepts proper exception logging methods."""
        proper_methods = ['error', 'exception', 'critical']

        for method in proper_methods:
            code = f"""
try:
    risky_operation()
except Exception:
    logger.{method}('Operation failed')
"""
            tree = ast.parse(code)
            except_node = tree.body[0].handlers[0]

            violations = self.rule.check_node(except_node, self.context)
            self.assertEqual(len(violations), 0, f"Failed for method: {method}")

    def test_check_node_wrong_type_raises_error(self):
        """Test check_node raises TypeError for non-ExceptHandler nodes."""
        code = "x = 5"
        tree = ast.parse(code)
        assign_node = tree.body[0]

        with self.assertRaises(TypeError):
            self.rule.check_node(assign_node, self.context)

    def test_has_logging_in_handler_true(self):
        """Test _has_logging_in_handler detects logging calls."""
        code = """
try:
    pass
except Exception:
    logger.error('Error occurred')
"""
        tree = ast.parse(code)
        except_node = tree.body[0].handlers[0]

        result = self.rule._has_logging_in_handler(except_node)
        self.assertTrue(result)

    def test_has_logging_in_handler_false(self):
        """Test _has_logging_in_handler returns False when no logging."""
        code = """
try:
    pass
except Exception:
    x = 1
"""
        tree = ast.parse(code)
        except_node = tree.body[0].handlers[0]

        result = self.rule._has_logging_in_handler(except_node)
        self.assertFalse(result)

    def test_has_reraise_true(self):
        """Test _has_reraise detects bare raise statements."""
        code = """
try:
    pass
except Exception:
    cleanup()
    raise
"""
        tree = ast.parse(code)
        except_node = tree.body[0].handlers[0]

        result = self.rule._has_reraise(except_node)
        self.assertTrue(result)

    def test_has_reraise_false_no_raise(self):
        """Test _has_reraise returns False when no raise."""
        code = """
try:
    pass
except Exception:
    x = 1
"""
        tree = ast.parse(code)
        except_node = tree.body[0].handlers[0]

        result = self.rule._has_reraise(except_node)
        self.assertFalse(result)

    def test_has_reraise_false_raise_with_exception(self):
        """Test _has_reraise returns False for raise with specific exception."""
        code = """
try:
    pass
except Exception:
    raise ValueError('New error')
"""
        tree = ast.parse(code)
        except_node = tree.body[0].handlers[0]

        result = self.rule._has_reraise(except_node)
        self.assertFalse(result)

    def test_get_logging_calls_in_handler(self):
        """Test _get_logging_calls_in_handler finds all logging calls."""
        code = """
try:
    pass
except Exception:
    logger.error('First error')
    cleanup()
    logger.warning('Second warning')
"""
        tree = ast.parse(code)
        except_node = tree.body[0].handlers[0]

        calls = self.rule._get_logging_calls_in_handler(except_node)
        self.assertEqual(len(calls), 2)

    def test_get_logging_calls_in_handler_empty(self):
        """Test _get_logging_calls_in_handler returns empty when no logging."""
        code = """
try:
    pass
except Exception:
    x = 1
    y = 2
"""
        tree = ast.parse(code)
        except_node = tree.body[0].handlers[0]

        calls = self.rule._get_logging_calls_in_handler(except_node)
        self.assertEqual(len(calls), 0)

    def test_is_logging_call_various_loggers(self):
        """Test _is_logging_call with various logger names."""
        test_cases = [
            "logger.error('test')",
            "log.exception('test')",
            "logging.critical('test')"
        ]

        for code in test_cases:
            tree = ast.parse(code)
            call_node = tree.body[0].value
            self.assertTrue(self.rule._is_logging_call(call_node), f"Failed for: {code}")

    def test_is_logging_call_includes_exception_method(self):
        """Test _is_logging_call includes exception method."""
        code = "logger.exception('Error with traceback')"
        tree = ast.parse(code)
        call_node = tree.body[0].value

        self.assertTrue(self.rule._is_logging_call(call_node))

    def test_is_logging_call_invalid_method(self):
        """Test _is_logging_call rejects invalid methods."""
        code = "logger.invalid('test')"
        tree = ast.parse(code)
        call_node = tree.body[0].value

        self.assertFalse(self.rule._is_logging_call(call_node))

    def test_is_logging_call_non_attribute(self):
        """Test _is_logging_call rejects non-attribute calls."""
        code = "some_function('test')"
        tree = ast.parse(code)
        call_node = tree.body[0].value

        self.assertFalse(self.rule._is_logging_call(call_node))

    def test_nested_exception_handler(self):
        """Test complex nested exception handling."""
        code = """
try:
    try:
        risky_operation()
    except ValueError:
        logger.warning('Value error in nested try')
        raise
except Exception:
    pass  # No logging here
"""
        tree = ast.parse(code)
        outer_except = tree.body[0].handlers[0]

        violations = self.rule.check_node(outer_except, self.context)

        # Should flag the outer exception handler for missing logging
        self.assertEqual(len(violations), 1)
        self.assertIn('Exception handler without logging', violations[0].message)


if __name__ == '__main__':
    unittest.main()
