"""
Main FastAPI application module.

This module demonstrates durable code practices with
strict complexity limits and comprehensive type safety.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .oscilloscope import router as oscilloscope_router
from .security import SecurityMiddleware, get_rate_limiter, get_security_config

# Application configuration
API_TITLE = "Durable Code API"
API_DESCRIPTION = "API demonstrating durable code practices"
API_VERSION = "1.0.0"

# CORS configuration - Secure settings
ALLOWED_ORIGINS: list[str] = [
    "http://localhost:3000",  # React dev server
    "http://localhost:5173",  # Vite dev server
]

# Security configuration
ALLOWED_METHODS: list[str] = ["GET", "POST", "DELETE"]  # Only specific methods
ALLOWED_HEADERS: list[str] = ["Content-Type", "Authorization"]  # Only necessary headers

# API Messages and Constants
WELCOME_MESSAGE = "Welcome to Durable Code API"
ROOT_ENDPOINT_DESCRIPTION = "Root endpoint returning welcome message."
HEALTH_ENDPOINT_PATH = "/health"
HEALTH_ENDPOINT_DESCRIPTION = "Health check endpoint for monitoring."
HEALTH_STATUS_OK = "healthy"


def create_application() -> FastAPI:
    """Create and configure the FastAPI application with security hardening."""
    application = FastAPI(
        title=API_TITLE,
        description=API_DESCRIPTION,
        version=API_VERSION,
    )

    # Configure rate limiting for the app
    from slowapi.errors import RateLimitExceeded

    from .security import RATE_LIMITER, _rate_limit_exceeded_handler

    application.state.limiter = RATE_LIMITER
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Add security middleware
    application.add_middleware(SecurityMiddleware)

    # Add CORS middleware with secure configuration
    application.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=False,  # Disable credentials for security
        allow_methods=ALLOWED_METHODS,  # Only specific methods
        allow_headers=ALLOWED_HEADERS,  # Only necessary headers
        max_age=3600,  # Cache preflight for 1 hour
    )

    return application


app = create_application()

# Include routers
app.include_router(oscilloscope_router)


@app.get("/")
@get_rate_limiter().limit(get_security_config("api_data")["rate_limit"])
async def root(request: Request) -> dict[str, str]:
    """Root endpoint returning welcome message."""
    return {"message": WELCOME_MESSAGE}


@app.get(HEALTH_ENDPOINT_PATH)
@get_rate_limiter().limit(get_security_config("health_check")["rate_limit"])
async def health_check(request: Request) -> dict[str, str]:
    """Health check endpoint for monitoring."""
    return {"status": HEALTH_STATUS_OK}
