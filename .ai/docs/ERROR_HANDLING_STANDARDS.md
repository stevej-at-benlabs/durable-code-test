# Error Handling Standards

## Overview
This document defines standards for error handling across the codebase to ensure robust, maintainable, and debuggable applications.

## Core Principles

### 1. No Broad Exception Catching
**NEVER** catch broad exceptions like `Exception` or `BaseException` unless you're implementing a global error handler.

```python
# ❌ BAD - Too broad
try:
    result = process_data()
except Exception as e:
    logger.error(f"Error: {e}")

# ✅ GOOD - Specific exceptions
try:
    result = process_data()
except (ConnectionError, TimeoutError) as e:
    logger.error(f"Connection error: {e}")
    raise ExternalServiceError("Service unavailable")
except (ValueError, TypeError) as e:
    logger.error(f"Data error: {e}")
    raise ValidationError("Invalid data format")
```

### 2. Always Enable Linting Checks
The W0718 (broad-exception-caught) check must **NEVER** be disabled globally.

```toml
# pyproject.toml
[tool.pylint.messages_control]
disable = [
    # DO NOT ADD: "W0718"  # This check must remain enabled!
]
```

### 3. Structured Exception Hierarchy
All custom exceptions should inherit from a base exception class with structured error information:

```python
class AppException(Exception):
    def __init__(self, message: str, status_code: int, error_code: str, details: dict):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
```

### 4. Global Exception Handlers
FastAPI/Flask apps must have global exception handlers that:
- Log errors appropriately
- Return structured error responses
- Never expose internal error details to clients

```python
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unexpected error")
    return JSONResponse(
        status_code=500,
        content={"error": "INTERNAL_ERROR", "message": "An error occurred"}
    )
```

## Backend Error Handling Checklist

### Exception Design
- [ ] Base exception class with status_code, error_code, and details
- [ ] Specific exception classes for different error scenarios
- [ ] Consistent error codes across the application
- [ ] No hardcoded error messages in multiple places

### Exception Catching
- [ ] Only catch specific exception types
- [ ] Re-raise or wrap exceptions appropriately
- [ ] Log errors with appropriate context
- [ ] Clean up resources in finally blocks

### Retry Logic
- [ ] External API calls have retry decorators
- [ ] Database operations have retry logic
- [ ] Exponential backoff configured
- [ ] Maximum retry attempts defined

### Circuit Breakers
- [ ] Critical external services use circuit breakers
- [ ] Failure thresholds configured appropriately
- [ ] Timeout durations set based on service SLAs
- [ ] Fallback behavior implemented

### Error Responses
- [ ] Consistent error response format
- [ ] Appropriate HTTP status codes
- [ ] Error codes for client-side handling
- [ ] No sensitive information in error messages

## Frontend Error Handling Checklist

### Error Boundaries
- [ ] Root-level error boundary
- [ ] Route-level error boundaries
- [ ] Component-level boundaries for risky operations
- [ ] Fallback UI components

### Error Recovery
- [ ] Retry mechanisms for failed requests
- [ ] User-friendly error messages
- [ ] Recovery actions available to users
- [ ] Error state management

## Common Antipatterns to Avoid

1. **Silently swallowing exceptions**
   ```python
   # ❌ BAD
   try:
       operation()
   except:
       pass  # Silent failure!
   ```

2. **Logging and continuing with invalid state**
   ```python
   # ❌ BAD
   try:
       user = get_user(id)
   except:
       logger.error("Failed to get user")
       user = None  # Continues with None!
   ```

3. **Using exceptions for control flow**
   ```python
   # ❌ BAD
   try:
       if condition:
           raise ValueError("Use this for control")
   except ValueError:
       handle_condition()
   ```

4. **Not cleaning up resources**
   ```python
   # ❌ BAD
   file = open("data.txt")
   process(file)  # If this fails, file never closes!

   # ✅ GOOD
   with open("data.txt") as file:
       process(file)
   ```

## Testing Error Handling

Every error path should be tested:

```python
def test_handles_connection_error():
    with pytest.raises(ExternalServiceError):
        with mock.patch('requests.get', side_effect=ConnectionError):
            fetch_data()

def test_retry_on_failure():
    mock_func = Mock(side_effect=[Exception, Exception, "success"])
    result = retry_operation(mock_func)
    assert result == "success"
    assert mock_func.call_count == 3
```

## Monitoring and Alerting

- Log all errors with appropriate levels (ERROR, CRITICAL)
- Include request IDs for tracing
- Monitor error rates and alert on spikes
- Track specific error codes for trends
- Review and address recurring errors

## References

- [Backend Error Handling Guide](.ai/howto/implement-backend-error-handling.md)
- [Exception Hierarchy Template](.ai/templates/backend-exception-hierarchy.py.template)
- [Retry Logic Template](.ai/templates/backend-retry-logic.py.template)
- [Frontend Error Boundaries](.ai/howto/implement-error-boundaries.md)
