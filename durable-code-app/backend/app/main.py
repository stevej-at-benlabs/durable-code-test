"""
Main FastAPI application module.

This module demonstrates durable code practices with
strict complexity limits and comprehensive type safety.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Application configuration
API_TITLE = "Durable Code API"
API_DESCRIPTION = "API demonstrating durable code practices"
API_VERSION = "1.0.0"

# CORS configuration
ALLOWED_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://localhost:5173",
]

# API Messages and Constants
WELCOME_MESSAGE = "Welcome to Durable Code API"
ROOT_ENDPOINT_DESCRIPTION = "Root endpoint returning welcome message."
HEALTH_ENDPOINT_PATH = "/health"
HEALTH_ENDPOINT_DESCRIPTION = "Health check endpoint for monitoring."
HEALTH_STATUS_OK = "healthy"


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title=API_TITLE,
        description=API_DESCRIPTION,
        version=API_VERSION,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return application


app = create_application()


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint returning welcome message."""
    return {"message": WELCOME_MESSAGE}


@app.get(HEALTH_ENDPOINT_PATH)
async def health_check() -> dict[str, str]:
    """Health check endpoint for monitoring."""
    return {"status": HEALTH_STATUS_OK}
