#!/usr/bin/env python3
"""
Purpose: Test skip detection rules for preventing indefinitely skipped tests
Scope: Testing category rule implementation for pytest and unittest skip patterns
Overview: This module implements a rule that detects and flags skipped tests in the codebase,
    ensuring that tests are either fixed or removed rather than being indefinitely skipped.
    It identifies various forms of test skipping including @pytest.mark.skip decorators,
    pytest.skip() function calls, unittest skip decorators, and similar patterns. The rule
    allows conditional skips (skipif) for legitimate cases like missing optional dependencies,
    but flags unconditional skips that indicate broken or outdated tests. This helps maintain
    test suite integrity by preventing the accumulation of skipped tests that mask failures
    and reduce effective test coverage.
Dependencies: Framework interfaces, AST analysis utilities
Exports: NoSkippedTestsRule for test skip detection
Interfaces: Implements ASTLintRule interface from framework
Implementation: AST-based detection of test skip patterns with configurable exceptions
"""

import ast
from typing import Any

from design_linters.framework.interfaces import ASTLintRule, LintContext, LintViolation, Severity


class NoSkippedTestsRule(ASTLintRule):
    """Rule to detect skipped tests that should be fixed or removed.

    This rule helps maintain test suite quality by preventing tests from being
    indefinitely skipped, which can mask failures and reduce test coverage.
    """

    @property
    def rule_id(self) -> str:
        return "testing.no-skipped-tests"

    @property
    def rule_name(self) -> str:
        return "No Skipped Tests"

    @property
    def description(self) -> str:
        return "Tests should not be skipped - they should be fixed or removed"

    @property
    def severity(self) -> Severity:
        return Severity.ERROR

    @property
    def categories(self) -> set[str]:
        return {"testing", "quality", "coverage"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        """Check if this node should be analyzed for test skip patterns."""
        # Only check test files
        if not self._is_test_file(context):
            return False

        # Check for decorator patterns
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
            return self._has_skip_decorator(node)

        # Check for skip function calls
        if isinstance(node, ast.Call):
            return self._is_skip_call(node)

        return False

    def check_node(self, node: ast.AST, context: LintContext) -> list[LintViolation]:
        """Check node for test skip patterns."""
        violations = []
        config = self.get_configuration(context.metadata or {})

        # Check for disable comments
        if self._has_disable_comment(node, context):
            return []

        # Handle decorated functions/classes
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            violations.extend(self._check_decorators(node, context, config))

        # Handle skip function calls
        if isinstance(node, ast.Call):
            violations.extend(self._check_skip_call(node, context, config))

        return violations

    def _is_test_file(self, context: LintContext) -> bool:
        """Check if the current file is a test file."""
        file_path = str(context.file_path)
        return (
            "/test" in file_path
            or "_test.py" in file_path
            or "test_" in file_path
            or ".test." in file_path
            or ".spec." in file_path
        )

    def _has_skip_decorator(self, node: ast.FunctionDef | ast.ClassDef) -> bool:
        """Check if node has skip-related decorators."""
        for decorator in node.decorator_list:
            decorator_str = ast.unparse(decorator) if hasattr(ast, "unparse") else str(decorator)
            if any(
                pattern in decorator_str
                for pattern in [
                    "pytest.mark.skip",
                    "unittest.skip",
                    "@skip",
                    "mark.skip",
                ]
            ):
                return True
        return False

    def _is_skip_call(self, node: ast.Call) -> bool:
        """Check if node is a skip function call."""
        if isinstance(node.func, ast.Attribute):
            # Check for pytest.skip() or similar
            func_str = ast.unparse(node.func) if hasattr(ast, "unparse") else ""
            return "skip" in func_str.lower()
        elif isinstance(node.func, ast.Name):
            # Check for direct skip() calls
            return node.func.id == "skip"
        return False

    def _check_decorators(
        self,
        node: ast.FunctionDef | ast.ClassDef,
        context: LintContext,
        config: dict[str, Any],
    ) -> list[LintViolation]:
        """Check decorators for skip patterns."""
        violations = []

        for decorator in node.decorator_list:
            decorator_str = ast.unparse(decorator) if hasattr(ast, "unparse") else str(decorator)

            # Allow skipif for conditional skips (e.g., missing dependencies)
            if "skipif" in decorator_str:
                if not config.get("allow_skipif", True):
                    violations.append(
                        self._create_violation(
                            node,
                            context,
                            f"Conditional skip (skipif) found in {node.name}",
                            "Consider making the dependency required or mocking it in tests",
                        )
                    )
            # Flag unconditional skips
            elif any(pattern in decorator_str for pattern in ["pytest.mark.skip", "unittest.skip", "@skip"]):
                violations.append(
                    self._create_violation(
                        node,
                        context,
                        f"Skipped test found: {node.name}",
                        "Fix the test or remove it if it's no longer needed",
                    )
                )

        return violations

    def _check_skip_call(self, node: ast.Call, context: LintContext, config: dict[str, Any]) -> list[LintViolation]:
        """Check for skip function calls."""
        violations = []

        # Check if this is a conditional skip (has a condition argument)
        is_conditional = len(node.args) > 1 or any(kw.arg in ["condition", "reason"] for kw in node.keywords)

        if is_conditional and config.get("allow_conditional_skip_calls", True):
            return []

        func_str = ast.unparse(node) if hasattr(ast, "unparse") else "skip()"
        violations.append(
            self._create_violation(
                node,
                context,
                f"Test skip call found: {func_str[:50]}",
                "Fix the test condition or remove the skip call",
            )
        )

        return violations

    def _create_violation(self, node: ast.AST, context: LintContext, message: str, suggestion: str) -> LintViolation:
        """Create a violation for a skipped test."""
        return self.create_violation(
            context=context,
            node=node,
            message=message,
            description=(
                "Skipped tests reduce test coverage effectiveness and can hide "
                "regressions. Tests should either be fixed to pass or removed if "
                "they are no longer relevant."
            ),
            suggestion=suggestion,
            violation_context={
                "file": str(context.file_path),
                "line": node.lineno,
                "function": context.current_function,
                "class": context.current_class,
            },
        )

    def _has_disable_comment(self, node: ast.AST, context: LintContext) -> bool:
        """Check if the node has a disable comment."""
        # Check for disable comments like: # design-lint: ignore[testing.no-skipped-tests]
        if hasattr(context, "source_lines") and context.source_lines:
            line_idx = node.lineno - 1
            if 0 <= line_idx < len(context.source_lines):
                line = context.source_lines[line_idx]
                return "design-lint: ignore" in line and (self.rule_id in line or "testing.no-skipped-tests" in line)
        return False
