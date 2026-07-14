"""Pytest fixtures for RailOps Nusantara."""

import pytest

from app import create_app
from config import TestingConfig


@pytest.fixture
def app():
    """Create application for testing."""
    application = create_app(config_class=TestingConfig)
    yield application


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()
