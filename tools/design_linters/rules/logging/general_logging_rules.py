#!/usr/bin/env python3
"""
Purpose: General logging best practices rules
Scope: Enforces general logging patterns beyond loguru-specific rules
Overview: This module provides general logging rules that apply regardless
    of the logging library used. It focuses on proper logging practices,
    error handling, and avoiding anti-patterns like using print statements
    for logging in production code.
Dependencies: Framework interfaces, AST analysis utilities
Exports: General logging linting rules
Interfaces: All rules implement ASTLintRule interface
Implementation: Rule-based architecture with logging pattern detection
"""

import ast
from typing import List, Set, Dict, Any

from ...framework.interfaces import ASTLintRule, LintViolation, LintContext, Severity


class NoPlainPrintRule(ASTLintRule):
    """Rule to discourage print statements in favor of proper logging."""

    @property
    def rule_id(self) -> str:
        return "logging.no-print"

    @property
    def rule_name(self) -> str:
        return "No Print Statements"

    @property
    def description(self) -> str:
        return "Use proper logging instead of print statements for production code"

    @property
    def severity(self) -> Severity:
        return Severity.WARNING

    @property
    def categories(self) -> Set[str]:
        return {"logging", "production", "anti-patterns"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        # Check for print() function calls
        return (isinstance(node, ast.Call) and
                isinstance(node.func, ast.Name) and
                node.func.id == 'print')

    def check_node(self, node: ast.Call, context: LintContext) -> List[LintViolation]:
        config = self.get_configuration(context.metadata or {})

        # Check if print statements are allowed in certain contexts
        if self._is_allowed_context(context, config):
            return []

        # Determine appropriate logging suggestion based on content
        suggestion = self._get_logging_suggestion(node)

        return [LintViolation(
            rule_id=self.rule_id,
            file_path=str(context.file_path),
            line=node.lineno,
            column=node.col_offset,
            severity=self.severity,
            message="Print statement found - use logging instead",
            description="Print statements should be replaced with proper logging for better control and observability",
            suggestion=suggestion,
            context={
                'function': context.current_function,
                'class': context.current_class,
                'replacement': suggestion
            }
        )]

    def _is_allowed_context(self, context: LintContext, config: Dict[str, Any]) -> bool:
        """Check if print statements are allowed in this context."""
        allowed_patterns = config.get('allowed_patterns', [
            'test_', '__main__', 'debug_', 'example_', 'demo_', 'script_'
        ])

        # Allow in test files
        file_name = str(context.file_path).lower()
        if any(pattern in file_name for pattern in ['test', 'example', 'demo', 'script']):
            return True

        # Allow in main blocks
        if context.current_function == '__main__':
            return True

        # Allow in functions with allowed patterns
        function_name = context.current_function or ''
        if any(pattern in function_name.lower() for pattern in allowed_patterns):
            return True

        # Allow in CLI scripts (if they have argparse usage)
        if 'argparse' in str(context.file_content or ''):
            return True

        return False

    def _get_logging_suggestion(self, node: ast.Call) -> str:
        """Generate appropriate logging suggestion based on print content."""
        if not node.args:
            return "logger.info('...')  # Use appropriate log level"

        first_arg = node.args[0]

        # Analyze the content to suggest appropriate log level
        if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
            message = first_arg.value.lower()

            if any(keyword in message for keyword in ['error', 'fail', 'exception', 'crash']):
                return "logger.error('...')  # For error messages"
            elif any(keyword in message for keyword in ['warn', 'warning', 'deprecated']):
                return "logger.warning('...')  # For warnings"
            elif any(keyword in message for keyword in ['debug', 'trace', 'dump']):
                return "logger.debug('...')  # For debug information"
            elif any(keyword in message for keyword in ['success', 'complete', 'done']):
                return "logger.success('...')  # For success messages (loguru)"
            else:
                return "logger.info('...')  # For informational messages"

        return "logger.info('...')  # Use appropriate log level"


class ProperLogLevelsRule(ASTLintRule):
    """Rule to ensure proper usage of log levels."""

    @property
    def rule_id(self) -> str:
        return "logging.proper-levels"

    @property
    def rule_name(self) -> str:
        return "Proper Log Levels"

    @property
    def description(self) -> str:
        return "Use appropriate log levels based on message importance and context"

    @property
    def severity(self) -> Severity:
        return Severity.INFO

    @property
    def categories(self) -> Set[str]:
        return {"logging", "best-practices", "levels"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        # Check for any logger method calls (not just loguru)
        return (isinstance(node, ast.Call) and
                isinstance(node.func, ast.Attribute) and
                self._is_logging_call(node))

    def check_node(self, node: ast.Call, context: LintContext) -> List[LintViolation]:
        if not self._is_logging_call(node):
            return []

        violations = []
        method_name = node.func.attr.lower()

        # Check for overuse of certain log levels
        if method_name == 'error' and self._is_in_loop(context):
            violations.append(LintViolation(
                rule_id=self.rule_id,
                file_path=str(context.file_path),
                line=node.lineno,
                column=node.col_offset,
                severity=self.severity,
                message="Error logging inside loop may be too verbose",
                description="Consider using debug level or rate limiting for errors in loops",
                suggestion="Use logger.debug() or implement rate limiting for repeated errors",
                context={'level': method_name, 'issue': 'loop_error'}
            ))

        # Check for debug level in what appears to be production code
        if method_name == 'debug' and self._appears_production_critical(node, context):
            violations.append(LintViolation(
                rule_id=self.rule_id,
                file_path=str(context.file_path),
                line=node.lineno,
                column=node.col_offset,
                severity=self.severity,
                message="Debug level used for potentially important information",
                description="Consider using info level for important operational information",
                suggestion="Use logger.info() for operational information that should be visible",
                context={'level': method_name, 'issue': 'debug_for_important'}
            ))

        return violations

    def _is_logging_call(self, node: ast.Call) -> bool:
        """Check if this is a logging method call."""
        if not isinstance(node.func, ast.Attribute):
            return False

        method_name = node.func.attr.lower()
        logger_names = ['logger', 'log', 'logging']

        # Check for direct logger calls
        if isinstance(node.func.value, ast.Name):
            return (node.func.value.id in logger_names and
                   method_name in ['debug', 'info', 'warning', 'error', 'critical', 'success'])

        # Check for logger.getLogger().method() pattern
        if (isinstance(node.func.value, ast.Call) and
            isinstance(node.func.value.func, ast.Attribute) and
            node.func.value.func.attr == 'getLogger'):
            return method_name in ['debug', 'info', 'warning', 'error', 'critical']

        return False

    def _is_in_loop(self, context: LintContext) -> bool:
        """Check if the current context is inside a loop."""
        if not context.node_stack:
            return False

        for node in reversed(context.node_stack):
            if isinstance(node, (ast.For, ast.While)):
                return True
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                break  # Stop at function/class boundary

        return False

    def _appears_production_critical(self, node: ast.Call, context: LintContext) -> bool:
        """Check if this debug log appears to contain production-critical information."""
        if not node.args:
            return False

        first_arg = node.args[0]
        if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
            message = first_arg.value.lower()

            # Keywords that suggest this should be info level
            important_keywords = [
                'started', 'starting', 'initialized', 'connected', 'loaded',
                'finished', 'completed', 'processed', 'received', 'sent'
            ]

            return any(keyword in message for keyword in important_keywords)

        return False


class LoggingInExceptionsRule(ASTLintRule):
    """Rule to ensure proper logging in exception handlers."""

    @property
    def rule_id(self) -> str:
        return "logging.exception-logging"

    @property
    def rule_name(self) -> str:
        return "Exception Logging"

    @property
    def description(self) -> str:
        return "Ensure proper logging in exception handlers with traceback information"

    @property
    def severity(self) -> Severity:
        return Severity.WARNING

    @property
    def categories(self) -> Set[str]:
        return {"logging", "exceptions", "debugging"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        return isinstance(node, ast.ExceptHandler)

    def check_node(self, node: ast.ExceptHandler, context: LintContext) -> List[LintViolation]:
        violations = []

        # Check if exception handler has any logging
        has_logging = self._has_logging_in_handler(node)
        has_reraise = self._has_reraise(node)

        if not has_logging and not has_reraise:
            violations.append(LintViolation(
                rule_id=self.rule_id,
                file_path=str(context.file_path),
                line=node.lineno,
                column=node.col_offset,
                severity=self.severity,
                message="Exception handler without logging or re-raising",
                description="Exception handlers should log the error or re-raise for proper error tracking",
                suggestion="Add: logger.exception('Error occurred') or logger.error('Error', exc_info=True)",
                context={'issue': 'missing_logging'}
            ))

        elif has_logging:
            # Check if using appropriate logging methods for exceptions
            logging_calls = self._get_logging_calls_in_handler(node)
            for call in logging_calls:
                if self._is_logging_call(call):
                    method_name = call.func.attr.lower()
                    if method_name not in ['error', 'exception', 'critical']:
                        violations.append(LintViolation(
                            rule_id=self.rule_id,
                            file_path=str(context.file_path),
                            line=call.lineno,
                            column=call.col_offset,
                            severity=Severity.INFO,
                            message=f"Using {method_name} level for exception logging",
                            description="Consider using error or exception level for exception handlers",
                            suggestion="Use logger.error() or logger.exception() for exception logging",
                            context={'current_level': method_name, 'issue': 'wrong_level'}
                        ))

        return violations

    def _has_logging_in_handler(self, node: ast.ExceptHandler) -> bool:
        """Check if exception handler contains logging calls."""
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Call) and self._is_logging_call(stmt):
                return True
        return False

    def _has_reraise(self, node: ast.ExceptHandler) -> bool:
        """Check if exception handler re-raises the exception."""
        for stmt in node.body:
            if isinstance(stmt, ast.Raise) and stmt.exc is None:
                return True
        return False

    def _get_logging_calls_in_handler(self, node: ast.ExceptHandler) -> List[ast.Call]:
        """Get all logging calls in the exception handler."""
        calls = []
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Call) and self._is_logging_call(stmt):
                calls.append(stmt)
        return calls

    def _is_logging_call(self, node: ast.Call) -> bool:
        """Check if this is a logging method call."""
        if not isinstance(node.func, ast.Attribute):
            return False

        method_name = node.func.attr.lower()
        logger_names = ['logger', 'log', 'logging']

        if isinstance(node.func.value, ast.Name):
            return (node.func.value.id in logger_names and
                   method_name in ['debug', 'info', 'warning', 'error', 'critical', 'success', 'exception'])

        return False
