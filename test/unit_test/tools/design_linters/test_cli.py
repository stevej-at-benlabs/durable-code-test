#!/usr/bin/env python3
"""
Purpose: Tests for CLI module
Scope: Test CLI functionality
Overview: This module tests the CLI implementation.
Dependencies: unittest, CLI module
"""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

import sys
sys.path.insert(0, '/home/stevejackson/Projects/durable-code-test/tools')

from design_linters.cli import DesignLinterCLI, main
from design_linters.framework.interfaces import LintViolation, Severity


class TestDesignLinterCLI(unittest.TestCase):
    """Test DesignLinterCLI implementation."""

    def setUp(self):
        self.cli = DesignLinterCLI()

    def test_cli_creation(self):
        """Test CLI creation."""
        self.assertIsNotNone(self.cli)
        self.assertIsNone(self.cli.orchestrator)  # Not initialized until run()

    @patch('design_linters.cli.create_orchestrator')
    def test_create_orchestrator(self, mock_create_orchestrator):
        """Test orchestrator creation."""
        mock_orchestrator = Mock()
        mock_create_orchestrator.return_value = mock_orchestrator

        args = Mock()
        args.rules = None
        args.exclude_rules = None
        args.config = None
        args.strict = False
        args.lenient = False
        args.legacy = None
        args.list_rules = False
        args.list_categories = False

        result = self.cli._create_orchestrator(args)
        self.assertEqual(result, mock_orchestrator)
        mock_create_orchestrator.assert_called_once()

    def test_load_configuration(self):
        """Test configuration loading."""
        args = Mock()
        args.config = None
        args.strict = False
        args.lenient = False
        args.legacy = None
        args.rules = None
        args.exclude_rules = None

        config = self.cli._load_configuration(args)
        self.assertIn('rules', config)
        self.assertIn('include', config)
        self.assertIn('exclude', config)

    def test_load_configuration_with_rules(self):
        """Test configuration with rule filters."""
        args = Mock()
        args.config = None
        args.strict = False
        args.lenient = False
        args.legacy = None
        args.rules = 'rule1,rule2'
        args.exclude_rules = 'rule3'

        config = self.cli._load_configuration(args)
        self.assertTrue(config['rules']['rule1']['enabled'])
        self.assertTrue(config['rules']['rule2']['enabled'])
        self.assertFalse(config['rules']['rule3']['enabled'])

    def test_determine_exit_code(self):
        """Test exit code determination."""
        # No violations
        args = Mock()
        args.fail_on_error = False
        args.fail_on_warnings = False
        self.assertEqual(self.cli._determine_exit_code([], args), 0)

        # With violations but no fail flags
        violations = [Mock()]
        self.assertEqual(self.cli._determine_exit_code(violations, args), 0)

        # With error and fail_on_error
        error_violation = Mock()
        error_violation.severity = Severity.ERROR
        args.fail_on_error = True
        self.assertEqual(self.cli._determine_exit_code([error_violation], args), 1)

    @patch('design_linters.cli.yaml.safe_load')
    @patch('builtins.open')
    def test_load_config_file(self, mock_open, mock_yaml):
        """Test loading config file."""
        mock_yaml.return_value = {'rules': {'test.rule': {'enabled': True}}}

        config = self.cli._load_config_file('config.yml')
        self.assertIn('rules', config)

    def test_load_config_file_not_found(self):
        """Test loading non-existent config."""
        config = self.cli._load_config_file('/nonexistent.yml')
        self.assertEqual(config, {})

    def test_get_strict_config(self):
        """Test strict configuration."""
        config = self.cli._get_strict_config()
        self.assertIsInstance(config, dict)

    def test_get_lenient_config(self):
        """Test lenient configuration."""
        config = self.cli._get_lenient_config()
        self.assertIsInstance(config, dict)

    def test_get_legacy_config(self):
        """Test legacy configuration."""
        config = self.cli._get_legacy_config('srp')
        self.assertIsInstance(config, dict)

    def test_filter_by_severity(self):
        """Test filtering violations by severity."""
        violations = [
            Mock(severity=Severity.ERROR),
            Mock(severity=Severity.WARNING),
            Mock(severity=Severity.INFO)
        ]

        # Filter to error only
        filtered = self.cli._filter_by_severity(violations, 'error')
        self.assertEqual(len(filtered), 1)

        # Filter to warning and above
        filtered = self.cli._filter_by_severity(violations, 'warning')
        self.assertEqual(len(filtered), 2)

    @patch('design_linters.cli.sys.exit')
    def test_list_rules(self, mock_exit):
        """Test list rules functionality."""
        mock_orchestrator = Mock()
        mock_rule = Mock()
        mock_rule.rule_id = 'test.rule'
        mock_rule.rule_name = 'Test Rule'
        mock_rule.description = 'Test description'
        mock_rule.categories = {'test'}
        mock_orchestrator.get_available_rules.return_value = [mock_rule]

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.cli._list_rules(mock_orchestrator)
            output = mock_stdout.getvalue()
            self.assertIn('test.rule', output)

    @patch('design_linters.cli.sys.exit')
    def test_list_categories(self, mock_exit):
        """Test list categories functionality."""
        mock_orchestrator = Mock()
        mock_orchestrator.registry.get_categories.return_value = {'test', 'example'}

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.cli._list_categories(mock_orchestrator)
            output = mock_stdout.getvalue()
            self.assertIn('test', output)
            self.assertIn('example', output)


class TestMainFunction(unittest.TestCase):
    """Test main function."""

    @patch('design_linters.cli.argparse.ArgumentParser.parse_args')
    @patch('design_linters.cli.DesignLinterCLI')
    def test_main_function(self, mock_cli_class, mock_parse_args):
        """Test main function execution."""
        mock_args = Mock()
        mock_parse_args.return_value = mock_args

        mock_cli = Mock()
        mock_cli.run.return_value = 0
        mock_cli_class.return_value = mock_cli

        with patch('sys.exit') as mock_exit:
            main()
            mock_cli.run.assert_called_once()
            mock_exit.assert_called_once_with(0)

    @patch('design_linters.cli.argparse.ArgumentParser.parse_args')
    def test_main_with_exception(self, mock_parse_args):
        """Test main handles exceptions."""
        mock_parse_args.side_effect = Exception("Test error")

        with patch('sys.exit') as mock_exit:
            with patch('sys.stderr', new_callable=StringIO):
                main()
                mock_exit.assert_called_once_with(1)


if __name__ == '__main__':
    unittest.main()
