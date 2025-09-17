#!/usr/bin/env python3
"""
Purpose: Loguru-specific linting rules for best practices
Scope: Enforces loguru usage patterns and best practices
Overview: This module provides rules specifically for loguru logging library,
    promoting structured logging, proper configuration, and consistent usage
    patterns. It helps teams adopt loguru effectively while avoiding common
    pitfalls and ensuring observability best practices.
Dependencies: Framework interfaces, AST analysis utilities
Exports: Loguru-specific linting rules
Interfaces: All rules implement ASTLintRule interface
Implementation: Rule-based architecture with loguru pattern detection
"""

import ast
from typing import List, Set, Dict, Any, Optional

from ...framework.interfaces import ASTLintRule, LintViolation, LintContext, Severity


class UseLoguruRule(ASTLintRule):
    """Rule to encourage loguru usage over standard logging."""

    @property
    def rule_id(self) -> str:
        return "logging.use-loguru"

    @property
    def rule_name(self) -> str:
        return "Use Loguru for Logging"

    @property
    def description(self) -> str:
        return "Prefer loguru over standard logging for better functionality and ease of use"

    @property
    def severity(self) -> Severity:
        return Severity.INFO

    @property
    def categories(self) -> Set[str]:
        return {"logging", "loguru", "best-practices"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        # Check for standard logging imports
        return isinstance(node, (ast.Import, ast.ImportFrom))

    def check_node(self, node: ast.AST, context: LintContext) -> List[LintViolation]:
        violations = []

        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == 'logging':
                    violations.append(self._create_violation(node, context, 'logging'))

        elif isinstance(node, ast.ImportFrom):
            if node.module == 'logging':
                violations.append(self._create_violation(node, context, 'logging'))

        return violations

    def _create_violation(self, node: ast.AST, context: LintContext,
                         logging_type: str) -> LintViolation:
        """Create a violation for standard logging usage."""
        return LintViolation(
            rule_id=self.rule_id,
            file_path=str(context.file_path),
            line=node.lineno,
            column=node.col_offset,
            severity=self.severity,
            message=f"Consider using loguru instead of standard {logging_type}",
            description="Loguru provides better functionality, easier configuration, and more intuitive API",
            suggestion="Replace with: from loguru import logger",
            context={'logging_type': logging_type}
        )


class LoguruImportRule(ASTLintRule):
    """Rule to enforce proper loguru import patterns."""

    @property
    def rule_id(self) -> str:
        return "logging.loguru-import"

    @property
    def rule_name(self) -> str:
        return "Proper Loguru Import"

    @property
    def description(self) -> str:
        return "Import loguru logger using the recommended pattern"

    @property
    def severity(self) -> Severity:
        return Severity.WARNING

    @property
    def categories(self) -> Set[str]:
        return {"logging", "loguru", "imports"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        return isinstance(node, (ast.Import, ast.ImportFrom))

    def check_node(self, node: ast.AST, context: LintContext) -> List[LintViolation]:
        violations = []

        if isinstance(node, ast.ImportFrom) and node.module == 'loguru':
            # Check for recommended import pattern
            for alias in node.names:
                if alias.name != 'logger':
                    violations.append(LintViolation(
                        rule_id=self.rule_id,
                        file_path=str(context.file_path),
                        line=node.lineno,
                        column=node.col_offset,
                        severity=self.severity,
                        message=f"Import loguru.{alias.name} not recommended",
                        description="The recommended pattern is to import only 'logger' from loguru",
                        suggestion="Use: from loguru import logger",
                        context={'imported_name': alias.name}
                    ))

        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == 'loguru':
                    violations.append(LintViolation(
                        rule_id=self.rule_id,
                        file_path=str(context.file_path),
                        line=node.lineno,
                        column=node.col_offset,
                        severity=self.severity,
                        message="Use 'from loguru import logger' instead of 'import loguru'",
                        description="Importing logger directly is more convenient and follows loguru best practices",
                        suggestion="Use: from loguru import logger",
                        context={'import_type': 'full_module'}
                    ))

        return violations


class StructuredLoggingRule(ASTLintRule):
    """Rule to encourage structured logging with loguru."""

    @property
    def rule_id(self) -> str:
        return "logging.structured-logging"

    @property
    def rule_name(self) -> str:
        return "Structured Logging"

    @property
    def description(self) -> str:
        return "Use structured logging with context variables for better observability"

    @property
    def severity(self) -> Severity:
        return Severity.INFO

    @property
    def categories(self) -> Set[str]:
        return {"logging", "loguru", "observability"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        # Check for logger method calls
        return (isinstance(node, ast.Call) and
                isinstance(node.func, ast.Attribute) and
                isinstance(node.func.value, ast.Name) and
                node.func.value.id == 'logger')

    def check_node(self, node: ast.Call, context: LintContext) -> List[LintViolation]:
        if not self._is_logger_call(node):
            return []

        violations = []
        method_name = node.func.attr

        # Check if using f-strings or format() instead of structured logging
        if self._uses_string_formatting(node):
            violations.append(LintViolation(
                rule_id=self.rule_id,
                file_path=str(context.file_path),
                line=node.lineno,
                column=node.col_offset,
                severity=self.severity,
                message=f"Use structured logging instead of string formatting in logger.{method_name}()",
                description="Structured logging provides better searchability and parsing capabilities",
                suggestion="Use: logger.info('User logged in', user_id=user_id, ip=ip) instead of f-strings",
                context={'method': method_name, 'issue': 'string_formatting'}
            ))

        # Check for complex log messages that could benefit from context
        if self._has_complex_message(node):
            violations.append(LintViolation(
                rule_id=self.rule_id,
                file_path=str(context.file_path),
                line=node.lineno,
                column=node.col_offset,
                severity=self.severity,
                message=f"Consider adding context variables to logger.{method_name}() call",
                description="Adding context variables makes logs more searchable and parseable",
                suggestion="Add context: logger.info('Operation completed', duration=elapsed, status=result)",
                context={'method': method_name, 'issue': 'missing_context'}
            ))

        return violations

    def _is_logger_call(self, node: ast.Call) -> bool:
        """Check if this is a loguru logger method call."""
        return (isinstance(node.func, ast.Attribute) and
                isinstance(node.func.value, ast.Name) and
                node.func.value.id == 'logger' and
                node.func.attr in ['debug', 'info', 'warning', 'error', 'critical', 'success'])

    def _uses_string_formatting(self, node: ast.Call) -> bool:
        """Check if the log call uses string formatting instead of structured logging."""
        if not node.args:
            return False

        first_arg = node.args[0]

        # Check for f-strings
        if isinstance(first_arg, ast.JoinedStr):
            return True

        # Check for .format() calls
        if (isinstance(first_arg, ast.Call) and
            isinstance(first_arg.func, ast.Attribute) and
            first_arg.func.attr == 'format'):
            return True

        # Check for % formatting
        if isinstance(first_arg, ast.BinOp) and isinstance(first_arg.op, ast.Mod):
            return True

        return False

    def _has_complex_message(self, node: ast.Call) -> bool:
        """Check if the log message is complex and could benefit from context variables."""
        if not node.args:
            return False

        # If there are keyword arguments, structured logging is already being used
        if node.keywords:
            return False

        first_arg = node.args[0]

        # Check for string literals with multiple sentences or complex content
        if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
            message = first_arg.value
            # Heuristics for complex messages
            if (len(message) > 50 or
                message.count(' ') > 5 or
                any(word in message.lower() for word in ['completed', 'failed', 'started', 'finished', 'processing'])):
                return True

        return False


class LogLevelConsistencyRule(ASTLintRule):
    """Rule to ensure consistent log level usage."""

    @property
    def rule_id(self) -> str:
        return "logging.log-level-consistency"

    @property
    def rule_name(self) -> str:
        return "Log Level Consistency"

    @property
    def description(self) -> str:
        return "Use appropriate log levels consistently based on message content"

    @property
    def severity(self) -> Severity:
        return Severity.INFO

    @property
    def categories(self) -> Set[str]:
        return {"logging", "loguru", "consistency"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        return (isinstance(node, ast.Call) and
                isinstance(node.func, ast.Attribute) and
                isinstance(node.func.value, ast.Name) and
                node.func.value.id == 'logger')

    def check_node(self, node: ast.Call, context: LintContext) -> List[LintViolation]:
        if not self._is_logger_call(node):
            return []

        violations = []
        method_name = node.func.attr

        if node.args and isinstance(node.args[0], ast.Constant):
            message = node.args[0].value
            if isinstance(message, str):
                suggested_level = self._suggest_log_level(message)

                if suggested_level and suggested_level != method_name:
                    violations.append(LintViolation(
                        rule_id=self.rule_id,
                        file_path=str(context.file_path),
                        line=node.lineno,
                        column=node.col_offset,
                        severity=self.severity,
                        message=f"Message suggests '{suggested_level}' level but using '{method_name}'",
                        description=f"Log message content suggests using logger.{suggested_level}() instead",
                        suggestion=f"Consider using logger.{suggested_level}() for this message",
                        context={
                            'current_level': method_name,
                            'suggested_level': suggested_level,
                            'message': message[:50] + '...' if len(message) > 50 else message
                        }
                    ))

        return violations

    def _is_logger_call(self, node: ast.Call) -> bool:
        """Check if this is a loguru logger method call."""
        return (isinstance(node.func, ast.Attribute) and
                isinstance(node.func.value, ast.Name) and
                node.func.value.id == 'logger' and
                node.func.attr in ['debug', 'info', 'warning', 'error', 'critical', 'success'])

    def _suggest_log_level(self, message: str) -> Optional[str]:
        """Suggest appropriate log level based on message content."""
        message_lower = message.lower()

        # Error indicators
        if any(word in message_lower for word in ['error', 'exception', 'failed', 'failure', 'crash', 'fatal']):
            return 'error'

        # Warning indicators
        if any(word in message_lower for word in ['warning', 'warn', 'deprecated', 'fallback', 'retry']):
            return 'warning'

        # Success indicators (loguru-specific)
        if any(word in message_lower for word in ['success', 'completed successfully', 'finished successfully']):
            return 'success'

        # Debug indicators
        if any(word in message_lower for word in ['debug', 'trace', 'dump', 'variable', 'state']):
            return 'debug'

        # Info is default for most cases
        return None


class LoguruConfigurationRule(ASTLintRule):
    """Rule to check for proper loguru configuration."""

    @property
    def rule_id(self) -> str:
        return "logging.loguru-configuration"

    @property
    def rule_name(self) -> str:
        return "Loguru Configuration"

    @property
    def description(self) -> str:
        return "Ensure proper loguru configuration for production use"

    @property
    def severity(self) -> Severity:
        return Severity.WARNING

    @property
    def categories(self) -> Set[str]:
        return {"logging", "loguru", "configuration"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        # Check for logger.add() calls
        return (isinstance(node, ast.Call) and
                isinstance(node.func, ast.Attribute) and
                isinstance(node.func.value, ast.Name) and
                node.func.value.id == 'logger' and
                node.func.attr == 'add')

    def check_node(self, node: ast.Call, context: LintContext) -> List[LintViolation]:
        violations = []

        # Check for proper sink configuration
        if not node.args:
            violations.append(LintViolation(
                rule_id=self.rule_id,
                file_path=str(context.file_path),
                line=node.lineno,
                column=node.col_offset,
                severity=self.severity,
                message="logger.add() called without sink argument",
                description="loguru.add() requires a sink argument (file, handler, etc.)",
                suggestion="Specify a sink: logger.add('app.log') or logger.add(sys.stderr)",
                context={'issue': 'missing_sink'}
            ))
            return violations

        # Check for recommended configuration options
        keyword_args = {kw.arg for kw in node.keywords}

        recommended_options = {
            'level': 'Specify log level for better control',
            'format': 'Use custom format for better readability',
            'rotation': 'Enable log rotation for file sinks',
            'retention': 'Set log retention policy'
        }

        # Only suggest these for file sinks (not stderr/stdout)
        first_arg = node.args[0]
        is_file_sink = (isinstance(first_arg, ast.Constant) and
                       isinstance(first_arg.value, str) and
                       not first_arg.value.startswith('<'))

        if is_file_sink:
            for option, description in recommended_options.items():
                if option not in keyword_args:
                    violations.append(LintViolation(
                        rule_id=self.rule_id,
                        file_path=str(context.file_path),
                        line=node.lineno,
                        column=node.col_offset,
                        severity=Severity.INFO,
                        message=f"Consider adding '{option}' parameter to logger.add()",
                        description=description,
                        suggestion=f"Add {option} parameter for better log management",
                        context={'missing_option': option, 'sink_type': 'file'}
                    ))

        return violations
