#!/usr/bin/env python3
"""
Purpose: API security rules for FastAPI applications
Scope: Rate limiting, input validation, and endpoint security checks
Overview: This module provides security-focused rules for API endpoints,
    detecting missing rate limiting, input validation, and other security
    antipatterns common in AI-generated FastAPI code.
Dependencies: Framework interfaces, AST analysis utilities
Exports: API security-focused rules
Interfaces: All rules implement ASTLintRule interface
Implementation: Rule-based architecture with focus on API security patterns
"""

import ast

from design_linters.framework.interfaces import ASTLintRule, LintContext, LintViolation, Severity


class MissingRateLimitingRule(ASTLintRule):
    """Rule to detect API endpoints without rate limiting."""

    @property
    def rule_id(self) -> str:
        return "security.api.missing-rate-limiting"

    @property
    def rule_name(self) -> str:
        return "Missing Rate Limiting"

    @property
    def description(self) -> str:
        return "FastAPI endpoints should have rate limiting to prevent abuse"

    @property
    def severity(self) -> Severity:
        return Severity.WARNING

    @property
    def categories(self) -> set[str]:
        return {"security", "api", "rate-limiting"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        """Check if node is a function that should be examined."""
        return isinstance(node, ast.FunctionDef) and self._is_api_endpoint(node)

    def check_node(self, node: ast.AST, context: LintContext) -> list[LintViolation]:
        """Check if API endpoint has rate limiting."""
        violations = []
        func_node = node  # Type narrowing handled by should_check_node

        if not self._has_rate_limiting(func_node):
            violations.append(
                self.create_violation(
                    context=context,
                    node=func_node,
                    message=f"API endpoint '{func_node.name}' is missing rate limiting protection",
                    description=self.description,
                    suggestion="Add @get_rate_limiter().limit() decorator or rate limiting middleware",
                )
            )

        return violations

    def _is_api_endpoint(self, node: ast.FunctionDef) -> bool:
        """Check if function is a FastAPI endpoint."""
        # Look for FastAPI HTTP method decorators
        api_methods = {"get", "post", "put", "delete", "patch", "options", "head"}

        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Attribute)
                or isinstance(decorator, ast.Attribute)
            ) and decorator.func.attr in api_methods:
                return True

        return False

    def _has_rate_limiting(self, node: ast.FunctionDef) -> bool:
        """Check if function has rate limiting decorator."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                # Check for rate limiter decorator patterns
                if isinstance(decorator.func, ast.Attribute) and "limit" in str(decorator.func.attr):
                    return True
                # Check for rate limiting function calls
                if isinstance(decorator.func, ast.Call) and self._contains_rate_limit_call(decorator.func):
                    return True

        # Check for rate limiting calls in function body
        return any(isinstance(stmt, ast.Call) and self._is_rate_limit_call(stmt) for stmt in ast.walk(node))

    def _contains_rate_limit_call(self, node: ast.Call) -> bool:
        """Check if call contains rate limiting."""
        return self._is_rate_limit_call(node)

    def _is_rate_limit_call(self, node: ast.Call) -> bool:
        """Check if call is a rate limiting call."""
        if isinstance(node.func, ast.Name):
            return node.func.id in ["check_rate_limit", "rate_limit"]
        elif isinstance(node.func, ast.Attribute):
            return "limit" in str(node.func.attr) or "rate" in str(node.func.attr)
        return False


class MissingInputValidationRule(ASTLintRule):
    """Rule to detect API endpoints without proper input validation."""

    @property
    def rule_id(self) -> str:
        return "security.api.missing-input-validation"

    @property
    def rule_name(self) -> str:
        return "Missing Input Validation"

    @property
    def description(self) -> str:
        return "API endpoints should validate user input to prevent security vulnerabilities"

    @property
    def severity(self) -> Severity:
        return Severity.HIGH

    @property
    def categories(self) -> set[str]:
        return {"security", "api", "validation"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        """Check if node is a function that should be examined."""
        return isinstance(node, ast.FunctionDef) and self._is_api_endpoint(node) and self._accepts_user_input(node)

    def check_node(self, node: ast.AST, context: LintContext) -> list[LintViolation]:
        """Check if API endpoint has proper input validation."""
        violations = []
        func_node = node

        if not self._has_input_validation(func_node):
            violations.append(
                self.create_violation(
                    context=context,
                    node=func_node,
                    message=f"API endpoint '{func_node.name}' accepts user input without validation",
                    description=self.description,
                    suggestion="Use Pydantic models, validation decorators, or input sanitization",
                )
            )

        return violations

    def _is_api_endpoint(self, node: ast.FunctionDef) -> bool:
        """Check if function is a FastAPI endpoint."""
        api_methods = {"get", "post", "put", "delete", "patch"}

        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Attribute)
                and decorator.func.attr in api_methods
            ):
                return True
        return False

    def _accepts_user_input(self, node: ast.FunctionDef) -> bool:
        """Check if function accepts user input."""
        # Check for Request parameters, form data, or JSON body
        for arg in node.args.args:
            if arg.annotation:
                if isinstance(arg.annotation, ast.Name):
                    # Look for Request, BaseModel, or form parameters
                    if arg.annotation.id in ["Request"]:
                        return True
                # Look for Pydantic model parameters (often indicate user input)
                elif isinstance(arg.annotation, ast.Attribute):
                    return True

        # Check for POST/PUT methods that typically accept data
        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Attribute)
                and decorator.func.attr in ["post", "put", "patch"]
            ):
                return True

        return False

    def _has_input_validation(self, node: ast.FunctionDef) -> bool:
        """Check if function has input validation."""
        # Check for Pydantic models in parameters
        for arg in node.args.args:
            if (
                arg.annotation
                and isinstance(arg.annotation, ast.Name)
                and arg.annotation.id in ["BaseModel", "SecureTextInput", "SecureNumericInput"]
            ):
                return True

        # Check for validation calls in function body
        for stmt in ast.walk(node):
            if (
                isinstance(stmt, ast.Call)
                and isinstance(stmt.func, ast.Name)
                and stmt.func.id in ["validate", "sanitize", "check_input", "sanitize_text_input"]
            ):
                return True

        return False


class InsecureExceptionHandlingRule(ASTLintRule):
    """Rule to detect overly broad exception handling that can mask security issues."""

    @property
    def rule_id(self) -> str:
        return "security.exceptions.too-broad"

    @property
    def rule_name(self) -> str:
        return "Overly Broad Exception Handling"

    @property
    def description(self) -> str:
        return "Broad exception handling can mask security vulnerabilities and errors"

    @property
    def severity(self) -> Severity:
        return Severity.WARNING

    @property
    def categories(self) -> set[str]:
        return {"security", "exceptions", "error-handling"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        """Check if node is an exception handler."""
        return isinstance(node, ast.ExceptHandler)

    def check_node(self, node: ast.AST, context: LintContext) -> list[LintViolation]:
        """Check if exception handling is too broad."""
        violations = []
        except_node = node

        if self._is_too_broad(except_node):
            violations.append(
                self.create_violation(
                    context=context,
                    node=except_node,
                    message="Overly broad exception handling can mask security issues",
                    description=self.description,
                    suggestion="Use specific exception types and ensure proper error logging",
                )
            )

        return violations

    def _is_too_broad(self, node: ast.ExceptHandler) -> bool:
        """Check if exception handler is too broad."""
        # Bare except clause
        if node.type is None:
            return True

        # Catching generic Exception
        if isinstance(node.type, ast.Name) and node.type.id == "Exception":
            return True

        # Catching BaseException (even broader)
        return isinstance(node.type, ast.Name) and node.type.id == "BaseException"


class HardcodedSecretsRule(ASTLintRule):
    """Rule to detect hardcoded secrets and credentials."""

    @property
    def rule_id(self) -> str:
        return "security.secrets.hardcoded"

    @property
    def rule_name(self) -> str:
        return "Hardcoded Secrets"

    @property
    def description(self) -> str:
        return "Secrets and credentials should not be hardcoded in source code"

    @property
    def severity(self) -> Severity:
        return Severity.CRITICAL

    @property
    def categories(self) -> set[str]:
        return {"security", "secrets", "credentials"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        """Check if node is an assignment that might contain secrets."""
        return isinstance(node, ast.Assign)

    def check_node(self, node: ast.AST, context: LintContext) -> list[LintViolation]:
        """Check if assignment contains hardcoded secrets."""
        violations = []
        assign_node = node

        if self._contains_hardcoded_secret(assign_node):
            violations.append(
                self.create_violation(
                    context=context,
                    node=assign_node,
                    message="Hardcoded secret or credential detected",
                    description=self.description,
                    suggestion="Use environment variables or secure secret management systems",
                )
            )

        return violations

    def _contains_hardcoded_secret(self, node: ast.Assign) -> bool:
        """Check if assignment contains hardcoded secrets."""
        # Check variable names that suggest secrets
        secret_indicators = {"password", "secret", "key", "token", "credential", "auth"}

        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id.lower()
                # Check if variable name suggests a secret and value is a string literal
                if (
                    any(indicator in var_name for indicator in secret_indicators)
                    and isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, str)
                ):
                    # Ignore obvious dummy values
                    value = node.value.value.lower()
                    if not any(dummy in value for dummy in ["test", "dummy", "example", "placeholder"]):
                        return True

        return False


class MissingSecurityHeadersRule(ASTLintRule):
    """Rule to detect FastAPI applications missing security headers."""

    @property
    def rule_id(self) -> str:
        return "security.headers.missing"

    @property
    def rule_name(self) -> str:
        return "Missing Security Headers"

    @property
    def description(self) -> str:
        return "FastAPI applications should implement security headers middleware"

    @property
    def severity(self) -> Severity:
        return Severity.WARNING

    @property
    def categories(self) -> set[str]:
        return {"security", "headers", "middleware"}

    def should_check_node(self, node: ast.AST, context: LintContext) -> bool:
        """Check if node is a function call that creates FastAPI app."""
        return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "FastAPI"

    def check_node(self, node: ast.AST, context: LintContext) -> list[LintViolation]:
        """Check if FastAPI app has security headers middleware."""
        violations = []

        # Check if SecurityMiddleware is added anywhere in the module
        # Use the full AST tree from the context
        if not context.ast_tree:
            return violations

        has_security_middleware = False
        for child_node in ast.walk(context.ast_tree):
            # Check for add_middleware(SecurityMiddleware) pattern
            if (
                isinstance(child_node, ast.Call)
                and isinstance(child_node.func, ast.Attribute)
                and child_node.func.attr == "add_middleware"
                and child_node.args
            ):
                # Check if first arg is SecurityMiddleware
                first_arg = child_node.args[0]
                if isinstance(first_arg, ast.Name) and first_arg.id == "SecurityMiddleware":
                    has_security_middleware = True
                    break

        # Only create violation if we didn't find SecurityMiddleware
        if not has_security_middleware:
            violations.append(
                self.create_violation(
                    context=context,
                    node=node,
                    message="Ensure FastAPI application includes security headers middleware",
                    description=self.description,
                    suggestion="Add SecurityMiddleware to set proper security headers",
                )
            )

        return violations
