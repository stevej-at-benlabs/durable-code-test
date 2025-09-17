#!/usr/bin/env python3
"""
Purpose: Unit tests for SOLID principle rules
Scope: Tests for SRP and other SOLID principle detection rules
Overview: This module tests the SOLID principle rules including detection of
    multiple responsibilities, low cohesion, too many methods, and other
    violations that indicate poor adherence to SOLID principles.
Dependencies: unittest, ast, SOLID rules
"""

import unittest
import ast
from pathlib import Path

import sys
sys.path.insert(0, '/home/stevejackson/Projects/durable-code-test/tools')

from design_linters.framework.interfaces import LintContext, Severity
from design_linters.rules.solid.srp_rules import (
    TooManyMethodsRule,
    TooManyResponsibilitiesRule,
    LowCohesionRule,
    ClassTooBigRule,
    TooManyDependenciesRule
)


class TestTooManyMethodsRule(unittest.TestCase):
    """Test the TooManyMethodsRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = TooManyMethodsRule()

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, "solid.srp.too-many-methods")
        self.assertEqual(self.rule.severity, Severity.WARNING)
        self.assertIn("solid", self.rule.categories)
        self.assertIn("srp", self.rule.categories)

    def test_class_with_too_many_methods(self):
        """Test detection of class with excessive methods."""
        code = """
class OverloadedClass:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
    def method9(self): pass
    def method10(self): pass
"""

        tree = ast.parse(code)
        context = LintContext(
            file_path=Path('/src/file.py'),
            file_content=code,
            metadata={'rules': {'solid.srp.too-many-methods': {'config': {'max_methods': 7}}}}
        )

        # Find the class node
        class_node = tree.body[0]
        violations = self.rule.check_node(class_node, context)

        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].rule_id, "solid.srp.too-many-methods")
        self.assertIn("10 methods", violations[0].message)

    def test_class_within_limits(self):
        """Test class with acceptable number of methods."""
        code = """
class NormalClass:
    def __init__(self):
        pass

    def method1(self):
        pass

    def method2(self):
        pass
"""

        tree = ast.parse(code)
        context = LintContext(
            file_path=Path('/src/file.py'),
            file_content=code
        )

        class_node = tree.body[0]
        violations = self.rule.check_node(class_node, context)

        self.assertEqual(len(violations), 0)

    def test_special_methods_excluded(self):
        """Test that special methods are not counted."""
        code = """
class ClassWithSpecialMethods:
    def __init__(self): pass
    def __str__(self): pass
    def __repr__(self): pass
    def __eq__(self): pass
    def regular_method1(self): pass
    def regular_method2(self): pass
    def regular_method3(self): pass
"""

        tree = ast.parse(code)
        context = LintContext(
            file_path=Path('/src/file.py'),
            file_content=code,
            metadata={'rules': {'solid.srp.too-many-methods': {'max_methods': 5}}}
        )

        class_node = tree.body[0]
        violations = self.rule.check_node(class_node, context)

        # Should not violate as special methods are excluded
        self.assertEqual(len(violations), 0)


class TestTooManyResponsibilitiesRule(unittest.TestCase):
    """Test the TooManyResponsibilitiesRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = TooManyResponsibilitiesRule()

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, "solid.srp.multiple-responsibilities")
        self.assertEqual(self.rule.severity, Severity.ERROR)
        self.assertIn("solid", self.rule.categories)

    def test_multiple_responsibilities_detection(self):
        """Test detection of class with multiple responsibilities."""
        code = """
class MultiResponsibilityClass:
    def load_data(self): pass
    def save_data(self): pass
    def validate_input(self): pass
    def verify_data(self): pass
    def send_email(self): pass
    def notify_users(self): pass
    def calculate_total(self): pass
    def compute_average(self): pass
    def render_html(self): pass
    def format_output(self): pass
"""

        tree = ast.parse(code)
        context = LintContext(
            file_path=Path('/src/file.py'),
            file_content=code
        )

        class_node = tree.body[0]
        violations = self.rule.check_node(class_node, context)

        # Should detect multiple responsibilities
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].rule_id, "solid.srp.multiple-responsibilities")
        self.assertIn("multiple responsibilities", violations[0].message.lower())

    def test_single_responsibility_class(self):
        """Test class with single responsibility."""
        code = """
class DataValidator:
    def validate_email(self): pass
    def validate_phone(self): pass
    def validate_address(self): pass
    def check_format(self): pass
    def verify_integrity(self): pass
"""

        tree = ast.parse(code)
        context = LintContext(
            file_path=Path('/src/file.py'),
            file_content=code
        )

        class_node = tree.body[0]
        violations = self.rule.check_node(class_node, context)

        # All methods are validation-related, single responsibility
        self.assertEqual(len(violations), 0)


class TestLowCohesionRule(unittest.TestCase):
    """Test the LowCohesionRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = LowCohesionRule()

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, "solid.srp.low-cohesion")
        self.assertEqual(self.rule.severity, Severity.WARNING)
        self.assertIn("cohesion", self.rule.categories)

    def test_low_cohesion_detection(self):
        """Test detection of class with low cohesion."""
        code = """
class LowCohesionClass:
    def __init__(self):
        self.data1 = []
        self.data2 = {}
        self.data3 = None

    def method1(self):
        # Only uses data1
        return self.data1

    def method2(self):
        # Only uses data2
        return self.data2

    def method3(self):
        # Only uses data3
        return self.data3

    def method4(self):
        # Uses no instance variables
        return "static"
"""

        violations = self.rule.check('/test/file.py', code)

        # Should detect low cohesion
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].rule_id, "solid.srp.low-cohesion")

    def test_high_cohesion_class(self):
        """Test class with high cohesion."""
        code = """
class HighCohesionClass:
    def __init__(self):
        self.data = []
        self.count = 0

    def add(self, item):
        self.data.append(item)
        self.count += 1

    def remove(self, item):
        self.data.remove(item)
        self.count -= 1

    def get_size(self):
        return self.count

    def get_data(self):
        return self.data
"""

        violations = self.rule.check('/test/file.py', code)

        # Should not detect low cohesion
        self.assertEqual(len(violations), 0)


class TestClassTooBigRule(unittest.TestCase):
    """Test the ClassTooBigRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = ClassTooBigRule()

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, "solid.srp.class-too-big")
        self.assertEqual(self.rule.severity, Severity.INFO)
        self.assertIn("size", self.rule.categories)

    def test_large_class_detection(self):
        """Test detection of excessively large class."""
        # Generate a large class
        methods = []
        for i in range(50):
            methods.append(f"""
    def method{i}(self):
        # Some implementation
        x = 1
        y = 2
        z = x + y
        return z
""")

        code = f"""
class LargeClass:
    def __init__(self):
        self.data = []
{''.join(methods)}
"""

        tree = ast.parse(code)
        context = LintContext(
            file_path=Path('/src/file.py'),
            file_content=code,
            metadata={'rules': {'solid.srp.class-too-big': {'max_lines': 200}}}
        )

        class_node = tree.body[0]
        violations = self.rule.check_node(class_node, context)

        # Should detect large class
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].rule_id, "solid.srp.class-too-big")

    def test_normal_size_class(self):
        """Test class with acceptable size."""
        code = """
class NormalSizeClass:
    def __init__(self):
        self.data = []

    def add(self, item):
        self.data.append(item)

    def remove(self, item):
        self.data.remove(item)

    def clear(self):
        self.data = []
"""

        tree = ast.parse(code)
        context = LintContext(
            file_path=Path('/src/file.py'),
            file_content=code
        )

        class_node = tree.body[0]
        violations = self.rule.check_node(class_node, context)

        self.assertEqual(len(violations), 0)


class TestTooManyDependenciesRule(unittest.TestCase):
    """Test the TooManyDependenciesRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = TooManyDependenciesRule()

    def test_rule_properties(self):
        """Test rule metadata."""
        self.assertEqual(self.rule.rule_id, "solid.srp.too-many-dependencies")
        self.assertEqual(self.rule.severity, Severity.WARNING)
        self.assertIn("dependencies", self.rule.categories)

    def test_many_dependencies_detection(self):
        """Test detection of class with too many dependencies."""
        code = """
class HighDependencyClass:
    def __init__(self, db_connection, cache_client, logger,
                 email_service, auth_service, payment_gateway,
                 notification_service, analytics_tracker):
        self.db = db_connection
        self.cache = cache_client
        self.logger = logger
        self.email = email_service
        self.auth = auth_service
        self.payment = payment_gateway
        self.notifications = notification_service
        self.analytics = analytics_tracker

    def process(self):
        self.logger.info("Processing")
        data = self.db.fetch()
        self.cache.store(data)
        self.email.send()
"""

        tree = ast.parse(code)
        context = LintContext(
            file_path=Path('/src/file.py'),
            file_content=code,
            metadata={'rules': {'solid.srp.too-many-dependencies': {'max_dependencies': 5}}}
        )

        class_node = tree.body[0]
        violations = self.rule.check_node(class_node, context)

        # Should detect too many dependencies
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].rule_id, "solid.srp.too-many-dependencies")
        self.assertIn("8 dependencies", violations[0].message)

    def test_acceptable_dependencies(self):
        """Test class with acceptable number of dependencies."""
        code = """
class NormalDependencyClass:
    def __init__(self, db_connection, logger):
        self.db = db_connection
        self.logger = logger

    def process(self):
        self.logger.info("Processing")
        return self.db.fetch()
"""

        tree = ast.parse(code)
        context = LintContext(
            file_path=Path('/src/file.py'),
            file_content=code
        )

        class_node = tree.body[0]
        violations = self.rule.check_node(class_node, context)

        self.assertEqual(len(violations), 0)


if __name__ == '__main__':
    unittest.main()
