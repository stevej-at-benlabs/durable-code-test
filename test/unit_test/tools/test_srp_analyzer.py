#!/usr/bin/env python3
"""Unit tests for the Single Responsibility Principle Analyzer."""

import ast
import os
import tempfile
from dataclasses import replace
from pathlib import Path

import pytest
from __init__ import DEFAULT_SRP_THRESHOLDS, Severity
from srp_analyzer import SRPAnalyzer, SRPViolation, analyze_directory, analyze_file


class TestSRPAnalyzer:
    """Test suite for SRP violation detection."""

    def test_detects_too_many_methods(self):
        """Test detection of classes with too many methods."""
        code = """
class UserManager:
    def create_user(self): pass
    def delete_user(self): pass
    def update_user(self): pass
    def get_user(self): pass
    def list_users(self): pass
    def validate_user(self): pass
    def authenticate_user(self): pass
    def authorize_user(self): pass  # 8 methods - over threshold of 7
        """
        tree = ast.parse(code)
        analyzer = SRPAnalyzer("test.py")
        analyzer.visit(tree)

        assert len(analyzer.violations) == 1
        assert analyzer.violations[0].class_name == "UserManager"
        assert any(
            "Too many methods" in reason for reason in analyzer.violations[0].reasons
        )

    def test_detects_multiple_responsibilities(self):
        """Test detection of classes with multiple responsibility groups."""
        code = """
class UserManagerAndEmailer:
    def create_user(self): pass
    def update_user(self): pass
    def delete_user(self): pass
    def send_email(self): pass
    def validate_email(self): pass
    def format_email(self): pass
        """
        tree = ast.parse(code)
        analyzer = SRPAnalyzer("test.py")
        analyzer.visit(tree)

        # Should detect multiple responsibility groups
        assert len(analyzer.violations) > 0
        violation = analyzer.violations[0]
        assert any(
            "Multiple responsibility groups" in reason for reason in violation.reasons
        )

    def test_detects_large_classes(self):
        """Test detection of classes that are too large."""
        # Generate a large class
        methods = "\n    ".join([f"def method_{i}(self): pass" for i in range(50)])
        code = f"""
class LargeClass:
    {methods}
        """
        tree = ast.parse(code)

        # Use strict thresholds for testing
        strict_thresholds = replace(DEFAULT_SRP_THRESHOLDS, MAX_CLASS_LINES=100)
        analyzer = SRPAnalyzer("test.py", strict_thresholds)
        analyzer.visit(tree)

        assert len(analyzer.violations) > 0
        assert any(
            "Class too large" in reason for reason in analyzer.violations[0].reasons
        )

    def test_detects_low_cohesion(self):
        """Test detection of low cohesion in classes."""
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

    # Methods don't share instance variables - low cohesion
        """
        tree = ast.parse(code)
        analyzer = SRPAnalyzer("test.py")
        analyzer.visit(tree)

        # The cohesion calculation should detect this
        metrics = analyzer._analyze_class(tree.body[0])
        assert metrics["cohesion_score"] < 0.5

    def test_class_name_with_and(self):
        """Test detection of 'and' in class names."""
        code = """
class UserAndOrderManager:
    def manage(self): pass
        """
        tree = ast.parse(code)
        analyzer = SRPAnalyzer("test.py")
        analyzer.visit(tree)

        assert len(analyzer.violations) == 1
        assert any(
            "Class name contains 'and'" in reason
            for reason in analyzer.violations[0].reasons
        )

    def test_severity_levels(self):
        """Test that severity levels are assigned correctly."""
        # Minor violation - should be INFO
        code_info = """
class MinorViolation:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass  # Just over threshold
        """
        tree = ast.parse(code_info)
        analyzer = SRPAnalyzer("test.py")
        analyzer.visit(tree)

        if analyzer.violations:
            assert (
                analyzer.violations[0].severity == Severity.INFO
                or analyzer.violations[0].severity == Severity.WARNING
            )

        # Major violation - should be ERROR
        code_error = """
class MajorViolationAndMultipleProblems:
    def __init__(self):
        self.a = 1; self.b = 2; self.c = 3; self.d = 4
        self.e = 5; self.f = 6; self.g = 7; self.h = 8

    def get_a(self): return self.a
    def get_b(self): return self.b
    def set_c(self): self.c = 0
    def set_d(self): self.d = 0
    def calculate_e(self): return self.e * 2
    def calculate_f(self): return self.f * 2
    def send_notification(self): pass
    def send_email(self): pass
    def validate_data(self): pass
    def validate_input(self): pass
        """
        tree = ast.parse(code_error)
        analyzer = SRPAnalyzer("test.py")
        analyzer.visit(tree)

        assert len(analyzer.violations) == 1
        # This should have multiple violations leading to ERROR severity
        assert len(analyzer.violations[0].reasons) >= 3

    def test_custom_thresholds(self):
        """Test using custom thresholds."""
        code = """
class SmallClass:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
        """
        tree = ast.parse(code)

        # Strict thresholds - should detect violation
        strict_thresholds = replace(DEFAULT_SRP_THRESHOLDS, MAX_METHODS_PER_CLASS=2)
        analyzer = SRPAnalyzer("test.py", strict_thresholds)
        analyzer.visit(tree)
        assert len(analyzer.violations) == 1

        # Lenient thresholds - should not detect violation
        lenient_thresholds = replace(DEFAULT_SRP_THRESHOLDS, MAX_METHODS_PER_CLASS=10)
        analyzer = SRPAnalyzer("test.py", lenient_thresholds)
        analyzer.visit(tree)
        assert len(analyzer.violations) == 0


class TestSRPViolation:
    """Test the SRPViolation class."""

    def test_to_dict(self):
        """Test conversion to dictionary."""
        violation = SRPViolation(
            "test.py",
            "TestClass",
            10,
            Severity.WARNING,
            ["Too many methods", "Low cohesion"],
        )
        result = violation.to_dict()

        assert result["file"] == "test.py"
        assert result["class"] == "TestClass"
        assert result["line"] == 10
        assert result["severity"] == Severity.WARNING
        assert result["reasons"] == ["Too many methods", "Low cohesion"]


class TestResponsibilityGrouping:
    """Test method responsibility grouping."""

    def test_groups_methods_by_prefix(self):
        """Test that methods are grouped by their prefixes."""
        code = """
class MixedResponsibilities:
    def get_user(self): pass
    def get_order(self): pass
    def save_user(self): pass
    def save_order(self): pass
    def validate_user(self): pass
    def send_email(self): pass
        """
        tree = ast.parse(code)
        analyzer = SRPAnalyzer("test.py")

        methods = [n for n in tree.body[0].body if isinstance(n, ast.FunctionDef)]
        groups = analyzer._group_methods_by_responsibility(methods)

        assert "data_access" in groups  # get_* methods
        assert "data_mutation" in groups  # save_* methods
        assert "validation" in groups  # validate_* methods
        assert "notification" in groups  # send_* methods

        assert len(groups["data_access"]) == 2
        assert len(groups["data_mutation"]) == 2

    def test_uncategorized_methods(self):
        """Test that uncategorized methods go to 'other' group."""
        code = """
class CustomMethods:
    def custom_method(self): pass
    def another_custom(self): pass
        """
        tree = ast.parse(code)
        analyzer = SRPAnalyzer("test.py")

        methods = [n for n in tree.body[0].body if isinstance(n, ast.FunctionDef)]
        groups = analyzer._group_methods_by_responsibility(methods)

        assert "other" in groups
        assert len(groups["other"]) == 2


class TestFileAnalysis:
    """Test file and directory analysis functions."""

    def test_analyze_file(self):
        """Test analyzing a single file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
class GoodClass:
    def method1(self): pass
    def method2(self): pass

class ProblematicClassWithManyMethods:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
    def method9(self): pass
            """
            )
            f.flush()

            violations = analyze_file(f.name)

            # Clean up
            os.unlink(f.name)

            # Should only find violations in ProblematicClass
            assert len(violations) == 1
            assert violations[0].class_name == "ProblematicClassWithManyMethods"

    def test_analyze_directory(self):
        """Test analyzing a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            file1 = Path(tmpdir) / "module1.py"
            file1.write_text(
                """
class SimpleClass:
    def method(self): pass

class ComplexClassWithManyResponsibilities:
    def get_data(self): pass
    def set_data(self): pass
    def validate_data(self): pass
    def send_notification(self): pass
    def calculate_metrics(self): pass
    def render_output(self): pass
    def authenticate(self): pass
    def configure(self): pass
            """
            )

            # Excluded file
            test_file = Path(tmpdir) / "test_module.py"
            test_file.write_text(
                """
class TestClass:
    def test_method1(self): pass
    def test_method2(self): pass
            """
            )

            violations = analyze_directory(tmpdir)

            # Should find violations in ComplexClass
            assert len(violations) >= 1
            assert any(
                v.class_name == "ComplexClassWithManyResponsibilities"
                for v in violations
            )


class TestDependencyExtraction:
    """Test dependency extraction."""

    def test_extracts_imports(self):
        """Test that imports are correctly extracted."""
        code = """
import os
import sys
from pathlib import Path
from typing import List

class MyClass:
    def method(self):
        import json
        return json.dumps({})
        """
        tree = ast.parse(code)
        analyzer = SRPAnalyzer("test.py")

        dependencies = analyzer._extract_dependencies(tree.body[-1])  # MyClass

        # Should find json (local import within class)
        assert "json" in dependencies


class TestInstanceVariables:
    """Test instance variable extraction."""

    def test_extracts_instance_variables(self):
        """Test that instance variables are correctly extracted."""
        code = """
class MyClass:
    def __init__(self):
        self.var1 = 1
        self.var2 = 2

    def method(self):
        self.var3 = 3
        return self.var1 + self.var2
        """
        tree = ast.parse(code)
        analyzer = SRPAnalyzer("test.py")

        instance_vars = analyzer._extract_instance_variables(tree.body[0])

        assert "var1" in instance_vars
        assert "var2" in instance_vars
        assert "var3" in instance_vars


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
