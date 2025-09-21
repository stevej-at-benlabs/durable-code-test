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

from design_linters.framework.interfaces import ASTLintRule, LintContext, LintViolation, Severity

# Configuration constants
COMPLEX_MESSAGE_MAX_LENGTH = 50
COMPLEX_MESSAGE_MAX_WORDS = 7

# Constants for message truncation
MAX_LOG_MESSAGE_DISPLAY_LENGTH = 50


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
    def categories(self) -> set[str]:
        return {"logging", "loguru", "best-practices"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        # Check for standard logging imports
        return isinstance(node, (ast.Import, ast.ImportFrom))

    def check_node(self, node: ast.AST, context: LintContext) -> list[LintViolation]:
        violations = []

        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "logging":
                    violations.append(self._create_violation(node, context, "logging"))

        elif isinstance(node, ast.ImportFrom) and node.module == "logging":
            violations.append(self._create_violation(node, context, "logging"))

        return violations

    def _create_violation(self, node: ast.AST, context: LintContext, logging_type: str) -> LintViolation:
        """Create a violation for standard logging usage."""
        return self.create_violation(
            context,
            node,
            message=f"Consider using loguru instead of standard {logging_type}",
            description="Loguru provides better functionality, easier configuration, and more intuitive API",
            suggestion="Replace with: from loguru import logger",
            violation_context={"logging_type": logging_type},
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
    def categories(self) -> set[str]:
        return {"logging", "loguru", "imports"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        return isinstance(node, (ast.Import, ast.ImportFrom))

    def check_node(self, node: ast.AST, context: LintContext) -> list[LintViolation]:
        if isinstance(node, ast.ImportFrom) and node.module == "loguru":
            return self._check_import_from_loguru(node, context)

        if isinstance(node, ast.Import):
            return self._check_import_loguru(node, context)

        return []

    def _check_import_from_loguru(self, node: ast.ImportFrom, context: LintContext) -> list[LintViolation]:
        """Check for recommended import pattern from loguru."""
        violations = []
        for alias in node.names:
            if alias.name != "logger":
                violations.append(
                    self.create_violation(
                        context,
                        node,
                        message=f"Import loguru.{alias.name} not recommended",
                        description="The recommended pattern is to import only 'logger' from loguru",
                        suggestion="Use: from loguru import logger",
                        violation_context={"imported_name": alias.name},
                    )
                )
        return violations

    def _check_import_loguru(self, node: ast.Import, context: LintContext) -> list[LintViolation]:
        """Check for direct loguru import patterns."""
        violations = []
        for alias in node.names:
            if alias.name == "loguru":
                violations.append(
                    self.create_violation(
                        context,
                        node,
                        message="Use 'from loguru import logger' instead of 'import loguru'",
                        description=("Importing logger directly is more convenient and follows loguru best practices"),
                        suggestion="Use: from loguru import logger",
                        violation_context={"import_type": "full_module"},
                    )
                )
        return violations


class LoggingFormatAnalyzer:
    """Helper class for analyzing logging format patterns."""

    def __init__(self):
        """Initialize the analyzer with pattern detection methods."""
        self._format_checkers = [
            self._is_f_string,
            self._is_format_call,
            self._is_percent_formatting,
        ]

    def uses_string_formatting(self, node: ast.Call) -> bool:
        """Check if the log call uses string formatting instead of structured logging."""
        if not node.args:
            return False

        first_arg = node.args[0]
        return any(checker(first_arg) for checker in self._format_checkers)

    def has_complex_message(self, node: ast.Call) -> bool:
        """Check if the log call has a complex message that would benefit from context."""
        if not node.args:
            return False

        first_arg = node.args[0]
        if not isinstance(first_arg, ast.Constant) or not isinstance(first_arg.value, str):
            return False

        message = first_arg.value
        return self._is_message_complex(message)

    def _is_f_string(self, node: ast.AST) -> bool:
        """Check if node is an f-string."""
        return isinstance(node, ast.JoinedStr)

    def _is_format_call(self, node: ast.AST) -> bool:
        """Check if node is a .format() call."""
        return isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "format"

    def _is_percent_formatting(self, node: ast.AST) -> bool:
        """Check if node uses % formatting."""
        return isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod)

    def _is_message_complex(self, message: str) -> bool:
        """Check if message meets complexity criteria."""
        # Much higher thresholds to reduce noise - only flag genuinely complex messages
        return (
            len(message) > COMPLEX_MESSAGE_MAX_LENGTH
            or message.count(" ") > COMPLEX_MESSAGE_MAX_WORDS
            or self._has_action_words(message)
        )

    def _has_action_words(self, message: str) -> bool:
        """Check if message contains action-related words that suggest measurable context."""
        # Check for patterns that suggest missing context
        action_patterns = [
            "processing completed",
            "operation failed",
            "request failed",
            "task completed",
            "job finished",
            "operation completed successfully",
            "completed successfully",
            "started",
        ]
        message_lower = message.lower()
        return any(pattern in message_lower for pattern in action_patterns)


class StructuredLoggingRule(ASTLintRule):
    """Rule to encourage structured logging with loguru."""

    def __init__(self):
        """Initialize with format analyzer."""
        super().__init__()
        self._format_analyzer = LoggingFormatAnalyzer()

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
    def categories(self) -> set[str]:
        return {"logging", "loguru", "observability"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        # Check for logger method calls
        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "logger"
        )

    def check_node(self, node: ast.AST, context: LintContext) -> list[LintViolation]:
        if not isinstance(node, ast.Call):
            raise TypeError("StructuredLoggingRule should only receive ast.Call nodes")
        if not self._is_logger_call(node):
            return []

        if not isinstance(node.func, ast.Attribute):
            raise TypeError("Expected attribute access")
        method_name = node.func.attr

        violations = []
        violations.extend(self._check_string_formatting(node, context, method_name))
        violations.extend(self._check_complex_messages(node, context, method_name))

        return violations

    def _check_string_formatting(self, node: ast.Call, context: LintContext, method_name: str) -> list[LintViolation]:
        """Check for string formatting issues."""
        if not self._format_analyzer.uses_string_formatting(node):
            return []

        return [
            self.create_violation(
                context,
                node,
                message=f"Use structured logging instead of string formatting in logger.{method_name}()",
                description="Structured logging provides better searchability and parsing capabilities",
                suggestion="Use: logger.info('User logged in', user_id=user_id, ip=ip) instead of f-strings",
                violation_context={"method": method_name, "issue": "string_formatting"},
            )
        ]

    def _check_complex_messages(self, node: ast.Call, context: LintContext, method_name: str) -> list[LintViolation]:
        """Check for complex messages that need context."""
        if not self._format_analyzer.has_complex_message(node):
            return []

        # Check if context variables are already present via keyword arguments
        if node.keywords:
            return []  # Context variables already present

        return [
            self.create_violation(
                context,
                node,
                message=f"Consider adding context variables to logger.{method_name}() call",
                description="Adding context variables makes logs more searchable and parseable",
                suggestion="Add context: logger.info('Operation completed', duration=elapsed, status=result)",
                violation_context={"method": method_name, "issue": "missing_context"},
            )
        ]

    def _is_logger_call(self, node: ast.Call) -> bool:
        """Check if this is a loguru logger method call."""
        return (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "logger"
            and node.func.attr in ["debug", "info", "warning", "error", "critical", "success"]
        )

    def _uses_string_formatting(self, node: ast.Call) -> bool:
        """Check if the log call uses string formatting instead of structured logging."""
        return self._format_analyzer.uses_string_formatting(node)

    def _has_complex_message(self, node: ast.Call) -> bool:
        """Check if the log call has a complex message that would benefit from context."""
        return self._format_analyzer.has_complex_message(node)


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
    def categories(self) -> set[str]:
        return {"logging", "loguru", "consistency"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "logger"
        )

    def check_node(self, node: ast.AST, context: LintContext) -> list[LintViolation]:
        if not isinstance(node, ast.Call):
            raise TypeError("LogLevelConsistencyRule should only receive ast.Call nodes")
        if not self._is_logger_call(node):
            return []

        if not isinstance(node.func, ast.Attribute):
            raise TypeError("Expected attribute access")
        method_name = node.func.attr

        return self._check_log_level_consistency(node, context, method_name)

    def _check_log_level_consistency(
        self, node: ast.Call, context: LintContext, method_name: str
    ) -> list[LintViolation]:
        """Check if log level matches message content."""
        if not self._has_string_message(node):
            return []

        message = node.args[0].value  # type: ignore
        suggested_level = self._suggest_log_level(message)

        if not suggested_level or suggested_level == method_name:
            return []

        return self._create_level_mismatch_violation(node, context, method_name, suggested_level, message=message)

    def _has_string_message(self, node: ast.Call) -> bool:
        """Check if node has a string message as first argument."""
        return bool(node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str))

    def _create_level_mismatch_violation(
        self, node: ast.Call, context: LintContext, current_level: str, suggested_level: str, *, message: str
    ) -> list[LintViolation]:
        """Create violation for log level mismatch."""
        truncated_message = (
            message[:MAX_LOG_MESSAGE_DISPLAY_LENGTH] + "..."
            if len(message) > MAX_LOG_MESSAGE_DISPLAY_LENGTH
            else message
        )

        return [
            self.create_violation(
                context,
                node,
                message=f"Message suggests '{suggested_level}' level but using '{current_level}'",
                description=f"Log message content suggests using logger.{suggested_level}() instead",
                suggestion=f"Consider using logger.{suggested_level}() for this message",
                violation_context={
                    "current_level": current_level,
                    "suggested_level": suggested_level,
                    "message": truncated_message,
                },
            )
        ]

    def _is_logger_call(self, node: ast.Call) -> bool:
        """Check if this is a loguru logger method call."""
        return (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "logger"
            and node.func.attr in ["debug", "info", "warning", "error", "critical", "success"]
        )

    def _suggest_log_level(self, message: str) -> str | None:
        """Suggest appropriate log level based on message content."""
        message_lower = message.lower()

        level_indicators = {
            "error": ["error", "exception", "crash", "fatal", "failed", "failure"],
            "warning": ["warning", "warn", "deprecated", "fallback", "retry"],
            "success": ["success", "completed successfully", "finished successfully"],
            "debug": [
                "debug",
                "trace",
                "dump",
                "variable",
                "state",
                "skipped",
            ],
        }

        for level, indicators in level_indicators.items():
            if any(word in message_lower for word in indicators):
                return level

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
    def categories(self) -> set[str]:
        return {"logging", "loguru", "configuration"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        # Check for logger.add() calls
        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "logger"
            and node.func.attr == "add"
        )

    def check_node(self, node: ast.AST, context: LintContext) -> list[LintViolation]:
        if not isinstance(node, ast.Call):
            raise TypeError("LoguruConfigurationRule should only receive ast.Call nodes")

        violations = []
        violations.extend(self._check_sink_argument(node, context))
        violations.extend(self._check_configuration_options(node, context))

        return violations

    def _check_sink_argument(self, node: ast.Call, context: LintContext) -> list[LintViolation]:
        """Check for proper sink configuration."""
        if node.args:
            return []

        return [
            self.create_violation(
                context,
                node,
                message="logger.add() called without sink argument",
                description="loguru.add() requires a sink argument (file, handler, etc.)",
                suggestion="Specify a sink: logger.add('app.log') or logger.add(sys.stderr)",
                violation_context={"issue": "missing_sink"},
            )
        ]

    def _check_configuration_options(self, node: ast.Call, context: LintContext) -> list[LintViolation]:
        """Check for recommended configuration options."""
        if not node.args:
            return []

        if not self._is_file_sink(node.args[0]):
            return []

        keyword_args = {kw.arg for kw in node.keywords}
        return self._create_missing_option_violations(node, context, keyword_args)

    def _is_file_sink(self, sink_arg: ast.AST) -> bool:
        """Check if sink argument is a file sink."""
        return (
            isinstance(sink_arg, ast.Constant)
            and isinstance(sink_arg.value, str)
            and not sink_arg.value.startswith("<")
        )

    def _create_missing_option_violations(
        self, node: ast.Call, context: LintContext, keyword_args: set
    ) -> list[LintViolation]:
        """Create violations for missing configuration options."""
        recommended_options = {
            "level": "Specify log level for better control",
            "format": "Use custom format for better readability",
            "rotation": "Enable log rotation for file sinks",
            "retention": "Set log retention policy",
        }

        violations = []
        for option, description in recommended_options.items():
            if option not in keyword_args:
                violation = self.create_violation(
                    context,
                    node,
                    message=f"Consider adding '{option}' parameter to logger.add()",
                    description=description,
                    suggestion=f"Add {option} parameter for better log management",
                    violation_context={"missing_option": option, "sink_type": "file"},
                )
                violation.severity = Severity.INFO
                violations.append(violation)

        return violations
