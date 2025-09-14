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
    assert response.json() == {"message": "Welcome to Durable Code App"}


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_api_version():
    """Test the API version endpoint."""
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert data["version"] == "1.0.0"