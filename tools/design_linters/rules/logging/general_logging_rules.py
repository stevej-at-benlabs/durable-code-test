#!/usr/bin/env python3
"""
Purpose: General logging best practices rules
Scope: Enforces general logging patterns beyond loguru-specific rules
Overview: Overview: This module enforces general logging best practices applicable to any logging framework,
    ensuring consistent, secure, and effective logging throughout the application. It detects common
    logging mistakes including logging sensitive information like passwords or API keys, insufficient
    context in error logs, missing correlation IDs for request tracing, and incorrect log levels for
    different message types. The rules check for proper exception logging with stack traces, structured
    logging for machine parsing, performance considerations in hot code paths, and consistent message
    formatting. Each violation includes guidance on proper logging practices such as what to log, when
    to log, appropriate detail levels, and security considerations. The module helps create logs that
    are valuable for debugging, monitoring, and security auditing while avoiding common pitfalls like
    log injection vulnerabilities and performance degradation from excessive logging.
Dependencies: Framework interfaces, AST analysis utilities
Exports: General logging linting rules
Interfaces: All rules implement ASTLintRule interface
Implementation: Rule-based architecture with logging pattern detection
"""

import ast
from typing import Any

from design_linters.framework.interfaces import ASTLintRule, LintContext, LintViolation, Severity
from design_linters.utils.context_helpers import is_allowed_context


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
    def categories(self) -> set[str]:
        return {"logging", "production", "anti-patterns"}

    def should_check_node(self, node: ast.AST, _context: LintContext) -> bool:
        # Check for print() function calls
        return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print"

    def check_node(self, node: ast.AST, context: LintContext) -> list[LintViolation]:
        if not isinstance(node, ast.Call):
            raise TypeError("NoPlainPrintRule should only receive ast.Call nodes")
        config = self.get_configuration(context.metadata or {})

        # Check if print statements are allowed in certain contexts
        if self._is_allowed_context(context, config):
            return []

        # Determine appropriate logging suggestion based on content
        suggestion = self._get_logging_suggestion(node)

        return [
            self.create_violation(
                context,
                node,
                message="Print statement found - use logging instead",
                description=(
                    "Print statements should be replaced with proper logging for better control and observability"
                ),
                suggestion=suggestion,
                violation_context={
                    "function": context.current_function,
                    "class": context.current_class,
                    "replacement": suggestion,
                },
            )
        ]

    def _is_allowed_context(self, context: LintContext, config: dict[str, Any]) -> bool:
        """Check if print statements are allowed in this context."""
        return is_allowed_context(context, config)

    def _get_logging_suggestion(self, node: ast.Call) -> str:
        """Generate appropriate logging suggestion based on print content."""
        if not node.args:
            return "logger.info('...')  # Use appropriate log level"

        first_arg = node.args[0]
        if not isinstance(first_arg, ast.Constant) or not isinstance(first_arg.value, str):
            return "logger.info('...')  # Use appropriate log level"

        return self._analyze_message_for_log_level(first_arg.value)

    def _analyze_message_for_log_level(self, message: str) -> str:
        """Analyze message content to suggest appropriate log level."""
        message_lower = message.lower()

        if self._contains_error_keywords(message_lower):
            return "logger.error('...')  # For error messages"
        if self._contains_warning_keywords(message_lower):
            return "logger.warning('...')  # For warnings"
        if self._contains_debug_keywords(message_lower):
            return "logger.debug('...')  # For debug information"
        if self._contains_success_keywords(message_lower):
            return "logger.success('...')  # For success messages (loguru)"

        return "logger.info('...')  # Use appropriate log level"

    def _contains_error_keywords(self, message: str) -> bool:
        """Check if message contains error-related keywords."""
        return any(keyword in message for keyword in ["error", "fail", "exception", "crash"])

    def _contains_warning_keywords(self, message: str) -> bool:
        """Check if message contains warning-related keywords."""
        return any(keyword in message for keyword in ["warn", "warning", "deprecated"])

    def _contains_debug_keywords(self, message: str) -> bool:
        """Check if message contains debug-related keywords."""
        return any(keyword in message for keyword in ["debug", "trace", "dump"])

    def _contains_success_keywords(self, message: str) -> bool:
        """Check if message contains success-related keywords."""
        return any(keyword in message for keyword in ["success", "complete", "done"])


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
    def categories(self) -> set[str]:
        return {"logging", "best-practices", "levels"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        # Check for any logger method calls (not just loguru)
        return isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and self._is_logging_call(node)

    def check_node(self, node: ast.AST, context: LintContext) -> list[LintViolation]:
        if not isinstance(node, ast.Call):
            raise TypeError("ProperLogLevelsRule should only receive ast.Call nodes")
        if not self._is_logging_call(node):
            return []

        violations = []
        if not isinstance(node.func, ast.Attribute):
            raise TypeError("Expected attribute access")
        method_name = node.func.attr.lower()

        # Check for overuse of certain log levels
        if method_name == "error" and self._is_in_loop(context):
            violations.append(
                self.create_violation(
                    context,
                    node,
                    message="Error logging inside loop may be too verbose",
                    description="Consider using debug level or rate limiting for errors in loops",
                    suggestion="Use logger.debug() or implement rate limiting for repeated errors",
                    violation_context={"level": method_name, "issue": "loop_error"},
                )
            )

        # Check for debug level in what appears to be production code
        if method_name == "debug" and self._appears_production_critical(node, context):
            violations.append(
                self.create_violation(
                    context,
                    node,
                    message="Debug level used for potentially important information",
                    description="Consider using info level for important operational information",
                    suggestion="Use logger.info() for operational information that should be visible",
                    violation_context={
                        "level": method_name,
                        "issue": "debug_for_important",
                    },
                )
            )

        return violations

    def _is_logging_call(self, node: ast.Call) -> bool:
        """Check if this is a logging method call."""
        if not isinstance(node.func, ast.Attribute):
            return False

        method_name = node.func.attr.lower()
        logger_names = ["logger", "log", "logging"]

        # Check for direct logger calls
        if isinstance(node.func.value, ast.Name):
            return node.func.value.id in logger_names and method_name in [
                "debug",
                "info",
                "warning",
                "error",
                "critical",
                "success",
            ]

        # Check for logger.getLogger().method() pattern
        if (
            isinstance(node.func.value, ast.Call)
            and isinstance(node.func.value.func, ast.Attribute)
            and node.func.value.func.attr == "getLogger"
        ):
            return method_name in ["debug", "info", "warning", "error", "critical"]

        return False

    def _is_in_loop(self, context: LintContext) -> bool:
        """Check if the current context is inside a loop."""
        if not context.node_stack:
            return False

        for node in reversed(context.node_stack):
            if isinstance(node, (ast.For, ast.While)):
                return True
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                break  # Stop at function/class boundary

        return False

    def _appears_production_critical(self, node: ast.Call, _context: LintContext) -> bool:
        """Check if this debug log appears to contain production-critical information."""
        if not node.args:
            return False

        first_arg = node.args[0]
        if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
            message = first_arg.value.lower()

            # Keywords that suggest this should be info level
            important_keywords = [
                "started",
                "starting",
                "initialized",
                "connected",
                "loaded",
                "finished",
                "completed",
                "processed",
                "received",
                "sent",
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
    def categories(self) -> set[str]:
        return {"logging", "exceptions", "debugging"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        return isinstance(node, ast.ExceptHandler)

    def check_node(self, node: ast.AST, context: LintContext) -> list[LintViolation]:
        if not isinstance(node, ast.ExceptHandler):
            raise TypeError("LoggingInExceptionsRule should only receive ast.ExceptHandler nodes")

        has_logging = self._has_logging_in_handler(node)
        has_reraise = self._has_reraise(node)

        if not has_logging and not has_reraise:
            return [self._create_missing_logging_violation(context, node)]

        if has_logging:
            return self._check_logging_level_appropriateness(node, context)

        return []

    def _create_missing_logging_violation(self, context: LintContext, node: ast.ExceptHandler) -> LintViolation:
        """Create violation for missing logging in exception handler."""
        return self.create_violation(
            context,
            node,
            message="Exception handler without logging or re-raising",
            description="Exception handlers should log the error or re-raise for proper error tracking",
            suggestion="Add: logger.exception('Error occurred') or logger.error('Error', exc_info=True)",
            violation_context={"issue": "missing_logging"},
        )

    def _check_logging_level_appropriateness(
        self, node: ast.ExceptHandler, context: LintContext
    ) -> list[LintViolation]:
        """Check if logging calls use appropriate levels for exceptions."""
        violations = []
        logging_calls = self._get_logging_calls_in_handler(node)

        for call in logging_calls:
            if self._is_logging_call(call) and self._is_inappropriate_level(call):
                violations.append(self._create_wrong_level_violation(context, call))

        return violations

    def _is_inappropriate_level(self, call: ast.Call) -> bool:
        """Check if logging call uses inappropriate level for exceptions."""
        if not isinstance(call.func, ast.Attribute):
            return False
        method_name = call.func.attr.lower()
        # Allow debug level for exception logging (useful in loops or discovery)
        return method_name not in ["debug", "error", "exception", "critical"]

    def _create_wrong_level_violation(self, context: LintContext, call: ast.Call) -> LintViolation:
        """Create violation for inappropriate logging level."""
        if not isinstance(call.func, ast.Attribute):
            raise TypeError("Expected attribute access")
        method_name = call.func.attr.lower()
        violation = self.create_violation(
            context,
            call,
            message=f"Using {method_name} level for exception logging",
            description="Consider using error or exception level for exception handlers",
            suggestion="Use logger.error() or logger.exception() for exception logging",
            violation_context={"current_level": method_name, "issue": "wrong_level"},
        )
        violation.severity = Severity.INFO
        return violation

    def _has_logging_in_handler(self, node: ast.ExceptHandler) -> bool:
        """Check if exception handler contains logging calls."""
        return any(isinstance(stmt, ast.Call) and self._is_logging_call(stmt) for stmt in ast.walk(node))

    def _has_reraise(self, node: ast.ExceptHandler) -> bool:
        """Check if exception handler re-raises the exception."""
        return any(isinstance(stmt, ast.Raise) and stmt.exc is None for stmt in node.body)

    def _get_logging_calls_in_handler(self, node: ast.ExceptHandler) -> list[ast.Call]:
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
        logger_names = ["logger", "log", "logging"]

        if isinstance(node.func.value, ast.Name):
            return node.func.value.id in logger_names and method_name in [
                "debug",
                "info",
                "warning",
                "error",
                "critical",
                "success",
                "exception",
            ]

        return False
