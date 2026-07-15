"""Pytest fixtures for RailOps Nusantara."""

import pytest

from app import create_app
from app.extensions import db as _db
from app.models.user import User
from config import TestingConfig


@pytest.fixture
def app():
    """Create application for testing."""
    application = create_app(config_class=TestingConfig)

    with application.app_context():
        _db.create_all()
        yield application
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture
def db(app):
    """Provide database session."""
    return _db


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def active_user(app, db):
    """Create an active user for testing."""
    user = User(
        full_name="Test User",
        email="test@railops.local",
        role=User.ROLE_OPERATOR,
        is_active=True,
    )
    user.set_password("TestPass123!")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def admin_user(app, db):
    """Create an admin user for testing."""
    user = User(
        full_name="Admin User",
        email="admin@railops.local",
        role=User.ROLE_ADMINISTRATOR,
        is_active=True,
    )
    user.set_password("Admin123!")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def inactive_user(app, db):
    """Create an inactive user for testing."""
    user = User(
        full_name="Inactive User",
        email="inactive@railops.local",
        role=User.ROLE_OPERATOR,
        is_active=False,
    )
    user.set_password("Inactive123!")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def logged_in_client(client, active_user):
    """Client with an authenticated session."""
    client.post("/login", data={
        "email": active_user.email,
        "password": "TestPass123!",
    })
    return client


@pytest.fixture
def admin_client(client, admin_user):
    """Client with an authenticated administrator session."""
    client.post("/login", data={
        "email": admin_user.email,
        "password": "Admin123!",
    })
    return client


@pytest.fixture
def sample_train(app, db):
    """Create a sample train for testing."""
    from app.models.train import Train

    train = Train(
        train_code="KA-TST",
        train_name="Test Express",
        train_type="Eksekutif",
        capacity=200,
        carriage_number=5,
        status="Aktif",
    )
    db.session.add(train)
    db.session.commit()
    return train


@pytest.fixture
def sample_station(app, db):
    """Create a sample station for testing."""
    from app.models.station import Station

    station = Station(
        station_code="TST",
        station_name="Stasiun Test",
        city="Jakarta",
        province="DKI Jakarta",
        platform_count=3,
        operational_status="Aktif",
    )
    db.session.add(station)
    db.session.commit()
    return station
