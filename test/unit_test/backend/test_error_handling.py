"""
Unit tests for error handling and resilience patterns.

Tests the exception hierarchy, retry logic, circuit breakers,
and global exception handlers.
"""

import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse

# Import our error handling modules - modules should be accessible directly
from app.core.exceptions import (
    AppExceptionError,
    ValidationError,
    ServiceError,
    WebSocketError,
    ExternalServiceError,
    ResourceNotFoundError,
    AuthenticationError,
    AuthorizationError,
    RateLimitExceededError,
)
from app.core.retry import (
    RetryConfig,
    with_retry,
    retry_on_external_error,
    retry_on_connection_error,
)
from app.core.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerState,
)


class TestExceptionHierarchy:
    """Test custom exception classes."""

    def test_app_exception_base(self):
        """Test base AppExceptionError."""
        exc = AppExceptionError(
            message="Test error",
            status_code=500,
            error_code="TEST_ERROR",
            details={"key": "value"}
        )
        assert exc.message == "Test error"
        assert exc.status_code == 500
        assert exc.error_code == "TEST_ERROR"
        assert exc.details == {"key": "value"}

    def test_validation_error(self):
        """Test ValidationError specific defaults."""
        exc = ValidationError(
            message="Invalid input",
            details={"field": "email", "error": "invalid format"}
        )
        assert exc.status_code == 422
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.details["field"] == "email"

    def test_service_error(self):
        """Test ServiceError."""
        exc = ServiceError(message="Service failed")
        assert exc.status_code == 500
        assert exc.error_code == "SERVICE_ERROR"

    def test_websocket_error(self):
        """Test WebSocketError."""
        exc = WebSocketError(message="Connection lost")
        assert exc.status_code == 500
        assert exc.error_code == "WEBSOCKET_ERROR"

    def test_external_service_error(self):
        """Test ExternalServiceError."""
        exc = ExternalServiceError(message="API unavailable")
        assert exc.status_code == 503
        assert exc.error_code == "EXTERNAL_SERVICE_ERROR"

    def test_resource_not_found_error(self):
        """Test ResourceNotFoundError."""
        exc = ResourceNotFoundError(
            message="User not found",
            resource_type="User",
            resource_id="123"
        )
        assert exc.status_code == 404
        assert exc.error_code == "RESOURCE_NOT_FOUND"
        assert exc.details["resource_type"] == "User"
        assert exc.details["resource_id"] == "123"

    def test_authentication_error(self):
        """Test AuthenticationError."""
        exc = AuthenticationError(message="Invalid token")
        assert exc.status_code == 401
        assert exc.error_code == "AUTHENTICATION_ERROR"

    def test_authorization_error(self):
        """Test AuthorizationError."""
        exc = AuthorizationError(message="Access denied")
        assert exc.status_code == 403
        assert exc.error_code == "AUTHORIZATION_ERROR"

    def test_rate_limit_error(self):
        """Test RateLimitExceededError."""
        exc = RateLimitExceededError(
            message="Too many requests",
            retry_after=60
        )
        assert exc.status_code == 429
        assert exc.error_code == "RATE_LIMIT_EXCEEDED"
        assert exc.details["retry_after"] == 60


class TestRetryLogic:
    """Test retry decorator and configurations."""

    @pytest.mark.asyncio
    async def test_retry_on_external_error(self):
        """Test retry decorator with ExternalServiceError."""
        call_count = 0

        @retry_on_external_error
        async def flaky_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ExternalServiceError("Service unavailable")
            return "success"

        result = await flaky_operation()
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_with_custom_config(self):
        """Test retry with custom configuration."""
        call_count = 0
        config = RetryConfig(
            max_attempts=2,
            min_wait=0.01,
            max_wait=0.1,
            exceptions=(ValueError,)
        )

        @with_retry(config=config)
        async def custom_retry_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Test error")
            return "success"

        result = await custom_retry_operation()
        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_retry_exhaustion(self):
        """Test retry exhaustion raises exception."""
        config = RetryConfig(
            max_attempts=2,
            min_wait=0.01,
            max_wait=0.1,
            exceptions=(ExternalServiceError,)
        )

        @with_retry(config=config)
        async def always_failing_operation():
            raise ExternalServiceError("Always fails")

        with pytest.raises(ExternalServiceError):
            await always_failing_operation()

    @pytest.mark.asyncio
    async def test_retry_on_connection_error(self):
        """Test retry on multiple connection-related errors."""
        errors = [ConnectionError("Connection lost"), TimeoutError("Timeout")]
        attempt = 0

        @retry_on_connection_error
        async def connection_operation():
            nonlocal attempt
            if attempt < len(errors):
                error = errors[attempt]
                attempt += 1
                raise error
            return "connected"

        result = await connection_operation()
        assert result == "connected"
        assert attempt == len(errors)


class TestCircuitBreaker:
    """Test circuit breaker functionality."""

    @pytest.mark.asyncio
    async def test_circuit_breaker_closed_to_open(self):
        """Test circuit breaker transitions from closed to open."""
        cb = CircuitBreaker(
            name="test",
            failure_threshold=2,
            success_threshold=1,
            timeout_duration=0.1
        )

        async def failing_operation():
            raise ExternalServiceError("Failed")

        # First failure
        with pytest.raises(ExternalServiceError):
            await cb.call(failing_operation)
        assert cb.state == CircuitBreakerState.CLOSED

        # Second failure - should open circuit
        with pytest.raises(ExternalServiceError):
            await cb.call(failing_operation)
        assert cb.state == CircuitBreakerState.OPEN

    @pytest.mark.asyncio
    async def test_circuit_breaker_open_rejects_calls(self):
        """Test that open circuit breaker rejects calls."""
        cb = CircuitBreaker(
            name="test",
            failure_threshold=1,
            timeout_duration=10  # Long timeout
        )

        async def failing_operation():
            raise ExternalServiceError("Failed")

        # Open the circuit
        with pytest.raises(ExternalServiceError):
            await cb.call(failing_operation)
        assert cb.state == CircuitBreakerState.OPEN

        # Next call should be rejected immediately
        with pytest.raises(ExternalServiceError) as exc_info:
            await cb.call(failing_operation)
        assert "Circuit breaker 'test' is open" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_to_closed(self):
        """Test circuit breaker recovers from half-open to closed."""
        cb = CircuitBreaker(
            name="test",
            failure_threshold=1,
            success_threshold=2,
            timeout_duration=0.01  # Very short timeout
        )

        call_count = 0

        async def recovering_operation():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ExternalServiceError("Failed")
            return "success"

        # Open the circuit
        with pytest.raises(ExternalServiceError):
            await cb.call(recovering_operation)
        assert cb.state == CircuitBreakerState.OPEN

        # Wait for timeout
        await asyncio.sleep(0.02)

        # Should transition to half-open and succeed
        result = await cb.call(recovering_operation)
        assert result == "success"
        assert cb.state == CircuitBreakerState.HALF_OPEN

        # Second success should close circuit
        result = await cb.call(recovering_operation)
        assert result == "success"
        assert cb.state == CircuitBreakerState.CLOSED

    def test_circuit_breaker_get_status(self):
        """Test circuit breaker status reporting."""
        cb = CircuitBreaker(
            name="test_cb",
            failure_threshold=5,
            success_threshold=3,
            timeout_duration=60.0
        )

        status = cb.get_status()
        assert status["name"] == "test_cb"
        assert status["state"] == "closed"
        assert status["failure_threshold"] == 5
        assert status["success_threshold"] == 3
        assert status["timeout_duration"] == 60.0


class TestGlobalExceptionHandlers:
    """Test global exception handlers integration."""

    def setup_method(self):
        """Set up test FastAPI app with exception handlers."""
        from app.main import create_application
        self.app = create_application()
        self.client = TestClient(self.app)

    @patch("app.main.logger")
    def test_app_exception_handler(self, mock_logger):
        """Test AppExceptionError handler returns structured response."""
        @self.app.get("/test-app-error")
        async def test_endpoint():
            raise ServiceError(
                message="Service operation failed",
                details={"operation": "test"}
            )

        response = self.client.get("/test-app-error")
        assert response.status_code == 500
        data = response.json()
        assert data["error"] == "SERVICE_ERROR"
        assert data["message"] == "Service operation failed"
        assert data["details"]["operation"] == "test"

    @patch("app.main.logger")
    def test_validation_exception_handler(self, mock_logger):
        """Test ValidationError handler."""
        @self.app.get("/test-validation-error")
        async def test_endpoint():
            raise ValidationError(
                message="Invalid input",
                details={"field": "email"}
            )

        response = self.client.get("/test-validation-error")
        assert response.status_code == 422
        data = response.json()
        assert data["error"] == "VALIDATION_ERROR"
        assert data["details"]["field"] == "email"

    @patch("app.main.logger")
    def test_general_exception_handler(self, mock_logger):
        """Test general exception handler doesn't expose internals."""
        @self.app.get("/test-general-error")
        async def test_endpoint():
            raise RuntimeError("Internal error details")

        response = self.client.get("/test-general-error")
        assert response.status_code == 500
        data = response.json()
        assert data["error"] == "INTERNAL_ERROR"
        assert data["message"] == "An unexpected error occurred"
        # Should not expose internal error details
        assert "Internal error details" not in str(data)


class TestErrorHandlingIntegration:
    """Integration tests for error handling components."""

    @pytest.mark.asyncio
    async def test_retry_with_circuit_breaker(self):
        """Test combining retry logic with circuit breaker."""
        cb = CircuitBreaker(
            name="integration_test",
            failure_threshold=3,
            success_threshold=1,
            timeout_duration=0.1
        )

        call_count = 0

        @retry_on_external_error
        async def operation_with_cb():
            nonlocal call_count
            call_count += 1

            async def inner_operation():
                if call_count < 3:
                    raise ExternalServiceError("Service down")
                return "success"

            return await cb.call(inner_operation)

        # Should succeed after retries
        result = await operation_with_cb()
        assert result == "success"
        assert call_count == 3
        # Circuit should still be closed (failures were retried)
        assert cb.state == CircuitBreakerState.CLOSED

    @pytest.mark.asyncio
    async def test_error_propagation_chain(self):
        """Test error propagation through multiple layers."""

        @retry_on_external_error
        async def data_layer():
            raise ExternalServiceError("Database unavailable")

        async def service_layer():
            try:
                return await data_layer()
            except ExternalServiceError as e:
                raise ServiceError(
                    message="Service operation failed",
                    details={"cause": str(e)}
                )

        async def api_layer():
            try:
                return await service_layer()
            except ServiceError as e:
                # Transform to user-friendly error
                raise AppExceptionError(
                    message="Operation temporarily unavailable",
                    status_code=503,
                    error_code="TEMP_UNAVAILABLE",
                    details=e.details
                )

        with pytest.raises(AppExceptionError) as exc_info:
            await api_layer()

        assert exc_info.value.error_code == "TEMP_UNAVAILABLE"
        assert "Database unavailable" in str(exc_info.value.details)
