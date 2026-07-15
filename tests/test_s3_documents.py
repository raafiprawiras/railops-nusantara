"""Tests for S3 Document Management.

Unit tests mock the S3 service. Integration tests (marked) require LocalStack.
"""

import io
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

import pytest

from app.models.document import Document
from app.models.trip import Trip
from app.models.incident import Incident
from app.models.train import Train
from app.models.station import Station
from app.models.user import User


def _setup_trip(db):
    """Create supporting trip data."""
    train = Train(train_code="KA-DOC", train_name="Doc Train",
                  train_type="Eksekutif", capacity=200, carriage_number=5, status="Aktif")
    s1 = Station(station_code="DOC1", station_name="St Doc Asal",
                 city="Jakarta", province="DKI Jakarta", platform_count=3, operational_status="Aktif")
    s2 = Station(station_code="DOC2", station_name="St Doc Tujuan",
                 city="Bandung", province="Jawa Barat", platform_count=4, operational_status="Aktif")
    db.session.add_all([train, s1, s2])
    db.session.flush()

    trip = Trip(
        trip_number="TRN-DOC-01", train_id=train.id,
        origin_station_id=s1.id, destination_station_id=s2.id,
        scheduled_departure=datetime.now(timezone.utc),
        scheduled_arrival=datetime.now(timezone.utc) + timedelta(hours=3),
        platform=1, status="Dalam Perjalanan",
    )
    db.session.add(trip)
    db.session.commit()
    return trip


# === UNIT TESTS (mocked S3) ===

@patch("app.routes.document_routes.s3_service")
def test_upload_valid_file(mock_s3, admin_client, db):
    """Valid file upload succeeds (S3 mocked)."""
    trip = _setup_trip(db)
    mock_s3.ensure_bucket.return_value = {"success": True, "message": "ok"}
    mock_s3.upload_file.return_value = {"success": True, "message": "ok"}

    data = {
        "file": (io.BytesIO(b"%PDF-1.4 fake pdf content"), "test.pdf"),
        "document_category": "Manifest",
        "trip_id": str(trip.id),
        "incident_id": "0",
    }
    response = admin_client.post(
        "/documents/upload", data=data,
        content_type="multipart/form-data",
        follow_redirects=False,
    )
    assert response.status_code == 302

    doc = Document.query.filter_by(original_filename="test.pdf").first()
    assert doc is not None
    assert doc.document_category == "Manifest"
    assert doc.trip_id == trip.id
    assert doc.file_size > 0


@patch("app.routes.document_routes.s3_service")
def test_upload_invalid_extension_rejected(mock_s3, admin_client, db):
    """File with invalid extension is rejected."""
    trip = _setup_trip(db)

    data = {
        "file": (io.BytesIO(b"malicious content"), "hack.exe"),
        "document_category": "Lainnya",
        "trip_id": str(trip.id),
        "incident_id": "0",
    }
    response = admin_client.post(
        "/documents/upload", data=data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"tidak diizinkan" in response.data
    assert Document.query.count() == 0


@patch("app.routes.document_routes.s3_service")
def test_upload_requires_trip_or_incident(mock_s3, admin_client, db):
    """Upload without trip or incident is rejected."""
    _setup_trip(db)  # Create supporting data but don't link

    data = {
        "file": (io.BytesIO(b"%PDF-1.4 content"), "orphan.pdf"),
        "document_category": "Lainnya",
        "trip_id": "0",
        "incident_id": "0",
    }
    response = admin_client.post(
        "/documents/upload", data=data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"terkait" in response.data


@patch("app.routes.document_routes.s3_service")
def test_metadata_stored_after_upload(mock_s3, admin_client, db):
    """Document metadata is stored in PostgreSQL after S3 upload."""
    trip = _setup_trip(db)
    mock_s3.ensure_bucket.return_value = {"success": True, "message": "ok"}
    mock_s3.upload_file.return_value = {"success": True, "message": "ok"}

    data = {
        "file": (io.BytesIO(b"PNG fake image data"), "photo.png"),
        "document_category": "Inspeksi",
        "trip_id": str(trip.id),
        "incident_id": "0",
    }
    admin_client.post("/documents/upload", data=data, content_type="multipart/form-data")

    doc = Document.query.first()
    assert doc is not None
    assert doc.bucket_name != ""
    assert doc.object_key != ""
    assert doc.content_type in ("image/png", "application/octet-stream")


@patch("app.routes.document_routes.s3_service")
def test_download_document(mock_s3, admin_client, db):
    """Download streams file from S3."""
    trip = _setup_trip(db)

    # Create document record directly
    doc = Document(
        trip_id=trip.id, original_filename="test.pdf", stored_filename="stored.pdf",
        bucket_name="test-bucket", object_key="manifests/2026/TRN-DOC-01/test.pdf",
        content_type="application/pdf", file_size=100,
        document_category="Manifest", uploaded_by=1,
    )
    db.session.add(doc)
    db.session.commit()

    mock_s3.download_file.return_value = {
        "success": True,
        "body": io.BytesIO(b"PDF CONTENT"),
        "content_type": "application/pdf",
        "content_length": 11,
    }

    response = admin_client.get(f"/documents/{doc.id}/download")
    assert response.status_code == 200
    assert b"PDF CONTENT" in response.data


@patch("app.routes.document_routes.s3_service")
def test_delete_document(mock_s3, admin_client, db):
    """Admin can soft-delete a document."""
    trip = _setup_trip(db)
    doc = Document(
        trip_id=trip.id, original_filename="delete_me.pdf", stored_filename="x.pdf",
        bucket_name="test-bucket", object_key="test/key.pdf",
        content_type="application/pdf", file_size=50,
        document_category="Lainnya", uploaded_by=1,
    )
    db.session.add(doc)
    db.session.commit()

    mock_s3.delete_object.return_value = {"success": True, "message": "ok"}

    response = admin_client.post(f"/documents/{doc.id}/delete", follow_redirects=False)
    assert response.status_code == 302

    db.session.refresh(doc)
    assert doc.deleted_at is not None


def test_supervisor_cannot_upload(client, db, app):
    """Supervisor cannot upload documents."""
    user = User(full_name="SV Doc", email="sv-doc@railops.local",
                role=User.ROLE_SUPERVISOR, is_active=True)
    user.set_password("Super123!")
    db.session.add(user)
    db.session.commit()

    client.post("/login", data={"email": "sv-doc@railops.local", "password": "Super123!"})
    response = client.get("/documents/upload")
    assert response.status_code == 403


def test_operator_cannot_delete(client, db, app):
    """Operator cannot delete documents."""
    user = User(full_name="OP Doc", email="op-doc@railops.local",
                role=User.ROLE_OPERATOR, is_active=True)
    user.set_password("Oper123!")
    db.session.add(user)
    db.session.commit()

    trip = _setup_trip(db)
    doc = Document(
        trip_id=trip.id, original_filename="nodelete.pdf", stored_filename="x.pdf",
        bucket_name="b", object_key="k", content_type="application/pdf",
        file_size=10, document_category="Lainnya", uploaded_by=1,
    )
    db.session.add(doc)
    db.session.commit()

    client.post("/login", data={"email": "op-doc@railops.local", "password": "Oper123!"})
    response = client.post(f"/documents/{doc.id}/delete")
    assert response.status_code == 403


@patch("app.routes.document_routes.s3_service")
def test_s3_unavailable_no_crash(mock_s3, admin_client, db):
    """If LocalStack is unavailable, upload fails gracefully."""
    trip = _setup_trip(db)
    mock_s3.ensure_bucket.return_value = {"success": True, "message": "ok"}
    mock_s3.upload_file.return_value = {"success": False, "error": "LocalStack tidak tersedia."}

    data = {
        "file": (io.BytesIO(b"%PDF-1.4 content"), "fail.pdf"),
        "document_category": "Manifest",
        "trip_id": str(trip.id),
        "incident_id": "0",
    }
    response = admin_client.post(
        "/documents/upload", data=data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Gagal upload" in response.data
    assert Document.query.count() == 0


def test_document_list_accessible(admin_client, db):
    """Document list page accessible."""
    response = admin_client.get("/documents")
    assert response.status_code == 200


@patch("app.routes.document_routes.s3_service")
def test_cloud_s3_panel(mock_s3, admin_client, db):
    """Cloud S3 panel renders without error."""
    mock_s3.check_health.return_value = True
    mock_s3.list_buckets.return_value = [{"Name": "test-bucket", "CreationDate": datetime.now(timezone.utc)}]
    mock_s3.get_bucket_object_count.return_value = 5

    response = admin_client.get("/cloud/s3")
    assert response.status_code == 200
    assert b"Online" in response.data


@patch("app.routes.document_routes.s3_service")
def test_cloud_s3_panel_offline(mock_s3, admin_client, db):
    """Cloud S3 panel handles offline LocalStack."""
    mock_s3.check_health.return_value = False

    response = admin_client.get("/cloud/s3")
    assert response.status_code == 200
    assert b"Offline" in response.data
