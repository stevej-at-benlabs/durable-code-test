#!/usr/bin/env python3
# design-lint: ignore-file[literals.*]
"""
Purpose: Comprehensive unit tests for magic number detection rules
Scope: Test MagicNumberRule and MagicComplexRule classes
Overview: This module provides comprehensive test coverage for the magic number
    detection rules, including rule properties, node checking behavior, configuration
    handling, context-based exceptions, and suggestion generation.
Dependencies: unittest, ast, pathlib, framework interfaces
Exports: Test classes for magic number rules
Interfaces: Uses unittest.TestCase for test structure
Implementation: Production-ready tests with edge cases and error conditions
"""

import ast
import sys
import unittest
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, "/home/stevejackson/Projects/durable-code-test/tools")

from design_linters.framework.interfaces import LintContext, LintViolation, Severity
from design_linters.rules.literals.magic_number_rules import MagicComplexRule, MagicNumberRule


class TestMagicNumberRule(unittest.TestCase):
    """Test cases for MagicNumberRule class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.rule = MagicNumberRule()
        self.context = LintContext(file_path=Path("/example.py"), node_stack=[])

    def test_rule_properties(self):
        """Test that rule properties return expected values."""
        self.assertEqual(self.rule.rule_id, "literals.magic-number")
        self.assertEqual(self.rule.rule_name, "Magic Number")
        self.assertEqual(
            self.rule.description, "Numeric literals should be replaced with named constants for better maintainability"
        )
        self.assertEqual(self.rule.severity, Severity.WARNING)
        self.assertEqual(self.rule.categories, {"literals", "constants", "maintainability"})

    def test_should_check_node_with_integer_constant(self):
        """Test should_check_node returns True for integer constants."""
        node = ast.Constant(value=42)
        result = self.rule.should_check_node(node, self.context)
        self.assertTrue(result)

    def test_should_check_node_with_float_constant(self):
        """Test should_check_node returns True for float constants."""
        node = ast.Constant(value=3.14)
        result = self.rule.should_check_node(node, self.context)
        self.assertTrue(result)

    def test_should_check_node_with_string_constant(self):
        """Test should_check_node returns False for string constants."""
        node = ast.Constant(value="hello")
        result = self.rule.should_check_node(node, self.context)
        self.assertFalse(result)

    def test_should_check_node_with_complex_constant(self):
        """Test should_check_node returns False for complex constants."""
        node = ast.Constant(value=1 + 2j)
        result = self.rule.should_check_node(node, self.context)
        self.assertFalse(result)

    def test_should_check_node_with_non_constant(self):
        """Test should_check_node returns False for non-constant nodes."""
        node = ast.Name(id="x", ctx=ast.Load())
        result = self.rule.should_check_node(node, self.context)
        self.assertFalse(result)

    def test_check_node_with_allowed_number(self):
        """Test check_node returns no violations for allowed numbers."""
        # Test default allowed numbers
        allowed_values = [-1, 0, 1, 2, 10, 100, 1000, 1024]
        for value in allowed_values:
            with self.subTest(value=value):
                node = ast.Constant(value=value)
                violations = self.rule.check_node(node, self.context)
                self.assertEqual(len(violations), 0)

    def test_check_node_with_disallowed_number(self):
        """Test check_node returns violation for disallowed numbers."""
        # Set up context that won't trigger acceptable context exceptions
        self.context.file_path = Path("/src/main.py")  # Not a test file
        self.context.current_function = "normal_function"  # Not config/setup/init
        self.context.node_stack = [ast.Constant(value=42)]  # Not in range or math context

        node = ast.Constant(value=42)
        violations = self.rule.check_node(node, self.context)

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation.rule_id, "literals.magic-number")
        self.assertEqual(violation.message, "Magic number 42 found")
        self.assertIn("Replace magic number 42", violation.description)
        self.assertEqual(violation.severity, Severity.WARNING)
        self.assertIsNotNone(violation.suggestion)

    def test_check_node_with_custom_allowed_numbers(self):
        """Test check_node respects custom allowed numbers configuration."""
        # Set up context that won't trigger acceptable context exceptions
        self.context.file_path = Path("/src/main.py")  # Not a test file
        self.context.current_function = "normal_function"  # Not config/setup/init
        self.context.node_stack = [ast.Constant(value=42)]  # Not in range or math context

        # Configure context with custom allowed numbers
        self.context.metadata = {"rules": {"literals.magic-number": {"config": {"allowed_numbers": {42, 100}}}}}

        node = ast.Constant(value=42)
        violations = self.rule.check_node(node, self.context)
        self.assertEqual(len(violations), 0)

        # Also test with non-allowed number in same context
        self.context.node_stack = [ast.Constant(value=50)]  # Update stack for new node
        node = ast.Constant(value=50)
        violations = self.rule.check_node(node, self.context)
        self.assertEqual(len(violations), 1)

    def test_check_node_with_non_numeric_value(self):
        """Test check_node handles non-numeric values gracefully."""
        node = ast.Constant(value="not a number")
        violations = self.rule.check_node(node, self.context)
        self.assertEqual(len(violations), 0)

    def test_check_node_type_error(self):
        """Test check_node raises TypeError for non-constant nodes."""
        node = ast.Name(id="x", ctx=ast.Load())
        with self.assertRaises(TypeError):
            self.rule.check_node(node, self.context)

    def test_is_acceptable_context_test_file(self):
        """Test numbers are acceptable in test files."""
        test_context = LintContext(file_path=Path("/test_module.py"))
        node = ast.Constant(value=42)
        config = {}

        result = self.rule._is_acceptable_context(node, test_context, config)
        self.assertTrue(result)

    def test_is_acceptable_context_config_function(self):
        """Test numbers are acceptable in configuration functions."""
        self.context.current_function = "setup_config"
        node = ast.Constant(value=42)
        config = {}

        result = self.rule._is_acceptable_context(node, self.context, config)
        self.assertTrue(result)

    def test_is_acceptable_context_init_function(self):
        """Test numbers are acceptable in init functions."""
        self.context.current_function = "__init__"
        node = ast.Constant(value=42)
        config = {}

        result = self.rule._is_acceptable_context(node, self.context, config)
        self.assertTrue(result)

    def test_is_acceptable_context_small_int_in_range(self):
        """Test small integers are acceptable in range contexts."""
        # Set up context with range function in node stack
        node = ast.Constant(value=5)
        range_node = ast.Call(func=ast.Name(id="range", ctx=ast.Load()), args=[node], keywords=[])
        # Need at least 3 nodes for range context detection (dummy, range, constant)
        dummy_node = ast.Module(body=[], type_ignores=[])
        self.context.node_stack = [dummy_node, range_node, node]
        config = {"max_acceptable_small_int": 10}

        result = self.rule._is_acceptable_context(node, self.context, config)
        self.assertTrue(result)

    def test_is_acceptable_context_math_operation(self):
        """Test numbers are acceptable in mathematical operations."""
        # Set up context with binary operation in node stack
        node = ast.Constant(value=42)
        binop_node = ast.BinOp(left=ast.Name(id="x", ctx=ast.Load()), op=ast.Add(), right=node)
        self.context.node_stack = [binop_node, node]
        config = {}

        result = self.rule._is_acceptable_context(node, self.context, config)
        self.assertTrue(result)

    def test_is_acceptable_context_normal_case(self):
        """Test numbers are not acceptable in normal contexts."""
        # Set up context that doesn't match any exception patterns
        self.context.file_path = Path("/src/main.py")  # Not a test file
        self.context.current_function = "normal_function"  # Not config/setup/init
        self.context.node_stack = [ast.Constant(value=42)]  # Not in range or math context

        node = ast.Constant(value=42)
        config = {}

        result = self.rule._is_acceptable_context(node, self.context, config)
        self.assertFalse(result)

    def test_is_in_range_context_with_range_call(self):
        """Test detection of range function context."""
        # Create range call node and build proper stack
        constant_node = ast.Constant(value=5)
        range_node = ast.Call(func=ast.Name(id="range", ctx=ast.Load()), args=[constant_node], keywords=[])
        # The stack should have nodes in order, with current node at the end
        # For _is_in_range_context to find the range call at index -2, we need the range call as parent
        dummy_node = ast.Module(body=[], type_ignores=[])
        self.context.node_stack = [dummy_node, range_node, constant_node]

        result = self.rule._is_in_range_context(self.context)
        self.assertTrue(result)

    def test_is_in_range_context_with_enumerate_call(self):
        """Test detection of enumerate function context."""
        constant_node = ast.Constant(value=1)
        enum_node = ast.Call(func=ast.Name(id="enumerate", ctx=ast.Load()), args=[constant_node], keywords=[])
        # Need at least 3 nodes for the algorithm to find the enumerate call at index -2
        dummy_node = ast.Module(body=[], type_ignores=[])
        self.context.node_stack = [dummy_node, enum_node, constant_node]

        result = self.rule._is_in_range_context(self.context)
        self.assertTrue(result)

    def test_is_in_range_context_empty_stack(self):
        """Test range context detection with empty node stack."""
        self.context.node_stack = []

        result = self.rule._is_in_range_context(self.context)
        self.assertFalse(result)

    def test_is_in_range_context_shallow_stack(self):
        """Test range context detection with shallow node stack."""
        self.context.node_stack = [ast.Constant(value=5)]

        result = self.rule._is_in_range_context(self.context)
        self.assertFalse(result)

    def test_is_in_math_context_with_binop(self):
        """Test detection of binary operation context."""
        constant_node = ast.Constant(value=42)
        binop_node = ast.BinOp(left=ast.Name(id="x", ctx=ast.Load()), op=ast.Add(), right=constant_node)
        # Stack should have binop as parent of constant (binop at -2, constant at -1)
        self.context.node_stack = [binop_node, constant_node]

        result = self.rule._is_in_math_context(self.context)
        self.assertTrue(result)

    def test_is_in_math_context_with_unaryop(self):
        """Test detection of unary operation context."""
        constant_node = ast.Constant(value=42)
        unaryop_node = ast.UnaryOp(op=ast.USub(), operand=constant_node)
        # Stack should have unaryop as parent of constant
        self.context.node_stack = [unaryop_node, constant_node]

        result = self.rule._is_in_math_context(self.context)
        self.assertTrue(result)

    def test_is_in_math_context_with_compare(self):
        """Test detection of comparison context."""
        constant_node = ast.Constant(value=42)
        compare_node = ast.Compare(left=ast.Name(id="x", ctx=ast.Load()), ops=[ast.Lt()], comparators=[constant_node])
        # Stack should have compare as parent of constant
        self.context.node_stack = [compare_node, constant_node]

        result = self.rule._is_in_math_context(self.context)
        self.assertTrue(result)

    def test_is_in_math_context_empty_stack(self):
        """Test math context detection with empty node stack."""
        self.context.node_stack = []

        result = self.rule._is_in_math_context(self.context)
        self.assertFalse(result)

    def test_is_in_math_context_no_math_parent(self):
        """Test math context detection with non-math parent."""
        constant_node = ast.Constant(value=42)
        assign_node = ast.Assign(targets=[ast.Name(id="x", ctx=ast.Store())], value=constant_node)
        # Stack should have assign as parent of constant
        self.context.node_stack = [assign_node, constant_node]

        result = self.rule._is_in_math_context(self.context)
        self.assertFalse(result)

    def test_generate_constant_suggestion_common_patterns(self):
        """Test suggestion generation for common time/mathematical patterns."""
        test_cases = [
            (60, "SECONDS_PER_MINUTE = 60"),
            (3600, "SECONDS_PER_HOUR = 3600"),
            (24, "HOURS_PER_DAY = 24"),
            (365, "DAYS_PER_YEAR = 365"),
            (1000, "MILLISECONDS_PER_SECOND = 1000"),
            (0.5, "THRESHOLD_VALUE = 0.5"),
            (0.1, "THRESHOLD_VALUE = 0.1"),
        ]

        for value, expected in test_cases:
            with self.subTest(value=value):
                result = self.rule._generate_constant_suggestion(value, self.context)
                self.assertEqual(result, expected)

    def test_generate_constant_suggestion_context_based(self):
        """Test suggestion generation based on function context."""
        test_cases = [
            ("setup_timeout", 30, "DEFAULT_TIMEOUT = 30"),
            ("retry_logic", 5, "MAX_RETRIES = 5"),
            ("connect_port", 8080, "DEFAULT_PORT = 8080"),
            ("buffer_size", 1024, "MAX_SIZE = 1024"),
            ("memory_limit", 512, "MAX_SIZE = 512"),
        ]

        for func_name, value, expected in test_cases:
            with self.subTest(func_name=func_name, value=value):
                self.context.current_function = func_name
                result = self.rule._generate_constant_suggestion(value, self.context)
                self.assertEqual(result, expected)

    def test_generate_constant_suggestion_generic(self):
        """Test generic suggestion generation."""
        value = 987
        result = self.rule._generate_constant_suggestion(value, self.context)
        self.assertEqual(result, "Consider extracting to a named constant: CONSTANT_NAME = 987")

    def test_get_common_pattern_suggestion_unknown_value(self):
        """Test common pattern suggestion for unknown values."""
        result = self.rule._get_common_pattern_suggestion(999)
        self.assertEqual(result, "")

    def test_get_context_based_suggestion_no_function(self):
        """Test context-based suggestion with no function context."""
        result = self.rule._get_context_based_suggestion(42, "")
        self.assertEqual(result, "")

    def test_violation_context_information(self):
        """Test that violations contain proper context information."""
        # Set up context that won't trigger acceptable context exceptions
        self.context.file_path = Path("/src/main.py")  # Not a test file
        self.context.current_function = "normal_function"  # Not config/setup/init
        self.context.current_class = "TestClass"
        self.context.node_stack = [ast.Constant(value=42)]  # Not in range or math context

        node = ast.Constant(value=42)
        violations = self.rule.check_node(node, self.context)

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        context_info = violation.context

        self.assertIsNotNone(context_info)
        self.assertEqual(context_info["value"], 42)
        self.assertEqual(context_info["type"], "int")
        self.assertEqual(context_info["function"], "normal_function")
        self.assertEqual(context_info["class"], "TestClass")


class TestMagicComplexRule(unittest.TestCase):
    """Test cases for MagicComplexRule class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.rule = MagicComplexRule()
        self.context = LintContext(file_path=Path("/example.py"), node_stack=[])

    def test_rule_properties(self):
        """Test that rule properties return expected values."""
        self.assertEqual(self.rule.rule_id, "literals.magic-complex")
        self.assertEqual(self.rule.rule_name, "Magic Complex Number")
        self.assertEqual(self.rule.description, "Complex number literals should be replaced with named constants")
        self.assertEqual(self.rule.severity, Severity.WARNING)
        self.assertEqual(self.rule.categories, {"literals", "constants", "complex", "maintainability"})

    def test_should_check_node_with_complex_constant(self):
        """Test should_check_node returns True for complex constants."""
        node = ast.Constant(value=1 + 2j)
        result = self.rule.should_check_node(node, self.context)
        self.assertTrue(result)

    def test_should_check_node_with_pure_imaginary(self):
        """Test should_check_node returns True for pure imaginary numbers."""
        node = ast.Constant(value=1j)
        result = self.rule.should_check_node(node, self.context)
        self.assertTrue(result)

    def test_should_check_node_with_integer_constant(self):
        """Test should_check_node returns False for integer constants."""
        node = ast.Constant(value=42)
        result = self.rule.should_check_node(node, self.context)
        self.assertFalse(result)

    def test_should_check_node_with_float_constant(self):
        """Test should_check_node returns False for float constants."""
        node = ast.Constant(value=3.14)
        result = self.rule.should_check_node(node, self.context)
        self.assertFalse(result)

    def test_should_check_node_with_string_constant(self):
        """Test should_check_node returns False for string constants."""
        node = ast.Constant(value="hello")
        result = self.rule.should_check_node(node, self.context)
        self.assertFalse(result)

    def test_check_node_with_complex_number(self):
        """Test check_node returns violation for complex numbers."""
        node = ast.Constant(value=3 + 4j)
        violations = self.rule.check_node(node, self.context)

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation.rule_id, "literals.magic-complex")
        self.assertEqual(violation.message, "Magic complex number (3+4j) found")
        self.assertIn("Replace complex number (3+4j)", violation.description)
        self.assertEqual(violation.severity, Severity.WARNING)
        self.assertIsNotNone(violation.suggestion)

    def test_check_node_with_pure_imaginary(self):
        """Test check_node handles pure imaginary numbers correctly."""
        node = ast.Constant(value=5j)
        violations = self.rule.check_node(node, self.context)

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation.message, "Magic complex number 5j found")

    def test_check_node_with_non_complex_value(self):
        """Test check_node handles non-complex values gracefully."""
        node = ast.Constant(value=42)
        violations = self.rule.check_node(node, self.context)
        self.assertEqual(len(violations), 0)

    def test_check_node_type_error(self):
        """Test check_node raises TypeError for non-constant nodes."""
        node = ast.Name(id="x", ctx=ast.Load())
        with self.assertRaises(TypeError):
            self.rule.check_node(node, self.context)

    def test_generate_complex_constant_suggestion_imaginary_unit(self):
        """Test suggestion generation for imaginary unit."""
        result = self.rule._generate_complex_constant_suggestion(1j, self.context)
        self.assertEqual(result, "IMAGINARY_UNIT = 1j")

    def test_generate_complex_constant_suggestion_pure_imaginary(self):
        """Test suggestion generation for pure imaginary numbers."""
        result = self.rule._generate_complex_constant_suggestion(5j, self.context)
        self.assertEqual(result, "IMAGINARY_CONSTANT = 5j")

    def test_generate_complex_constant_suggestion_pure_real(self):
        """Test suggestion generation for complex numbers with zero imaginary part."""
        result = self.rule._generate_complex_constant_suggestion(5 + 0j, self.context)
        self.assertEqual(result, "REAL_CONSTANT = (5+0j)")

    def test_generate_complex_constant_suggestion_fourier_context(self):
        """Test suggestion generation in Fourier analysis context."""
        self.context.current_function = "fourier_transform"
        result = self.rule._generate_complex_constant_suggestion(2 + 3j, self.context)
        self.assertEqual(result, "FREQUENCY_COMPONENT = (2+3j)")

    def test_generate_complex_constant_suggestion_signal_context(self):
        """Test suggestion generation in signal processing context."""
        self.context.current_function = "process_signal"
        result = self.rule._generate_complex_constant_suggestion(1 + 1j, self.context)
        self.assertEqual(result, "SIGNAL_CONSTANT = (1+1j)")

    def test_generate_complex_constant_suggestion_impedance_context(self):
        """Test suggestion generation in electrical engineering context."""
        self.context.current_function = "calculate_impedance"
        result = self.rule._generate_complex_constant_suggestion(50 + 25j, self.context)
        self.assertEqual(result, "IMPEDANCE_VALUE = (50+25j)")

    def test_generate_complex_constant_suggestion_generic(self):
        """Test generic suggestion generation for complex numbers."""
        result = self.rule._generate_complex_constant_suggestion(7 + 8j, self.context)
        self.assertEqual(result, "COMPLEX_CONSTANT = (7+8j)  # Consider a more descriptive name")

    def test_get_complex_math_suggestion_edge_cases(self):
        """Test math suggestion for edge cases."""
        # Very close to 1j but not exactly - this should not be treated as exactly 1j
        # The tolerance check in the code uses 1e-10, so 1.0000000001j is outside that
        result = self.rule._get_complex_math_suggestion(1.0000000001j)
        self.assertEqual(result, "IMAGINARY_CONSTANT = 1.0000000001j")

        # Complex number that's very close to real
        result = self.rule._get_complex_math_suggestion(5.0 + 1e-15j)
        self.assertEqual(result, "REAL_CONSTANT = (5+1e-15j)")

    def test_get_complex_context_suggestion_no_function(self):
        """Test context-based suggestion with no function context."""
        result = self.rule._get_complex_context_suggestion(1 + 2j, "")
        self.assertEqual(result, "")

    def test_get_complex_context_suggestion_unrecognized_context(self):
        """Test context-based suggestion with unrecognized function name."""
        result = self.rule._get_complex_context_suggestion(1 + 2j, "random_function")
        self.assertEqual(result, "")

    def test_violation_context_information(self):
        """Test that violations contain proper context information."""
        self.context.current_function = "complex_function"
        self.context.current_class = "ComplexClass"
        node = ast.Constant(value=3 + 4j)
        violations = self.rule.check_node(node, self.context)

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        context_info = violation.context

        self.assertIsNotNone(context_info)
        self.assertEqual(context_info["value"], "(3+4j)")
        self.assertEqual(context_info["real"], 3.0)
        self.assertEqual(context_info["imag"], 4.0)
        self.assertEqual(context_info["function"], "complex_function")
        self.assertEqual(context_info["class"], "ComplexClass")


class TestMagicNumberRuleIntegration(unittest.TestCase):
    """Integration tests for magic number rules with AST parsing."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = MagicNumberRule()

    def test_real_code_analysis(self):
        """Test rule behavior with real Python code snippets."""
        code_snippets = [
            # Should trigger violation (use non-test file path)
            ("x = 42", True, Path("/src/main.py")),
            ("timeout = 30", True, Path("/src/main.py")),
            ("buffer_size = 8192", True, Path("/src/main.py")),
            # Should not trigger violation (allowed numbers)
            ("x = 0", False, Path("/src/main.py")),
            ("y = 1", False, Path("/src/main.py")),
            ("z = -1", False, Path("/src/main.py")),
            # Should not trigger violation (test file)
            ("x = 42", False, Path("/tests/test_module.py")),
        ]

        for code, should_violate, file_path in code_snippets:
            with self.subTest(code=code):
                tree = ast.parse(code)
                context = LintContext(file_path=file_path, ast_tree=tree, file_content=code, node_stack=[])

                violations = self.rule.check(context)
                if should_violate:
                    self.assertGreater(len(violations), 0, f"Expected violation for: {code}")
                else:
                    self.assertEqual(len(violations), 0, f"Unexpected violation for: {code}")

    def test_range_context_integration(self):
        """Test that numbers in range contexts are properly handled."""
        code = "for i in range(10): pass"
        tree = ast.parse(code)
        context = LintContext(file_path=Path("/test.py"), ast_tree=tree, node_stack=[])

        violations = self.rule.check(context)
        # The 10 in range(10) should not trigger a violation
        self.assertEqual(len(violations), 0)

    def test_math_operation_integration(self):
        """Test that numbers in math operations are properly handled."""
        code = "result = x + 42 * 2"
        tree = ast.parse(code)
        context = LintContext(file_path=Path("/src/main.py"), ast_tree=tree, node_stack=[])

        violations = self.rule.check(context)
        # Numbers in math operations should not trigger violations
        self.assertEqual(len(violations), 0)


class TestMagicComplexRuleIntegration(unittest.TestCase):
    """Integration tests for magic complex number rules with AST parsing."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = MagicComplexRule()

    def test_real_code_analysis(self):
        """Test rule behavior with real Python code containing complex numbers."""
        code_snippets = [
            # Should trigger violations
            "z = 3+4j",
            "impedance = 50+25j",
            "frequency_response = 1j",
            "signal = 2-3j",
        ]

        for code in code_snippets:
            with self.subTest(code=code):
                tree = ast.parse(code)
                context = LintContext(file_path=Path("/src/main.py"), ast_tree=tree, file_content=code, node_stack=[])

                violations = self.rule.check(context)
                self.assertGreater(len(violations), 0, f"Expected violation for: {code}")

    def test_complex_math_operations(self):
        """Test complex numbers in mathematical operations."""
        code = "result = (2+3j) * (1-1j)"
        tree = ast.parse(code)
        context = LintContext(file_path=Path("/src/main.py"), ast_tree=tree, file_content=code, node_stack=[])

        violations = self.rule.check(context)
        # All complex literals should trigger violations
        self.assertEqual(len(violations), 2)


class TestEdgeCasesAndErrorConditions(unittest.TestCase):
    """Test edge cases and error conditions for both rules."""

    def test_magic_number_rule_with_none_context(self):
        """Test MagicNumberRule behavior with minimal context."""
        rule = MagicNumberRule()
        context = LintContext()
        node = ast.Constant(value=42)

        violations = rule.check_node(node, context)
        self.assertEqual(len(violations), 1)

    def test_magic_complex_rule_with_none_context(self):
        """Test MagicComplexRule behavior with minimal context."""
        rule = MagicComplexRule()
        context = LintContext()
        node = ast.Constant(value=1 + 2j)

        violations = rule.check_node(node, context)
        self.assertEqual(len(violations), 1)

    def test_configuration_handling_edge_cases(self):
        """Test configuration handling with various edge cases."""
        rule = MagicNumberRule()

        # Test with None metadata
        context = LintContext(metadata=None)
        config = rule.get_configuration(context.metadata)
        self.assertEqual(config, {})

        # Test with empty metadata
        context = LintContext(metadata={})
        config = rule.get_configuration(context.metadata)
        self.assertEqual(config, {})

        # Test with partial metadata
        context = LintContext(metadata={"rules": {}})
        config = rule.get_configuration(context.metadata)
        self.assertEqual(config, {})

    def test_node_stack_edge_cases(self):
        """Test behavior with various node stack configurations."""
        rule = MagicNumberRule()

        # Test with None node stack
        context = LintContext(node_stack=None)
        result = rule._is_in_range_context(context)
        self.assertFalse(result)

        result = rule._is_in_math_context(context)
        self.assertFalse(result)

    def test_numeric_edge_values(self):
        """Test behavior with edge numeric values."""
        rule = MagicNumberRule()
        context = LintContext()

        # Test with very large numbers
        node = ast.Constant(value=999999999999)
        violations = rule.check_node(node, context)
        self.assertEqual(len(violations), 1)

        # Test with very small floats
        node = ast.Constant(value=1e-10)
        violations = rule.check_node(node, context)
        self.assertEqual(len(violations), 1)

        # Test with negative floats
        node = ast.Constant(value=-3.14159)
        violations = rule.check_node(node, context)
        self.assertEqual(len(violations), 1)

    def test_complex_number_edge_values(self):
        """Test complex rule behavior with edge values."""
        rule = MagicComplexRule()
        context = LintContext()

        # Test with very small real/imaginary parts
        node = ast.Constant(value=1e-15 + 1e-15j)
        violations = rule.check_node(node, context)
        self.assertEqual(len(violations), 1)

        # Test with zero real part
        node = ast.Constant(value=0 + 5j)
        violations = rule.check_node(node, context)
        self.assertEqual(len(violations), 1)

        # Test with zero imaginary part
        node = ast.Constant(value=5 + 0j)
        violations = rule.check_node(node, context)
        self.assertEqual(len(violations), 1)


if __name__ == "__main__":
    unittest.main()
