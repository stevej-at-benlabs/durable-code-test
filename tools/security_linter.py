#!/usr/bin/env python3
"""
Purpose: Refactored security linting tool with proper separation of concerns
Scope: FastAPI applications, input validation, rate limiting, and security headers
Overview: This tool scans Python files for security vulnerabilities using a
    clean architecture with separated responsibilities for pattern detection,
    issue collection, and reporting.
Dependencies: Python standard library, ast module for code parsing
Exports: Security vulnerability detection and reporting with SRP compliance
Interfaces: Command-line interface for file scanning
Implementation: AST-based static analysis with focused, single-responsibility classes
"""

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple


class SecurityIssue(NamedTuple):
    """Represents a security issue found in code."""

    file_path: str
    line_number: int
    column: int
    severity: str
    issue_type: str
    message: str
    suggestion: str


class SecurityIssueCollector:
    """Collects and manages security issues found during analysis."""

    def __init__(self) -> None:
        """Initialize the issue collector."""
        self.issues: list[SecurityIssue] = []

    def add_issue(self, issue: SecurityIssue) -> None:
        """Add a security issue to the collection."""
        self.issues.append(issue)

    def get_issues(self) -> list[SecurityIssue]:
        """Get all collected security issues."""
        return self.issues

    def clear_issues(self) -> None:
        """Clear all collected issues."""
        self.issues.clear()

    def has_critical_issues(self) -> bool:
        """Check if any critical issues were found."""
        return any(issue.severity == "CRITICAL" for issue in self.issues)


class SecurityPatternDetector:
    """Detects security patterns and vulnerabilities in code using regex patterns."""

    def __init__(self) -> None:
        """Initialize the pattern detector."""
        self.dangerous_patterns = {
            "hardcoded_secrets": [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']',
            ],
            "sql_injection": [
                r'execute\s*\(\s*["\'].*%.*["\']',
                r'query\s*=\s*["\'].*\+.*["\']',
                r'sql\s*=\s*f["\'].*\{.*\}.*["\']',
            ],
            "command_injection": [
                r"os\.system\s*\(",
                r"subprocess\.call\s*\(",
                r"eval\s*\(",
                r"exec\s*\(",
            ],
            "insecure_random": [
                r"random\.random\s*\(",
                r"random\.randint\s*\(",
            ],
        }

    def check_patterns(self, file_path: Path, content: str, collector: SecurityIssueCollector) -> None:
        """Check for dangerous patterns in code content."""
        lines = content.split('\n')

        for category, patterns in self.dangerous_patterns.items():
            for pattern_str in patterns:
                pattern = re.compile(pattern_str)
                for line_num, line in enumerate(lines, 1):
                    if pattern.search(line):
                        collector.add_issue(SecurityIssue(
                            file_path=str(file_path),
                            line_number=line_num,
                            column=0,
                            severity=self._get_severity(category),
                            issue_type=category,
                            message=f"Detected {category.replace('_', ' ')}: {line.strip()}",
                            suggestion=self._get_suggestion(category)
                        ))

    def _get_severity(self, category: str) -> str:
        """Get severity level for issue category."""
        severity_map = {
            "hardcoded_secrets": "CRITICAL",
            "sql_injection": "CRITICAL",
            "command_injection": "HIGH",
            "insecure_random": "MEDIUM",
        }
        return severity_map.get(category, "LOW")

    def _get_suggestion(self, category: str) -> str:
        """Get suggestion for fixing the issue."""
        suggestions = {
            "hardcoded_secrets": "Use environment variables or secret management systems",
            "sql_injection": "Use parameterized queries or ORM methods",
            "command_injection": "Validate input and use subprocess with shell=False",
            "insecure_random": "Use secrets module for cryptographic randomness",
        }
        return suggestions.get(category, "Review code for security best practices")


class SecurityASTAnalyzer:
    """Analyzes AST structures for security vulnerabilities."""

    def analyze_ast(self, file_path: Path, tree: ast.AST, collector: SecurityIssueCollector) -> None:
        """Analyze AST for security issues."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._check_function_security(file_path, node, collector)
            elif isinstance(node, ast.Call):
                self._check_call_security(file_path, node, collector)

    def _check_function_security(self, file_path: Path, node: ast.FunctionDef, collector: SecurityIssueCollector) -> None:
        """Check function for security issues."""
        # Check for missing input validation
        if self._handles_user_input(node) and not self._has_validation(node):
            collector.add_issue(SecurityIssue(
                file_path=str(file_path),
                line_number=node.lineno,
                column=node.col_offset,
                severity="MEDIUM",
                issue_type="missing_input_validation",
                message=f"Function '{node.name}' handles user input without validation",
                suggestion="Add input validation using Pydantic models or validators"
            ))

        # Check for missing rate limiting on API endpoints
        if self._is_api_endpoint(node) and not self._has_rate_limiting(node):
            collector.add_issue(SecurityIssue(
                file_path=str(file_path),
                line_number=node.lineno,
                column=node.col_offset,
                severity="MEDIUM",
                issue_type="missing_rate_limiting",
                message=f"API endpoint '{node.name}' lacks rate limiting",
                suggestion="Add rate limiting decorators to prevent abuse"
            ))

    def _check_call_security(self, file_path: Path, node: ast.Call, collector: SecurityIssueCollector) -> None:
        """Check function calls for security issues."""
        if isinstance(node.func, ast.Name) and node.func.id == "eval":
            collector.add_issue(SecurityIssue(
                file_path=str(file_path),
                line_number=node.lineno,
                column=node.col_offset,
                severity="CRITICAL",
                issue_type="dangerous_eval",
                message="Use of eval() is dangerous and should be avoided",
                suggestion="Use safer alternatives like ast.literal_eval() for data parsing"
            ))

    def _handles_user_input(self, node: ast.FunctionDef) -> bool:
        """Check if function handles user input."""
        for arg in node.args.args:
            if arg.annotation and isinstance(arg.annotation, ast.Name) and arg.annotation.id in ["Request", "BaseModel"]:
                return True
        return False

    def _has_validation(self, node: ast.FunctionDef) -> bool:
        """Check if function has input validation."""
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Call) and isinstance(stmt.func, ast.Name) and stmt.func.id in ["validate", "sanitize", "check_input"]:
                return True
        return False

    def _is_api_endpoint(self, node: ast.FunctionDef) -> bool:
        """Check if function is an API endpoint."""
        api_decorators = {"get", "post", "put", "delete", "patch"}
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                if decorator.func.attr in api_decorators:
                    return True
        return False

    def _has_rate_limiting(self, node: ast.FunctionDef) -> bool:
        """Check if function has rate limiting."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                if "limit" in str(decorator.func.attr):
                    return True
        return False


class SecurityReporter:
    """Handles reporting and formatting of security issues."""

    def report_text(self, issues: list[SecurityIssue]) -> None:
        """Report issues in text format."""
        if not issues:
            print("✅ No security issues found!")
            return

        print(f"🔒 Security Analysis Results: {len(issues)} issues found\n")

        # Group by severity
        by_severity: dict[str, list[SecurityIssue]] = {}
        for issue in issues:
            if issue.severity not in by_severity:
                by_severity[issue.severity] = []
            by_severity[issue.severity].append(issue)

        # Report by severity level
        severity_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "ERROR"]
        for severity in severity_order:
            if severity in by_severity:
                self._report_severity_group(severity, by_severity[severity])

    def report_json(self, issues: list[SecurityIssue]) -> None:
        """Report issues in JSON format."""
        issues_data = []
        for issue in issues:
            issues_data.append({
                "file_path": issue.file_path,
                "line_number": issue.line_number,
                "column": issue.column,
                "severity": issue.severity,
                "issue_type": issue.issue_type,
                "message": issue.message,
                "suggestion": issue.suggestion,
            })

        result = {
            "total_issues": len(issues),
            "issues": issues_data,
        }
        print(json.dumps(result, indent=2))

    def _report_severity_group(self, severity: str, issues: list[SecurityIssue]) -> None:
        """Report a group of issues with the same severity."""
        severity_colors = {
            "CRITICAL": "🔴",
            "HIGH": "🟠",
            "MEDIUM": "🟡",
            "LOW": "🔵",
            "ERROR": "⚫",
        }

        color = severity_colors.get(severity, "⚪")
        print(f"{color} {severity} ({len(issues)} issues)")
        print("-" * 50)

        for issue in issues:
            print(f"📁 {issue.file_path}:{issue.line_number}:{issue.column}")
            print(f"   {issue.message}")
            print(f"   💡 {issue.suggestion}")
            print()


class SecurityFileScanner:
    """Handles file scanning operations."""

    def __init__(self, collector: SecurityIssueCollector, detector: SecurityPatternDetector, analyzer: SecurityASTAnalyzer) -> None:
        """Initialize the file scanner."""
        self.collector = collector
        self.detector = detector
        self.analyzer = analyzer

    def scan_file(self, file_path: Path) -> None:
        """Scan a Python file for security issues."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse AST for structural analysis
            try:
                tree = ast.parse(content)
                self.analyzer.analyze_ast(file_path, tree, self.collector)
            except SyntaxError as e:
                self.collector.add_issue(SecurityIssue(
                    file_path=str(file_path),
                    line_number=e.lineno or 0,
                    column=e.offset or 0,
                    severity="ERROR",
                    issue_type="syntax_error",
                    message=f"Syntax error: {e.msg}",
                    suggestion="Fix syntax errors before security analysis"
                ))

            # Check for dangerous patterns
            self.detector.check_patterns(file_path, content, self.collector)

        except Exception as e:
            self.collector.add_issue(SecurityIssue(
                file_path=str(file_path),
                line_number=0,
                column=0,
                severity="ERROR",
                issue_type="scan_error",
                message=f"Error scanning file: {str(e)}",
                suggestion="Check file permissions and encoding"
            ))


class SecurityLinter:
    """Main security linter orchestrator following SRP."""

    def __init__(self) -> None:
        """Initialize the security linter with all components."""
        self.collector = SecurityIssueCollector()
        self.detector = SecurityPatternDetector()
        self.analyzer = SecurityASTAnalyzer()
        self.reporter = SecurityReporter()
        self.scanner = SecurityFileScanner(self.collector, self.detector, self.analyzer)

    def scan_file(self, file_path: Path) -> None:
        """Scan a single file for security issues."""
        self.scanner.scan_file(file_path)

    def report_issues(self, format_type: str) -> None:
        """Report all collected issues."""
        issues = self.collector.get_issues()
        if format_type == "json":
            self.reporter.report_json(issues)
        else:
            self.reporter.report_text(issues)

    def has_critical_issues(self) -> bool:
        """Check if any critical issues were found."""
        return self.collector.has_critical_issues()


def _scan_path(linter: SecurityLinter, path: Path, recursive: bool) -> None:
    """Scan a single path (file or directory) for security issues."""
    if path.is_file() and path.suffix == ".py":
        linter.scan_file(path)
    elif path.is_dir() and recursive:
        for py_file in path.rglob("*.py"):
            linter.scan_file(py_file)
    elif path.is_dir():
        for py_file in path.glob("*.py"):
            linter.scan_file(py_file)


def main() -> None:
    """Main entry point for security linter."""
    parser = argparse.ArgumentParser(description="Security linter for Python code")
    parser.add_argument("paths", nargs="+", help="Files or directories to scan")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--recursive", "-r", action="store_true", help="Scan directories recursively")

    args = parser.parse_args()
    linter = SecurityLinter()

    # Scan all provided paths
    for path_str in args.paths:
        _scan_path(linter, Path(path_str), args.recursive)

    linter.report_issues(args.format)

    # Exit with error code if critical issues found
    if linter.has_critical_issues():
        sys.exit(1)


if __name__ == "__main__":
    main()