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
from typing import List, Set, Dict, Any

from ...framework.interfaces import ASTLintRule, LintViolation, LintContext, Severity


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
    def categories(self) -> Set[str]:
        return {"style", "logging", "production"}

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

        # Check for disable comments
        if self._has_disable_comment(node, context):
            return []

        suggestion = self._generate_logging_suggestion(node, context)

        return [LintViolation(
            rule_id=self.rule_id,
            file_path=str(context.file_path),
            line=node.lineno,
            column=node.col_offset,
            severity=self.severity,
            message="Print statement found - use logging instead",
            description="Print statements should be replaced with proper logging for better control and production readiness",
            suggestion=suggestion,
            context={'function': context.current_function, 'class': context.current_class}
        )]

    def _is_allowed_context(self, context: LintContext, config: Dict[str, Any]) -> bool:
        """Check if print statements are allowed in this context."""
        allowed_patterns = config.get('allowed_patterns', ['test_', '__main__', 'debug_', 'example_'])

        # Allow in test files
        file_name = str(context.file_path).lower()
        if any(pattern in file_name for pattern in ['test', 'example', 'demo']):
            return True

        # Allow in main blocks
        if context.current_function == '__main__':
            return True

        # Allow in functions with allowed patterns
        function_name = context.current_function or ''
        if any(pattern in function_name.lower() for pattern in allowed_patterns):
            return True

        return False

    def _has_disable_comment(self, node: ast.Call, context: LintContext) -> bool:
        """Check if there's a disable comment for this print statement."""
        # This would require parsing comments from the source code
        # For now, we'll implement a basic check
        return False

    def _generate_logging_suggestion(self, node: ast.Call, context: LintContext) -> str:
        """Generate a suggestion for replacing print with logging."""
        if len(node.args) == 1 and isinstance(node.args[0], ast.Constant):
            message = node.args[0].value
            if isinstance(message, str):
                if any(keyword in message.lower() for keyword in ['error', 'fail', 'exception']):
                    return f"logger.error('{message}')"
                elif any(keyword in message.lower() for keyword in ['warn', 'warning']):
                    return f"logger.warning('{message}')"
                elif any(keyword in message.lower() for keyword in ['info', 'start', 'finish']):
                    return f"logger.info('{message}')"
                else:
                    return f"logger.debug('{message}')"

        return "logger.info('...')  # Use appropriate logging level"


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
    def categories(self) -> Set[str]:
        return {"style", "logging", "console"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        # Check for sys.stdout.write, sys.stderr.write, etc.
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                # Check for sys.stdout.write, sys.stderr.write
                if (isinstance(node.func.value, ast.Attribute) and
                    isinstance(node.func.value.value, ast.Name) and
                    node.func.value.value.id == 'sys' and
                    node.func.value.attr in ['stdout', 'stderr'] and
                    node.func.attr == 'write'):
                    return True

                # Check for console.log (JavaScript-style, sometimes used in Python)
                if (isinstance(node.func.value, ast.Name) and
                    node.func.value.id == 'console' and
                    node.func.attr == 'log'):
                    return True

        return False

    def check_node(self, node: ast.Call, context: LintContext) -> List[LintViolation]:
        config = self.get_configuration(context.metadata or {})

        # Skip if in allowed contexts
        if self._is_allowed_context(context, config):
            return []

        output_method = self._get_output_method(node)
        suggestion = self._generate_suggestion(output_method)

        return [LintViolation(
            rule_id=self.rule_id,
            file_path=str(context.file_path),
            line=node.lineno,
            column=node.col_offset,
            severity=self.severity,
            message=f"Console output method '{output_method}' found - use logging instead",
            description=f"Replace {output_method} with appropriate logging calls",
            suggestion=suggestion,
            context={'output_method': output_method}
        )]

    def _is_allowed_context(self, context: LintContext, config: Dict[str, Any]) -> bool:
        """Check if console output is allowed in this context."""
        # Similar logic to PrintStatementRule
        file_name = str(context.file_path).lower()
        if any(pattern in file_name for pattern in ['test', 'example', 'demo', 'script']):
            return True

        function_name = context.current_function or ''
        if any(pattern in function_name.lower() for pattern in ['test_', 'debug_', 'main']):
            return True

        return False

    def _get_output_method(self, node: ast.Call) -> str:
        """Get the name of the output method being used."""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Attribute):
                # sys.stdout.write
                return f"{node.func.value.value.id}.{node.func.value.attr}.{node.func.attr}"
            else:
                # console.log
                return f"{node.func.value.id}.{node.func.attr}"
        return "unknown"

    def _generate_suggestion(self, output_method: str) -> str:
        """Generate appropriate logging suggestion based on output method."""
        if 'stderr' in output_method:
            return "logger.error('...')  # For error output"
        elif 'stdout' in output_method:
            return "logger.info('...')   # For standard output"
        else:
            return "logger.debug('...')  # Use appropriate logging level"
