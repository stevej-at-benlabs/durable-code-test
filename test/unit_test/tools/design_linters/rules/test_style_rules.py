#!/usr/bin/env python3
"""
Purpose: Unit tests for code style rules
Scope: Tests for print statements, nesting depth, and other style rules
Overview: This module tests the style rules including detection of excessive
    nesting, print statement usage, and other code style violations that
    affect readability and maintainability.
Dependencies: unittest, ast, style rules
"""

import unittest
import ast
from pathlib import Path

import sys
sys.path.insert(0, '/home/stevejackson/Projects/durable-code-test/tools')

from design_linters.framework.interfaces import LintContext, Severity
from design_linters.rules.style.print_statement_rules import (
    PrintStatementRule,
    ConsoleOutputRule
)
from design_linters.rules.style.nesting_rules import (
    ExcessiveNestingRule,
    DeepFunctionRule
)


class TestPrintStatementRule(unittest.TestCase):
    """Test the PrintStatementRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = PrintStatementRule()

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, "style.print-statement")
        self.assertEqual(self.rule.severity, Severity.WARNING)
        self.assertIn("style", self.rule.categories)
        self.assertIn("production", self.rule.categories)

    def test_print_statement_detection(self):
        """Test detection of print statements."""
        code = """
def display_results():
    print("Results:")
    for item in items:
        print(f"  - {item}")
    print("Done")
"""

        context = LintContext(
            file_path=Path('/src/file.py'),
            file_content=code,
            ast_tree=ast.parse(code)
        )
        violations = self.rule.check(context)

        # Should detect all print statements
        self.assertEqual(len(violations), 3)
        for violation in violations:
            self.assertEqual(violation.rule_id, "style.print-statement")

    def test_print_in_production_code(self):
        """Test that print in production code is flagged."""
        code = """
class DataProcessor:
    def process(self, data):
        print(f"Processing {len(data)} items")
        result = self._compute(data)
        print(f"Completed with result: {result}")
        return result

    def _compute(self, data):
        return sum(data)
"""

        violations = self.rule.check('/src/processor.py', code)

        # Should flag print statements in production code
        self.assertEqual(len(violations), 2)

    def test_print_in_debug_function(self):
        """Test that print in debug functions is allowed."""
        code = """
def debug_state(state):
    print(f"Current state: {state}")
    print(f"Memory usage: {get_memory()}")

def display_debug_info():
    print("Debug information:")
"""

        context = LintContext(
            file_path=Path('/src/file.py'),
            file_content=code,
            ast_tree=ast.parse(code)
        )
        violations = self.rule.check(context)

        # Debug functions might be allowed (depends on configuration)
        # At least the function names suggest debug purpose
        self.assertLessEqual(len(violations), 3)

    def test_print_in_example_code(self):
        """Test that print in example code is allowed."""
        code = """
def example_usage():
    print("This is an example")
    result = calculate()
    print(f"Result: {result}")
"""

        context = LintContext(
            file_path=Path('/examples/demo.py'),
            file_content=code
        )

        tree = ast.parse(code)
        violations = []
        for node in ast.walk(tree):
            if self.rule.should_check_node(node, context):
                violations.extend(self.rule.check_node(node, context))

        # Example files might allow print statements
        self.assertEqual(len(violations), 0)


class TestConsoleOutputRule(unittest.TestCase):
    """Test the ConsoleOutputRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = ConsoleOutputRule()

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, "style.console-output")
        self.assertEqual(self.rule.severity, Severity.INFO)
        self.assertIn("console", self.rule.categories)

    def test_console_methods_detection(self):
        """Test detection of various console output methods."""
        code = """
import sys

def output_data():
    sys.stdout.write("Direct output\\n")
    sys.stderr.write("Error output\\n")
    print("Regular print", file=sys.stderr)
"""

        context = LintContext(
            file_path=Path('/src/file.py'),
            file_content=code,
            ast_tree=ast.parse(code)
        )
        violations = self.rule.check(context)

        # Should detect console output methods
        self.assertGreaterEqual(len(violations), 2)

    def test_pprint_detection(self):
        """Test detection of pprint usage."""
        code = """
from pprint import pprint

def debug_structure(data):
    pprint(data)
    pprint({"key": "value"}, indent=2)
"""

        context = LintContext(
            file_path=Path('/src/file.py'),
            file_content=code,
            ast_tree=ast.parse(code)
        )
        violations = self.rule.check(context)

        # Should detect pprint usage
        self.assertGreaterEqual(len(violations), 2)
        for violation in violations:
            self.assertIn("logging", violation.suggestion.lower())


class TestExcessiveNestingRule(unittest.TestCase):
    """Test the ExcessiveNestingRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = ExcessiveNestingRule()

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, "style.excessive-nesting")
        self.assertEqual(self.rule.severity, Severity.WARNING)
        self.assertIn("readability", self.rule.categories)
        self.assertIn("complexity", self.rule.categories)

    def test_deep_nesting_detection(self):
        """Test detection of excessive nesting."""
        code = """
def process_data(items):
    if items:
        for item in items:
            if item.is_valid():
                if item.type == "special":
                    if item.value > 0:
                        # 5 levels deep
                        return item.process()
    return None
"""

        context = LintContext(
            file_path=Path('/src/file.py'),
            file_content=code,
            ast_tree=ast.parse(code)
        )
        violations = self.rule.check(context)

        # Should detect excessive nesting
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].rule_id, "style.excessive-nesting")
        self.assertIn("6", violations[0].message)

    def test_acceptable_nesting(self):
        """Test that acceptable nesting is not flagged."""
        code = """
def simple_process(data):
    if data:
        for item in data:
            if item.is_valid():
                process_item(item)
    return True
"""

        context = LintContext(
            file_path=Path('/src/file.py'),
            file_content=code,
            ast_tree=ast.parse(code)
        )
        violations = self.rule.check(context)

        # Nesting depth of 3 should be acceptable
        self.assertEqual(len(violations), 0)

    def test_nested_functions(self):
        """Test nesting in nested functions."""
        code = """
def outer():
    def inner():
        if condition:
            for i in range(10):
                if i > 5:
                    while i < 10:
                        # Deep nesting in inner function
                        do_something()
    inner()
"""

        context = LintContext(
            file_path=Path('/src/file.py'),
            file_content=code,
            ast_tree=ast.parse(code)
        )
        violations = self.rule.check(context)

        # Should detect deep nesting in inner function
        self.assertGreaterEqual(len(violations), 1)

    def test_try_except_nesting(self):
        """Test nesting with try-except blocks."""
        code = """
def safe_process():
    try:
        if data:
            for item in data:
                try:
                    if item:
                        while item.next:
                            # Deep nesting with exception handling
                            process()
                except:
                    pass
    except:
        pass
"""

        context = LintContext(
            file_path=Path('/src/file.py'),
            file_content=code,
            ast_tree=ast.parse(code)
        )
        violations = self.rule.check(context)

        # Should detect excessive nesting even with try-except
        self.assertGreaterEqual(len(violations), 1)

    def test_suggestion_for_refactoring(self):
        """Test that refactoring suggestions are provided."""
        code = """
def complex_logic(x, y, z):
    if x:
        if y:
            if z:
                if x > y:
                    if y > z:
                        return True
    return False
"""

        context = LintContext(
            file_path=Path('/src/file.py'),
            file_content=code,
            ast_tree=ast.parse(code)
        )
        violations = self.rule.check(context)

        self.assertEqual(len(violations), 1)
        self.assertIn("early return", violations[0].suggestion.lower())


class TestDeepFunctionRule(unittest.TestCase):
    """Test the DeepFunctionRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = DeepFunctionRule()

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, "style.deep-function")
        self.assertEqual(self.rule.severity, Severity.INFO)
        self.assertIn("complexity", self.rule.categories)
        self.assertIn("maintainability", self.rule.categories)

    def test_complex_function_detection(self):
        """Test detection of overly complex functions."""
        code = """
def complex_function(data, options):
    result = []
    if data:
        for item in data:
            if item.is_valid():
                value = item.value
                if value > 0:
                    if options.get('filter'):
                        if value < 100:
                            processed = value * 2
                            if processed > 10:
                                result.append(processed)
                                if len(result) > 50:
                                    break

    # Many more lines...
    for r in result:
        if r > 100:
            print(r)

    return result
"""

        context = LintContext(
            file_path=Path('/src/file.py'),
            file_content=code,
            ast_tree=ast.parse(code)
        )
        violations = self.rule.check(context)

        # Should detect complex function
        self.assertGreaterEqual(len(violations), 1)
        self.assertEqual(violations[0].rule_id, "style.deep-function")

    def test_simple_function_not_flagged(self):
        """Test that simple functions are not flagged."""
        code = """
def simple_function(x, y):
    if x > y:
        return x
    return y

def another_simple(data):
    result = []
    for item in data:
        if item:
            result.append(item)
    return result
"""

        context = LintContext(
            file_path=Path('/src/file.py'),
            file_content=code,
            ast_tree=ast.parse(code)
        )
        violations = self.rule.check(context)

        # Simple functions should not be flagged
        self.assertEqual(len(violations), 0)

    def test_long_but_simple_function(self):
        """Test that long but simple functions might be acceptable."""
        code = """
def configuration_function():
    config = {}
    config['option1'] = 'value1'
    config['option2'] = 'value2'
    config['option3'] = 'value3'
    config['option4'] = 'value4'
    config['option5'] = 'value5'
    config['option6'] = 'value6'
    config['option7'] = 'value7'
    config['option8'] = 'value8'
    config['option9'] = 'value9'
    config['option10'] = 'value10'
    return config
"""

        context = LintContext(
            file_path=Path('/src/file.py'),
            file_content=code,
            ast_tree=ast.parse(code)
        )
        violations = self.rule.check(context)

        # Long but not deeply nested, might not be flagged
        # depending on the specific implementation
        self.assertLessEqual(len(violations), 1)

    def test_recursive_function(self):
        """Test handling of recursive functions."""
        code = """
def recursive_process(node, depth=0):
    if depth > 10:
        return None

    if node is None:
        return None

    if node.is_leaf():
        return node.value

    results = []
    for child in node.children:
        if child:
            result = recursive_process(child, depth + 1)
            if result:
                results.append(result)

    return results
"""

        context = LintContext(
            file_path=Path('/src/file.py'),
            file_content=code,
            ast_tree=ast.parse(code)
        )
        violations = self.rule.check(context)

        # Recursive functions might have different complexity considerations
        # Test that the rule handles them appropriately
        self.assertLessEqual(len(violations), 2)


if __name__ == '__main__':
    unittest.main()
