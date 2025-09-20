#!/usr/bin/env python3
"""
Purpose: Security linting tool for detecting common security antipatterns
Scope: FastAPI applications, input validation, rate limiting, and security headers
Overview: This tool scans Python files for security vulnerabilities and antipatterns,
    specifically targeting issues common in AI-generated code such as missing input
    validation, hardcoded secrets, and insecure configurations.
Dependencies: Python standard library, ast module for code parsing
Exports: Security vulnerability detection and reporting
Interfaces: Command-line interface for file scanning
Implementation: AST-based static analysis with configurable rules
"""

import argparse
import ast
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


class SecurityLinter:
    """Security linter for detecting common vulnerabilities."""

    def __init__(self) -> None:
        """Initialize the security linter."""
        self.issues: list[SecurityIssue] = []

        # Patterns for dangerous code
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

    def scan_file(self, file_path: Path) -> None:
        """Scan a Python file for security issues.

        Args:
            file_path: Path to the Python file to scan
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse AST for structural analysis
            try:
                tree = ast.parse(content)
                self._check_ast_patterns(file_path, tree)
            except SyntaxError as e:
                self.issues.append(
                    SecurityIssue(
                        file_path=str(file_path),
                        line_number=e.lineno or 0,
                        column=e.offset or 0,
                        severity="ERROR",
                        issue_type="syntax_error",
                        message=f"Syntax error: {e.msg}",
                        suggestion="Fix syntax errors before security analysis",
                    )
                )

            # Check for dangerous patterns
            self._check_text_patterns(file_path, content)

        except Exception as e:
            self.issues.append(
                SecurityIssue(
                    file_path=str(file_path),
                    line_number=0,
                    column=0,
                    severity="ERROR",
                    issue_type="scan_error",
                    message=f"Failed to scan file: {e}",
                    suggestion="Ensure file is readable and contains valid Python",
                )
            )

    def _check_ast_patterns(self, file_path: Path, tree: ast.AST) -> None:
        """Check AST for security patterns.

        Args:
            file_path: Path to the file being scanned
            tree: AST tree of the file
        """
        for node in ast.walk(tree):
            # Check for missing input validation in FastAPI endpoints
            if isinstance(node, ast.FunctionDef):
                self._check_function_security(file_path, node)

            # Check for insecure exception handling
            elif isinstance(node, ast.ExceptHandler):
                self._check_exception_handling(file_path, node)

            # Check for missing rate limiting decorators
            elif isinstance(node, ast.FunctionDef) and self._is_api_endpoint(node):
                self._check_rate_limiting(file_path, node)

    def _check_function_security(self, file_path: Path, node: ast.FunctionDef) -> None:
        """Check function for security issues.

        Args:
            file_path: Path to the file
            node: Function definition node
        """
        # Check if function handles user input without validation
        if self._handles_user_input(node) and not self._has_validation(node):
            self.issues.append(
                SecurityIssue(
                    file_path=str(file_path),
                    line_number=node.lineno,
                    column=node.col_offset,
                    severity="HIGH",
                    issue_type="missing_input_validation",
                    message=f"Function '{node.name}' handles user input without validation",
                    suggestion="Add Pydantic models or input validation to sanitize user data",
                )
            )

    def _check_exception_handling(self, file_path: Path, node: ast.ExceptHandler) -> None:
        """Check exception handling for security issues.

        Args:
            file_path: Path to the file
            node: Exception handler node
        """
        # Check for overly broad exception handling
        if node.type is None or (isinstance(node.type, ast.Name) and node.type.id == "Exception"):
            self.issues.append(
                SecurityIssue(
                    file_path=str(file_path),
                    line_number=node.lineno,
                    column=node.col_offset,
                    severity="MEDIUM",
                    issue_type="broad_exception_handling",
                    message="Overly broad exception handling can mask security issues",
                    suggestion="Use specific exception types and proper error logging",
                )
            )

    def _check_rate_limiting(self, file_path: Path, node: ast.FunctionDef) -> None:
        """Check if API endpoints have rate limiting.

        Args:
            file_path: Path to the file
            node: Function definition node
        """
        # Check if endpoint has rate limiting decorator
        has_rate_limit = any(self._is_rate_limit_decorator(decorator) for decorator in node.decorator_list)

        if not has_rate_limit:
            self.issues.append(
                SecurityIssue(
                    file_path=str(file_path),
                    line_number=node.lineno,
                    column=node.col_offset,
                    severity="MEDIUM",
                    issue_type="missing_rate_limiting",
                    message=f"API endpoint '{node.name}' missing rate limiting",
                    suggestion="Add @get_rate_limiter().limit() decorator or rate limiting check",
                )
            )

    def _check_text_patterns(self, file_path: Path, content: str) -> None:
        """Check file content for dangerous text patterns.

        Args:
            file_path: Path to the file
            content: File content as string
        """
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            for category, patterns in self.dangerous_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        severity = self._get_severity_for_category(category)
                        message = self._get_message_for_category(category)
                        suggestion = self._get_suggestion_for_category(category)

                        self.issues.append(
                            SecurityIssue(
                                file_path=str(file_path),
                                line_number=line_num,
                                column=0,
                                severity=severity,
                                issue_type=category,
                                message=f"{message}: {line.strip()}",
                                suggestion=suggestion,
                            )
                        )

    def _is_api_endpoint(self, node: ast.FunctionDef) -> bool:
        """Check if function is a FastAPI endpoint.

        Args:
            node: Function definition node

        Returns:
            True if function appears to be an API endpoint
        """
        return any(
            isinstance(decorator, ast.Attribute) and decorator.attr in ["get", "post", "put", "delete", "patch"]
            for decorator in node.decorator_list
        )

    def _handles_user_input(self, node: ast.FunctionDef) -> bool:
        """Check if function handles user input.

        Args:
            node: Function definition node

        Returns:
            True if function appears to handle user input
        """
        # Check for Request parameter or Pydantic models in arguments
        for arg in node.args.args:
            if (
                arg.annotation
                and isinstance(arg.annotation, ast.Name)
                and arg.annotation.id in ["Request", "BaseModel"]
            ):
                return True
        return False

    def _has_validation(self, node: ast.FunctionDef) -> bool:
        """Check if function has input validation.

        Args:
            node: Function definition node

        Returns:
            True if function has validation
        """
        # Look for Pydantic models, validators, or validation calls
        for stmt in ast.walk(node):
            if (
                isinstance(stmt, ast.Call)
                and isinstance(stmt.func, ast.Name)
                and stmt.func.id in ["validate", "sanitize", "check_input"]
            ):
                return True
        return False

    def _is_rate_limit_decorator(self, decorator: ast.expr) -> bool:
        """Check if decorator is for rate limiting.

        Args:
            decorator: Decorator node

        Returns:
            True if decorator is for rate limiting
        """
        if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
            return "limit" in str(decorator.func.attr)
        return False

    def _get_severity_for_category(self, category: str) -> str:
        """Get severity level for issue category."""
        severity_map = {
            "hardcoded_secrets": "CRITICAL",
            "sql_injection": "CRITICAL",
            "command_injection": "CRITICAL",
            "insecure_random": "HIGH",
        }
        return severity_map.get(category, "MEDIUM")

    def _get_message_for_category(self, category: str) -> str:
        """Get message for issue category."""
        message_map = {
            "hardcoded_secrets": "Hardcoded secret detected",
            "sql_injection": "Potential SQL injection vulnerability",
            "command_injection": "Potential command injection vulnerability",
            "insecure_random": "Insecure random number generation",
        }
        return message_map.get(category, "Security issue detected")

    def _get_suggestion_for_category(self, category: str) -> str:
        """Get suggestion for issue category."""
        suggestion_map = {
            "hardcoded_secrets": "Use environment variables or secure secret management",
            "sql_injection": "Use parameterized queries or ORM methods",
            "command_injection": "Avoid system calls or use subprocess with shell=False",
            "insecure_random": "Use secrets module for cryptographic randomness",
        }
        return suggestion_map.get(category, "Review and fix security issue")

    def report_issues(self, output_format: str = "text") -> None:
        """Report found security issues.

        Args:
            output_format: Format for output ('text' or 'json')
        """
        if output_format == "json":
            import json

            issues_dict = [issue._asdict() for issue in self.issues]
            print(json.dumps(issues_dict, indent=2))
        else:
            if not self.issues:
                print("✅ No security issues found!")
                return

            print(f"🔒 Security Analysis Results: {len(self.issues)} issues found\n")

            # Group by severity
            by_severity: dict[str, list[SecurityIssue]] = {}
            for issue in self.issues:
                if issue.severity not in by_severity:
                    by_severity[issue.severity] = []
                by_severity[issue.severity].append(issue)

            # Report by severity level
            severity_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "ERROR"]
            for severity in severity_order:
                if severity in by_severity:
                    print(f"📊 {severity} Issues ({len(by_severity[severity])})")
                    print("=" * 50)

                    for issue in by_severity[severity]:
                        print(f"File: {issue.file_path}:{issue.line_number}")
                        print(f"Issue: {issue.message}")
                        print(f"Type: {issue.issue_type}")
                        print(f"Suggestion: {issue.suggestion}")
                        print("-" * 30)
                    print()


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
    critical_issues = [i for i in linter.issues if i.severity == "CRITICAL"]
    if critical_issues:
        sys.exit(1)


if __name__ == "__main__":
    main()
