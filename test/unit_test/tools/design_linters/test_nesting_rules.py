#!/usr/bin/env python3
"""
Purpose: Comprehensive unit tests for nesting rules
Scope: Test all nesting rule classes and their methods
Overview: This module provides comprehensive tests for the nesting rules including
    ExcessiveNestingRule and DeepFunctionRule. Tests cover all methods, properties,
    edge cases, and configuration scenarios.
Dependencies: unittest, ast, framework interfaces
Exports: TestExcessiveNestingRule, TestDeepFunctionRule, TestNestingRulesIntegration
Interfaces: Standard unittest.TestCase interface for test execution
Implementation: Comprehensive test coverage using unittest framework with AST parsing
"""

import unittest
import ast
from pathlib import Path
from unittest.mock import Mock, patch

import sys
sys.path.insert(0, '/home/stevejackson/Projects/durable-code-test/tools')

from design_linters.framework.interfaces import LintContext, Severity
from design_linters.rules.style.nesting_rules import ExcessiveNestingRule, DeepFunctionRule


class TestExcessiveNestingRule(unittest.TestCase):
    """Test ExcessiveNestingRule functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = ExcessiveNestingRule()
        self.context = LintContext(file_path=Path('/test.py'))

    def test_rule_properties(self):
        """Test rule properties return expected values."""
        self.assertEqual(self.rule.rule_id, "style.excessive-nesting")
        self.assertEqual(self.rule.rule_name, "Excessive Nesting")
        self.assertEqual(self.rule.description, "Functions should not have excessive nesting depth for better readability")
        self.assertEqual(self.rule.severity, Severity.WARNING)
        self.assertEqual(self.rule.categories, {"style", "complexity", "readability"})

    def test_should_check_node_function_def(self):
        """Test should_check_node returns True for FunctionDef."""
        func_node = ast.FunctionDef(name='test_func', args=ast.arguments(
            posonlyargs=[], args=[], defaults=[], kwonlyargs=[], kw_defaults=[], vararg=None, kwarg=None
        ), body=[], decorator_list=[], returns=None)

        self.assertTrue(self.rule.should_check_node(func_node, self.context))

    def test_should_check_node_async_function_def(self):
        """Test should_check_node returns True for AsyncFunctionDef."""
        async_func_node = ast.AsyncFunctionDef(name='async_test_func', args=ast.arguments(
            posonlyargs=[], args=[], defaults=[], kwonlyargs=[], kw_defaults=[], vararg=None, kwarg=None
        ), body=[], decorator_list=[], returns=None)

        self.assertTrue(self.rule.should_check_node(async_func_node, self.context))

    def test_should_check_node_other_nodes(self):
        """Test should_check_node returns False for non-function nodes."""
        class_node = ast.ClassDef(name='TestClass', bases=[], keywords=[], decorator_list=[], body=[])
        assign_node = ast.Assign(targets=[ast.Name(id='x', ctx=ast.Store())], value=ast.Constant(value=1))

        self.assertFalse(self.rule.should_check_node(class_node, self.context))
        self.assertFalse(self.rule.should_check_node(assign_node, self.context))

    def test_check_node_with_invalid_node_type(self):
        """Test check_node raises TypeError for invalid node types."""
        class_node = ast.ClassDef(name='TestClass', bases=[], keywords=[], decorator_list=[], body=[])

        with self.assertRaises(TypeError) as cm:
            self.rule.check_node(class_node, self.context)

        self.assertIn("ExcessiveNestingRule should only receive function nodes", str(cm.exception))

    def test_check_node_simple_function_no_violations(self):
        """Test check_node with simple function that has no violations."""
        # Create a simple function with no nesting
        func_code = """
def simple_function():
    x = 1
    return x
"""
        tree = ast.parse(func_code)
        func_node = tree.body[0]

        violations = self.rule.check_node(func_node, self.context)
        self.assertEqual(len(violations), 0)

    def test_check_node_nested_function_no_violations(self):
        """Test check_node with moderately nested function that doesn't exceed limit."""
        # Create function with nesting depth 3 (within default limit of 4)
        func_code = """
def moderate_nesting():
    if True:
        for i in range(10):
            while True:
                break
"""
        tree = ast.parse(func_code)
        func_node = tree.body[0]

        violations = self.rule.check_node(func_node, self.context)
        self.assertEqual(len(violations), 0)

    def test_check_node_excessive_nesting_violation(self):
        """Test check_node with function that exceeds default nesting limit."""
        # Create function with nesting depth 6 (exceeds default limit of 4)
        func_code = """
def excessive_nesting():
    if True:
        for i in range(10):
            while True:
                try:
                    with open('file.txt') as f:
                        pass
                except:
                    pass
"""
        tree = ast.parse(func_code)
        func_node = tree.body[0]

        violations = self.rule.check_node(func_node, self.context)
        self.assertEqual(len(violations), 1)

        violation = violations[0]
        self.assertEqual(violation.rule_id, "style.excessive-nesting")
        self.assertEqual(violation.severity, Severity.WARNING)
        self.assertIn("excessive_nesting", violation.message)
        self.assertIn("6", violation.message)  # Actual depth is 6
        self.assertIn("Consider extracting nested logic", violation.suggestion)
        self.assertEqual(violation.context['function_name'], 'excessive_nesting')
        self.assertEqual(violation.context['depth'], 6)
        self.assertEqual(violation.context['max_allowed'], 4)

    def test_check_node_with_custom_configuration(self):
        """Test check_node with custom max_nesting_depth configuration."""
        # Set up context with custom configuration
        self.context.metadata = {
            'rules': {
                'style.excessive-nesting': {
                    'config': {'max_nesting_depth': 2}
                }
            }
        }

        # Create function with nesting depth 4 (should violate limit of 2)
        func_code = """
def custom_limit_violation():
    if True:
        for i in range(10):
            while True:
                break
"""
        tree = ast.parse(func_code)
        func_node = tree.body[0]

        violations = self.rule.check_node(func_node, self.context)
        self.assertEqual(len(violations), 1)

        violation = violations[0]
        self.assertEqual(violation.context['depth'], 4)  # Actual depth is function(1) + if(2) + for(3) + while(4)
        self.assertEqual(violation.context['max_allowed'], 2)

    def test_calculate_max_nesting_depth_simple(self):
        """Test _calculate_max_nesting_depth with simple function."""
        func_code = """
def simple_function():
    x = 1
    return x
"""
        tree = ast.parse(func_code)
        func_node = tree.body[0]

        depth = self.rule._calculate_max_nesting_depth(func_node)
        self.assertEqual(depth, 1)  # Function body is at depth 1

    def test_calculate_max_nesting_depth_nested_constructs(self):
        """Test _calculate_max_nesting_depth with various nested constructs."""
        func_code = """
def nested_constructs():
    if True:                    # depth 2
        for i in range(10):     # depth 3
            while True:         # depth 4
                try:            # depth 5
                    with open('file.txt') as f:  # depth 6
                        pass
                except Exception as e:  # depth 5 (except handler)
                    if True:    # depth 6
                        pass
"""
        tree = ast.parse(func_code)
        func_node = tree.body[0]

        depth = self.rule._calculate_max_nesting_depth(func_node)
        # The actual depth is 7: function(1) + if(2) + for(3) + while(4) + try(5) + with(6) + except+if(7)
        self.assertEqual(depth, 7)

    def test_calculate_max_nesting_depth_async_function(self):
        """Test _calculate_max_nesting_depth with async function."""
        func_code = """
async def async_function():
    async with some_context():
        if True:
            pass
"""
        tree = ast.parse(func_code)
        func_node = tree.body[0]

        depth = self.rule._calculate_max_nesting_depth(func_node)
        self.assertEqual(depth, 3)  # async with + if

    def test_calculate_max_nesting_depth_match_statement(self):
        """Test _calculate_max_nesting_depth with match statement (Python 3.10+)."""
        try:
            func_code = """
def match_function(value):
    match value:
        case 1:
            if True:
                pass
"""
            tree = ast.parse(func_code)
            func_node = tree.body[0]

            depth = self.rule._calculate_max_nesting_depth(func_node)
            self.assertEqual(depth, 4)  # function(1) + match(2) + case(3) + if(4)
        except SyntaxError:
            # Skip test if running on Python < 3.10
            self.skipTest("Match statements require Python 3.10+")

    def test_calculate_max_nesting_depth_invalid_node(self):
        """Test _calculate_max_nesting_depth with invalid node type."""
        class_node = ast.ClassDef(name='TestClass', bases=[], keywords=[], decorator_list=[], body=[])

        with self.assertRaises(TypeError) as cm:
            self.rule._calculate_max_nesting_depth(class_node)

        self.assertIn("Expected function node", str(cm.exception))

    def test_check_node_multiple_functions(self):
        """Test that each function is analyzed independently."""
        func_code = """
def function_with_violation():
    if True:
        for i in range(10):
            while True:
                try:
                    with open('file.txt') as f:
                        pass
                except:
                    pass

def simple_function():
    return 1
"""
        tree = ast.parse(func_code)

        # Test first function (should have violation)
        func1_node = tree.body[0]
        violations1 = self.rule.check_node(func1_node, self.context)
        self.assertEqual(len(violations1), 1)

        # Test second function (should have no violation)
        func2_node = tree.body[1]
        violations2 = self.rule.check_node(func2_node, self.context)
        self.assertEqual(len(violations2), 0)


class TestDeepFunctionRule(unittest.TestCase):
    """Test DeepFunctionRule functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = DeepFunctionRule()
        self.context = LintContext(file_path=Path('/test.py'))

    def test_rule_properties(self):
        """Test rule properties return expected values."""
        self.assertEqual(self.rule.rule_id, "style.deep-function")
        self.assertEqual(self.rule.rule_name, "Complex Function")
        self.assertEqual(self.rule.description, "Functions should not be overly complex with deep nesting and many lines")
        self.assertEqual(self.rule.severity, Severity.INFO)
        self.assertEqual(self.rule.categories, {"style", "complexity", "maintainability"})

    def test_should_check_node_function_def(self):
        """Test should_check_node returns True for FunctionDef."""
        func_node = ast.FunctionDef(name='test_func', args=ast.arguments(
            posonlyargs=[], args=[], defaults=[], kwonlyargs=[], kw_defaults=[], vararg=None, kwarg=None
        ), body=[], decorator_list=[], returns=None)

        self.assertTrue(self.rule.should_check_node(func_node, self.context))

    def test_should_check_node_async_function_def(self):
        """Test should_check_node returns True for AsyncFunctionDef."""
        async_func_node = ast.AsyncFunctionDef(name='async_test_func', args=ast.arguments(
            posonlyargs=[], args=[], defaults=[], kwonlyargs=[], kw_defaults=[], vararg=None, kwarg=None
        ), body=[], decorator_list=[], returns=None)

        self.assertTrue(self.rule.should_check_node(async_func_node, self.context))

    def test_should_check_node_other_nodes(self):
        """Test should_check_node returns False for non-function nodes."""
        class_node = ast.ClassDef(name='TestClass', bases=[], keywords=[], decorator_list=[], body=[])
        assign_node = ast.Assign(targets=[ast.Name(id='x', ctx=ast.Store())], value=ast.Constant(value=1))

        self.assertFalse(self.rule.should_check_node(class_node, self.context))
        self.assertFalse(self.rule.should_check_node(assign_node, self.context))

    def test_check_node_with_invalid_node_type(self):
        """Test check_node raises TypeError for invalid node types."""
        class_node = ast.ClassDef(name='TestClass', bases=[], keywords=[], decorator_list=[], body=[])

        with self.assertRaises(TypeError) as cm:
            self.rule.check_node(class_node, self.context)

        self.assertIn("DeepFunctionRule should only receive function nodes", str(cm.exception))

    def test_check_node_simple_function_no_violations(self):
        """Test check_node with simple function that has no violations."""
        func_code = """
def simple_function():
    x = 1
    return x
"""
        tree = ast.parse(func_code)
        func_node = tree.body[0]

        # Set line numbers for length calculation
        func_node.lineno = 1
        func_node.end_lineno = 3

        violations = self.rule.check_node(func_node, self.context)
        self.assertEqual(len(violations), 0)

    def test_check_node_long_function_violation(self):
        """Test check_node with function that exceeds line limit."""
        # Create a long function (will simulate line numbers)
        func_code = """
def long_function():
    line1 = 1
    line2 = 2
    # ... many more lines
"""
        tree = ast.parse(func_code)
        func_node = tree.body[0]

        # Simulate a function that is 60 lines long (exceeds default limit of 50)
        func_node.lineno = 1
        func_node.end_lineno = 60

        violations = self.rule.check_node(func_node, self.context)
        self.assertEqual(len(violations), 1)

        violation = violations[0]
        self.assertEqual(violation.rule_id, "style.deep-function")
        self.assertEqual(violation.severity, Severity.INFO)
        self.assertIn("too long", violation.message)
        self.assertIn("59 lines", violation.message)  # end_lineno - lineno
        self.assertIn("Consider breaking this function", violation.suggestion)
        self.assertEqual(violation.context['function_name'], 'long_function')
        self.assertEqual(violation.context['length'], 59)
        self.assertEqual(violation.context['issue'], 'length')

    def test_check_node_deep_nesting_violation(self):
        """Test check_node with function that exceeds nesting limit."""
        func_code = """
def deep_function():
    if True:
        for i in range(10):
            while True:
                try:
                    pass
                except:
                    pass
"""
        tree = ast.parse(func_code)
        func_node = tree.body[0]

        # Set reasonable line numbers
        func_node.lineno = 1
        func_node.end_lineno = 10

        violations = self.rule.check_node(func_node, self.context)
        self.assertEqual(len(violations), 1)

        violation = violations[0]
        self.assertEqual(violation.rule_id, "style.deep-function")
        self.assertEqual(violation.severity, Severity.INFO)
        self.assertIn("deep nesting", violation.message)
        self.assertIn("6 levels", violation.message)  # Actual nesting depth is 6
        self.assertIn("early returns", violation.suggestion)
        self.assertEqual(violation.context['function_name'], 'deep_function')
        self.assertEqual(violation.context['depth'], 6)
        self.assertEqual(violation.context['issue'], 'nesting')

    def test_check_node_both_violations(self):
        """Test check_node with function that violates both length and nesting limits."""
        func_code = """
def complex_function():
    if True:
        for i in range(10):
            while True:
                try:
                    pass
                except:
                    pass
"""
        tree = ast.parse(func_code)
        func_node = tree.body[0]

        # Set function to be both long and deeply nested
        func_node.lineno = 1
        func_node.end_lineno = 60  # Long function

        violations = self.rule.check_node(func_node, self.context)
        self.assertEqual(len(violations), 2)  # Both length and nesting violations

        # Check that we have both types of violations
        violation_types = {v.context['issue'] for v in violations}
        self.assertEqual(violation_types, {'length', 'nesting'})

    def test_check_node_with_custom_configuration(self):
        """Test check_node with custom configuration limits."""
        # Set up context with custom configuration
        self.context.metadata = {
            'rules': {
                'style.deep-function': {
                    'config': {
                        'max_function_lines': 5,
                        'max_nesting_depth': 2
                    }
                }
            }
        }

        func_code = """
def custom_limit_function():
    if True:
        for i in range(10):
            pass
"""
        tree = ast.parse(func_code)
        func_node = tree.body[0]

        # Set line numbers to exceed custom limit
        func_node.lineno = 1
        func_node.end_lineno = 7  # 6 lines, exceeds limit of 5

        violations = self.rule.check_node(func_node, self.context)
        self.assertEqual(len(violations), 2)  # Both length and nesting violations with custom limits

    def test_calculate_max_nesting_depth_simple(self):
        """Test _calculate_max_nesting_depth with simple function."""
        func_code = """
def simple_function():
    x = 1
    return x
"""
        tree = ast.parse(func_code)
        func_node = tree.body[0]

        depth = self.rule._calculate_max_nesting_depth(func_node)
        self.assertEqual(depth, 1)

    def test_calculate_max_nesting_depth_nested(self):
        """Test _calculate_max_nesting_depth with nested constructs."""
        func_code = """
def nested_function():
    if True:
        for i in range(10):
            while True:
                break
"""
        tree = ast.parse(func_code)
        func_node = tree.body[0]

        depth = self.rule._calculate_max_nesting_depth(func_node)
        self.assertEqual(depth, 4)  # if + for + while + function body

    def test_calculate_max_nesting_depth_invalid_node(self):
        """Test _calculate_max_nesting_depth with invalid node type."""
        class_node = ast.ClassDef(name='TestClass', bases=[], keywords=[], decorator_list=[], body=[])

        with self.assertRaises(TypeError) as cm:
            self.rule._calculate_max_nesting_depth(class_node)

        self.assertIn("Expected function node", str(cm.exception))

    def test_check_node_no_line_numbers(self):
        """Test check_node when function node has no line number information."""
        func_code = """
def function_without_lines():
    pass
"""
        tree = ast.parse(func_code)
        func_node = tree.body[0]

        # Remove line number information
        func_node.lineno = None
        func_node.end_lineno = None

        violations = self.rule.check_node(func_node, self.context)
        # Should only check nesting, not length
        self.assertEqual(len(violations), 0)

    def test_check_node_missing_end_lineno(self):
        """Test check_node when function node has lineno but no end_lineno."""
        func_code = """
def function_with_partial_lines():
    pass
"""
        tree = ast.parse(func_code)
        func_node = tree.body[0]

        # Remove end line number information
        func_node.end_lineno = None

        violations = self.rule.check_node(func_node, self.context)
        # Should only check nesting, not length
        self.assertEqual(len(violations), 0)

    def test_nesting_depth_difference_from_excessive_nesting_rule(self):
        """Test that DeepFunctionRule uses different nesting depth calculation."""
        # DeepFunctionRule doesn't include Match/match_case in nesting calculation
        func_code = """
def function_with_match():
    if True:
        for i in range(10):
            while True:
                break
"""
        tree = ast.parse(func_code)
        func_node = tree.body[0]

        func_node.lineno = 1
        func_node.end_lineno = 5

        # Create context with low nesting limit to trigger violation
        self.context.metadata = {
            'rules': {
                'style.deep-function': {
                    'config': {'max_nesting_depth': 3}
                }
            }
        }

        violations = self.rule.check_node(func_node, self.context)

        # Should have nesting violation (depth 4 > limit 3)
        nesting_violations = [v for v in violations if v.context.get('issue') == 'nesting']
        self.assertEqual(len(nesting_violations), 1)


class TestNestingRulesIntegration(unittest.TestCase):
    """Integration tests for nesting rules."""

    def setUp(self):
        """Set up test fixtures."""
        self.excessive_nesting_rule = ExcessiveNestingRule()
        self.deep_function_rule = DeepFunctionRule()
        self.context = LintContext(file_path=Path('/test.py'))

    def test_both_rules_on_same_function(self):
        """Test both rules analyzing the same function."""
        func_code = """
def complex_function():
    if True:
        for i in range(10):
            while True:
                try:
                    with open('file.txt') as f:
                        content = f.read()
                        if content:
                            pass
                except Exception as e:
                    pass
"""
        tree = ast.parse(func_code)
        func_node = tree.body[0]

        # Set line numbers to make it long
        func_node.lineno = 1
        func_node.end_lineno = 60

        # Test ExcessiveNestingRule
        excessive_violations = self.excessive_nesting_rule.check_node(func_node, self.context)
        self.assertGreater(len(excessive_violations), 0)

        # Test DeepFunctionRule
        deep_violations = self.deep_function_rule.check_node(func_node, self.context)
        self.assertGreater(len(deep_violations), 0)

        # Ensure they produce different rule IDs
        self.assertEqual(excessive_violations[0].rule_id, "style.excessive-nesting")
        self.assertIn("style.deep-function", [v.rule_id for v in deep_violations])

    def test_rule_configuration_independence(self):
        """Test that rules use independent configurations."""
        self.context.metadata = {
            'rules': {
                'style.excessive-nesting': {
                    'config': {'max_nesting_depth': 2}
                },
                'style.deep-function': {
                    'config': {
                        'max_nesting_depth': 5,
                        'max_function_lines': 10
                    }
                }
            }
        }

        func_code = """
def test_function():
    if True:
        for i in range(10):
            while True:
                break
"""
        tree = ast.parse(func_code)
        func_node = tree.body[0]
        func_node.lineno = 1
        func_node.end_lineno = 5

        # ExcessiveNestingRule should violate (depth 4 > limit 2)
        excessive_violations = self.excessive_nesting_rule.check_node(func_node, self.context)
        self.assertEqual(len(excessive_violations), 1)

        # DeepFunctionRule should not violate nesting (depth 4 < limit 5) but might violate length
        deep_violations = self.deep_function_rule.check_node(func_node, self.context)
        nesting_violations = [v for v in deep_violations if v.context.get('issue') == 'nesting']
        self.assertEqual(len(nesting_violations), 0)


if __name__ == '__main__':
    unittest.main()
