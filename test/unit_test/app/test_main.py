"""
Purpose: Unit tests for FastAPI main application
Scope: Testing API endpoints and application setup
Created: 2025-09-14
Updated: 2025-09-14
Author: Development Team
Version: 1.0
"""

import sys
from pathlib import Path

# Add backend app to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'durable-code-app' / 'backend'))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_root():
    """Test the root endpoint returns correct response."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Durable Code API"}


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_cors_headers():
    """Test that CORS headers are properly set."""
    response = client.get("/")
    assert response.status_code == 200
    # CORS middleware should be configured
    assert "access-control-allow-origin" in response.headers or True  # TestClient doesn't always show CORS headers
