"""Core repository modules for the backend application."""

from .exceptions import (
    AppExceptionError,
    AuthenticationError,
    AuthorizationError,
    ConfigurationError,
    ExternalServiceError,
    RateLimitExceededError,
    ResourceNotFoundError,
    ServiceError,
    ValidationError,
    WebSocketError,
)

__all__ = [
    "AppExceptionError",
    "AuthenticationError",
    "AuthorizationError",
    "ConfigurationError",
    "ExternalServiceError",
    "RateLimitExceededError",
    "ResourceNotFoundError",
    "ServiceError",
    "ValidationError",
    "WebSocketError",
]
