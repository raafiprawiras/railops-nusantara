"""Tests for Integrated Demo Data seeder."""

from unittest.mock import patch

from app.models.user import User
from app.models.train import Train
from app.models.station import Station
from app.models.trip import Trip, TripStatusHistory
from app.models.incident import Incident, IncidentStatusHistory
from app.models.infrastructure import AuditLog


def _run_seed(app):
    """Run seed_demo within app context, mocking cloud services."""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scripts.seed_demo import seed_demo

    with patch("app.services.ec2_service.check_health", return_value=False), \
         patch("app.services.s3_service.check_health", return_value=False):
        return seed_demo(reset=False, app=app)


def test_seed_on_empty_database(app, db):
    """Seed works on empty database."""
    result = _run_seed(app)
    assert result is True

    assert User.query.count() >= 4
    assert Train.query.count() >= 8
    assert Station.query.count() >= 10
    assert Trip.query.count() >= 20
    assert Incident.query.count() >= 8


def test_seed_idempotent(app, db):
    """Running seed twice doesn't create duplicates."""
    _run_seed(app)
    first_user_count = User.query.count()
    first_train_count = Train.query.count()
    first_trip_count = Trip.query.count()

    # Run again
    _run_seed(app)
    assert User.query.count() == first_user_count
    assert Train.query.count() == first_train_count
    assert Trip.query.count() == first_trip_count


def test_relational_integrity(app, db):
    """Seeded data has proper foreign key relationships."""
    _run_seed(app)

    # All trips reference valid trains and stations
    trips = Trip.query.all()
    for trip in trips:
        assert trip.train_id is not None
        assert trip.origin_station_id is not None
        assert trip.destination_station_id is not None
        assert trip.origin_station_id != trip.destination_station_id

    # All incidents reference valid trips
    incidents = Incident.query.all()
    for inc in incidents:
        assert inc.trip_id is not None
        assert db.session.get(Trip, inc.trip_id) is not None


def test_status_history_created(app, db):
    """Trips and incidents have status history records."""
    _run_seed(app)

    trip = Trip.query.first()
    assert TripStatusHistory.query.filter_by(trip_id=trip.id).count() >= 1

    incident = Incident.query.first()
    assert IncidentStatusHistory.query.filter_by(incident_id=incident.id).count() >= 1


def test_seed_without_localstack(app, db):
    """Seed succeeds even without LocalStack (S3/EC2 optional)."""
    # LocalStack isn't running in test env — seed should still work
    result = _run_seed(app)
    assert result is True

    # Core data seeded regardless
    assert User.query.count() >= 4
    assert Trip.query.count() >= 20


def test_reset_only_in_development(app, db):
    """Reset guard — only works in debug/testing mode."""
    # Our test app has TESTING=True, so reset should work
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scripts.seed_demo import seed_demo

    with patch("app.services.ec2_service.check_health", return_value=False), \
         patch("app.services.s3_service.check_health", return_value=False):
        # First seed
        seed_demo(reset=False, app=app)
        assert User.query.count() >= 4

        # Reset and reseed
        seed_demo(reset=True, app=app)
        # After reset + reseed, data should be present again
        assert User.query.count() >= 4
        assert Train.query.count() >= 8


def test_audit_log_created(app, db):
    """Seed creates an audit log entry."""
    _run_seed(app)
    log = AuditLog.query.filter_by(action="seed_demo").first()
    assert log is not None
