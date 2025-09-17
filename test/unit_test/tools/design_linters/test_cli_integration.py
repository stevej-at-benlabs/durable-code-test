#!/usr/bin/env python3
"""
Purpose: Integration tests for the unified CLI
Scope: Tests for the complete CLI functionality and integration
Overview: This module tests the unified CLI including command-line argument
    parsing, rule discovery, report generation, legacy compatibility modes,
    and end-to-end linting functionality.
Dependencies: unittest, tempfile, subprocess, CLI module
"""

import unittest
import tempfile
import os
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

sys.path.insert(0, '/home/stevejackson/Projects/durable-code-test/tools')

from design_linters.cli import DesignLinterCLI
from design_linters.framework.interfaces import LintViolation, Severity


class TestCLIArgumentParsing(unittest.TestCase):
    """Test CLI argument parsing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.cli = DesignLinterCLI()

    def test_parse_basic_arguments(self):
        """Test parsing basic command-line arguments."""
        args = self.cli._parse_arguments(['file.py'])

        self.assertEqual(args.paths, ['file.py'])
        self.assertEqual(args.format, 'text')
        self.assertFalse(args.verbose)

    def test_parse_format_argument(self):
        """Test parsing output format arguments."""
        args = self.cli._parse_arguments(['--format', 'json', 'file.py'])

        self.assertEqual(args.format, 'json')

    def test_parse_rules_argument(self):
        """Test parsing rule selection arguments."""
        args = self.cli._parse_arguments([
            '--rules', 'solid.srp.too-many-methods,literals.magic-number',
            'file.py'
        ])

        self.assertEqual(args.rules, 'solid.srp.too-many-methods,literals.magic-number')

    def test_parse_categories_argument(self):
        """Test parsing category selection arguments."""
        args = self.cli._parse_arguments([
            '--categories', 'solid,style',
            'file.py'
        ])

        self.assertEqual(args.categories, 'solid,style')

    def test_parse_severity_argument(self):
        """Test parsing minimum severity argument."""
        args = self.cli._parse_arguments([
            '--min-severity', 'warning',
            'file.py'
        ])

        self.assertEqual(args.min_severity, 'warning')

    def test_parse_legacy_mode(self):
        """Test parsing legacy compatibility mode."""
        args = self.cli._parse_arguments([
            '--legacy', 'srp',
            'file.py'
        ])

        self.assertEqual(args.legacy, 'srp')

    def test_parse_recursive_flag(self):
        """Test parsing recursive directory scanning flag."""
        args = self.cli._parse_arguments([
            '--recursive',
            'src/'
        ])

        self.assertTrue(args.recursive)

    def test_parse_output_file(self):
        """Test parsing output file argument."""
        args = self.cli._parse_arguments([
            '--output', 'report.txt',
            'file.py'
        ])

        self.assertEqual(args.output, 'report.txt')


class TestCLIExecution(unittest.TestCase):
    """Test CLI execution and integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.cli = DesignLinterCLI()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_file(self, filename, content):
        """Create a test file with given content."""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath

    @patch('design_linters.cli.CLI._create_orchestrator')
    def test_lint_single_file(self, mock_create_orchestrator):
        """Test linting a single file."""
        # Create test file
        test_file = self.create_test_file('test.py', """
def test():
    print("Hello")  # Should trigger print rule
    magic = 42  # Should trigger magic number rule
""")

        # Mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator.lint_file.return_value = [
            LintViolation(
                rule_id='style.print-statement',
                file_path=test_file,
                line=3,
                column=4,
                severity=Severity.WARNING,
                message='Print statement found',
                description='Use logging',
                suggestion='Use logger.info()'
            )
        ]
        mock_orchestrator.generate_report.return_value = "Test Report"
        mock_create_orchestrator.return_value = mock_orchestrator

        # Run CLI
        with patch('sys.argv', ['cli', test_file]):
            exit_code = self.cli.run([test_file])

        # Verify
        mock_orchestrator.lint_file.assert_called_once()
        self.assertEqual(exit_code, 0)

    @patch('design_linters.cli.CLI._create_orchestrator')
    def test_lint_directory(self, mock_create_orchestrator):
        """Test linting a directory recursively."""
        # Create test files
        self.create_test_file('file1.py', 'print("test")')
        os.makedirs(os.path.join(self.temp_dir, 'subdir'))
        self.create_test_file('subdir/file2.py', 'x = 999')

        # Mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator.lint_directory.return_value = []
        mock_orchestrator.generate_report.return_value = "✅ No violations"
        mock_create_orchestrator.return_value = mock_orchestrator

        # Run CLI
        exit_code = self.cli.run([self.temp_dir, '--recursive'])

        # Verify
        mock_orchestrator.lint_directory.assert_called_once()
        self.assertEqual(exit_code, 0)

    @patch('design_linters.cli.CLI._create_orchestrator')
    def test_fail_on_error_flag(self, mock_create_orchestrator):
        """Test --fail-on-error flag behavior."""
        test_file = self.create_test_file('test.py', 'print("test")')

        # Mock orchestrator with error violation
        mock_orchestrator = Mock()
        mock_orchestrator.lint_file.return_value = [
            LintViolation(
                rule_id='test.rule',
                file_path=test_file,
                line=1,
                column=0,
                severity=Severity.ERROR,
                message='Test error',
                description='Error',
                suggestion='Fix'
            )
        ]
        mock_orchestrator.generate_report.return_value = "Error Report"
        mock_create_orchestrator.return_value = mock_orchestrator

        # Run CLI with --fail-on-error
        exit_code = self.cli.run([test_file, '--fail-on-error'])

        # Should exit with error code
        self.assertNotEqual(exit_code, 0)

    @patch('design_linters.cli.CLI._create_orchestrator')
    @patch('builtins.print')
    def test_list_rules(self, mock_print, mock_create_orchestrator):
        """Test --list-rules functionality."""
        # Mock orchestrator with rules
        mock_orchestrator = Mock()
        mock_orchestrator.registry = Mock()
        mock_orchestrator.registry.get_rule_info.return_value = {
            'test.rule1': {
                'name': 'Test Rule 1',
                'description': 'Description 1',
                'severity': 'warning',
                'categories': ['test']
            },
            'test.rule2': {
                'name': 'Test Rule 2',
                'description': 'Description 2',
                'severity': 'error',
                'categories': ['test', 'sample']
            }
        }
        mock_orchestrator.registry.get_categories.return_value = {'test', 'sample'}
        mock_create_orchestrator.return_value = mock_orchestrator

        # Run CLI with --list-rules
        with self.assertRaises(SystemExit) as cm:
            self.cli.run(['--list-rules'])

        # Should exit cleanly
        self.assertEqual(cm.exception.code, 0)
        # Should print rule information
        mock_print.assert_called()

    @patch('design_linters.cli.CLI._create_orchestrator')
    @patch('builtins.print')
    def test_list_categories(self, mock_print, mock_create_orchestrator):
        """Test --list-categories functionality."""
        # Mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator.registry = Mock()
        mock_orchestrator.registry.get_categories.return_value = {
            'solid', 'style', 'literals', 'logging'
        }
        mock_create_orchestrator.return_value = mock_orchestrator

        # Run CLI with --list-categories
        with self.assertRaises(SystemExit) as cm:
            self.cli.run(['--list-categories'])

        # Should exit cleanly
        self.assertEqual(cm.exception.code, 0)
        # Should print categories
        mock_print.assert_called()


class TestLegacyCompatibility(unittest.TestCase):
    """Test legacy linter compatibility modes."""

    def setUp(self):
        """Set up test fixtures."""
        self.cli = DesignLinterCLI()

    @patch('design_linters.cli.CLI._create_orchestrator')
    def test_legacy_srp_mode(self, mock_create_orchestrator):
        """Test legacy SRP analyzer compatibility."""
        # Mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator.lint_file.return_value = []
        mock_orchestrator.generate_report.return_value = "Report"
        mock_create_orchestrator.return_value = mock_orchestrator

        # Run in legacy SRP mode
        args = self.cli._parse_arguments(['--legacy', 'srp', 'file.py'])
        config = self.cli._load_configuration(args)

        # Should enable only SRP rules
        self.assertIn('rules', config)
        srp_rules = [k for k in config['rules'] if k.startswith('solid.srp')]
        self.assertTrue(len(srp_rules) > 0)

    @patch('design_linters.cli.CLI._create_orchestrator')
    def test_legacy_magic_mode(self, mock_create_orchestrator):
        """Test legacy magic number detector compatibility."""
        mock_orchestrator = Mock()
        mock_orchestrator.lint_file.return_value = []
        mock_orchestrator.generate_report.return_value = "Report"
        mock_create_orchestrator.return_value = mock_orchestrator

        # Run in legacy magic mode
        args = self.cli._parse_arguments(['--legacy', 'magic', 'file.py'])
        config = self.cli._load_configuration(args)

        # Should enable only magic literal rules
        self.assertIn('rules', config)
        magic_rules = [k for k in config['rules'] if k.startswith('literals.magic')]
        self.assertTrue(len(magic_rules) > 0)

    def test_all_legacy_modes(self):
        """Test all legacy mode mappings."""
        legacy_modes = ['srp', 'magic', 'print', 'nesting', 'header']

        for mode in legacy_modes:
            args = self.cli._parse_arguments(['--legacy', mode, 'file.py'])
            config = self.cli._load_configuration(args)

            # Each mode should enable some rules
            self.assertIn('rules', config)
            self.assertTrue(len(config['rules']) > 0)


class TestOutputFormats(unittest.TestCase):
    """Test different output format generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.cli = DesignLinterCLI()

    def create_test_violations(self):
        """Create test violations for output testing."""
        return [
            LintViolation(
                rule_id='test.rule1',
                file_path='/test/file1.py',
                line=10,
                column=5,
                severity=Severity.WARNING,
                message='Test warning',
                description='Warning description',
                suggestion='Fix suggestion'
            ),
            LintViolation(
                rule_id='test.rule2',
                file_path='/test/file2.py',
                line=20,
                column=10,
                severity=Severity.ERROR,
                message='Test error',
                description='Error description',
                suggestion='Error fix'
            )
        ]

    @patch('design_linters.cli.CLI._create_orchestrator')
    @patch('builtins.print')
    def test_text_output_format(self, mock_print, mock_create_orchestrator):
        """Test text output format generation."""
        violations = self.create_test_violations()

        # Mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator.lint_file.return_value = violations
        mock_orchestrator.generate_report.return_value = "Text Report"
        mock_create_orchestrator.return_value = mock_orchestrator

        # Create args for text output
        args = Mock()
        args.format = 'text'
        args.output = None
        args.verbose = False

        # Output results
        self.cli._output_results(violations, args)

        # Should generate and print text report
        mock_orchestrator.generate_report.assert_called_with(violations, 'text')
        mock_print.assert_called()

    @patch('design_linters.cli.CLI._create_orchestrator')
    def test_json_output_format(self, mock_create_orchestrator):
        """Test JSON output format generation."""
        violations = self.create_test_violations()

        # Mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator.lint_file.return_value = violations

        # Create JSON report
        json_report = json.dumps([{
            'rule_id': v.rule_id,
            'file': v.file_path,
            'line': v.line,
            'column': v.column,
            'severity': v.severity.value,
            'message': v.message
        } for v in violations])

        mock_orchestrator.generate_report.return_value = json_report
        mock_create_orchestrator.return_value = mock_orchestrator

        # Create args for JSON output
        args = Mock()
        args.format = 'json'
        args.output = None
        args.verbose = False

        # Capture output
        with patch('builtins.print') as mock_print:
            self.cli._output_results(violations, args)

        # Should generate JSON report
        mock_orchestrator.generate_report.assert_called_with(violations, 'json')

        # Verify JSON is valid
        output = mock_print.call_args[0][0]
        parsed = json.loads(output)
        self.assertIsInstance(parsed, list)

    @patch('design_linters.cli.CLI._create_orchestrator')
    def test_output_to_file(self, mock_create_orchestrator):
        """Test writing output to file."""
        violations = self.create_test_violations()
        output_file = os.path.join(tempfile.gettempdir(), 'test_output.txt')

        # Mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator.generate_report.return_value = "Report Content"
        mock_create_orchestrator.return_value = mock_orchestrator

        # Create args for file output
        args = Mock()
        args.format = 'text'
        args.output = output_file
        args.verbose = False

        try:
            # Output to file
            self.cli._output_results(violations, args)

            # Verify file was created with content
            self.assertTrue(os.path.exists(output_file))
            with open(output_file, 'r') as f:
                content = f.read()
            self.assertEqual(content, "Report Content")
        finally:
            # Clean up
            if os.path.exists(output_file):
                os.remove(output_file)


class TestRuleFiltering(unittest.TestCase):
    """Test rule selection and filtering functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.cli = DesignLinterCLI()

    def test_filter_by_severity(self):
        """Test filtering violations by minimum severity."""
        violations = [
            LintViolation(
                rule_id='test.info',
                file_path='/test.py',
                line=1, column=0,
                severity=Severity.INFO,
                message='Info',
                description='Info',
                suggestion='Info'
            ),
            LintViolation(
                rule_id='test.warning',
                file_path='/test.py',
                line=2, column=0,
                severity=Severity.WARNING,
                message='Warning',
                description='Warning',
                suggestion='Warning'
            ),
            LintViolation(
                rule_id='test.error',
                file_path='/test.py',
                line=3, column=0,
                severity=Severity.ERROR,
                message='Error',
                description='Error',
                suggestion='Error'
            )
        ]

        # Filter by WARNING level
        filtered = self.cli._filter_by_severity(violations, 'warning')

        # Should include WARNING and ERROR, but not INFO
        self.assertEqual(len(filtered), 2)
        severities = [v.severity for v in filtered]
        self.assertNotIn(Severity.INFO, severities)
        self.assertIn(Severity.WARNING, severities)
        self.assertIn(Severity.ERROR, severities)

    def test_configuration_loading(self):
        """Test configuration file loading."""
        # Create temporary config file
        config_content = {
            'rules': {
                'solid.srp.too-many-methods': {
                    'enabled': True,
                    'max_methods': 5
                },
                'literals.magic-number': {
                    'enabled': False
                }
            }
        }

        config_file = os.path.join(tempfile.gettempdir(), 'test_config.json')
        with open(config_file, 'w') as f:
            json.dump(config_content, f)

        try:
            # Parse args with config file
            args = self.cli._parse_arguments(['--config', config_file, 'test.py'])
            config = self.cli._load_configuration(args)

            # Verify configuration was loaded
            self.assertIn('rules', config)
            self.assertIn('solid.srp.too-many-methods', config['rules'])
            self.assertEqual(
                config['rules']['solid.srp.too-many-methods']['max_methods'],
                5
            )
            self.assertFalse(
                config['rules']['literals.magic-number']['enabled']
            )
        finally:
            # Clean up
            if os.path.exists(config_file):
                os.remove(config_file)

    def test_strict_vs_lenient_mode(self):
        """Test strict and lenient configuration modes."""
        # Test strict mode
        args_strict = self.cli._parse_arguments(['--strict', 'test.py'])
        config_strict = self.cli._load_configuration(args_strict)

        # Test lenient mode
        args_lenient = self.cli._parse_arguments(['--lenient', 'test.py'])
        config_lenient = self.cli._load_configuration(args_lenient)

        # Configurations should be different
        self.assertNotEqual(config_strict, config_lenient)


if __name__ == '__main__':
    unittest.main()
