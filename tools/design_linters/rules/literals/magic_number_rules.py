#!/usr/bin/env python3
# design-lint: ignore-file[literals.*]
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
from typing import Any

from design_linters.framework.interfaces import ASTLintRule, LintContext, LintViolation, Severity


class MagicNumberRule(ASTLintRule):
    """Rule to detect magic numbers that should be replaced with named constants."""

    # Common time constants
    SECONDS_PER_MINUTE = 60  # design-lint: ignore[literals.magic-number]
    SECONDS_PER_HOUR = 3600  # design-lint: ignore[literals.magic-number]
    HOURS_PER_DAY = 24  # design-lint: ignore[literals.magic-number]
    DAYS_PER_YEAR = 365  # design-lint: ignore[literals.magic-number]
    MILLISECONDS_PER_SECOND = 1000  # design-lint: ignore[literals.magic-number]

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
    def categories(self) -> set[str]:
        return {"literals", "constants", "maintainability"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        return isinstance(node, ast.Constant) and isinstance(node.value, (int, float))

    def check_node(self, node: ast.AST, context: LintContext) -> list[LintViolation]:
        if not isinstance(node, ast.Constant):
            raise TypeError("MagicNumberRule should only receive ast.Constant nodes")
        # Ensure we have a numeric value
        if not isinstance(node.value, (int, float)):
            return []
        config = self.get_configuration(context.metadata or {})

        # Get allowed numbers from configuration
        allowed_numbers = config.get("allowed_numbers", {-1, 0, 1, 2, 10, 100, 1000, 1024})

        if node.value in allowed_numbers:
            return []

        # Check for specific contexts where numbers are acceptable
        if self._is_acceptable_context(node, context, config):
            return []

        # Generate appropriate suggestion
        suggestion = self._generate_constant_suggestion(node.value, context)

        return [
            self.create_violation(
                context=context,
                node=node,
                message=f"Magic number {node.value} found",
                description=f"Replace magic number {node.value} with a named constant for better maintainability",
                suggestion=suggestion,
                violation_context={
                    "value": node.value,
                    "type": type(node.value).__name__,
                    "function": context.current_function,
                    "class": context.current_class,
                },
            )
        ]

    def _is_acceptable_context(self, node: ast.Constant, context: LintContext, config: dict[str, Any]) -> bool:
        """Check if the number appears in an acceptable context."""
        if self._is_test_file(context):
            return True

        if self._is_configuration_context(context):
            return True

        if self._is_constant_definition(node, context):
            return True

        if self._is_small_integer_in_range(node, context, config):
            return True

        return self._is_in_math_context(context)

    def _is_test_file(self, context: LintContext) -> bool:
        """Check if current file is a test file."""
        return "test" in str(context.file_path).lower()

    def _is_configuration_context(self, context: LintContext) -> bool:
        """Check if current context is configuration-related."""
        if not context.current_function:
            return False
        return any(word in context.current_function.lower() for word in ["config", "setup", "init"])

    def _is_small_integer_in_range(self, node: ast.Constant, context: LintContext, config: dict[str, Any]) -> bool:
        """Check if number is a small integer used in range context."""
        if not isinstance(node.value, int):
            return False

        max_small_int = config.get("max_acceptable_small_int", 10)
        return abs(node.value) <= max_small_int and self._is_in_range_context(context)

    def _is_in_range_context(self, context: LintContext) -> bool:
        """Check if the number is used in range() function or similar contexts."""
        if not self._has_sufficient_context(context):
            return False

        return self._check_range_functions_in_stack(context)

    def _has_sufficient_context(self, context: LintContext) -> bool:
        """Check if context has sufficient node stack for analysis."""
        return bool(context.node_stack and len(context.node_stack) >= 2)

    def _check_range_functions_in_stack(self, context: LintContext) -> bool:
        """Check if any parent nodes are range-like function calls."""
        if not context.node_stack:
            return False

        for i in range(1, min(4, len(context.node_stack))):
            index = -i
            if abs(index) <= len(context.node_stack):
                node = context.node_stack[index]
                if self._is_range_like_call(node):
                    return True
        return False

    def _is_range_like_call(self, node: ast.AST) -> bool:
        """Check if node is a range-like function call."""
        return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ["range", "enumerate"]

    def _is_constant_name(self, name: str, context: LintContext) -> bool:
        """Check if a name follows constant naming conventions."""
        if name.isupper() or name.startswith("DEFAULT_"):
            return True
        return bool(context.current_class and name and name[0].isupper())

    def _is_constant_definition(self, _node: ast.Constant, context: LintContext) -> bool:
        """Check if this number is part of a constant definition (ALL_CAPS variable)."""
        if not context.node_stack or len(context.node_stack) < 2:
            return False

        parent = context.node_stack[-2]
        if not isinstance(parent, ast.Assign) or context.current_function:
            return False

        return any(
            isinstance(target, ast.Name) and self._is_constant_name(target.id, context) for target in parent.targets
        )

    def _is_in_math_context(self, context: LintContext) -> bool:
        """Check if the number is part of a mathematical operation."""
        if not context.node_stack or len(context.node_stack) < 2:
            return False

        # The parent is the second-to-last node (current node is last)
        parent = context.node_stack[-2]
        return isinstance(parent, (ast.BinOp, ast.UnaryOp, ast.Compare))

    def _generate_constant_suggestion(self, value: Any, context: LintContext) -> str:
        """Generate an appropriate constant name suggestion."""
        function_name = context.current_function or ""

        suggestion = (
            self._get_common_pattern_suggestion(value)
            or self._get_context_based_suggestion(value, function_name)
            or self._get_generic_suggestion(value)
        )

        return suggestion

    def _get_generic_suggestion(self, value: Any) -> str:
        """Get generic constant suggestion."""
        return f"Consider extracting to a named constant: CONSTANT_NAME = {value}"

    def _get_common_pattern_suggestion(self, value: Any) -> str:
        """Get suggestion for common time/mathematical patterns."""
        common_patterns = {
            self.SECONDS_PER_MINUTE: "SECONDS_PER_MINUTE = 60",
            self.SECONDS_PER_HOUR: "SECONDS_PER_HOUR = 3600",
            self.HOURS_PER_DAY: "HOURS_PER_DAY = 24",
            self.DAYS_PER_YEAR: "DAYS_PER_YEAR = 365",
            self.MILLISECONDS_PER_SECOND: "MILLISECONDS_PER_SECOND = 1000",
        }

        if value in common_patterns:
            return common_patterns[value]

        if isinstance(value, float) and 0 < value < 1:
            return f"THRESHOLD_VALUE = {value}"

        return ""

    def _get_context_based_suggestion(self, value: Any, function_name: str) -> str:
        """Get suggestion based on function context."""
        if not function_name:
            return ""

        lower_func_name = function_name.lower()
        suggestion = self._check_specific_patterns(value, lower_func_name)
        if suggestion:
            return suggestion

        return self._check_size_patterns(value, lower_func_name)

    def _check_specific_patterns(self, value: Any, lower_func_name: str) -> str:
        """Check for specific context patterns."""
        context_patterns = {
            "timeout": f"DEFAULT_TIMEOUT = {value}",
            "retry": f"MAX_RETRIES = {value}",
            "port": f"DEFAULT_PORT = {value}",
        }

        for pattern, suggestion in context_patterns.items():
            if pattern in lower_func_name:
                return suggestion
        return ""

    def _check_size_patterns(self, value: Any, lower_func_name: str) -> str:
        """Check for size-related patterns."""
        if "size" in lower_func_name or "limit" in lower_func_name:
            return f"MAX_SIZE = {value}"
        return ""


class MagicComplexRule(ASTLintRule):
    """Rule to detect magic complex numbers that should be replaced with named constants."""

    # Mathematical constants
    IMAGINARY_UNIT = 1j  # design-lint: ignore[literals.magic-complex]

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
    def categories(self) -> set[str]:
        return {"literals", "constants", "complex", "maintainability"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        return isinstance(node, ast.Constant) and isinstance(node.value, complex)

    def check_node(self, node: ast.AST, context: LintContext) -> list[LintViolation]:
        if not isinstance(node, ast.Constant):
            raise TypeError("MagicComplexRule should only receive ast.Constant nodes")
        # Ensure we have a complex value
        if not isinstance(node.value, complex):
            return []

        # Skip test files
        if self._is_test_file(context):
            return []

        # Check if this is a constant definition
        if self._is_constant_definition(node, context):
            return []

        # Always flag complex numbers as they're usually domain-specific
        suggestion = self._generate_complex_constant_suggestion(node.value, context)

        return [
            self.create_violation(
                context=context,
                node=node,
                message=f"Magic complex number {node.value} found",
                description=f"Replace complex number {node.value} with a named constant for better readability",
                suggestion=suggestion,
                violation_context={
                    "value": str(node.value),
                    "real": node.value.real,
                    "imag": node.value.imag,
                    "function": context.current_function,
                    "class": context.current_class,
                },
            )
        ]

    def _generate_complex_constant_suggestion(self, value: complex, context: LintContext) -> str:
        """Generate an appropriate constant name suggestion for complex numbers."""
        function_name = context.current_function or ""

        suggestion = (
            self._get_complex_math_suggestion(value)
            or self._get_complex_context_suggestion(value, function_name)
            or self._get_generic_complex_suggestion(value)
        )

        return suggestion

    def _get_generic_complex_suggestion(self, value: complex) -> str:
        """Get generic suggestion for complex constants."""
        return f"COMPLEX_CONSTANT = {value}  # Consider a more descriptive name"

    def _get_complex_math_suggestion(self, value: complex) -> str:
        """Get suggestion for common complex mathematical constants."""
        if abs(value - self.IMAGINARY_UNIT) < 1e-10:
            return "IMAGINARY_UNIT = 1j"
        if abs(value.real) < 1e-10 and abs(value.imag) > 0:
            return f"IMAGINARY_CONSTANT = {value}"
        if abs(value.imag) < 1e-10 and abs(value.real) > 0:
            return f"REAL_CONSTANT = {value}"
        return ""

    def _get_complex_context_suggestion(self, value: complex, function_name: str) -> str:
        """Get suggestion based on function context for complex numbers."""
        if not function_name:
            return ""

        lower_func_name = function_name.lower()
        if any(word in lower_func_name for word in ["fourier", "fft", "frequency"]):
            return f"FREQUENCY_COMPONENT = {value}"
        if any(word in lower_func_name for word in ["signal", "wave"]):
            return f"SIGNAL_CONSTANT = {value}"
        if any(word in lower_func_name for word in ["impedance", "electrical"]):
            return f"IMPEDANCE_VALUE = {value}"
        return ""

    def _is_complex_constant_name(self, name: str, context: LintContext) -> bool:
        """Check if a name follows complex constant naming conventions."""
        if name.isupper():
            return True
        if "_" in name and name.replace("_", "").isupper():
            return True
        return bool(context.current_class and name and name[0].isupper())

    def _is_constant_definition(self, _node: ast.Constant, context: LintContext) -> bool:
        """Check if this complex number is part of a constant definition."""
        if not context.node_stack or len(context.node_stack) < 2:
            return False

        parent = context.node_stack[-2]
        if not isinstance(parent, ast.Assign) or context.current_function:
            return False

        return any(
            isinstance(target, ast.Name) and self._is_complex_constant_name(target.id, context)
            for target in parent.targets
        )

    def _is_test_file(self, context: LintContext) -> bool:
        """Check if current file is a test file."""
        if not context.file_path:
            return False
        path_str = str(context.file_path).lower()
        return "test" in path_str or "spec" in path_str
