"""
Circuit breaker pattern implementation for resilient services.

This module provides circuit breaker functionality to prevent
cascading failures when external services are unavailable.
"""

import asyncio
import logging
import time
from enum import Enum
from typing import Any, Callable, Optional, TypeVar

from .exceptions import ExternalServiceError

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitBreakerState(Enum):
    """States of a circuit breaker."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker implementation to prevent cascading failures.

    The circuit breaker has three states:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Service is failing, requests are rejected immediately
    - HALF_OPEN: Testing if service has recovered

    Transitions:
    - CLOSED -> OPEN: After failure_threshold failures
    - OPEN -> HALF_OPEN: After timeout_duration seconds
    - HALF_OPEN -> CLOSED: After success_threshold successes
    - HALF_OPEN -> OPEN: After any failure
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout_duration: float = 60.0,
        expected_exceptions: Optional[tuple[type[Exception], ...]] = None,
    ) -> None:
        """
        Initialize circuit breaker.

        Args:
            name: Name for logging and identification
            failure_threshold: Number of failures before opening circuit
            success_threshold: Number of successes in half-open before closing
            timeout_duration: Seconds to wait before trying half-open
            expected_exceptions: Exceptions that trigger the circuit breaker
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout_duration = timeout_duration
        self.expected_exceptions = expected_exceptions or (
            ExternalServiceError,
            ConnectionError,
            TimeoutError,
        )

        # State management
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self._lock = asyncio.Lock()

    async def _transition_to_open(self) -> None:
        """Transition to OPEN state."""
        self.state = CircuitBreakerState.OPEN
        self.last_failure_time = time.time()
        self.success_count = 0
        logger.warning(
            f"Circuit breaker '{self.name}' opened after {self.failure_count} failures"
        )

    async def _transition_to_closed(self) -> None:
        """Transition to CLOSED state."""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        logger.info(f"Circuit breaker '{self.name}' closed")

    async def _transition_to_half_open(self) -> None:
        """Transition to HALF_OPEN state."""
        self.state = CircuitBreakerState.HALF_OPEN
        self.success_count = 0
        logger.info(f"Circuit breaker '{self.name}' half-opened for testing")

    async def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return False
        return time.time() - self.last_failure_time >= self.timeout_duration

    async def _on_success(self) -> None:
        """Handle successful call."""
        async with self._lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    await self._transition_to_closed()
            elif self.state == CircuitBreakerState.CLOSED:
                self.failure_count = 0

    async def _on_failure(self) -> None:
        """Handle failed call."""
        async with self._lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                await self._transition_to_open()
            elif self.state == CircuitBreakerState.CLOSED:
                self.failure_count += 1
                if self.failure_count >= self.failure_threshold:
                    await self._transition_to_open()

    async def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Execute function through circuit breaker.

        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result of func

        Raises:
            ExternalServiceError: When circuit is open
            Exception: Whatever func raises
        """
        async with self._lock:
            # Check if we should transition from OPEN to HALF_OPEN
            if self.state == CircuitBreakerState.OPEN and await self._should_attempt_reset():
                await self._transition_to_half_open()

            # Reject if circuit is open
            if self.state == CircuitBreakerState.OPEN:
                raise ExternalServiceError(
                    f"Circuit breaker '{self.name}' is open",
                    details={"circuit_breaker": self.name, "state": self.state.value},
                )

        # Attempt the call
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            await self._on_success()
            return result

        except self.expected_exceptions as e:
            await self._on_failure()
            raise

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """
        Decorator to wrap function with circuit breaker.

        Args:
            func: Function to wrap

        Returns:
            Wrapped function

        Example:
            @circuit_breaker
            async def external_api_call():
                ...
        """
        if asyncio.iscoroutinefunction(func):

            async def async_wrapper(*args: Any, **kwargs: Any) -> T:
                return await self.call(func, *args, **kwargs)

            return async_wrapper
        else:

            def sync_wrapper(*args: Any, **kwargs: Any) -> T:
                # For sync functions, we need to run in an event loop
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(self.call(func, *args, **kwargs))

            return sync_wrapper

    @property
    def is_open(self) -> bool:
        """Check if circuit is open."""
        return self.state == CircuitBreakerState.OPEN

    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed."""
        return self.state == CircuitBreakerState.CLOSED

    def get_status(self) -> dict[str, Any]:
        """
        Get current circuit breaker status.

        Returns:
            Dictionary with status information
        """
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "failure_threshold": self.failure_threshold,
            "success_threshold": self.success_threshold,
            "timeout_duration": self.timeout_duration,
        }


# Pre-configured circuit breakers for common scenarios
database_circuit_breaker = CircuitBreaker(
    name="database",
    failure_threshold=3,
    success_threshold=2,
    timeout_duration=30.0,
)

external_api_circuit_breaker = CircuitBreaker(
    name="external_api",
    failure_threshold=5,
    success_threshold=3,
    timeout_duration=60.0,
)

cache_circuit_breaker = CircuitBreaker(
    name="cache",
    failure_threshold=10,
    success_threshold=5,
    timeout_duration=20.0,
)
