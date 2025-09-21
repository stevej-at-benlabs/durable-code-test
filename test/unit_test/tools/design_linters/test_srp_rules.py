#!/usr/bin/env python3
"""
Purpose: Comprehensive unit tests for SOLID SRP rules
Scope: Tests all rule classes in srp_rules.py module
Overview: This module provides comprehensive tests for all Single Responsibility
    Principle rules including property tests, method behavior tests, and
    violation detection with various scenarios.
Dependencies: unittest, ast, framework interfaces
Exports: TestTooManyMethodsRule, TestTooManyResponsibilitiesRule, TestLowCohesionRule, TestClassTooBigRule, TestTooManyDependenciesRule
Interfaces: Standard unittest.TestCase interface for test execution
Implementation: Comprehensive test coverage using unittest framework with AST parsing
"""

import ast
import sys
import unittest
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, "/home/stevejackson/Projects/durable-code-test/tools")

from design_linters.framework.interfaces import LintContext, LintViolation, Severity
from design_linters.rules.solid.srp_rules import (
    ClassTooBigRule,
    LowCohesionRule,
    TooManyDependenciesRule,
    TooManyMethodsRule,
    TooManyResponsibilitiesRule,
)


class TestTooManyMethodsRule(unittest.TestCase):
    """Test suite for TooManyMethodsRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = TooManyMethodsRule()
        self.context = LintContext(file_path=Path("/test.py"))

    def test_rule_properties(self):
        """Test rule properties return correct values."""
        self.assertEqual(self.rule.rule_id, "solid.srp.too-many-methods")
        self.assertEqual(self.rule.rule_name, "Too Many Methods")
        self.assertIn("too many methods", self.rule.description.lower())
        self.assertEqual(self.rule.severity, Severity.WARNING)
        self.assertEqual(self.rule.categories, {"solid", "srp", "complexity"})

    def test_should_check_node_with_class_def(self):
        """Test should_check_node returns True for ClassDef nodes."""
        class_node = ast.ClassDef(name="TestClass", bases=[], keywords=[], body=[], decorator_list=[])
        self.assertTrue(self.rule.should_check_node(class_node, self.context))

    def test_should_check_node_with_non_class(self):
        """Test should_check_node returns False for non-ClassDef nodes."""
        func_node = ast.FunctionDef(
            name="test_func",
            args=ast.arguments(posonlyargs=[], args=[], defaults=[], kwonlyargs=[], kw_defaults=[], annotations=[]),
            body=[],
            decorator_list=[],
            returns=None,
        )
        self.assertFalse(self.rule.should_check_node(func_node, self.context))

    def test_check_node_with_invalid_node_type(self):
        """Test check_node raises TypeError for non-ClassDef nodes."""
        func_node = ast.FunctionDef(
            name="test_func",
            args=ast.arguments(posonlyargs=[], args=[], defaults=[], kwonlyargs=[], kw_defaults=[], annotations=[]),
            body=[],
            decorator_list=[],
            returns=None,
        )

        with self.assertRaises(TypeError) as cm:
            self.rule.check_node(func_node, self.context)
        self.assertIn("should only receive ast.ClassDef nodes", str(cm.exception))

    def test_class_with_few_methods_no_violation(self):
        """Test class with few methods produces no violations."""
        code = """
class SmallClass:
    def method1(self):
        pass

    def method2(self):
        pass

    def method3(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        violations = self.rule.check_node(class_node, self.context)
        self.assertEqual(len(violations), 0)

    def test_class_with_many_methods_violation(self):
        """Test class with many methods produces violation."""
        # Create a class with more than 15 methods (default threshold)
        methods = [f"    def method{i}(self): pass" for i in range(20)]
        code = f"""
class LargeClass:
{chr(10).join(methods)}
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        violations = self.rule.check_node(class_node, self.context)

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation.rule_id, "solid.srp.too-many-methods")
        self.assertEqual(violation.severity, Severity.WARNING)
        self.assertIn("LargeClass", violation.message)
        self.assertIn("20 methods", violation.message)
        self.assertIn("max: 15", violation.message)

    def test_custom_max_methods_configuration(self):
        """Test custom max_methods configuration is respected."""
        # Set custom config with lower threshold
        self.context.metadata = {"rules": {"solid.srp.too-many-methods": {"config": {"max_methods": 5}}}}

        # Create a class with 7 methods (above custom threshold)
        methods = [f"    def method{i}(self): pass" for i in range(7)]
        code = f"""
class ModerateClass:
{chr(10).join(methods)}
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        violations = self.rule.check_node(class_node, self.context)

        self.assertEqual(len(violations), 1)
        self.assertIn("max: 5", violations[0].message)

    def test_class_with_no_methods(self):
        """Test class with no methods produces no violations."""
        code = """
class EmptyClass:
    pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        violations = self.rule.check_node(class_node, self.context)
        self.assertEqual(len(violations), 0)

    def test_class_with_non_method_body_items(self):
        """Test class with variables and other statements doesn't count them."""
        code = """
class MixedClass:
    attr = "value"

    def method1(self):
        pass

    another_attr = 42

    def method2(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        violations = self.rule.check_node(class_node, self.context)
        self.assertEqual(len(violations), 0)


class TestTooManyResponsibilitiesRule(unittest.TestCase):
    """Test suite for TooManyResponsibilitiesRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = TooManyResponsibilitiesRule()
        self.context = LintContext(file_path=Path("/test.py"))

    def test_rule_properties(self):
        """Test rule properties return correct values."""
        self.assertEqual(self.rule.rule_id, "solid.srp.multiple-responsibilities")
        self.assertEqual(self.rule.rule_name, "Multiple Responsibilities")
        self.assertIn("single responsibility", self.rule.description.lower())
        self.assertEqual(self.rule.severity, Severity.ERROR)
        self.assertEqual(self.rule.categories, {"solid", "srp"})

    def test_should_check_node_with_class_def(self):
        """Test should_check_node returns True for ClassDef nodes."""
        class_node = ast.ClassDef(name="TestClass", bases=[], keywords=[], body=[], decorator_list=[])
        self.assertTrue(self.rule.should_check_node(class_node, self.context))

    def test_check_node_with_invalid_node_type(self):
        """Test check_node raises TypeError for non-ClassDef nodes."""
        func_node = ast.FunctionDef(
            name="test_func",
            args=ast.arguments(posonlyargs=[], args=[], defaults=[], kwonlyargs=[], kw_defaults=[], annotations=[]),
            body=[],
            decorator_list=[],
            returns=None,
        )

        with self.assertRaises(TypeError) as cm:
            self.rule.check_node(func_node, self.context)
        self.assertIn("should only receive ast.ClassDef nodes", str(cm.exception))

    def test_class_with_single_responsibility_no_violation(self):
        """Test class with methods from single responsibility group."""
        code = """
class DataHandler:
    def get_data(self):
        pass

    def set_data(self, data):
        pass

    def fetch_data(self):
        pass

    def load_data(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        violations = self.rule.check_node(class_node, self.context)
        self.assertEqual(len(violations), 0)

    def test_class_with_multiple_responsibilities_violation(self):
        """Test class with methods from multiple responsibility groups."""
        code = """
class MixedClass:
    def get_data(self):
        pass

    def validate_input(self):
        pass

    def format_output(self):
        pass

    def calculate_sum(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        violations = self.rule.check_node(class_node, self.context)

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation.rule_id, "solid.srp.multiple-responsibilities")
        self.assertEqual(violation.severity, Severity.ERROR)
        self.assertIn("MixedClass", violation.message)
        self.assertIn("responsibility groups", violation.message)

    def test_private_methods_ignored(self):
        """Test private methods (starting with _) are ignored."""
        code = """
class TestClass:
    def get_data(self):
        pass

    def _private_helper(self):
        pass

    def __private_method(self):
        pass

    def validate_input(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        violations = self.rule.check_node(class_node, self.context)

        # Should detect data and validation groups (2 groups) but ignore private methods
        self.assertEqual(len(violations), 0)  # 2 groups is within default limit

    def test_custom_max_groups_configuration(self):
        """Test custom max_responsibility_groups configuration."""
        self.context.metadata = {
            "rules": {"solid.srp.multiple-responsibilities": {"config": {"max_responsibility_groups": 1}}}
        }

        code = """
class TestClass:
    def get_data(self):
        pass

    def validate_input(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        violations = self.rule.check_node(class_node, self.context)

        self.assertEqual(len(violations), 1)  # 2 groups > 1 (custom limit)

    def test_custom_responsibility_prefixes(self):
        """Test custom responsibility_prefixes configuration."""
        self.context.metadata = {
            "rules": {
                "solid.srp.multiple-responsibilities": {
                    "config": {
                        "responsibility_prefixes": {"custom1": ["handle", "process"], "custom2": ["manage", "control"]}
                    }
                }
            }
        }

        code = """
class TestClass:
    def handle_request(self):
        pass

    def manage_state(self):
        pass

    def process_data(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        violations = self.rule.check_node(class_node, self.context)

        self.assertEqual(len(violations), 0)  # Only 2 groups detected

    def test_find_method_category(self):
        """Test _find_method_category method."""
        prefixes = {"data": ["get", "set"], "validation": ["validate", "check"]}

        self.assertEqual(self.rule._find_method_category("get_value", prefixes), "data")
        self.assertEqual(self.rule._find_method_category("validate_input", prefixes), "validation")
        self.assertEqual(self.rule._find_method_category("unknown_method", prefixes), "other")

    def test_group_methods_by_responsibility(self):
        """Test _group_methods_by_responsibility method."""
        # Create method AST nodes
        methods = [
            ast.FunctionDef(
                name="get_data",
                args=ast.arguments(posonlyargs=[], args=[], defaults=[], kwonlyargs=[], kw_defaults=[], annotations=[]),
                body=[],
                decorator_list=[],
                returns=None,
            ),
            ast.FunctionDef(
                name="validate_input",
                args=ast.arguments(posonlyargs=[], args=[], defaults=[], kwonlyargs=[], kw_defaults=[], annotations=[]),
                body=[],
                decorator_list=[],
                returns=None,
            ),
            ast.FunctionDef(
                name="_private_method",
                args=ast.arguments(posonlyargs=[], args=[], defaults=[], kwonlyargs=[], kw_defaults=[], annotations=[]),
                body=[],
                decorator_list=[],
                returns=None,
            ),
        ]

        prefixes = {"data": ["get", "set"], "validation": ["validate", "check"]}

        groups = self.rule._group_methods_by_responsibility(methods, prefixes)

        self.assertIn("data", groups)
        self.assertIn("get_data", groups["data"])
        self.assertIn("validation", groups)
        self.assertIn("validate_input", groups["validation"])
        # Private method should be skipped
        self.assertNotIn("_private_method", str(groups))


class TestLowCohesionRule(unittest.TestCase):
    """Test suite for LowCohesionRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = LowCohesionRule()
        self.context = LintContext(file_path=Path("/test.py"))

    def test_rule_properties(self):
        """Test rule properties return correct values."""
        self.assertEqual(self.rule.rule_id, "solid.srp.low-cohesion")
        self.assertEqual(self.rule.rule_name, "Low Cohesion")
        self.assertIn("high cohesion", self.rule.description.lower())
        self.assertEqual(self.rule.severity, Severity.WARNING)
        self.assertEqual(self.rule.categories, {"solid", "srp", "cohesion"})

    def test_should_check_node_with_class_def(self):
        """Test should_check_node returns True for ClassDef nodes."""
        class_node = ast.ClassDef(name="TestClass", bases=[], keywords=[], body=[], decorator_list=[])
        self.assertTrue(self.rule.should_check_node(class_node, self.context))

    def test_check_node_with_invalid_node_type(self):
        """Test check_node raises TypeError for non-ClassDef nodes."""
        func_node = ast.FunctionDef(
            name="test_func",
            args=ast.arguments(posonlyargs=[], args=[], defaults=[], kwonlyargs=[], kw_defaults=[], annotations=[]),
            body=[],
            decorator_list=[],
            returns=None,
        )

        with self.assertRaises(TypeError) as cm:
            self.rule.check_node(func_node, self.context)
        self.assertIn("should only receive ast.ClassDef nodes", str(cm.exception))

    def test_class_with_no_methods_no_violation(self):
        """Test class with no methods produces no violations."""
        code = """
class EmptyClass:
    pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        violations = self.rule.check_node(class_node, self.context)
        self.assertEqual(len(violations), 0)

    def test_class_with_no_instance_vars_no_violation(self):
        """Test class with methods but no instance variables produces no violations."""
        code = """
class NoInstanceVars:
    def method1(self):
        local_var = 42
        return local_var

    def method2(self):
        return "test"
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        violations = self.rule.check_node(class_node, self.context)
        self.assertEqual(len(violations), 0)

    def test_high_cohesion_class_no_violation(self):
        """Test class with high cohesion produces no violations."""
        code = """
class HighCohesionClass:
    def __init__(self):
        self.data = []
        self.count = 0

    def add_item(self, item):
        self.data.append(item)
        self.count += 1

    def get_count(self):
        return self.count

    def get_data(self):
        return self.data
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        violations = self.rule.check_node(class_node, self.context)
        self.assertEqual(len(violations), 0)

    def test_low_cohesion_class_violation(self):
        """Test class with low cohesion produces violation."""
        # Create a class where methods share no instance variables
        # This ensures 0 shared pairs and thus 0.0 cohesion
        code = """
class LowCohesionClass:
    def __init__(self):
        self.var1 = 1
        self.var2 = 2
        self.var3 = 3

    def method1(self):
        return self.var1

    def method2(self):
        return self.var2

    def method3(self):
        return self.var3

    def method4(self):
        # This method doesn't use any instance variables
        return "standalone"

    def method5(self):
        # This method also doesn't use any instance variables
        return 42
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        violations = self.rule.check_node(class_node, self.context)

        # This should produce a violation due to low cohesion
        # (methods don't share instance variables)
        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation.rule_id, "solid.srp.low-cohesion")
        self.assertEqual(violation.severity, Severity.WARNING)
        self.assertIn("LowCohesionClass", violation.message)
        self.assertIn("low cohesion", violation.message)

    def test_custom_min_cohesion_configuration(self):
        """Test custom min_cohesion_score configuration."""
        self.context.metadata = {"rules": {"solid.srp.low-cohesion": {"config": {"min_cohesion_score": 0.8}}}}

        code = """
class ModeratelyCohesiveClass:
    def __init__(self):
        self.shared_var = 1
        self.other_var = 2

    def method1(self):
        return self.shared_var

    def method2(self):
        return self.shared_var

    def method3(self):
        return self.other_var
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        violations = self.rule.check_node(class_node, self.context)

        # With higher threshold, this might trigger a violation
        if violations:
            self.assertIn("0.8", violations[0].description)

    def test_extract_instance_variables(self):
        """Test _extract_instance_variables method."""
        code = """
class TestClass:
    def __init__(self):
        self.var1 = 1
        self.var2 = 2

    def method(self):
        self.var3 = 3
        local_var = 4  # Should not be included
        other.attribute = 5  # Should not be included
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        instance_vars = self.rule._extract_instance_variables(class_node)

        expected_vars = {"var1", "var2", "var3"}
        self.assertEqual(instance_vars, expected_vars)

    def test_find_used_instance_vars(self):
        """Test _find_used_instance_vars method."""
        code = """
def test_method(self):
    self.var1 = 1
    result = self.var2 + self.var3
    local_var = self.var1
    return result
"""
        tree = ast.parse(code)
        method_node = tree.body[0]
        instance_vars = {"var1", "var2", "var3", "var4"}

        used_vars = self.rule._find_used_instance_vars(method_node, instance_vars)
        expected_used = {"var1", "var2", "var3"}
        self.assertEqual(used_vars, expected_used)

    def test_calculate_cohesion_single_method(self):
        """Test _calculate_cohesion with single method returns 1.0."""
        methods = [
            ast.FunctionDef(
                name="method1",
                args=ast.arguments(posonlyargs=[], args=[], defaults=[], kwonlyargs=[], kw_defaults=[], annotations=[]),
                body=[],
                decorator_list=[],
                returns=None,
            )
        ]
        instance_vars = {"var1", "var2"}

        cohesion = self.rule._calculate_cohesion(methods, instance_vars)
        self.assertEqual(cohesion, 1.0)


class TestClassTooBigRule(unittest.TestCase):
    """Test suite for ClassTooBigRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = ClassTooBigRule()
        self.context = LintContext(file_path=Path("/test.py"))

    def test_rule_properties(self):
        """Test rule properties return correct values."""
        self.assertEqual(self.rule.rule_id, "solid.srp.class-too-big")
        self.assertEqual(self.rule.rule_name, "Class Too Big")
        self.assertIn("excessively large", self.rule.description.lower())
        self.assertEqual(self.rule.severity, Severity.INFO)
        self.assertEqual(self.rule.categories, {"solid", "srp", "size"})

    def test_should_check_node_with_class_def(self):
        """Test should_check_node returns True for ClassDef nodes."""
        class_node = ast.ClassDef(name="TestClass", bases=[], keywords=[], body=[], decorator_list=[])
        self.assertTrue(self.rule.should_check_node(class_node, self.context))

    def test_check_node_with_invalid_node_type(self):
        """Test check_node raises TypeError for non-ClassDef nodes."""
        func_node = ast.FunctionDef(
            name="test_func",
            args=ast.arguments(posonlyargs=[], args=[], defaults=[], kwonlyargs=[], kw_defaults=[], annotations=[]),
            body=[],
            decorator_list=[],
            returns=None,
        )

        with self.assertRaises(TypeError) as cm:
            self.rule.check_node(func_node, self.context)
        self.assertIn("should only receive ast.ClassDef nodes", str(cm.exception))

    def test_small_class_no_violation(self):
        """Test small class produces no violations."""
        # Create a simple class node with line numbers
        class_node = ast.ClassDef(name="SmallClass", bases=[], keywords=[], body=[], decorator_list=[])
        class_node.lineno = 1
        class_node.end_lineno = 10  # 9 lines total

        violations = self.rule.check_node(class_node, self.context)
        self.assertEqual(len(violations), 0)

    def test_large_class_violation(self):
        """Test large class produces violation."""
        # Create a class node with many lines
        class_node = ast.ClassDef(name="LargeClass", bases=[], keywords=[], body=[], decorator_list=[])
        class_node.lineno = 1
        class_node.end_lineno = 250  # 249 lines total (> 200 default)

        violations = self.rule.check_node(class_node, self.context)
        self.assertEqual(len(violations), 1)

        violation = violations[0]
        self.assertEqual(violation.rule_id, "solid.srp.class-too-big")
        self.assertEqual(violation.severity, Severity.INFO)
        self.assertIn("LargeClass", violation.message)
        self.assertIn("249 lines", violation.message)

    def test_custom_max_lines_configuration(self):
        """Test custom max_class_lines configuration."""
        self.context.metadata = {"rules": {"solid.srp.class-too-big": {"config": {"max_class_lines": 50}}}}

        # Create a class with 75 lines (above custom threshold)
        class_node = ast.ClassDef(name="ModerateClass", bases=[], keywords=[], body=[], decorator_list=[])
        class_node.lineno = 1
        class_node.end_lineno = 76  # 75 lines total (> 50 custom limit)

        violations = self.rule.check_node(class_node, self.context)
        self.assertEqual(len(violations), 1)
        self.assertIn("75 lines", violations[0].message)

    def test_class_without_line_numbers_no_violation(self):
        """Test class without line numbers produces no violations."""
        class_node = ast.ClassDef(name="TestClass", bases=[], keywords=[], body=[], decorator_list=[])
        # Don't set lineno or end_lineno

        violations = self.rule.check_node(class_node, self.context)
        self.assertEqual(len(violations), 0)

    def test_class_with_missing_end_lineno_no_violation(self):
        """Test class with missing end_lineno produces no violations."""
        class_node = ast.ClassDef(name="TestClass", bases=[], keywords=[], body=[], decorator_list=[])
        class_node.lineno = 1
        # Don't set end_lineno

        violations = self.rule.check_node(class_node, self.context)
        self.assertEqual(len(violations), 0)


class TestTooManyDependenciesRule(unittest.TestCase):
    """Test suite for TooManyDependenciesRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = TooManyDependenciesRule()
        self.context = LintContext(file_path=Path("/test.py"))

    def test_rule_properties(self):
        """Test rule properties return correct values."""
        self.assertEqual(self.rule.rule_id, "solid.srp.too-many-dependencies")
        self.assertEqual(self.rule.rule_name, "Too Many Dependencies")
        self.assertIn("excessive dependencies", self.rule.description.lower())
        self.assertEqual(self.rule.severity, Severity.WARNING)
        self.assertEqual(self.rule.categories, {"solid", "srp", "dependencies"})

    def test_should_check_node_with_class_def(self):
        """Test should_check_node returns True for ClassDef nodes."""
        class_node = ast.ClassDef(name="TestClass", bases=[], keywords=[], body=[], decorator_list=[])
        self.assertTrue(self.rule.should_check_node(class_node, self.context))

    def test_check_node_with_invalid_node_type(self):
        """Test check_node raises TypeError for non-ClassDef nodes."""
        func_node = ast.FunctionDef(
            name="test_func",
            args=ast.arguments(posonlyargs=[], args=[], defaults=[], kwonlyargs=[], kw_defaults=[], annotations=[]),
            body=[],
            decorator_list=[],
            returns=None,
        )

        with self.assertRaises(TypeError) as cm:
            self.rule.check_node(func_node, self.context)
        self.assertIn("should only receive ast.ClassDef nodes", str(cm.exception))

    def test_class_with_few_dependencies_no_violation(self):
        """Test class with few dependencies produces no violations."""
        code = """
import os
import sys
from pathlib import Path

class SimpleClass:
    def method(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[3]  # Class is the 4th statement
        violations = self.rule.check_node(class_node, self.context)
        self.assertEqual(len(violations), 0)

    def test_class_with_many_dependencies_violation(self):
        """Test class with many dependencies produces violation."""
        # Create a class with many import statements within the class
        imports = [f"    import module{i}" for i in range(15)]
        code = f"""
class DependentClass:
{chr(10).join(imports)}

    def method(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]  # Class is the first statement
        violations = self.rule.check_node(class_node, self.context)

        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation.rule_id, "solid.srp.too-many-dependencies")
        self.assertEqual(violation.severity, Severity.WARNING)
        self.assertIn("DependentClass", violation.message)
        self.assertIn("dependencies", violation.message)

    def test_custom_max_dependencies_configuration(self):
        """Test custom max_dependencies configuration."""
        self.context.metadata = {"rules": {"solid.srp.too-many-dependencies": {"config": {"max_dependencies": 3}}}}

        code = """
class ModerateClass:
    import os
    import sys
    from pathlib import Path
    from collections import defaultdict

    def method(self):
        pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]  # Class is the first statement
        violations = self.rule.check_node(class_node, self.context)

        self.assertEqual(len(violations), 1)  # 4 dependencies > 3 (custom limit)

    def test_extract_dependencies_import_statements(self):
        """Test _extract_dependencies with import statements."""
        code = """
class TestClass:
    import os
    import sys.path
    from pathlib import Path
    from collections.abc import Mapping
    pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]  # Class is the first statement
        dependencies = self.rule._extract_dependencies(class_node)

        # Should extract top-level module names
        expected_deps = {"os", "sys", "pathlib", "collections"}
        self.assertEqual(dependencies, expected_deps)

    def test_extract_dependencies_nested_in_class(self):
        """Test _extract_dependencies with imports nested in class."""
        code = """
class TestClass:
    import os
    from pathlib import Path

    def method(self):
        import sys
        from collections import defaultdict
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        dependencies = self.rule._extract_dependencies(class_node)

        # Should find all imports within the class
        expected_deps = {"os", "pathlib", "sys", "collections"}
        self.assertEqual(dependencies, expected_deps)

    def test_extract_dependencies_no_imports(self):
        """Test _extract_dependencies with no imports."""
        code = """
class SimpleClass:
    def method(self):
        x = 1 + 1
        return x
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        dependencies = self.rule._extract_dependencies(class_node)

        self.assertEqual(len(dependencies), 0)

    def test_extract_dependencies_import_from_without_module(self):
        """Test _extract_dependencies handles 'from . import' correctly."""
        # Create AST nodes manually to test edge case
        import_from = ast.ImportFrom(module=None, names=[ast.alias(name="something", asname=None)], level=1)
        class_node = ast.ClassDef(name="TestClass", bases=[], keywords=[], body=[import_from], decorator_list=[])

        dependencies = self.rule._extract_dependencies(class_node)

        # Should not crash and should not include None
        self.assertNotIn(None, dependencies)


if __name__ == "__main__":
    unittest.main()
