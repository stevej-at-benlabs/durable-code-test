"""
Retry logic and resilience patterns for backend operations.

This module provides decorators and utilities for implementing
retry logic, circuit breakers, and other resilience patterns.
"""

import asyncio
import functools
import logging
from typing import Any, Callable, Optional, Type, TypeVar, Union

from tenacity import (
    RetryError,
    Retrying,
    retry,
    stop_after_attempt,
    wait_exponential,
)
from tenacity.before_sleep import before_sleep_log
from tenacity.stop import stop_base
from tenacity.wait import wait_base

from .exceptions import ExternalServiceError

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 3,
        min_wait: float = 1.0,
        max_wait: float = 10.0,
        multiplier: float = 2.0,
        exceptions: Optional[tuple[Type[Exception], ...]] = None,
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
    max_attempts=3,
    min_wait=1.0,
    max_wait=10.0,
)

AGGRESSIVE_RETRY = RetryConfig(
    max_attempts=5,
    min_wait=0.5,
    max_wait=30.0,
)

GENTLE_RETRY = RetryConfig(
    max_attempts=2,
    min_wait=2.0,
    max_wait=5.0,
)


def with_retry(
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable[[Any, Any], None]] = None,
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
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            """Async wrapper with retry logic."""
            attempt = 0
            last_exception = None

            async for attempt_manager in AsyncRetrying(
                stop=stop_after_attempt(config.max_attempts),
                wait=wait_exponential(
                    multiplier=config.multiplier,
                    min=config.min_wait,
                    max=config.max_wait,
                ),
                retry=(
                    retry_if_exception_type(config.exceptions)
                    if config.exceptions
                    else None
                ),
                before_sleep=before_sleep_log(logger, logging.INFO),
            ):
                with attempt_manager:
                    attempt += 1
                    try:
                        result = await func(*args, **kwargs)
                        if attempt > 1:
                            logger.info(
                                f"Operation {func.__name__} succeeded after {attempt} attempts"
                            )
                        return result
                    except config.exceptions as e:
                        last_exception = e
                        if on_retry:
                            on_retry(attempt, e)
                        if attempt < config.max_attempts:
                            logger.warning(
                                f"Operation {func.__name__} failed (attempt {attempt}/{config.max_attempts}): {str(e)}"
                            )
                        else:
                            logger.error(
                                f"Operation {func.__name__} failed after {attempt} attempts: {str(e)}"
                            )
                        raise

            # This should not be reached, but handle it gracefully
            if last_exception:
                raise last_exception
            raise RuntimeError(f"Unexpected retry state for {func.__name__}")

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            """Sync wrapper with retry logic."""
            return retry(
                stop=stop_after_attempt(config.max_attempts),
                wait=wait_exponential(
                    multiplier=config.multiplier,
                    min=config.min_wait,
                    max=config.max_wait,
                ),
                retry=(
                    retry_if_exception_type(config.exceptions)
                    if config.exceptions
                    else None
                ),
                before_sleep=before_sleep_log(logger, logging.INFO),
            )(func)(*args, **kwargs)

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def retry_if_exception_type(
    exceptions: tuple[Type[Exception], ...]
) -> Callable[[Any], bool]:
    """
    Helper to determine if an exception should trigger a retry.

    Args:
        exceptions: Tuple of exception types to retry on

    Returns:
        Function that checks if exception should be retried
    """

    def _retry_if_exception_type(retry_state: Any) -> bool:
        if retry_state.outcome.failed:
            return isinstance(retry_state.outcome.exception(), exceptions)
        return False

    return _retry_if_exception_type


class AsyncRetrying(Retrying):
    """Async version of tenacity's Retrying class."""

    def __aiter__(self) -> "AsyncRetrying":
        """Make this class an async iterator."""
        self.begin()
        return self

    async def __anext__(self) -> Any:
        """Async version of __next__."""
        while True:
            do = self.iter(retry_state=self.retry_state)
            if do is None:
                raise StopAsyncIteration
            return do


# Convenience decorators for common scenarios
retry_on_external_error = with_retry(
    config=RetryConfig(exceptions=(ExternalServiceError,))
)

retry_on_connection_error = with_retry(
    config=RetryConfig(
        exceptions=(ConnectionError, TimeoutError, ExternalServiceError)
    )
)

retry_critical = with_retry(config=AGGRESSIVE_RETRY)

retry_gentle = with_retry(config=GENTLE_RETRY)
