"""Retry logic decorators and resilience patterns for fault-tolerant operations.

Purpose: Retry logic decorators and resilience patterns for fault-tolerant backend operations.
Scope: Application-wide retry mechanisms for external service calls and transient failure handling
Overview: This module provides comprehensive retry and resilience patterns to handle transient
    failures in backend operations. It includes exponential backoff retry decorators for both
    synchronous and asynchronous functions, configurable retry policies, and integration with
    circuit breaker patterns. The module helps prevent cascading failures by implementing
    intelligent retry strategies that avoid overwhelming failing services. All retry attempts
    are logged for observability, and the decorators support customizable retry conditions,
    maximum attempts, and wait strategies to balance reliability with performance.
Dependencies: tenacity for retry logic, loguru for logging, asyncio for async operations
Exports: retry_on_exception decorator, async_retry decorator, retry configuration constants
Interfaces: Decorators that wrap functions with retry logic, customizable retry policies
Implementation: Uses tenacity library with exponential backoff and configurable retry conditions
"""

import asyncio
import functools
from collections.abc import Callable, Coroutine
from typing import Any, TypeVar, cast

from loguru import logger
from tenacity import AsyncRetrying, retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from .exceptions import ExternalServiceError

T = TypeVar("T")

# Retry Configuration Constants
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_MIN_WAIT = 1.0
DEFAULT_MAX_WAIT = 10.0
DEFAULT_MULTIPLIER = 2

AGGRESSIVE_MAX_ATTEMPTS = 5
AGGRESSIVE_MIN_WAIT = 0.5
AGGRESSIVE_MAX_WAIT = 30.0

GENTLE_MAX_ATTEMPTS = 2
GENTLE_MIN_WAIT = 2.0
GENTLE_MAX_WAIT = 5.0


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        min_wait: float = DEFAULT_MIN_WAIT,
        max_wait: float = DEFAULT_MAX_WAIT,
        *,
        multiplier: float = DEFAULT_MULTIPLIER,
        exceptions: tuple[type[Exception], ...] | None = None,
    ) -> None:
        """
        Initialize retry configuration.

        Args:
            max_attempts: Maximum number of retry attempts
            min_wait: Minimum wait time between retries (seconds)
            max_wait: Maximum wait time between retries (seconds)
            multiplier: Exponential backoff multiplier
            exceptions: Tuple of exceptions to retry on (defaults to ExternalServiceError)
        """
        self.max_attempts = max_attempts
        self.min_wait = min_wait
        self.max_wait = max_wait
        self.multiplier = multiplier
        self.exceptions = exceptions or (ExternalServiceError,)


# Default retry configurations for different scenarios
DEFAULT_RETRY = RetryConfig(
    max_attempts=DEFAULT_MAX_ATTEMPTS,
    min_wait=DEFAULT_MIN_WAIT,
    max_wait=DEFAULT_MAX_WAIT,
)

AGGRESSIVE_RETRY = RetryConfig(
    max_attempts=AGGRESSIVE_MAX_ATTEMPTS,
    min_wait=AGGRESSIVE_MIN_WAIT,
    max_wait=AGGRESSIVE_MAX_WAIT,
)

GENTLE_RETRY = RetryConfig(
    max_attempts=GENTLE_MAX_ATTEMPTS,
    min_wait=GENTLE_MIN_WAIT,
    max_wait=GENTLE_MAX_WAIT,
)


def _create_retry_config(config: RetryConfig) -> dict[str, Any]:
    """Create retry configuration for tenacity."""
    return {
        "stop": stop_after_attempt(config.max_attempts),
        "wait": wait_exponential(
            multiplier=config.multiplier,
            min=config.min_wait,
            max=config.max_wait,
        ),
        "retry": retry_if_exception_type(config.exceptions) if config.exceptions else None,
    }


def _handle_retry_exception(
    func_name: str, attempt: int, max_attempts: int, e: Exception, on_retry: Callable[[Any, Any], None] | None
) -> None:
    """Handle exception during retry."""
    if on_retry:
        on_retry(attempt, e)
    if attempt < max_attempts:
        logger.error(
            "Operation {func} failed (attempt {attempt}/{max}): {error}",
            func=func_name,
            attempt=attempt,
            max=max_attempts,
            error=str(e),
        )
    else:
        logger.error(
            "Operation {func} failed after {attempts} attempts: {error}",
            func=func_name,
            attempts=attempt,
            error=str(e),
        )


async def _retry_attempt(
    func: Callable[..., Coroutine[Any, Any, T]],
    config: RetryConfig,
    attempt: int,
    on_retry: Callable[[Any, Any], None] | None,
    *args: Any,
    **kwargs: Any,
) -> T:
    """Execute a single retry attempt."""
    try:
        result = await func(*args, **kwargs)
        if attempt > 1:
            logger.info(
                "Operation {func} succeeded after {attempts} attempts",
                func=func.__name__,
                attempts=attempt,
            )
        return result
    except config.exceptions as e:
        _handle_retry_exception(func.__name__, attempt, config.max_attempts, e, on_retry)
        raise


async def _execute_with_retry(
    func: Callable[..., Coroutine[Any, Any, T]],
    config: RetryConfig,
    on_retry: Callable[[Any, Any], None] | None,
    *args: Any,
    **kwargs: Any,
) -> T:
    """Execute async function with retry logic."""
    attempt = 0
    retry_config = _create_retry_config(config)

    async for attempt_manager in AsyncRetrying(**retry_config):
        with attempt_manager:
            attempt += 1
            return await _retry_attempt(func, config, attempt, on_retry, *args, **kwargs)

    raise RuntimeError(f"Unexpected retry state for {func.__name__}")


def _create_async_retry_wrapper(
    func: Callable[..., Coroutine[Any, Any, T]], config: RetryConfig, on_retry: Callable[[Any, Any], None] | None
) -> Callable[..., Coroutine[Any, Any, T]]:
    """Create async wrapper for retry logic."""

    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> T:
        """Async wrapper with retry logic."""
        return await _execute_with_retry(func, config, on_retry, *args, **kwargs)

    return cast(Callable[..., Coroutine[Any, Any, T]], async_wrapper)


def _create_sync_retry_wrapper(func: Callable[..., T], config: RetryConfig) -> Callable[..., T]:
    """Create sync wrapper for retry logic."""

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> T:
        """Sync wrapper with retry logic."""
        retry_config = _create_retry_config(config)
        wrapped_func = retry(**retry_config)(func)
        return cast(T, wrapped_func(*args, **kwargs))

    return sync_wrapper


def with_retry(
    config: RetryConfig | None = None,
    on_retry: Callable[[Any, Any], None] | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to add retry logic to a function.

    Args:
        config: Retry configuration (defaults to DEFAULT_RETRY)
        on_retry: Optional callback called on each retry

    Returns:
        Decorated function with retry logic

    Example:
        @with_retry()
        async def fetch_data():
            # This will retry on ExternalServiceError
            ...

        @with_retry(config=AGGRESSIVE_RETRY)
        async def critical_operation():
            # This will retry more aggressively
            ...
    """
    if config is None:
        config = DEFAULT_RETRY

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        if asyncio.iscoroutinefunction(func):
            return cast(Callable[..., T], _create_async_retry_wrapper(func, config, on_retry))
        return _create_sync_retry_wrapper(func, config)

    return decorator


# retry_if_exception_type and AsyncRetrying are already imported from tenacity


# Convenience decorators for common scenarios
retry_on_external_error = with_retry(config=RetryConfig(exceptions=(ExternalServiceError,)))

retry_on_connection_error = with_retry(
    config=RetryConfig(exceptions=(ConnectionError, TimeoutError, ExternalServiceError))
)

retry_critical = with_retry(config=AGGRESSIVE_RETRY)

retry_gentle = with_retry(config=GENTLE_RETRY)
