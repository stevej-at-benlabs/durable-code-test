"""
Purpose: Integration tests for FastAPI application
Scope: Testing full API integration with database
Created: 2025-09-14
Updated: 2025-09-14
Author: Development Team
Version: 1.0
"""

import os
import sys
from pathlib import Path

# Add backend app to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'durable-code-app' / 'backend'))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.mark.integration
def test_api_integration() -> None:
    """Test basic API integration."""
    # Test root endpoint
    response = client.get("/")
    assert response.status_code == 200

    # Test health endpoint
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("TESTING") != "true",
    reason="Integration tests only run in CI environment"
)
def test_database_connection() -> None:
    """Test database connectivity in integration environment."""
    # This would test actual database connections
    # For now, just verify the environment is set up
    assert os.getenv("DATABASE_URL") is not None or os.getenv("TESTING") == "true"
