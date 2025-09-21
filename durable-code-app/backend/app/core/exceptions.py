"""Structured exception hierarchy for consistent backend error handling.

Purpose: Structured exception hierarchy for consistent backend error handling and API responses.
Scope: Application-wide exception classes for all error scenarios in the backend system
Overview: This module provides a comprehensive exception hierarchy that ensures consistent
    error handling across the entire application. It defines base and specific exception
    classes with structured error information including HTTP status codes, error codes for
    client identification, human-readable messages, and optional debugging details. The
    hierarchy supports various error scenarios including validation errors, authentication
    failures, authorization issues, resource not found, rate limiting, and service unavailable
    conditions. All exceptions integrate seamlessly with FastAPI's error handling middleware.
Dependencies: FastAPI status codes, typing for type hints
Exports: AppExceptionError base class and specific exceptions (ValidationError, AuthenticationError, etc.)
Interfaces: Exception classes with status_code, error_code, message, and details attributes
Implementation: Inheritance-based hierarchy with structured error data for consistent API responses
"""

from typing import Any

from fastapi import status


class AppExceptionError(Exception):
    """
    Base exception for all application errors.

    Provides structured error information including:
    - Status code for HTTP responses
    - Error code for client identification
    - Human-readable message
    - Optional details for debugging
    """

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the exception with structured error information."""
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}


class ValidationError(AppExceptionError):
    """
    Exception for input validation failures.

    Used when user input doesn't meet validation requirements.
    """

    def __init__(
        self,
        message: str = "Invalid input provided",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize validation error with 422 status."""
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class ServiceError(AppExceptionError):
    """
    Exception for service layer errors.

    Used when business logic operations fail.
    """

    def __init__(
        self,
        message: str = "Service operation failed",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize service error with 500 status."""
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="SERVICE_ERROR",
            details=details,
        )


class WebSocketError(AppExceptionError):
    """
    Exception for WebSocket-specific errors.

    Used for WebSocket connection and communication issues.
    """

    def __init__(
        self,
        message: str = "WebSocket operation failed",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize WebSocket error with 500 status."""
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="WEBSOCKET_ERROR",
            details=details,
        )


class ConfigurationError(AppExceptionError):
    """
    Exception for configuration-related errors.

    Used when configuration is missing or invalid.
    """

    def __init__(
        self,
        message: str = "Configuration error",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize configuration error with 500 status."""
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="CONFIG_ERROR",
            details=details,
        )


class ExternalServiceError(AppExceptionError):
    """
    Exception for external service communication failures.

    Used when external API calls or database operations fail.
    Should be used with retry logic.
    """

    def __init__(
        self,
        message: str = "External service unavailable",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize external service error with 503 status."""
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details,
        )


class ResourceNotFoundError(AppExceptionError):
    """
    Exception for resource not found scenarios.

    Used when requested resource doesn't exist.
    """

    def __init__(
        self,
        message: str = "Resource not found",
        resource_type: str | None = None,
        resource_id: str | None = None,
    ) -> None:
        """Initialize not found error with 404 status."""
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id

        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            details=details,
        )


class AuthenticationError(AppExceptionError):
    """
    Exception for authentication failures.

    Used when authentication is required but fails.
    """

    def __init__(
        self,
        message: str = "Authentication failed",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize authentication error with 401 status."""
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR",
            details=details,
        )


class AuthorizationError(AppExceptionError):
    """
    Exception for authorization failures.

    Used when user lacks permission for an operation.
    """

    def __init__(
        self,
        message: str = "Insufficient permissions",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize authorization error with 403 status."""
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR",
            details=details,
        )


class RateLimitExceededError(AppExceptionError):
    """
    Exception for rate limit violations.

    Used when client exceeds rate limits.
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int | None = None,
    ) -> None:
        """Initialize rate limit error with 429 status."""
        details = {}
        if retry_after:
            details["retry_after"] = retry_after

        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details,
        )
