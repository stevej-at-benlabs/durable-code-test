#!/usr/bin/env python3
"""
Purpose: Additional coverage tests for design linters
Scope: More comprehensive testing to reach 90% coverage
Overview: This module provides additional tests to exercise more code paths.
Dependencies: unittest, all modules
"""

import unittest
import ast
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open

import sys
sys.path.insert(0, '/home/stevejackson/Projects/durable-code-test/tools')


class TestMoreInterfacesCoverage(unittest.TestCase):
    """Additional tests for interfaces module."""

    def test_abstract_lint_rule_implementation(self):
        """Test concrete LintRule implementation."""
        from design_linters.framework.interfaces import LintRule, Severity

        class TestRule(LintRule):
            @property
            def rule_id(self):
                return "test.rule"

            @property
            def rule_name(self):
                return "Test Rule"

            @property
            def description(self):
                return "Test description"

            @property
            def severity(self):
                return Severity.WARNING

            @property
            def categories(self):
                return {"test"}

            def check(self, context):
                return []

        rule = TestRule()

        # Test get_configuration with various metadata
        config = rule.get_configuration(None)
        self.assertEqual(config, {})

        config = rule.get_configuration({})
        self.assertEqual(config, {})

        metadata = {
            'rules': {
                'test.rule': {
                    'config': {'param1': 'value1'}
                }
            }
        }
        config = rule.get_configuration(metadata)
        self.assertEqual(config['param1'], 'value1')

        # Test is_enabled
        self.assertTrue(rule.is_enabled(None))
        self.assertTrue(rule.is_enabled({}))

        metadata_disabled = {
            'rules': {
                'test.rule': {
                    'enabled': False
                }
            }
        }
        self.assertFalse(rule.is_enabled(metadata_disabled))

    def test_ast_lint_rule_implementation(self):
        """Test concrete ASTLintRule implementation."""
        from design_linters.framework.interfaces import ASTLintRule, Severity, LintContext, LintViolation

        class TestASTRule(ASTLintRule):
            @property
            def rule_id(self):
                return "test.ast.rule"

            @property
            def rule_name(self):
                return "Test AST Rule"

            @property
            def description(self):
                return "Test AST description"

            @property
            def severity(self):
                return Severity.INFO

            @property
            def categories(self):
                return {"ast", "test"}

            def should_check_node(self, node, context):
                return isinstance(node, ast.Constant) and isinstance(node.value, int)

            def check_node(self, node, context):
                if node.value == 42:
                    return [LintViolation(
                        rule_id=self.rule_id,
                        file_path=str(context.file_path),
                        line=node.lineno,
                        column=node.col_offset,
                        severity=self.severity,
                        message="Found 42",
                        description="Magic number",
                        suggestion="Use constant"
                    )]
                return []

        rule = TestASTRule()
        code = "x = 42\ny = 10"
        context = LintContext(
            file_path=Path('/test.py'),
            file_content=code,
            ast_tree=ast.parse(code)
        )

        violations = rule.check(context)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].message, "Found 42")


class TestRuleImplementationsCoverage(unittest.TestCase):
    """Test rule implementations with various scenarios."""

    def test_magic_number_rule_coverage(self):
        """Test MagicNumberRule with various scenarios."""
        from design_linters.rules.literals.magic_number_rules import MagicNumberRule
        from design_linters.framework.interfaces import LintContext

        rule = MagicNumberRule()

        # Test _is_acceptable_context with various scenarios
        code = "x = 42"
        context = LintContext(
            file_path=Path('/test/test_file.py'),  # Test file path
            file_content=code,
            ast_tree=ast.parse(code),
            current_function='config_setup',  # Config function
            node_stack=[]
        )

        # Parse and test context checking
        tree = ast.parse(code)
        const_node = tree.body[0].value  # The constant 42

        # Test various acceptable contexts
        acceptable = rule._is_acceptable_context(const_node, context, {})
        # Should be True because it's in a test file
        self.assertTrue(acceptable)

        # Test with production file
        context.file_path = Path('/src/main.py')
        acceptable = rule._is_acceptable_context(const_node, context, {})
        # Should still be acceptable due to config function name
        self.assertTrue(acceptable)

        # Test _is_in_range_context
        range_code = "for i in range(10): pass"
        range_tree = ast.parse(range_code)
        # Build node stack to simulate being inside range call
        for_node = range_tree.body[0]
        call_node = for_node.iter  # range(10)
        const_node = call_node.args[0]  # 10

        context.node_stack = [const_node, call_node, for_node]
        is_range = rule._is_in_range_context(context)
        self.assertTrue(is_range)

        # Test _is_in_math_context
        math_code = "result = x + 42"
        math_tree = ast.parse(math_code)
        binop_node = math_tree.body[0].value
        const_node = binop_node.right

        context.node_stack = [const_node, binop_node]
        is_math = rule._is_in_math_context(context)
        self.assertTrue(is_math)

        # Test _generate_constant_suggestion
        suggestion = rule._generate_constant_suggestion(60, context)
        self.assertIn("SECONDS_PER_MINUTE", suggestion)

        suggestion = rule._generate_constant_suggestion(3600, context)
        self.assertIn("SECONDS_PER_HOUR", suggestion)

    def test_magic_string_rule_coverage(self):
        """Test MagicStringRule with various scenarios."""
        from design_linters.rules.literals.magic_string_rules import MagicStringRule
        from design_linters.framework.interfaces import LintContext

        rule = MagicStringRule()

        # Test various string patterns
        code = 'url = "https://api.example.com"'
        context = LintContext(
            file_path=Path('/src/main.py'),
            file_content=code,
            ast_tree=ast.parse(code)
        )

        # Test _looks_like_config
        self.assertTrue(rule._looks_like_config("API_KEY"))
        self.assertTrue(rule._looks_like_config("database.host"))
        self.assertTrue(rule._looks_like_config("--verbose"))
        self.assertFalse(rule._looks_like_config("hello"))

        # Test _looks_like_path_or_url
        self.assertTrue(rule._looks_like_path_or_url("/var/log/app.log"))
        self.assertTrue(rule._looks_like_path_or_url("C:\\Windows\\System32"))
        self.assertTrue(rule._looks_like_path_or_url("https://example.com"))
        self.assertFalse(rule._looks_like_path_or_url("hello"))

        # Test _looks_like_user_message
        self.assertTrue(rule._looks_like_user_message("Error: Something went wrong.", context))
        self.assertTrue(rule._looks_like_user_message("Processing complete!", context))
        self.assertFalse(rule._looks_like_user_message("hello", context))

        # Test _looks_like_query
        self.assertTrue(rule._looks_like_query("SELECT * FROM users"))
        self.assertTrue(rule._looks_like_query("INSERT INTO table VALUES"))
        self.assertFalse(rule._looks_like_query("hello"))

        # Test _looks_like_api_related
        self.assertTrue(rule._looks_like_api_related("/api/v1/users"))
        self.assertTrue(rule._looks_like_api_related("Bearer token123"))
        self.assertTrue(rule._looks_like_api_related("api_key"))
        self.assertFalse(rule._looks_like_api_related("hello"))

        # Test _generate_string_constant_suggestion
        suggestion = rule._generate_string_constant_suggestion("API_CONFIG", context)
        self.assertIn("CONFIG_VALUE", suggestion)

        suggestion = rule._generate_string_constant_suggestion("https://api.com", context)
        self.assertIn("API_ENDPOINT", suggestion)

        suggestion = rule._generate_string_constant_suggestion("Error: Failed", context)
        self.assertIn("ERROR_MESSAGE", suggestion)

    def test_print_statement_rule_coverage(self):
        """Test PrintStatementRule with various scenarios."""
        from design_linters.rules.style.print_statement_rules import PrintStatementRule
        from design_linters.framework.interfaces import LintContext

        rule = PrintStatementRule()

        # Test _is_debug_function
        context = LintContext(
            file_path=Path('/src/main.py'),
            current_function='debug_info'
        )
        self.assertTrue(rule._is_debug_function(context))

        context.current_function = 'display_results'
        self.assertTrue(rule._is_debug_function(context))

        context.current_function = 'process_data'
        self.assertFalse(rule._is_debug_function(context))

        # Test _is_main_block
        main_code = '''
if __name__ == "__main__":
    print("Starting")
'''
        tree = ast.parse(main_code)
        if_node = tree.body[0]
        print_node = if_node.body[0].value

        context = LintContext(
            file_path=Path('/src/main.py'),
            node_stack=[print_node, if_node.body[0], if_node]
        )
        self.assertTrue(rule._is_main_block(context))

        # Test _generate_logging_suggestion
        suggestion = rule._generate_logging_suggestion("ERROR: Failed to process")
        self.assertIn("logger.error", suggestion)

        suggestion = rule._generate_logging_suggestion("DEBUG: Processing item")
        self.assertIn("logger.debug", suggestion)

        suggestion = rule._generate_logging_suggestion("Hello world")
        self.assertIn("logger.info", suggestion)

    def test_nesting_rule_coverage(self):
        """Test nesting rules with various scenarios."""
        from design_linters.rules.style.nesting_rules import ExcessiveNestingRule
        from design_linters.framework.interfaces import LintContext

        rule = ExcessiveNestingRule()

        # Test _calculate_nesting_depth
        deep_code = '''
def deep_function():
    if condition1:
        for item in items:
            if condition2:
                while running:
                    if condition3:
                        process()
'''
        tree = ast.parse(deep_code)
        func_node = tree.body[0]

        depth = rule._calculate_nesting_depth(func_node)
        self.assertGreater(depth, 4)

        # Test _generate_refactoring_suggestion
        suggestion = rule._generate_refactoring_suggestion(depth, 'deep_function')
        self.assertIn("early return", suggestion.lower())

    def test_srp_rules_coverage(self):
        """Test SRP rules with various scenarios."""
        from design_linters.rules.solid.srp_rules import TooManyMethodsRule, TooManyResponsibilitiesRule
        from design_linters.framework.interfaces import LintContext

        # Test TooManyMethodsRule
        methods_rule = TooManyMethodsRule()

        # Test _count_methods
        class_code = '''
class TestClass:
    def __init__(self): pass
    def __str__(self): pass  # Special method
    def method1(self): pass
    def method2(self): pass
    def _private_method(self): pass
'''
        tree = ast.parse(class_code)
        class_node = tree.body[0]

        count = methods_rule._count_methods(class_node)
        self.assertEqual(count, 3)  # Excludes special methods

        # Test TooManyResponsibilitiesRule
        resp_rule = TooManyResponsibilitiesRule()

        # Test _analyze_method_responsibilities
        responsibilities = resp_rule._analyze_method_responsibilities(class_node)
        self.assertIsInstance(responsibilities, dict)

        # Test _get_responsibility_categories
        categories = resp_rule._get_responsibility_categories([
            'save_data', 'load_data', 'send_email', 'validate_input'
        ])
        self.assertGreater(len(categories), 1)


class TestCLIExtensiveCoverage(unittest.TestCase):
    """Extensive CLI coverage tests."""

    def test_cli_configuration_methods(self):
        """Test CLI configuration methods."""
        from design_linters.cli import DesignLinterCLI

        cli = DesignLinterCLI()

        # Test _get_strict_config
        strict_config = cli._get_strict_config()
        self.assertIn('rules', strict_config)

        # Test _get_lenient_config
        lenient_config = cli._get_lenient_config()
        self.assertIn('rules', lenient_config)

        # Test _get_legacy_config
        legacy_config = cli._get_legacy_config('srp')
        self.assertIn('rules', legacy_config)

        legacy_config = cli._get_legacy_config('magic')
        self.assertIn('rules', legacy_config)

        legacy_config = cli._get_legacy_config('print')
        self.assertIn('rules', legacy_config)

        legacy_config = cli._get_legacy_config('all')
        self.assertIn('rules', legacy_config)

        # Test _filter_by_severity
        from design_linters.framework.interfaces import LintViolation, Severity

        violations = [
            Mock(severity=Severity.ERROR),
            Mock(severity=Severity.WARNING),
            Mock(severity=Severity.INFO)
        ]

        filtered = cli._filter_by_severity(violations, 'error')
        self.assertEqual(len(filtered), 1)

        filtered = cli._filter_by_severity(violations, 'warning')
        self.assertEqual(len(filtered), 2)

        filtered = cli._filter_by_severity(violations, 'info')
        self.assertEqual(len(filtered), 3)

        # Test _determine_exit_code
        args = Mock()
        args.fail_on_error = False
        args.fail_on_warnings = False

        exit_code = cli._determine_exit_code([], args)
        self.assertEqual(exit_code, 0)

        args.fail_on_error = True
        error_violations = [Mock(severity=Severity.ERROR)]
        exit_code = cli._determine_exit_code(error_violations, args)
        self.assertEqual(exit_code, 1)

        warning_violations = [Mock(severity=Severity.WARNING)]
        exit_code = cli._determine_exit_code(warning_violations, args)
        self.assertEqual(exit_code, 0)  # No errors

        args.fail_on_warnings = True
        exit_code = cli._determine_exit_code(warning_violations, args)
        self.assertEqual(exit_code, 1)

    @patch('builtins.open', mock_open(read_data='rules:\n  test.rule:\n    enabled: true'))
    @patch('design_linters.cli.yaml.safe_load')
    def test_load_config_file_success(self, mock_yaml):
        """Test successful config file loading."""
        from design_linters.cli import DesignLinterCLI

        mock_yaml.return_value = {'rules': {'test.rule': {'enabled': True}}}

        cli = DesignLinterCLI()
        config = cli._load_config_file('config.yml')
        self.assertIn('rules', config)

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_load_config_file_not_found(self, mock_open):
        """Test config file not found."""
        from design_linters.cli import DesignLinterCLI

        cli = DesignLinterCLI()
        config = cli._load_config_file('nonexistent.yml')
        self.assertEqual(config, {})

    @patch('builtins.open', mock_open(read_data='invalid: yaml: content: ['))
    @patch('design_linters.cli.yaml.safe_load', side_effect=Exception("YAML error"))
    def test_load_config_file_yaml_error(self, mock_yaml):
        """Test YAML parsing error."""
        from design_linters.cli import DesignLinterCLI

        cli = DesignLinterCLI()
        config = cli._load_config_file('invalid.yml')
        self.assertEqual(config, {})


class TestFrameworkExtensiveCoverage(unittest.TestCase):
    """Extensive framework coverage tests."""

    @patch('design_linters.framework.DefaultRuleRegistry')
    @patch('design_linters.framework.DefaultLintOrchestrator')
    def test_create_orchestrator_comprehensive(self, mock_orchestrator_class, mock_registry_class):
        """Test create_orchestrator with comprehensive scenarios."""
        from design_linters.framework import create_orchestrator

        # Mock the classes
        mock_registry = Mock()
        mock_registry.discover_rules.return_value = 5
        mock_registry_class.return_value = mock_registry

        mock_orchestrator = Mock()
        mock_orchestrator.registry = mock_registry
        mock_orchestrator_class.return_value = mock_orchestrator

        # Test with empty packages
        result = create_orchestrator([], {})
        self.assertEqual(result, mock_orchestrator)

        # Test with packages and config
        packages = ['package1', 'package2']
        config = {'rules': {'test.rule': {'enabled': True}}}
        result = create_orchestrator(packages, config)
        self.assertEqual(result, mock_orchestrator)

        # Verify discovery was called
        mock_registry.discover_rules.assert_called_with(packages)

    @patch('design_linters.framework.DefaultRuleRegistry')
    def test_create_rule_registry_comprehensive(self, mock_registry_class):
        """Test create_rule_registry with comprehensive scenarios."""
        from design_linters.framework import create_rule_registry

        mock_registry = Mock()
        mock_registry.discover_rules.return_value = 3
        mock_registry_class.return_value = mock_registry

        # Test with packages
        packages = ['package1', 'package2']
        result = create_rule_registry(packages)
        self.assertEqual(result, mock_registry)

        # Verify discovery was called
        mock_registry.discover_rules.assert_called_with(packages)


if __name__ == '__main__':
    unittest.main()
