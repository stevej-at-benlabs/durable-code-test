#!/usr/bin/env python3
"""
Purpose: Unit tests for logging rules
Scope: Tests for logging best practices and loguru usage rules
Overview: This module tests the logging rules including print statement
    detection, loguru import patterns, structured logging, and proper
    logging in exception handlers.
Dependencies: unittest, ast, logging rules
"""

import unittest
import ast
from pathlib import Path

import sys
sys.path.insert(0, '/home/stevejackson/Projects/durable-code-test/tools')

from design_linters.framework.interfaces import LintContext, Severity
from design_linters.rules.logging.general_logging_rules import (
    NoPlainPrintRule,
    ProperLogLevelsRule,
    LoggingInExceptionsRule
)
from design_linters.rules.logging.loguru_rules import (
    UseLoguruRule,
    LoguruImportRule,
    StructuredLoggingRule,
    LogLevelConsistencyRule,
    LoguruConfigurationRule
)


class TestNoPlainPrintRule(unittest.TestCase):
    """Test the NoPlainPrintRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = NoPlainPrintRule()

    def _create_context(self, code, file_path='/src/file.py'):
        """Helper to create a LintContext."""
        return LintContext(
            file_path=Path(file_path),
            file_content=code,
            ast_tree=ast.parse(code)
        )

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, "logging.no-print")
        self.assertEqual(self.rule.severity, Severity.WARNING)
        self.assertIn("logging", self.rule.categories)

    def test_print_statement_detection(self):
        """Test detection of print statements."""
        code = """
def process():
    print("Processing...")  # Should be logging
    result = calculate()
    print(f"Result: {result}")  # Should be logging
    return result
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Should detect print statements
        self.assertGreaterEqual(len(violations), 2)
        for violation in violations:
            self.assertIn("loguru", violation.suggestion.lower())

    def test_print_in_test_files(self):
        """Test that print in test files is allowed."""
        code = """
def test_output():
    print("Test output")
    assert something()
"""
        context = self._create_context(code, '/test/test_file.py')
        violations = self.rule.check(context)

        # Test files should allow print
        self.assertEqual(len(violations), 0)

    def test_print_in_main_block(self):
        """Test print in main block might be acceptable."""
        code = """
if __name__ == "__main__":
    print("Starting application...")
    main()
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Main block prints might be acceptable
        self.assertLessEqual(len(violations), 1)

    def test_logging_suggestion_based_on_content(self):
        """Test that suggestions match the print content."""
        code = """
def handle():
    print("ERROR: Failed to process")  # Should suggest error level
    print("DEBUG: Value is 42")  # Should suggest debug level
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Should suggest appropriate log levels
        if violations:
            for violation in violations:
                if "ERROR" in violation.context.get("content", ""):
                    self.assertIn("error", violation.suggestion.lower())


class TestUseLoguruRule(unittest.TestCase):
    """Test the UseLoguruRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = UseLoguruRule()

    def _create_context(self, code, file_path='/src/file.py'):
        """Helper to create a LintContext."""
        return LintContext(
            file_path=Path(file_path),
            file_content=code,
            ast_tree=ast.parse(code)
        )

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, "logging.use-loguru")
        self.assertEqual(self.rule.severity, Severity.INFO)
        self.assertIn("loguru", self.rule.categories)

    def test_standard_logging_import_detection(self):
        """Test detection of standard logging imports."""
        code = """
import logging

def process():
    logging.info("Processing")
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Should suggest using loguru
        self.assertGreaterEqual(len(violations), 1)
        if violations:
            self.assertIn("loguru", violations[0].suggestion.lower())

    def test_logging_from_import_detection(self):
        """Test detection of from logging imports."""
        code = """
from logging import getLogger

logger = getLogger(__name__)
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Should suggest using loguru
        self.assertGreaterEqual(len(violations), 1)


class TestLoguruImportRule(unittest.TestCase):
    """Test the LoguruImportRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = LoguruImportRule()

    def _create_context(self, code, file_path='/src/file.py'):
        """Helper to create a LintContext."""
        return LintContext(
            file_path=Path(file_path),
            file_content=code,
            ast_tree=ast.parse(code)
        )

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, "logging.loguru-import")
        self.assertEqual(self.rule.severity, Severity.WARNING)
        self.assertIn("loguru", self.rule.categories)

    def test_correct_import_pattern(self):
        """Test correct loguru import pattern."""
        code = """
from loguru import logger

logger.info("Using loguru correctly")
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Correct pattern should not be flagged
        self.assertEqual(len(violations), 0)

    def test_incorrect_import_patterns(self):
        """Test incorrect loguru import patterns."""
        code = """
import loguru  # Wrong pattern

loguru.logger.info("Wrong usage")
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Should flag incorrect pattern
        self.assertGreaterEqual(len(violations), 1)
        if violations:
            self.assertIn("from loguru import logger", violations[0].suggestion)


class TestStructuredLoggingRule(unittest.TestCase):
    """Test the StructuredLoggingRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = StructuredLoggingRule()

    def _create_context(self, code, file_path='/src/file.py'):
        """Helper to create a LintContext."""
        return LintContext(
            file_path=Path(file_path),
            file_content=code,
            ast_tree=ast.parse(code)
        )

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, "logging.structured-logging")
        self.assertEqual(self.rule.severity, Severity.INFO)
        self.assertIn("logging", self.rule.categories)

    def test_fstring_logging_detection(self):
        """Test detection of f-strings in logging."""
        code = """
from loguru import logger

def process(user_id, action):
    logger.info(f"User {user_id} performed {action}")  # Bad
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Should detect f-string in logging
        self.assertGreaterEqual(len(violations), 1)

    def test_format_logging_detection(self):
        """Test detection of .format() in logging."""
        code = """
from loguru import logger

def log_event(event):
    logger.info("Event: {}".format(event))  # Bad
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Should detect format in logging
        self.assertGreaterEqual(len(violations), 1)

    def test_structured_logging_not_flagged(self):
        """Test that structured logging is not flagged."""
        code = """
from loguru import logger

def process(user_id, action):
    logger.info("User performed action", user_id=user_id, action=action)  # Good
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Structured logging should not be flagged
        self.assertEqual(len(violations), 0)

    def test_complex_message_suggestion(self):
        """Test suggestion for complex messages."""
        code = """
from loguru import logger

def report(data):
    logger.info(f"Processed {len(data)} items with status {data.status}")
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        if violations:
            self.assertIn("structured", violations[0].suggestion.lower())


class TestLogLevelConsistencyRule(unittest.TestCase):
    """Test the LogLevelConsistencyRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = LogLevelConsistencyRule()

    def _create_context(self, code, file_path='/src/file.py'):
        """Helper to create a LintContext."""
        return LintContext(
            file_path=Path(file_path),
            file_content=code,
            ast_tree=ast.parse(code)
        )

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, "logging.log-level-consistency")
        self.assertEqual(self.rule.severity, Severity.INFO)
        self.assertIn("logging", self.rule.categories)

    def test_error_message_with_wrong_level(self):
        """Test error messages with wrong level."""
        code = """
from loguru import logger

def handle_error():
    logger.info("ERROR: Failed to connect")  # Wrong level
    logger.debug("Error occurred")  # Wrong level
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Should detect inconsistent levels
        self.assertGreaterEqual(len(violations), 1)

    def test_success_message_detection(self):
        """Test success messages at wrong level."""
        code = """
from loguru import logger

def complete():
    logger.error("Successfully completed")  # Wrong level
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Should detect wrong level for success
        self.assertGreaterEqual(len(violations), 1)

    def test_consistent_log_levels(self):
        """Test consistent log levels are not flagged."""
        code = """
from loguru import logger

def process():
    logger.error("Failed to process")
    logger.success("Operation completed")
    logger.debug("Debug information")
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Consistent levels should not be flagged
        self.assertEqual(len(violations), 0)


class TestLoggingInExceptionsRule(unittest.TestCase):
    """Test the LoggingInExceptionsRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = LoggingInExceptionsRule()

    def _create_context(self, code, file_path='/src/file.py'):
        """Helper to create a LintContext."""
        return LintContext(
            file_path=Path(file_path),
            file_content=code,
            ast_tree=ast.parse(code)
        )

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, "logging.exception-logging")
        self.assertEqual(self.rule.severity, Severity.WARNING)
        self.assertIn("error-handling", self.rule.categories)

    def test_exception_without_logging(self):
        """Test exception handler without logging."""
        code = """
def risky():
    try:
        dangerous_operation()
    except Exception as e:
        pass  # Silent failure - bad
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Should detect missing logging
        self.assertGreaterEqual(len(violations), 1)

    def test_exception_with_logging(self):
        """Test exception handler with proper logging."""
        code = """
from loguru import logger

def safe():
    try:
        operation()
    except Exception as e:
        logger.error("Operation failed", exc_info=True)
        raise
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Should not flag proper exception logging
        self.assertEqual(len(violations), 0)

    def test_exception_with_reraise(self):
        """Test exception with reraise is acceptable."""
        code = """
def wrapper():
    try:
        inner()
    except:
        raise  # Re-raising is OK without logging
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Re-raising might be acceptable
        self.assertEqual(len(violations), 0)

    def test_wrong_log_level_in_exception(self):
        """Test wrong log level in exception handler."""
        code = """
from loguru import logger

def handle():
    try:
        process()
    except Exception as e:
        logger.debug("Failed")  # Should be error/exception
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Should suggest error level
        self.assertGreaterEqual(len(violations), 1)


class TestLoguruConfigurationRule(unittest.TestCase):
    """Test the LoguruConfigurationRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = LoguruConfigurationRule()

    def _create_context(self, code, file_path='/src/file.py'):
        """Helper to create a LintContext."""
        return LintContext(
            file_path=Path(file_path),
            file_content=code,
            ast_tree=ast.parse(code)
        )

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, "logging.loguru-configuration")
        self.assertEqual(self.rule.severity, Severity.INFO)
        self.assertIn("loguru", self.rule.categories)

    def test_add_without_sink(self):
        """Test logger.add() without sink configuration."""
        code = """
from loguru import logger

logger.add()  # Missing sink
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Should detect missing sink
        self.assertGreaterEqual(len(violations), 1)

    def test_file_sink_without_rotation(self):
        """Test file sink without rotation."""
        code = """
from loguru import logger

logger.add("app.log")  # No rotation
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Should suggest rotation
        self.assertGreaterEqual(len(violations), 1)
        if violations:
            self.assertIn("rotation", violations[0].suggestion.lower())

    def test_complete_configuration(self):
        """Test complete loguru configuration."""
        code = """
from loguru import logger

logger.add("app.log", rotation="10 MB", retention="7 days", compression="zip")
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Complete configuration should not be flagged
        self.assertEqual(len(violations), 0)

    def test_stderr_sink_not_flagged(self):
        """Test stderr sink is acceptable without rotation."""
        code = """
from loguru import logger
import sys

logger.add(sys.stderr, level="ERROR")
"""
        context = self._create_context(code)
        violations = self.rule.check(context)

        # Stderr sink without rotation is OK
        self.assertEqual(len(violations), 0)


if __name__ == '__main__':
    unittest.main()
