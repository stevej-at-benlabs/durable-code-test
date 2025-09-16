#!/usr/bin/env python3
"""
Purpose: Unit tests for the nesting depth linter
Scope: Tests the nesting_depth_linter module functionality
Overview: Comprehensive test suite covering nesting depth detection, threshold validation,
    edge cases, and various Python constructs. Tests ensure the linter correctly
    identifies excessive nesting in functions, methods, and async functions while
    properly handling different control flow structures.
Dependencies: unittest, ast, tempfile for test infrastructure
Exports: TestNestingDepthLinter test class
Interfaces: Standard unittest test methods
Implementation: Uses AST-based test cases to verify linter behavior
"""

import unittest
import ast
import sys
import os
from pathlib import Path
from typing import List

# Add the tools directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'tools' / 'design_linters'))
from nesting_depth_linter import NestingDepthAnalyzer, NestingViolation, analyze_file


class TestNestingDepthLinter(unittest.TestCase):
    """Test suite for the nesting depth linter."""

    def analyze_code(self, code: str, max_depth: int = 3) -> List[NestingViolation]:
        """Helper to analyze code string and return violations."""
        tree = ast.parse(code)
        analyzer = NestingDepthAnalyzer('test.py', max_depth)
        analyzer.visit(tree)
        return analyzer.violations

    def test_no_nesting(self):
        """Test function with no nesting."""
        code = '''
def simple_function():
    x = 1
    y = 2
    return x + y
'''
        violations = self.analyze_code(code)
        self.assertEqual(len(violations), 0)

    def test_single_level_nesting(self):
        """Test function with single level nesting (should pass)."""
        code = '''
def single_level():
    if condition:
        return True
    return False
'''
        violations = self.analyze_code(code, max_depth=3)
        self.assertEqual(len(violations), 0)

    def test_triple_nesting_at_limit(self):
        """Test function with nesting at the limit (should pass)."""
        code = '''
def triple_nested():
    if condition1:
        for item in items:
            if condition2:
                print(item)
'''
        violations = self.analyze_code(code, max_depth=3)
        self.assertEqual(len(violations), 0)

    def test_excessive_nesting_four_levels(self):
        """Test function with 4 levels of nesting (should fail with max_depth=3)."""
        code = '''
def excessive_nesting():
    if condition1:
        for item in items:
            if condition2:
                while running:
                    print(item)
'''
        violations = self.analyze_code(code, max_depth=3)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].function_name, 'excessive_nesting')
        self.assertEqual(violations[0].max_depth, 4)
        self.assertEqual(violations[0].nested_constructs, ['if', 'for', 'if', 'while'])

    def test_deeply_nested_example(self):
        """Test the deeply nested example from the user."""
        code = '''
def _is_docstring(self, node):
    parent = getattr(node, 'parent', None)
    if parent and isinstance(parent, Expr):
        grandparent = getattr(parent, 'parent', None)
        if grandparent:
            if isinstance(grandparent, (FunctionDef, AsyncFunctionDef, ClassDef, Module)):
                body = grandparent.body
                if body:
                    for stmt in body:
                        if isinstance(stmt, Expr) and stmt == parent:
                            if isinstance(stmt.value, Constant) and isinstance(stmt.value.value, str):
                                real_stmts = [s for s in body if not isinstance(s, Pass)]
                                if real_stmts and real_stmts[0] == stmt:
                                    return True
                        elif not isinstance(stmt, Pass):
                            break
    return False
'''
        violations = self.analyze_code(code, max_depth=3)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].function_name, '_is_docstring')
        self.assertEqual(violations[0].max_depth, 8)
        self.assertEqual(violations[0].nested_constructs,
                        ['if', 'if', 'if', 'if', 'for', 'if', 'if', 'if'])

    def test_try_except_nesting(self):
        """Test nesting with try/except blocks."""
        code = '''
def error_handler():
    try:
        if condition:
            for item in items:
                try:
                    if item:
                        process(item)
                except Exception:
                    if should_retry:
                        retry(item)
    except:
        pass
'''
        violations = self.analyze_code(code, max_depth=3)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].max_depth, 6)
        # Should track try -> if -> for -> try -> except -> if path
        self.assertIn('try', violations[0].nested_constructs)
        self.assertIn('except', violations[0].nested_constructs)

    def test_with_statement_nesting(self):
        """Test nesting with with statements."""
        code = '''
def file_processor():
    with open('file1'):
        with open('file2'):
            if condition:
                for line in file:
                    print(line)
'''
        violations = self.analyze_code(code, max_depth=3)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].max_depth, 4)
        self.assertEqual(violations[0].nested_constructs, ['with', 'with', 'if', 'for'])

    def test_async_function_nesting(self):
        """Test nesting in async functions."""
        code = '''
async def async_processor():
    async for item in items:
        async with resource:
            if condition:
                while running:
                    await process(item)
'''
        violations = self.analyze_code(code, max_depth=3)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].function_name, 'async_processor')
        self.assertEqual(violations[0].max_depth, 4)

    def test_multiple_functions_mixed_violations(self):
        """Test multiple functions with mixed violation status."""
        code = '''
def good_function():
    if x:
        return True

def bad_function():
    if a:
        if b:
            if c:
                if d:
                    return True

def another_good():
    for i in range(10):
        if i > 5:
            print(i)
'''
        violations = self.analyze_code(code, max_depth=3)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].function_name, 'bad_function')
        self.assertEqual(violations[0].max_depth, 4)

    def test_nested_functions(self):
        """Test nested function definitions."""
        code = '''
def outer():
    def inner():
        if condition:
            for item in items:
                if check:
                    while running:
                        print(item)

    if outer_condition:
        for x in range(10):
            inner()
'''
        violations = self.analyze_code(code, max_depth=3)
        # Only inner function should violate
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].function_name, 'inner')
        self.assertEqual(violations[0].max_depth, 4)

    def test_class_methods(self):
        """Test nesting in class methods."""
        code = '''
class MyClass:
    def method_one(self):
        if x:
            return True

    def method_two(self):
        if a:
            while b:
                for c in items:
                    if d:
                        print(c)
'''
        violations = self.analyze_code(code, max_depth=3)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].function_name, 'method_two')
        self.assertEqual(violations[0].max_depth, 4)

    def test_elif_branches(self):
        """Test that elif doesn't increase nesting depth."""
        code = '''
def elif_test():
    if condition1:
        if nested1:
            if nested2:
                action1()
    elif condition2:
        if nested3:
            if nested4:
                action2()
    else:
        if nested5:
            if nested6:
                action3()
'''
        violations = self.analyze_code(code, max_depth=2)
        self.assertEqual(len(violations), 1)
        # Else block has depth 4: if (the whole if/elif/else) -> else -> if -> if
        self.assertEqual(violations[0].max_depth, 4)

    def test_list_comprehension_not_counted(self):
        """Test that list comprehensions don't count as nesting."""
        code = '''
def comprehension_test():
    if condition:
        result = [x for x in range(10) if x > 5]
        for item in result:
            if item:
                print(item)
'''
        violations = self.analyze_code(code, max_depth=3)
        # Should be depth 3, not 4 (comprehension doesn't count)
        self.assertEqual(len(violations), 0)

    def test_custom_threshold(self):
        """Test with different threshold values."""
        code = '''
def deep_function():
    if a:
        if b:
            if c:
                if d:
                    if e:
                        return True
'''
        # Should fail with max_depth=3
        violations = self.analyze_code(code, max_depth=3)
        self.assertEqual(len(violations), 1)

        # Should pass with max_depth=5
        violations = self.analyze_code(code, max_depth=5)
        self.assertEqual(len(violations), 0)

        # Should fail with max_depth=4
        violations = self.analyze_code(code, max_depth=4)
        self.assertEqual(len(violations), 1)

    def test_match_statement(self):
        """Test match statement nesting (Python 3.10+)."""
        if sys.version_info >= (3, 10):
            code = '''
def match_test(value):
    match value:
        case 1:
            if condition:
                for item in items:
                    if check:
                        print(item)
'''
            violations = self.analyze_code(code, max_depth=3)
            self.assertEqual(len(violations), 1)
            self.assertEqual(violations[0].max_depth, 4)
            self.assertIn('match', violations[0].nested_constructs)

    def test_violation_details(self):
        """Test that violation details are correctly captured."""
        code = '''
def test_func():
    if x:  # Line 2
        for y in range(10):
            while z:
                if w:
                    print("too deep")
'''
        violations = self.analyze_code(code, max_depth=3)
        self.assertEqual(len(violations), 1)
        violation = violations[0]

        self.assertEqual(violation.file_path, 'test.py')
        self.assertEqual(violation.function_name, 'test_func')
        self.assertEqual(violation.line, 2)  # Function definition line
        self.assertEqual(violation.column, 0)
        self.assertEqual(violation.max_depth, 4)
        self.assertEqual(violation.threshold, 3)
        self.assertEqual(violation.nested_constructs, ['if', 'for', 'while', 'if'])

    def test_empty_function(self):
        """Test empty function doesn't cause issues."""
        code = '''
def empty_function():
    pass
'''
        violations = self.analyze_code(code)
        self.assertEqual(len(violations), 0)

    def test_docstring_only_function(self):
        """Test function with only docstring."""
        code = '''
def documented_function():
    """This function does nothing."""
    pass
'''
        violations = self.analyze_code(code)
        self.assertEqual(len(violations), 0)


if __name__ == '__main__':
    unittest.main()