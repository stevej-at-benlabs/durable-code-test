#!/usr/bin/env python3
"""
Purpose: Print statement detection rules for the pluggable framework
Scope: Converts print statement linter functionality to framework rules
Overview: This module converts the monolithic print statement linter into
    focused, pluggable rules. Rules detect print statements and console output
    that should be replaced with proper logging mechanisms for production code.
Dependencies: Framework interfaces, AST analysis utilities
Exports: Print statement detection rules
Interfaces: All rules implement ASTLintRule interface
Implementation: Rule-based architecture with language-specific detection
"""

import ast
from typing import Any

from design_linters.framework.interfaces import ASTLintRule, LintContext, LintViolation, Severity


class PrintStatementRule(ASTLintRule):
    """Rule to detect print statements that should use logging instead."""

    @property
    def rule_id(self) -> str:
        return "style.print-statement"

    @property
    def rule_name(self) -> str:
        return "Print Statement Usage"

    @property
    def description(self) -> str:
        return "Print statements should be replaced with proper logging for production code"

    @property
    def severity(self) -> Severity:
        return Severity.WARNING

    @property
    def categories(self) -> set[str]:
        return {"style", "logging", "production"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        # Check for print() function calls
        return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print"

    def check_node(self, node: ast.AST, context: LintContext) -> list[LintViolation]:
        if not isinstance(node, ast.Call):
            raise TypeError("PrintStatementRule should only receive ast.Call nodes")
        config = self.get_configuration(context.metadata or {})

        # Check if print statements are allowed in certain contexts
        if self._is_allowed_context(context, config):
            return []

        # Check for disable comments
        if self._has_disable_comment(node, context):
            return []

        suggestion = self._generate_logging_suggestion(node, context)

        return [
            self.create_violation(
                context=context,
                node=node,
                message="Print statement found - use logging instead",
                description=(
                    "Print statements should be replaced with proper logging "
                    "for better control and production readiness"
                ),
                suggestion=suggestion,
                violation_context={"function": context.current_function, "class": context.current_class},
            )
        ]

    def _is_allowed_context(self, context: LintContext, config: dict[str, Any]) -> bool:
        """Check if print statements are allowed in this context."""
        # Allow print statements in specific, limited contexts only

        # Check for rule-specific configuration
        rule_config = config.get("rules", {}).get(self.rule_id, {})
        if rule_config.get("allow_in_cli", True) and self._is_cli_output_context(context):
            return True

        if rule_config.get("allow_in_main", True) and context.current_function == "__main__":
            return True

        # Allow in specific test functions only (not entire test files)
        return rule_config.get("allow_in_tests", False) and self._is_test_function_context(context)

    def _has_disable_comment(self, _node: ast.Call, _context: LintContext) -> bool:
        """Check if there's a disable comment for this print statement."""
        # This would require parsing comments from the source code
        # For now, we'll implement a basic check
        return False

    def _generate_logging_suggestion(self, node: ast.Call, _context: LintContext) -> str:
        """Generate a suggestion for replacing print with logging."""
        if not self._has_single_string_arg(node):
            return "logger.info('...')  # Use appropriate logging level"

        message = node.args[0].value  # type: ignore
        log_level = self._determine_log_level(message)
        return f"logger.{log_level}('{message}')"

    def _is_cli_output_context(self, context: LintContext) -> bool:
        """Check if this is a CLI output context where print statements might be acceptable."""
        # Only allow in CLI scripts with specific user-facing output functions
        file_content = context.file_content or ""
        if "argparse" not in file_content:
            return False

        # Only allow in specific CLI output functions, not general code
        function_name = context.current_function or ""
        cli_output_functions = ["print_", "display_", "show_", "output_", "list_", "_print_"]
        return any(pattern in function_name.lower() for pattern in cli_output_functions)

    def _is_test_function_context(self, context: LintContext) -> bool:
        """Check if this is within a test function (not just any file in test directory)."""
        function_name = context.current_function or ""
        return function_name.startswith("test_") or function_name.startswith("debug_")

    def _has_single_string_arg(self, node: ast.Call) -> bool:
        """Check if node has a single string argument."""
        return len(node.args) == 1 and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)

    def _determine_log_level(self, message: str) -> str:
        """Determine appropriate log level based on message content."""
        message_lower = message.lower()

        if any(keyword in message_lower for keyword in ["error", "fail", "exception"]):
            return "error"
        if any(keyword in message_lower for keyword in ["warn", "warning"]):
            return "warning"
        if any(keyword in message_lower for keyword in ["info", "start", "finish"]):
            return "info"
        return "debug"


class ConsoleOutputRule(ASTLintRule):
    """Rule to detect other console output methods that should use logging."""

    @property
    def rule_id(self) -> str:
        return "style.console-output"

    @property
    def rule_name(self) -> str:
        return "Console Output Usage"

    @property
    def description(self) -> str:
        return "Console output methods should be replaced with proper logging"

    @property
    def severity(self) -> Severity:
        return Severity.INFO

    @property
    def categories(self) -> set[str]:
        return {"style", "logging", "console"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        if not isinstance(node, ast.Call):
            return False

        return self._is_console_output_call(node)

    def _is_console_output_call(self, node: ast.Call) -> bool:
        """Check if this is a console output call."""
        if not isinstance(node.func, ast.Attribute):
            return False

        return self._is_sys_output_call(node) or self._is_console_log_call(node)

    def _is_sys_output_call(self, node: ast.Call) -> bool:
        """Check for sys.stdout.write, sys.stderr.write calls."""
        func = node.func
        if not isinstance(func, ast.Attribute):
            return False

        return (
            isinstance(func.value, ast.Attribute)
            and isinstance(func.value.value, ast.Name)
            and func.value.value.id == "sys"
            and func.value.attr in ["stdout", "stderr"]
            and func.attr == "write"
        )

    def _is_console_log_call(self, node: ast.Call) -> bool:
        """Check for console.log calls."""
        func = node.func
        if not isinstance(func, ast.Attribute):
            return False

        return isinstance(func.value, ast.Name) and func.value.id == "console" and func.attr == "log"

    def check_node(self, node: ast.AST, context: LintContext) -> list[LintViolation]:
        if not isinstance(node, ast.Call):
            raise TypeError("ConsoleOutputRule should only receive ast.Call nodes")
        config = self.get_configuration(context.metadata or {})

        # Skip if in allowed contexts
        if self._is_allowed_context(context, config):
            return []

        output_method = self._get_output_method(node)
        suggestion = self._generate_suggestion(output_method)

        return [
            self.create_violation(
                context,
                node,
                message=(f"Console output method '{output_method}' found - " "use logging instead"),
                description=f"Replace {output_method} with appropriate logging calls",
                suggestion=suggestion,
                violation_context={"output_method": output_method},
            )
        ]

    def _is_allowed_context(self, context: LintContext, config: dict[str, Any]) -> bool:
        """Check if console output is allowed in this context."""
        # Use similar rule-specific configuration as PrintStatementRule
        rule_config = config.get("rules", {}).get(self.rule_id, {})

        # Allow in CLI output contexts
        if rule_config.get("allow_in_cli", True):
            file_content = context.file_content or ""
            if "argparse" in file_content:
                function_name = context.current_function or ""
                cli_output_functions = ["print_", "display_", "show_", "output_", "list_", "_print_"]
                if any(pattern in function_name.lower() for pattern in cli_output_functions):
                    return True

        # Allow in main function
        return rule_config.get("allow_in_main", True) and context.current_function == "__main__"

    def _get_output_method(self, node: ast.Call) -> str:
        """Get the name of the output method being used."""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Attribute):
                # sys.stdout.write
                if isinstance(node.func.value.value, ast.Name):
                    return f"{node.func.value.value.id}.{node.func.value.attr}.{node.func.attr}"
            else:
                # console.log
                if isinstance(node.func.value, ast.Name):
                    return f"{node.func.value.id}.{node.func.attr}"
        return "unknown"

    def _generate_suggestion(self, output_method: str) -> str:
        """Generate appropriate logging suggestion based on output method."""
        if "stderr" in output_method:
            return "logger.error('...')  # For error output"
        if "stdout" in output_method:
            return "logger.info('...')   # For standard output"
        return "logger.debug('...')  # Use appropriate logging level"
