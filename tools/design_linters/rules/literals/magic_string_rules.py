#!/usr/bin/env python3
"""
Purpose: Magic string detection rules for the pluggable framework
Scope: Framework-based implementation for string literal detection
Overview: This module provides rules for detecting magic strings that should
    be replaced with named constants. It focuses on improving code maintainability
    by identifying hardcoded string values that should be extracted into
    meaningful constants for better configuration management and localization.
Dependencies: Framework interfaces, AST analysis utilities
Exports: String literal linting rules
Interfaces: All rules implement ASTLintRule interface
Implementation: Rule-based architecture with string pattern detection
"""

import ast
from typing import List, Set, Dict, Any
import re

from ...framework.interfaces import ASTLintRule, LintViolation, LintContext, Severity


class MagicStringRule(ASTLintRule):
    """Rule to detect magic strings that should be replaced with named constants."""

    @property
    def rule_id(self) -> str:
        return "literals.magic-string"

    @property
    def rule_name(self) -> str:
        return "Magic String"

    @property
    def description(self) -> str:
        return "String literals should be replaced with named constants for better maintainability"

    @property
    def severity(self) -> Severity:
        return Severity.INFO

    @property
    def categories(self) -> Set[str]:
        return {"literals", "constants", "maintainability", "configuration"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        return isinstance(node, ast.Constant) and isinstance(node.value, str)

    def check_node(self, node: ast.Constant, context: LintContext) -> List[LintViolation]:
        config = self.get_configuration(context.metadata or {})

        # Get allowed string patterns from configuration
        allowed_patterns = config.get('allowed_patterns', {
            '', ' ', '\n', '\t', ',', '.', '/', ':', 'utf-8', 'utf8',
            'r', 'w', 'a', 'rb', 'wb', 'ab'
        })

        string_value = node.value

        if string_value in allowed_patterns:
            return []

        # Check for specific contexts where strings are acceptable
        if self._is_acceptable_context(node, context, config):
            return []

        # Only flag strings that seem to be configuration or business logic
        if not self._should_be_constant(string_value, context, config):
            return []

        # Generate appropriate suggestion
        suggestion = self._generate_string_constant_suggestion(string_value, context)

        return [LintViolation(
            rule_id=self.rule_id,
            file_path=str(context.file_path),
            line=node.lineno,
            column=node.col_offset,
            severity=self.severity,
            message=f"Magic string '{string_value}' found",
            description=f"Consider replacing string literal '{string_value}' with a named constant",
            suggestion=suggestion,
            context={
                'value': string_value,
                'length': len(string_value),
                'function': context.current_function,
                'class': context.current_class
            }
        )]

    def _is_acceptable_context(self, node: ast.Constant, context: LintContext, config: Dict[str, Any]) -> bool:
        """Check if the string appears in an acceptable context."""

        string_value = node.value

        # Allow very short strings (single characters, etc.)
        if len(string_value) <= config.get('min_string_length', 2):
            return True

        # Allow in test files
        if 'test' in str(context.file_path).lower():
            return True

        # Allow in docstrings
        if self._is_in_docstring(context):
            return True

        # Allow in assert statements
        if self._is_in_assert(context):
            return True

        # Allow in logging calls
        if self._is_in_logging_call(context):
            return True

        # Allow format strings and f-strings
        if any(char in string_value for char in ['{', '}', '%']):
            return True

        # Allow debug/development strings
        if any(word in string_value.lower() for word in ['debug', 'test', 'temp', 'todo', 'fixme']):
            return True

        return False

    def _should_be_constant(self, string_value: str, context: LintContext, config: Dict[str, Any]) -> bool:
        """Determine if this string should be extracted as a constant."""

        # Configuration-like strings
        if self._looks_like_config(string_value):
            return True

        # URLs, file paths, or identifiers
        if self._looks_like_path_or_url(string_value):
            return True

        # Error messages or user-facing text
        if self._looks_like_user_message(string_value, context):
            return True

        # SQL queries or similar
        if self._looks_like_query(string_value):
            return True

        # API endpoints or keys
        if self._looks_like_api_related(string_value):
            return True

        # Only flag if meets minimum complexity
        min_length = config.get('min_flaggable_length', 10)
        if len(string_value) >= min_length:
            return True

        # Also flag short strings that look like configuration values
        # (e.g. 'production', 'strict', 'debug', etc.)
        if len(string_value) >= 3 and string_value.isalpha():
            return True

        return False

    def _is_in_docstring(self, context: LintContext) -> bool:
        """Check if string is part of a docstring."""
        if not context.node_stack or len(context.node_stack) < 2:
            return False

        # Check if parent is an Expr node (docstring pattern)
        parent = context.node_stack[-2] if len(context.node_stack) >= 2 else None
        if not isinstance(parent, ast.Expr):
            return False

        # Check if the Expr is the first statement in a function/class
        grandparent = context.node_stack[-3] if len(context.node_stack) >= 3 else None
        if isinstance(grandparent, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            # Check if it's the first statement
            if grandparent.body and grandparent.body[0] is parent:
                return True

        # Module-level docstring
        if isinstance(grandparent, ast.Module):
            if grandparent.body and grandparent.body[0] is parent:
                return True

        return False

    def _is_in_assert(self, context: LintContext) -> bool:
        """Check if string is in an assert statement."""
        if not context.node_stack:
            return False

        return any(isinstance(node, ast.Assert) for node in context.node_stack)

    def _is_in_logging_call(self, context: LintContext) -> bool:
        """Check if string is in a logging call."""
        if not context.node_stack:
            return False

        for node in reversed(context.node_stack[:3]):
            if (isinstance(node, ast.Call) and
                isinstance(node.func, ast.Attribute) and
                node.func.attr in ['debug', 'info', 'warning', 'error', 'critical']):
                return True
        return False

    def _looks_like_config(self, string_value: str) -> bool:
        """Check if string looks like a configuration value."""
        config_patterns = [
            r'[A-Z][A-Z_]+',  # UPPER_CASE
            r'[a-z]+[._][a-z]+',  # dot.notation or under_score
            r'--[a-z-]+',  # command line flags
            r'[a-z]+://.*',  # protocol schemes
        ]

        return any(re.match(pattern, string_value) for pattern in config_patterns)

    def _looks_like_path_or_url(self, string_value: str) -> bool:
        """Check if string looks like a file path or URL."""
        path_indicators = ['/', '\\', '.', 'http://', 'https://', 'ftp://', 'file://']
        return any(indicator in string_value for indicator in path_indicators)

    def _looks_like_user_message(self, string_value: str, context: LintContext) -> bool:
        """Check if string looks like a user-facing message."""
        # Check for complete sentences or error messages
        if (string_value.endswith('.') or string_value.endswith('!') or
            string_value.startswith('Error') or string_value.startswith('Warning')):
            return True

        # Check if in exception context
        if context.node_stack:
            for node in reversed(context.node_stack[:3]):
                if isinstance(node, ast.Raise):
                    return True

        return False

    def _looks_like_query(self, string_value: str) -> bool:
        """Check if string looks like a database query or similar."""
        query_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'FROM', 'WHERE', 'JOIN']
        return any(keyword in string_value.upper() for keyword in query_keywords)

    def _looks_like_api_related(self, string_value: str) -> bool:
        """Check if string looks like API-related content."""
        api_patterns = [
            r'/api/',
            r'/v\d+/',
            r'Bearer\s+',
            r'[a-z]+_key',
            r'[a-z]+_token',
            r'application/[a-z]+',
        ]

        return any(re.search(pattern, string_value, re.IGNORECASE) for pattern in api_patterns)

    def _generate_string_constant_suggestion(self, string_value: str, context: LintContext) -> str:
        """Generate an appropriate constant name suggestion for strings."""

        function_name = context.current_function or ""
        class_name = context.current_class or ""

        # Try to infer meaning from the string content
        if self._looks_like_config(string_value):
            return f"CONFIG_VALUE = '{string_value}'"
        elif self._looks_like_path_or_url(string_value):
            if 'http' in string_value:
                return f"API_ENDPOINT = '{string_value}'"
            else:
                return f"FILE_PATH = '{string_value}'"
        elif self._looks_like_user_message(string_value, context):
            if string_value.startswith('Error'):
                return f"ERROR_MESSAGE = '{string_value}'"
            elif string_value.startswith('Warning'):
                return f"WARNING_MESSAGE = '{string_value}'"
            else:
                return f"USER_MESSAGE = '{string_value}'"
        elif self._looks_like_query(string_value):
            return f"SQL_QUERY = '{string_value}'"

        # Generate based on context
        if function_name:
            if 'error' in function_name.lower() or 'exception' in function_name.lower():
                return f"ERROR_TEXT = '{string_value}'"
            elif 'message' in function_name.lower():
                return f"MESSAGE_TEXT = '{string_value}'"
            elif 'format' in function_name.lower():
                return f"FORMAT_STRING = '{string_value}'"

        # Generate based on content patterns
        if len(string_value) > 50:
            return f"LONG_TEXT = '{string_value[:30]}...'  # Consider extracting to config file"
        elif ' ' in string_value:
            words = string_value.upper().replace(' ', '_').replace('-', '_')
            # Limit length for readability
            if len(words) > 30:
                words = words[:30] + "_TEXT"
            return f"{words} = '{string_value}'"

        # Generic suggestion
        return f"STRING_CONSTANT = '{string_value}'  # Consider a more descriptive name"


class HardcodedPathRule(ASTLintRule):
    """Rule to detect hardcoded file paths that should be configurable."""

    @property
    def rule_id(self) -> str:
        return "literals.hardcoded-path"

    @property
    def rule_name(self) -> str:
        return "Hardcoded Path"

    @property
    def description(self) -> str:
        return "Hardcoded file paths should be configurable for better portability"

    @property
    def severity(self) -> Severity:
        return Severity.WARNING

    @property
    def categories(self) -> Set[str]:
        return {"literals", "paths", "configuration", "portability"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        return (isinstance(node, ast.Constant) and
                isinstance(node.value, str) and
                self._looks_like_absolute_path(node.value))

    def check_node(self, node: ast.Constant, context: LintContext) -> List[LintViolation]:
        path_value = node.value

        # Skip if in test context
        if 'test' in str(context.file_path).lower():
            return []

        suggestion = self._generate_path_constant_suggestion(path_value, context)

        return [LintViolation(
            rule_id=self.rule_id,
            file_path=str(context.file_path),
            line=node.lineno,
            column=node.col_offset,
            severity=self.severity,
            message=f"Hardcoded path '{path_value}' found",
            description="Hardcoded paths reduce portability - consider using configuration or relative paths",
            suggestion=suggestion,
            context={
                'path': path_value,
                'type': 'absolute' if path_value.startswith('/') else 'windows' if ':' in path_value else 'relative',
                'function': context.current_function,
                'class': context.current_class
            }
        )]

    def _looks_like_absolute_path(self, string_value: str) -> bool:
        """Check if string looks like an absolute file path."""
        # Unix absolute paths
        if string_value.startswith('/'):
            return True

        # Windows paths
        if re.match(r'[A-Za-z]:[/\\]', string_value):
            return True

        # UNC paths
        if string_value.startswith('\\\\'):
            return True

        return False

    def _generate_path_constant_suggestion(self, path_value: str, context: LintContext) -> str:
        """Generate suggestion for path constants."""

        if '/tmp/' in path_value or '\\temp\\' in path_value.lower():
            return f"TEMP_DIR = '{path_value}'  # Consider using tempfile module"
        elif '/log/' in path_value or 'log' in path_value.lower():
            return f"LOG_PATH = '{path_value}'  # Consider using logging configuration"
        elif '/config/' in path_value or 'config' in path_value.lower():
            return f"CONFIG_PATH = '{path_value}'  # Consider using environment variables"
        elif '/data/' in path_value or '/var/' in path_value:
            return f"DATA_PATH = '{path_value}'  # Consider using configuration file"
        else:
            return f"FILE_PATH = '{path_value}'  # Consider making this configurable"
