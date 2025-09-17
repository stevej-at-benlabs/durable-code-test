#!/usr/bin/env python3
"""
Purpose: Magic number detection rules for the pluggable framework
Scope: Framework-based implementation for numeric literal detection
Overview: This module provides rules for detecting magic numbers and complex
    numbers that should be replaced with named constants. It focuses on
    improving code maintainability by identifying hardcoded numeric values
    that should be extracted into meaningful constants.
Dependencies: Framework interfaces, AST analysis utilities
Exports: Numeric literal linting rules
Interfaces: All rules implement ASTLintRule interface
Implementation: Rule-based architecture with numeric pattern detection
"""

import ast
from typing import List, Set, Dict, Any

from ...framework.interfaces import ASTLintRule, LintViolation, LintContext, Severity


class MagicNumberRule(ASTLintRule):
    """Rule to detect magic numbers that should be replaced with named constants."""

    @property
    def rule_id(self) -> str:
        return "literals.magic-number"

    @property
    def rule_name(self) -> str:
        return "Magic Number"

    @property
    def description(self) -> str:
        return "Numeric literals should be replaced with named constants for better maintainability"

    @property
    def severity(self) -> Severity:
        return Severity.WARNING

    @property
    def categories(self) -> Set[str]:
        return {"literals", "constants", "maintainability"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        return isinstance(node, ast.Constant) and isinstance(node.value, (int, float))

    def check_node(self, node: ast.Constant, context: LintContext) -> List[LintViolation]:
        config = self.get_configuration(context.metadata or {})

        # Get allowed numbers from configuration
        allowed_numbers = config.get('allowed_numbers', {
            -1, 0, 1, 2, 10, 100, 1000, 1024
        })

        if node.value in allowed_numbers:
            return []

        # Check for specific contexts where numbers are acceptable
        if self._is_acceptable_context(node, context, config):
            return []

        # Generate appropriate suggestion
        suggestion = self._generate_constant_suggestion(node.value, context)

        return [LintViolation(
            rule_id=self.rule_id,
            file_path=str(context.file_path),
            line=node.lineno,
            column=node.col_offset,
            severity=self.severity,
            message=f"Magic number {node.value} found",
            description=f"Replace magic number {node.value} with a named constant for better maintainability",
            suggestion=suggestion,
            context={
                'value': node.value,
                'type': type(node.value).__name__,
                'function': context.current_function,
                'class': context.current_class
            }
        )]

    def _is_acceptable_context(self, node: ast.Constant, context: LintContext, config: Dict[str, Any]) -> bool:
        """Check if the number appears in an acceptable context."""

        # Allow in test files
        if 'test' in str(context.file_path).lower():
            return True

        # Allow in configuration contexts
        if context.current_function and any(word in context.current_function.lower()
                                           for word in ['config', 'setup', 'init']):
            return True

        # Allow small integers in range operations
        if (isinstance(node.value, int) and
            abs(node.value) <= config.get('max_acceptable_small_int', 10) and
            self._is_in_range_context(context)):
            return True

        # Allow in mathematical expressions with operators
        if self._is_in_math_context(context):
            return True

        return False

    def _is_in_range_context(self, context: LintContext) -> bool:
        """Check if the number is used in range() function or similar contexts."""
        if not context.node_stack or len(context.node_stack) < 2:
            return False

        # Check parent nodes
        for i in range(1, min(4, len(context.node_stack))):
            node = context.node_stack[-i-1] if i < len(context.node_stack) else None
            if node and isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in ['range', 'enumerate']:
                    return True
        return False

    def _is_in_math_context(self, context: LintContext) -> bool:
        """Check if the number is part of a mathematical operation."""
        if not context.node_stack or len(context.node_stack) < 2:
            return False

        # The parent is the second-to-last node (current node is last)
        parent = context.node_stack[-2]
        return isinstance(parent, (ast.BinOp, ast.UnaryOp, ast.Compare))

    def _generate_constant_suggestion(self, value: Any, context: LintContext) -> str:
        """Generate an appropriate constant name suggestion."""

        # Try to infer meaning from context
        function_name = context.current_function or ""
        class_name = context.current_class or ""

        # Common patterns
        if value == 60:
            return "SECONDS_PER_MINUTE = 60"
        elif value == 3600:
            return "SECONDS_PER_HOUR = 3600"
        elif value == 24:
            return "HOURS_PER_DAY = 24"
        elif value == 365:
            return "DAYS_PER_YEAR = 365"
        elif value == 1000:
            return "MILLISECONDS_PER_SECOND = 1000"
        elif isinstance(value, float) and 0 < value < 1:
            return f"THRESHOLD_VALUE = {value}"

        # Generate based on context
        if function_name:
            if 'timeout' in function_name.lower():
                return f"DEFAULT_TIMEOUT = {value}"
            elif 'retry' in function_name.lower():
                return f"MAX_RETRIES = {value}"
            elif 'size' in function_name.lower() or 'limit' in function_name.lower():
                return f"MAX_SIZE = {value}"
            elif 'port' in function_name.lower():
                return f"DEFAULT_PORT = {value}"

        # Generic suggestion
        if isinstance(value, int):
            return f"Consider extracting to a named constant: CONSTANT_NAME = {value}"
        else:
            return f"Consider extracting to a named constant: CONSTANT_NAME = {value}"


class MagicComplexRule(ASTLintRule):
    """Rule to detect magic complex numbers that should be replaced with named constants."""

    @property
    def rule_id(self) -> str:
        return "literals.magic-complex"

    @property
    def rule_name(self) -> str:
        return "Magic Complex Number"

    @property
    def description(self) -> str:
        return "Complex number literals should be replaced with named constants"

    @property
    def severity(self) -> Severity:
        return Severity.WARNING

    @property
    def categories(self) -> Set[str]:
        return {"literals", "constants", "complex", "maintainability"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        return isinstance(node, ast.Constant) and isinstance(node.value, complex)

    def check_node(self, node: ast.Constant, context: LintContext) -> List[LintViolation]:
        # Always flag complex numbers as they're usually domain-specific
        suggestion = self._generate_complex_constant_suggestion(node.value, context)

        return [LintViolation(
            rule_id=self.rule_id,
            file_path=str(context.file_path),
            line=node.lineno,
            column=node.col_offset,
            severity=self.severity,
            message=f"Magic complex number {node.value} found",
            description=f"Replace complex number {node.value} with a named constant for better readability",
            suggestion=suggestion,
            context={
                'value': str(node.value),
                'real': node.value.real,
                'imag': node.value.imag,
                'function': context.current_function,
                'class': context.current_class
            }
        )]

    def _generate_complex_constant_suggestion(self, value: complex, context: LintContext) -> str:
        """Generate an appropriate constant name suggestion for complex numbers."""

        function_name = context.current_function or ""

        # Common mathematical constants
        if abs(value - 1j) < 1e-10:
            return "IMAGINARY_UNIT = 1j"
        elif abs(value.real) < 1e-10 and abs(value.imag) > 0:
            return f"IMAGINARY_CONSTANT = {value}"
        elif abs(value.imag) < 1e-10 and abs(value.real) > 0:
            return f"REAL_CONSTANT = {value}"

        # Context-based suggestions
        if any(word in function_name.lower() for word in ['fourier', 'fft', 'frequency']):
            return f"FREQUENCY_COMPONENT = {value}"
        elif any(word in function_name.lower() for word in ['signal', 'wave']):
            return f"SIGNAL_CONSTANT = {value}"
        elif any(word in function_name.lower() for word in ['impedance', 'electrical']):
            return f"IMPEDANCE_VALUE = {value}"

        # Generic suggestion
        return f"COMPLEX_CONSTANT = {value}  # Consider a more descriptive name"
