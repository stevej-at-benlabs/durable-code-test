"""
Purpose: Error handling and resilience pattern linting rules for code quality enforcement
Scope: Linting rules for exception handling, retry logic, circuit breakers, and structured error patterns
Overview: Comprehensive collection of AST-based linting rules that enforce proper error handling patterns including prevention of broad exception catching, requirement of retry logic for external operations, structured exception class validation, mandatory error logging, and circuit breaker usage recommendations for resilient system design and robust error management.
Dependencies: ast module for AST traversal, design_linters framework interfaces for rule implementation
Exports: NoBroadExceptionsRule, RequireRetryLogicRule, StructuredExceptionsRule, RequireErrorLoggingRule, CircuitBreakerUsageRule
Interfaces: ASTLintRule interface implementations with check methods for AST node analysis
Implementation: AST-based rule implementations using node traversal and pattern matching for error handling validation
"""

import ast

from design_linters.framework.interfaces import ASTLintRule, LintViolation, Severity


class NoBroadExceptionsRule(ASTLintRule):
    """Detect and prevent broad exception catching."""

    name = "error_handling.exceptions.no-broad"
    category = "error_handling"
    description = "Prohibits catching broad exception types"

    def check(self, tree: ast.AST, filepath: str, source: str) -> list[LintViolation]:
        """Check for broad exception catching in Python code."""
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    # Bare except: clause
                    violations.append(
                        LintViolation(
                            rule_id=self.name,
                            file_path=filepath,
                            line=node.lineno,
                            column=node.col_offset,
                            message="Bare except clause found - catch specific exceptions",
                            severity=Severity.ERROR,
                            description=self.description,
                        )
                    )
                elif isinstance(node.type, ast.Name):
                    if node.type.id in ["Exception", "BaseException"]:
                        violations.append(
                            LintViolation(
                                rule_id=self.name,
                                file_path=filepath,
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Broad exception type '{node.type.id}' - use specific exceptions",
                                severity=Severity.ERROR,
                                description=self.description,
                            )
                        )
                elif isinstance(node.type, ast.Tuple):
                    # Check tuple of exceptions
                    for exc in node.type.elts:
                        if isinstance(exc, ast.Name) and exc.id in [
                            "Exception",
                            "BaseException",
                        ]:
                            violations.append(
                                LintViolation(
                                    rule_id=self.name,
                                    file_path=filepath,
                                    line=node.lineno,
                                    column=node.col_offset,
                                    message=f"Broad exception type '{exc.id}' in tuple - use specific exceptions",
                                    severity=Severity.ERROR,
                                    description=self.description,
                                )
                            )

        return violations


class RequireRetryLogicRule(ASTLintRule):
    """Ensure external operations have retry logic."""

    name = "error_handling.resilience.require-retry"
    category = "error_handling"
    description = "External operations must have retry logic"

    def check(self, tree: ast.AST, filepath: str, source: str) -> list[LintViolation]:
        """Check that external operations have retry decorators."""
        violations = []

        # Skip if this is a test file
        if "test" in filepath:
            return violations

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Check if function name suggests external operation
                is_external = any(
                    keyword in node.name.lower()
                    for keyword in [
                        "fetch",
                        "call",
                        "request",
                        "api",
                        "external",
                        "remote",
                        "database",
                        "db",
                        "query",
                        "http",
                        "webhook",
                    ]
                )

                if is_external:
                    # Check if it has retry decorator
                    has_retry = any(self._is_retry_decorator(dec) for dec in node.decorator_list)

                    if not has_retry:
                        violations.append(
                            LintViolation(
                                rule_id=self.name,
                                file_path=filepath,
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"External operation '{node.name}' should have retry logic",
                                severity=Severity.WARNING,
                                description=self.description,
                            )
                        )

        return violations

    def _is_retry_decorator(self, decorator: ast.AST) -> bool:
        """Check if decorator is retry-related."""
        if isinstance(decorator, ast.Name):
            return "retry" in decorator.id.lower()
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return "retry" in decorator.func.id.lower()
            elif isinstance(decorator.func, ast.Attribute):
                return "retry" in decorator.func.attr.lower()
        return False


class StructuredExceptionsRule(ASTLintRule):
    """Ensure custom exceptions follow structured pattern."""

    name = "error_handling.exceptions.structured"
    category = "error_handling"
    description = "Custom exceptions must have proper structure"

    def check(self, tree: ast.AST, filepath: str, source: str) -> list[LintViolation]:
        """Check that exception classes are properly structured."""
        violations = []

        # Only check exception files
        if "exception" not in filepath.lower() and "error" not in filepath.lower():
            return violations

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it's an exception class
                is_exception = any(
                    (isinstance(base, ast.Name) and "Exception" in base.id)
                    or (isinstance(base, ast.Name) and "Error" in base.id)
                    for base in node.bases
                )

                if is_exception:
                    # Check for required attributes
                    has_status_code = False
                    has_error_code = False
                    has_init = False

                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                            has_init = True
                            # Check if __init__ sets required attributes
                            init_source = ast.unparse(item)
                            if "status_code" in init_source:
                                has_status_code = True
                            if "error_code" in init_source:
                                has_error_code = True

                    if has_init and not has_status_code and node.name not in ["AppException", "AppExceptionError"]:
                        violations.append(
                            LintViolation(
                                rule_id=self.name,
                                file_path=filepath,
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Exception '{node.name}' should define status_code",
                                severity=Severity.WARNING,
                                description=self.description,
                            )
                        )

                    if has_init and not has_error_code and node.name not in ["AppException", "AppExceptionError"]:
                        violations.append(
                            LintViolation(
                                rule_id=self.name,
                                file_path=filepath,
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Exception '{node.name}' should define error_code",
                                severity=Severity.WARNING,
                                description=self.description,
                            )
                        )

        return violations


class RequireErrorLoggingRule(ASTLintRule):
    """Ensure errors are properly logged."""

    name = "error_handling.logging.required"
    category = "error_handling"
    description = "Caught exceptions must be logged"

    def check(self, tree: ast.AST, filepath: str, source: str) -> list[LintViolation]:
        """Check that caught exceptions are logged."""
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                # Check if the except block logs the error
                has_logging = False

                for stmt in node.body:
                    if self._contains_logging(stmt):
                        has_logging = True
                        break
                    # Also check if it re-raises
                    if isinstance(stmt, ast.Raise):
                        has_logging = True  # Re-raising is acceptable
                        break

                if not has_logging and node.type:
                    # Get exception type name for better error message
                    exc_type = "exception"
                    if isinstance(node.type, ast.Name):
                        exc_type = node.type.id

                    violations.append(
                        LintViolation(
                            rule_id=self.name,
                            file_path=filepath,
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Caught {exc_type} should be logged or re-raised",
                            severity=Severity.WARNING,
                            description=self.description,
                        )
                    )

        return violations

    def _contains_logging(self, node: ast.AST) -> bool:
        """Check if node contains logging call."""
        if (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
        ):
            return node.value.func.attr in [
                "debug",
                "info",
                "warning",
                "error",
                "exception",
                "critical",
            ]

        # Recursively check in nested structures
        return any(self._contains_logging(child) for child in ast.iter_child_nodes(node))


class CircuitBreakerUsageRule(ASTLintRule):
    """Encourage circuit breaker pattern for external services."""

    name = "error_handling.resilience.circuit-breaker"
    category = "error_handling"
    description = "External service calls should use circuit breakers"

    def check(self, tree: ast.AST, filepath: str, source: str) -> list[LintViolation]:
        """Check for circuit breaker usage on external calls."""
        violations = []

        # Skip test files
        if "test" in filepath:
            return violations

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Check if it's an external service call
                is_service_call = any(
                    keyword in node.name.lower()
                    for keyword in [
                        "service",
                        "api",
                        "external",
                        "remote",
                        "database",
                        "cache",
                    ]
                )

                if is_service_call:
                    # Check for circuit breaker decorator or usage
                    has_circuit_breaker = any(self._is_circuit_breaker(dec) for dec in node.decorator_list)

                    if not has_circuit_breaker:
                        # Check if circuit breaker is used inside the function
                        has_internal_cb = self._contains_circuit_breaker(node)

                        if not has_internal_cb:
                            violations.append(
                                LintViolation(
                                    rule_id=self.name,
                                    file_path=filepath,
                                    line=node.lineno,
                                    column=node.col_offset,
                                    message=f"Service call '{node.name}' could benefit from circuit breaker",
                                    severity=Severity.INFO,
                                    description=self.description,
                                )
                            )

        return violations

    def _is_circuit_breaker(self, decorator: ast.AST) -> bool:
        """Check if decorator is circuit breaker related."""
        if isinstance(decorator, ast.Name):
            return "circuit" in decorator.id.lower() or "breaker" in decorator.id.lower()
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return "circuit" in decorator.func.id.lower() or "breaker" in decorator.func.id.lower()
            elif isinstance(decorator.func, ast.Attribute):
                return "circuit" in decorator.func.attr.lower() or "breaker" in decorator.func.attr.lower()
        return False

    def _contains_circuit_breaker(self, node: ast.AST) -> bool:
        """Check if function body contains circuit breaker usage."""
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and "circuit" in child.id.lower():
                return True
            if isinstance(child, ast.Attribute) and "circuit" in child.attr.lower():
                return True
        return False


# Export all rules
__all__ = [
    "NoBroadExceptionsRule",
    "RequireRetryLogicRule",
    "StructuredExceptionsRule",
    "RequireErrorLoggingRule",
    "CircuitBreakerUsageRule",
]
