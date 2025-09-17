#!/usr/bin/env python3
"""
Purpose: Tests for reporter modules
Scope: Test reporter implementations
Overview: This module tests all reporter implementations.
Dependencies: unittest, reporter modules
"""

import unittest
import json
from pathlib import Path

import sys
sys.path.insert(0, '/home/stevejackson/Projects/durable-code-test/tools')

from design_linters.framework.interfaces import LintViolation, Severity
from design_linters.framework.reporters import (
    TextReporter, JSONReporter, SARIFReporter,
    GitHubActionsReporter, ReporterFactory
)


class TestTextReporter(unittest.TestCase):
    """Test TextReporter."""

    def setUp(self):
        self.reporter = TextReporter()

    def test_no_violations(self):
        """Test report with no violations."""
        report = self.reporter.generate_report([])
        self.assertIn("No linting violations found", report)

    def test_single_violation(self):
        """Test report with single violation."""
        violation = LintViolation(
            rule_id='test.rule',
            file_path='/src/test.py',
            line=10,
            column=5,
            severity=Severity.WARNING,
            message='Test violation',
            description='Test description',
            suggestion='Fix suggestion'
        )

        report = self.reporter.generate_report([violation])
        self.assertIn('/src/test.py', report)
        self.assertIn('Test violation', report)

    def test_format_violation(self):
        """Test violation formatting."""
        violation = LintViolation(
            rule_id='test.rule',
            file_path='/src/test.py',
            line=15,
            column=20,
            severity=Severity.ERROR,
            message='Test message',
            description='Test description',
            suggestion='Test suggestion'
        )

        formatted = self.reporter.format_violation(violation)
        self.assertIn('/src/test.py', formatted)
        self.assertIn('15:20', formatted)
        self.assertIn('ERROR', formatted)

    def test_group_by_file(self):
        """Test grouping violations by file."""
        violations = [
            LintViolation(
                rule_id='rule1',
                file_path='/src/file1.py',
                line=1,
                column=0,
                severity=Severity.WARNING,
                message='Message 1',
                description='Desc 1',
                suggestion='Fix 1'
            ),
            LintViolation(
                rule_id='rule2',
                file_path='/src/file1.py',
                line=10,
                column=5,
                severity=Severity.ERROR,
                message='Message 2',
                description='Desc 2',
                suggestion='Fix 2'
            )
        ]

        grouped = self.reporter._group_by_file(violations)
        self.assertIn('/src/file1.py', grouped)
        self.assertEqual(len(grouped['/src/file1.py']), 2)


class TestJSONReporter(unittest.TestCase):
    """Test JSONReporter."""

    def setUp(self):
        self.reporter = JSONReporter()

    def test_no_violations_json(self):
        """Test JSON report with no violations."""
        report = self.reporter.generate_report([])
        data = json.loads(report)

        self.assertEqual(data['total_violations'], 0)
        self.assertEqual(len(data['violations']), 0)

    def test_single_violation_json(self):
        """Test JSON report with single violation."""
        violation = LintViolation(
            rule_id='test.rule',
            file_path='/src/test.py',
            line=10,
            column=5,
            severity=Severity.WARNING,
            message='Test violation',
            description='Test description',
            suggestion='Fix suggestion'
        )

        report = self.reporter.generate_report([violation])
        data = json.loads(report)

        self.assertEqual(data['total_violations'], 1)
        self.assertEqual(len(data['violations']), 1)

        v = data['violations'][0]
        self.assertEqual(v['rule_id'], 'test.rule')
        self.assertEqual(v['file_path'], '/src/test.py')
        self.assertEqual(v['line'], 10)
        self.assertEqual(v['severity'], 'warning')

    def test_format_violation_json(self):
        """Test JSON violation formatting."""
        violation = LintViolation(
            rule_id='test.rule',
            file_path='/src/test.py',
            line=15,
            column=20,
            severity=Severity.ERROR,
            message='Test message',
            description='Test description',
            suggestion='Test suggestion',
            context={'key': 'value'}
        )

        formatted = self.reporter.format_violation(violation)
        self.assertEqual(formatted['rule_id'], 'test.rule')
        self.assertEqual(formatted['severity'], 'error')
        self.assertEqual(formatted['context'], {'key': 'value'})


class TestSARIFReporter(unittest.TestCase):
    """Test SARIFReporter."""

    def setUp(self):
        self.reporter = SARIFReporter()

    def test_sarif_format(self):
        """Test SARIF format generation."""
        violation = LintViolation(
            rule_id='test.rule',
            file_path='/src/test.py',
            line=10,
            column=5,
            severity=Severity.ERROR,
            message='Test violation',
            description='Test description',
            suggestion='Fix suggestion'
        )

        report = self.reporter.generate_report([violation])
        data = json.loads(report)

        # Check SARIF structure
        self.assertIn('$schema', data)
        self.assertIn('version', data)
        self.assertIn('runs', data)


class TestGitHubActionsReporter(unittest.TestCase):
    """Test GitHubActionsReporter."""

    def setUp(self):
        self.reporter = GitHubActionsReporter()

    def test_github_annotation_format(self):
        """Test GitHub annotation format."""
        violation = LintViolation(
            rule_id='test.rule',
            file_path='/src/test.py',
            line=10,
            column=5,
            severity=Severity.ERROR,
            message='Test violation',
            description='Test description',
            suggestion='Fix suggestion'
        )

        annotation = self.reporter.format_violation(violation)
        self.assertIn('::error', annotation)
        self.assertIn('file=/src/test.py', annotation)
        self.assertIn('line=10', annotation)

    def test_github_warning_annotation(self):
        """Test GitHub warning annotation."""
        violation = LintViolation(
            rule_id='test.rule',
            file_path='/src/test.py',
            line=5,
            column=10,
            severity=Severity.WARNING,
            message='Warning message',
            description='Warning description',
            suggestion='Fix warning'
        )

        annotation = self.reporter.format_violation(violation)
        self.assertIn('::warning', annotation)

    def test_github_notice_annotation(self):
        """Test GitHub notice annotation for info."""
        violation = LintViolation(
            rule_id='test.rule',
            file_path='/src/test.py',
            line=1,
            column=0,
            severity=Severity.INFO,
            message='Info message',
            description='Info description',
            suggestion='Fix info'
        )

        annotation = self.reporter.format_violation(violation)
        self.assertIn('::notice', annotation)


class TestReporterFactory(unittest.TestCase):
    """Test ReporterFactory."""

    def test_create_text_reporter(self):
        """Test creating text reporter."""
        reporter = ReporterFactory.create_reporter('text')
        self.assertIsInstance(reporter, TextReporter)

    def test_create_json_reporter(self):
        """Test creating JSON reporter."""
        reporter = ReporterFactory.create_reporter('json')
        self.assertIsInstance(reporter, JSONReporter)

    def test_create_sarif_reporter(self):
        """Test creating SARIF reporter."""
        reporter = ReporterFactory.create_reporter('sarif')
        self.assertIsInstance(reporter, SARIFReporter)

    def test_create_github_reporter(self):
        """Test creating GitHub Actions reporter."""
        reporter = ReporterFactory.create_reporter('github')
        self.assertIsInstance(reporter, GitHubActionsReporter)

    def test_create_invalid_reporter(self):
        """Test creating invalid reporter defaults to text."""
        reporter = ReporterFactory.create_reporter('invalid')
        self.assertIsInstance(reporter, TextReporter)


if __name__ == '__main__':
    unittest.main()
