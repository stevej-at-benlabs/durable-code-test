"""
Main FastAPI application module.

This module demonstrates durable code practices with
strict complexity limits and comprehensive type safety.
"""

from typing import Dict, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Application configuration
API_TITLE = "Durable Code API"
API_DESCRIPTION = "API demonstrating durable code practices"
API_VERSION = "1.0.0"

# CORS configuration
ALLOWED_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://localhost:5173",
]


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
async def root() -> Dict[str, str]:
    """Root endpoint returning welcome message."""
    return {"message": "Welcome to Durable Code API"}


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}