#!/usr/bin/env python3
# print-linter: disable
"""
Purpose: Unit tests for the print statement linter
Scope: Testing print statement detection across Python, JavaScript, TypeScript
Created: 2025-09-12
Updated: 2025-09-12
Author: Development Team
Version: 1.0
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add tools directory to path for import
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'tools' / 'design-linters'))

from print_statement_linter import PrintStatementLinter, PrintViolation


class TestPrintStatementLinter(unittest.TestCase):
    """Test cases for PrintStatementLinter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.linter = PrintStatementLinter()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_temp_file(self, filename: str, content: str) -> Path:
        """Create a temporary file with given content."""
        file_path = self.temp_path / filename
        file_path.write_text(content)
        return file_path
    
    # ========== Python Tests ==========
    
    def test_detect_python_print_statement(self):
        """Test detection of print() in Python."""
        content = '''
def hello():
    print("Hello, World!")
    return True
'''
        file_path = self.create_temp_file('hello.py', content)
        violations = self.linter.lint_file(file_path)
        
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].statement, 'print()')
        self.assertEqual(violations[0].line_number, 3)
        self.assertEqual(violations[0].language, 'python')
    
    def test_detect_python_pprint_statement(self):
        """Test detection of pprint() in Python."""
        content = '''
from pprint import pprint

data = {"key": "value"}
pprint(data)
'''
        file_path = self.create_temp_file('hello.py', content)
        violations = self.linter.lint_file(file_path)
        
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].statement, 'pprint()')
        self.assertEqual(violations[0].line_number, 5)
    
    def test_detect_python_pp_alias(self):
        """Test detection of pp() alias in Python."""
        content = '''
from pprint import pprint as pp

data = {"key": "value"}
pp(data)
'''
        file_path = self.create_temp_file('hello.py', content)
        violations = self.linter.lint_file(file_path)
        
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].statement, 'pp()')
    
    def test_python_no_false_positives(self):
        """Test that legitimate code doesn't trigger false positives."""
        content = '''
def print_header():
    """This function prints a header."""
    return "Header"

# This is a comment with print in it
class Printer:
    def format(self):
        return "formatted"
'''
        file_path = self.create_temp_file('hello.py', content)
        violations = self.linter.lint_file(file_path)
        
        self.assertEqual(len(violations), 0)
    
    def test_python_multiple_prints(self):
        """Test detection of multiple print statements."""
        content = '''
def debug_function():
    print("Start")
    x = 10
    print(f"Value: {x}")
    print("End")
'''
        file_path = self.create_temp_file('hello.py', content)
        violations = self.linter.lint_file(file_path)
        
        self.assertEqual(len(violations), 3)
        self.assertEqual(violations[0].line_number, 3)
        self.assertEqual(violations[1].line_number, 5)
        self.assertEqual(violations[2].line_number, 6)
    
    # ========== JavaScript Tests ==========
    
    def test_detect_javascript_console_log(self):
        """Test detection of console.log() in JavaScript."""
        content = '''
function greet() {
    console.log("Hello, World!");
    return true;
}
'''
        file_path = self.create_temp_file('app.js', content)
        violations = self.linter.lint_file(file_path)
        
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].statement, 'console.log()')
        self.assertEqual(violations[0].line_number, 3)
        self.assertEqual(violations[0].language, 'javascript')
    
    def test_detect_javascript_console_methods(self):
        """Test detection of various console methods."""
        content = '''
console.log("log");
console.debug("debug");
console.info("info");
console.warn("warn");
console.error("error");
console.trace("trace");
console.dir(obj);
console.table(data);
'''
        file_path = self.create_temp_file('app.js', content)
        violations = self.linter.lint_file(file_path)
        
        self.assertEqual(len(violations), 8)
        statements = [v.statement for v in violations]
        self.assertIn('console.log()', statements)
        self.assertIn('console.debug()', statements)
        self.assertIn('console.warn()', statements)
        self.assertIn('console.error()', statements)
    
    def test_detect_javascript_alert(self):
        """Test detection of alert() in JavaScript."""
        content = '''
function showMessage() {
    alert("This is an alert!");
}
'''
        file_path = self.create_temp_file('app.js', content)
        violations = self.linter.lint_file(file_path)
        
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].statement, 'alert()')
    
    def test_detect_javascript_debugger(self):
        """Test detection of debugger statement."""
        content = '''
function debug() {
    debugger;
    return false;
}
'''
        file_path = self.create_temp_file('app.js', content)
        violations = self.linter.lint_file(file_path)
        
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].statement, 'debugger')
        self.assertEqual(violations[0].severity, 'error')
    
    def test_javascript_with_spaces(self):
        """Test detection with various spacing."""
        content = '''
console . log("spaced");
console.  log("double space");
console
    .log("newline");
'''
        file_path = self.create_temp_file('app.js', content)
        violations = self.linter.lint_file(file_path)
        
        self.assertGreaterEqual(len(violations), 2)
    
    # ========== TypeScript Tests ==========
    
    def test_detect_typescript_console_log(self):
        """Test detection in TypeScript files."""
        content = '''
interface User {
    name: string;
}

function greet(user: User): void {
    console.log(`Hello, ${user.name}`);
}
'''
        file_path = self.create_temp_file('app.ts', content)
        violations = self.linter.lint_file(file_path)
        
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].statement, 'console.log()')
        self.assertEqual(violations[0].language, 'typescript')
    
    def test_detect_tsx_console_log(self):
        """Test detection in TSX files."""
        content = '''
const Component: React.FC = () => {
    console.log("Rendering component");
    return <div>Hello</div>;
};
'''
        file_path = self.create_temp_file('component.tsx', content)
        violations = self.linter.lint_file(file_path)
        
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].language, 'typescript')
    
    # ========== Skip Logic Tests ==========
    
    def test_skip_test_files(self):
        """Test that test files are skipped by default."""
        content = 'console.log("test");'
        
        # Test various test file patterns
        test_files = [
            'test.spec.js',
            'component.test.tsx',
            'test_module.py',
            'module_test.py',
            'conftest.py'
        ]
        
        for filename in test_files:
            file_path = self.create_temp_file(filename, content)
            violations = self.linter.lint_file(file_path)
            self.assertEqual(len(violations), 0, f"Should skip {filename}")
    
    def test_no_skip_tests_flag(self):
        """Test that test files are checked when flag is set."""
        linter = PrintStatementLinter(allow_in_tests=False)
        content = 'print("test")'
        
        file_path = self.create_temp_file('test_module.py', content)
        violations = linter.lint_file(file_path)
        
        self.assertEqual(len(violations), 1)
    
    def test_skip_non_source_files(self):
        """Test that non-source files are skipped."""
        content = 'print("hello")'
        
        non_source_files = [
            'readme.txt',
            'data.json',
            'style.css',
            'index.html'
        ]
        
        for filename in non_source_files:
            file_path = self.create_temp_file(filename, content)
            violations = self.linter.lint_file(file_path)
            self.assertEqual(len(violations), 0, f"Should skip {filename}")
    
    # ========== Allow Logging Tests ==========
    
    def test_allow_logging_javascript(self):
        """Test allowing warn/error in JavaScript."""
        linter = PrintStatementLinter(allow_logging=True)
        content = '''
console.log("debug");
console.warn("warning");
console.error("error");
'''
        file_path = self.create_temp_file('app.js', content)
        violations = linter.lint_file(file_path)
        
        # Should only detect console.log, not warn/error
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].statement, 'console.log()')
    
    def test_allow_logging_python(self):
        """Test allowing logging module in Python."""
        linter = PrintStatementLinter(allow_logging=True)
        content = '''
import logging

print("debug")
logging.info("info")
logging.error("error")
'''
        file_path = self.create_temp_file('hello.py', content)
        violations = linter.lint_file(file_path)
        
        # Should only detect print, not logging statements
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].statement, 'print()')
    
    # ========== Comment Handling Tests ==========
    
    def test_ignore_comments_python(self):
        """Test that comments are ignored in Python."""
        content = '''
# This is a comment with print("test")
def func():
    # print("commented out")
    return True
'''
        file_path = self.create_temp_file('hello.py', content)
        violations = self.linter.lint_file(file_path)
        
        self.assertEqual(len(violations), 0)
    
    def test_ignore_comments_javascript(self):
        """Test that comments are ignored in JavaScript."""
        content = '''
// console.log("commented");
function test() {
    /* console.log("block comment"); */
    // Another comment with console.log
    return true;
}
'''
        file_path = self.create_temp_file('app.js', content)
        violations = self.linter.lint_file(file_path)
        
        self.assertEqual(len(violations), 0)
    
    # ========== Directory Scanning Tests ==========
    
    def test_lint_directory_recursive(self):
        """Test recursive directory scanning."""
        # Create nested structure
        sub_dir = self.temp_path / 'subdir'
        sub_dir.mkdir()
        
        self.create_temp_file('root.py', 'print("root")')
        self.create_temp_file('subdir/nested.py', 'print("nested")')
        
        violations = self.linter.lint_directory(self.temp_path, recursive=True)
        
        self.assertEqual(len(violations), 2)
        file_names = {v.file_path.name for v in violations}
        self.assertIn('root.py', file_names)
        self.assertIn('nested.py', file_names)
    
    def test_lint_directory_non_recursive(self):
        """Test non-recursive directory scanning."""
        # Create nested structure
        sub_dir = self.temp_path / 'subdir'
        sub_dir.mkdir()
        
        self.create_temp_file('root.py', 'print("root")')
        self.create_temp_file('subdir/nested.py', 'print("nested")')
        
        violations = self.linter.lint_directory(self.temp_path, recursive=False)
        
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].file_path.name, 'root.py')
    
    # ========== Report Generation Tests ==========
    
    def test_generate_text_report(self):
        """Test text report generation."""
        self.create_temp_file('hello.py', 'print("test")')
        self.linter.lint_directory(self.temp_path)
        
        report = self.linter.generate_report('text')
        
        self.assertIn('PRINT STATEMENT LINTING REPORT', report)
        self.assertIn('Total violations: 1', report)
        self.assertIn('hello.py', report)
        self.assertIn('print()', report)
    
    def test_generate_json_report(self):
        """Test JSON report generation."""
        file_path = self.create_temp_file('hello.py', 'print("test")')
        self.linter.lint_directory(self.temp_path)  # Use lint_directory to populate violations
        
        report = self.linter.generate_report('json')
        data = json.loads(report)
        
        self.assertEqual(data['total_violations'], 1)
        self.assertEqual(len(data['violations']), 1)
        self.assertIn('file', data['violations'][0])
        self.assertIn('line', data['violations'][0])
        self.assertIn('statement', data['violations'][0])
    
    def test_generate_github_report(self):
        """Test GitHub Actions annotation format."""
        self.create_temp_file('hello.py', 'print("test")')
        self.linter.lint_directory(self.temp_path)
        
        report = self.linter.generate_report('github')
        
        # Accept either error or warning
        self.assertTrue('::error' in report or '::warning' in report)
        self.assertIn('file=', report)
        self.assertIn('line=', report)
    
    def test_empty_report(self):
        """Test report when no violations found."""
        self.create_temp_file('clean.py', 'def func(): return True')
        self.linter.lint_directory(self.temp_path)
        
        report = self.linter.generate_report('text')
        
        self.assertIn('No print statements found', report)
        self.assertIn('✅', report)
    
    # ========== Custom Patterns Tests ==========
    
    def test_custom_patterns(self):
        """Test adding custom patterns."""
        custom_patterns = {
            'python': [
                (r'\bdebug\s*\(', 'debug()'),
            ]
        }
        linter = PrintStatementLinter(custom_patterns=custom_patterns)
        
        content = '''
def test():
    debug("custom debug")
    return True
'''
        file_path = self.create_temp_file('hello.py', content)
        violations = linter.lint_file(file_path)
        
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].statement, 'debug()')
    
    # ========== Edge Cases ==========
    
    def test_syntax_error_fallback(self):
        """Test fallback to regex when AST parsing fails."""
        content = '''
This is not valid Python syntax!
But it has print("test") in it.
'''
        file_path = self.create_temp_file('hello.py', content)
        violations = self.linter.lint_file(file_path)
        
        # Should still detect print via regex
        self.assertEqual(len(violations), 1)
    
    def test_unicode_handling(self):
        """Test handling of unicode content."""
        content = '''
def greet():
    print("Hello, 世界! 🌍")
'''
        file_path = self.create_temp_file('hello.py', content)
        violations = self.linter.lint_file(file_path)
        
        self.assertEqual(len(violations), 1)
    
    def test_multiline_statements(self):
        """Test detection in multiline statements."""
        content = '''
print(
    "This is a",
    "multiline",
    "print statement"
)
'''
        file_path = self.create_temp_file('hello.py', content)
        violations = self.linter.lint_file(file_path)
        
        self.assertEqual(len(violations), 1)
    
    # ========== Integration Tests ==========
    
    def test_mixed_language_project(self):
        """Test scanning project with multiple languages."""
        self.create_temp_file('backend.py', 'print("python")')
        self.create_temp_file('frontend.js', 'console.log("javascript")')
        self.create_temp_file('component.tsx', 'console.debug("typescript")')
        
        violations = self.linter.lint_directory(self.temp_path)
        
        self.assertEqual(len(violations), 3)
        languages = {v.language for v in violations}
        self.assertEqual(languages, {'python', 'javascript', 'typescript'})
    
    def test_severity_levels(self):
        """Test different severity levels."""
        content = '''
function test() {
    console.log("log");
    debugger;
}
'''
        file_path = self.create_temp_file('app.js', content)
        violations = self.linter.lint_file(file_path)
        
        severities = {v.statement: v.severity for v in violations}
        self.assertEqual(severities['debugger'], 'error')
        self.assertIn(severities['console.log()'], ['warning', 'error'])


class TestPrintViolation(unittest.TestCase):
    """Test the PrintViolation namedtuple."""
    
    def test_violation_creation(self):
        """Test creating a PrintViolation."""
        violation = PrintViolation(
            file_path=Path('test.py'),
            line_number=10,
            column=4,
            statement='print()',
            context='print("test")',
            language='python',
            severity='error'
        )
        
        self.assertEqual(violation.file_path, Path('test.py'))
        self.assertEqual(violation.line_number, 10)
        self.assertEqual(violation.column, 4)
        self.assertEqual(violation.statement, 'print()')
        self.assertEqual(violation.context, 'print("test")')
        self.assertEqual(violation.language, 'python')
        self.assertEqual(violation.severity, 'error')


if __name__ == '__main__':
    unittest.main()