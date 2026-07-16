"""Security tests — verifying blocking and high-severity fixes."""

import pytest
from datetime import datetime, timezone
from config import ProductionConfig, TestingConfig


def test_production_rejects_default_secret_key():
    """ProductionConfig raises if SECRET_KEY is default."""
    import os
    original = os.environ.get("SECRET_KEY")
    try:
        os.environ["SECRET_KEY"] = "dev-secret-key"
        with pytest.raises(RuntimeError, match="SECRET_KEY"):
            ProductionConfig.validate()
    finally:
        if original:
            os.environ["SECRET_KEY"] = original
        else:
            os.environ.pop("SECRET_KEY", None)


def test_production_accepts_real_secret_key():
    """ProductionConfig works with a real secret key."""
    import os
    original = os.environ.get("SECRET_KEY")
    try:
        os.environ["SECRET_KEY"] = "my-very-secure-random-production-key-2026"
        # Should not raise
        ProductionConfig.validate()
        assert ProductionConfig.DEBUG is False
    finally:
        if original:
            os.environ["SECRET_KEY"] = original
        else:
            os.environ.pop("SECRET_KEY", None)


def test_aws_endpoint_guard(app):
    """Service refuses to create client if AWS_ENDPOINT_URL is empty."""
    from app.services import get_boto3_client

    # Temporarily clear endpoint
    app.config["AWS_ENDPOINT_URL"] = ""
    with app.app_context():
        with pytest.raises(RuntimeError, match="AWS_ENDPOINT_URL"):
            get_boto3_client("s3")


def test_aws_endpoint_always_localstack(app):
    """Default AWS_ENDPOINT_URL points to localhost:4566 (LocalStack)."""
    assert "localhost:4566" in app.config["AWS_ENDPOINT_URL"] or \
           "localstack" in app.config["AWS_ENDPOINT_URL"]


def test_env_example_no_real_secrets():
    """Verify .env.example doesn't contain real secrets."""
    with open(".env.example", "r") as f:
        content = f.read()

    # Should contain placeholder values, not real AWS keys
    assert "AKIA" not in content  # Real AWS keys start with AKIA
    assert "change-this" in content or "test" in content
    assert content.count("railops_secret") <= 2  # Only DB password placeholder


def test_gitignore_contains_env():
    """Verify .gitignore excludes .env file."""
    with open(".gitignore", "r") as f:
        content = f.read()
    assert ".env" in content


def test_debug_disabled_in_production():
    """Production config has DEBUG=False."""
    assert ProductionConfig.DEBUG is False


def test_content_disposition_sanitization(admin_client, db):
    """Download sanitizes filename in Content-Disposition header."""
    from unittest.mock import patch
    import io
    from app.models.document import Document
    from app.models.trip import Trip
    from app.models.train import Train
    from app.models.station import Station

    # Setup minimal data
    train = Train(train_code="KA-SEC", train_name="Sec Train", train_type="Eksekutif",
                  capacity=100, carriage_number=3, status="Aktif")
    s1 = Station(station_code="SE1", station_name="St1", city="J", province="DKI", platform_count=2, operational_status="Aktif")
    s2 = Station(station_code="SE2", station_name="St2", city="B", province="JB", platform_count=2, operational_status="Aktif")
    db.session.add_all([train, s1, s2])
    db.session.flush()
    trip = Trip(trip_number="SEC-T1", train_id=train.id, origin_station_id=s1.id,
                destination_station_id=s2.id,
                scheduled_departure=datetime(2026, 7, 15, 6, 0, tzinfo=timezone.utc),
                scheduled_arrival=datetime(2026, 7, 15, 9, 0, tzinfo=timezone.utc),
                platform=1, status="Dijadwalkan")
    db.session.add(trip)
    db.session.flush()

    # Document with malicious filename
    doc = Document(
        trip_id=trip.id,
        original_filename='evil"file\r\ninjection.pdf',
        stored_filename="stored.pdf",
        bucket_name="test", object_key="test/key.pdf",
        content_type="application/pdf", file_size=100,
        document_category="Lainnya", uploaded_by=1,
    )
    db.session.add(doc)
    db.session.commit()

    with patch("app.routes.document_routes.s3_service") as mock_s3:
        mock_s3.download_file.return_value = {
            "success": True, "body": io.BytesIO(b"content"),
            "content_type": "application/pdf", "content_length": 7,
        }
        response = admin_client.get(f"/documents/{doc.id}/download")
        assert response.status_code == 200

        # Verify no quotes or newlines in Content-Disposition
        cd = response.headers.get("Content-Disposition", "")
        assert "\r" not in cd
        assert "\n" not in cd
        # The filename should be sanitized (no raw quotes inside the value)
        assert 'evil' in cd  # filename preserved partially
        assert '\\r\\n' not in cd


def test_health_endpoint_no_auth_required(client):
    """Health endpoint accessible without login (for monitoring)."""
    response = client.get("/health")
    assert response.status_code == 200


def test_password_hash_not_exposed_in_templates(admin_client, db, admin_user):
    """User detail page does not show password_hash."""
    response = admin_client.get(f"/users/{admin_user.id}")
    assert response.status_code == 200
    assert b"password_hash" not in response.data
    assert b"scrypt:" not in response.data
    assert b"pbkdf2:" not in response.data
