"""Tests for Incident Management."""

from datetime import datetime, timedelta, timezone

from app.models.incident import Incident, IncidentStatusHistory
from app.models.trip import Trip
from app.models.train import Train
from app.models.station import Station
from app.models.user import User


def _setup_trip(db):
    """Create supporting data and return a trip."""
    train = Train(train_code="KA-INC", train_name="Incident Train",
                  train_type="Eksekutif", capacity=200, carriage_number=5, status="Aktif")
    s1 = Station(station_code="INC1", station_name="St. Asal Inc",
                 city="Jakarta", province="DKI Jakarta", platform_count=3, operational_status="Aktif")
    s2 = Station(station_code="INC2", station_name="St. Tujuan Inc",
                 city="Bandung", province="Jawa Barat", platform_count=4, operational_status="Aktif")
    db.session.add_all([train, s1, s2])
    db.session.flush()

    trip = Trip(
        trip_number="TRN-INC-01", train_id=train.id,
        origin_station_id=s1.id, destination_station_id=s2.id,
        scheduled_departure=datetime.now(timezone.utc),
        scheduled_arrival=datetime.now(timezone.utc) + timedelta(hours=3),
        platform=1, status="Dalam Perjalanan",
    )
    db.session.add(trip)
    db.session.commit()
    return trip


def _incident_data(trip):
    """Standard incident form data."""
    return {
        "incident_number": "INC-TEST",
        "trip_id": str(trip.id),
        "incident_type": "Gangguan Persinyalan",
        "location": "KM 50 Test",
        "occurred_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M"),
        "priority": "Tinggi",
        "description": "Test incident description yang cukup panjang.",
        "assigned_to": "0",
    }


# === TESTS ===

def test_create_incident(admin_client, db):
    """Admin can create an incident."""
    trip = _setup_trip(db)
    data = _incident_data(trip)

    response = admin_client.post("/incidents/create", data=data, follow_redirects=False)
    assert response.status_code == 302

    inc = Incident.query.filter_by(incident_number="INC-TEST").first()
    assert inc is not None
    assert inc.status == "Dilaporkan"
    assert inc.trip_id == trip.id


def test_status_history_recorded_on_create(admin_client, db):
    """Creating incident records initial status history."""
    trip = _setup_trip(db)
    data = _incident_data(trip)
    admin_client.post("/incidents/create", data=data)

    inc = Incident.query.filter_by(incident_number="INC-TEST").first()
    history = IncidentStatusHistory.query.filter_by(incident_id=inc.id).all()
    assert len(history) == 1
    assert history[0].new_status == "Dilaporkan"


def test_valid_transition_accepted(admin_client, db):
    """Valid status transition (Dilaporkan → Dalam Penanganan) works."""
    trip = _setup_trip(db)
    data = _incident_data(trip)
    admin_client.post("/incidents/create", data=data)
    inc = Incident.query.filter_by(incident_number="INC-TEST").first()

    response = admin_client.post(f"/incidents/{inc.id}/status", data={
        "new_status": "Dalam Penanganan",
        "notes": "Mulai penanganan",
        "resolution_notes": "",
    }, follow_redirects=False)
    assert response.status_code == 302

    db.session.refresh(inc)
    assert inc.status == "Dalam Penanganan"


def test_invalid_transition_rejected(admin_client, db):
    """Invalid status transition (Dilaporkan → Selesai) is rejected."""
    trip = _setup_trip(db)
    data = _incident_data(trip)
    admin_client.post("/incidents/create", data=data)
    inc = Incident.query.filter_by(incident_number="INC-TEST").first()

    response = admin_client.post(f"/incidents/{inc.id}/status", data={
        "new_status": "Selesai",
        "notes": "",
        "resolution_notes": "Trying to skip",
    }, follow_redirects=True)

    assert b"tidak diizinkan" in response.data
    db.session.refresh(inc)
    assert inc.status == "Dilaporkan"  # Unchanged


def test_invalid_transition_ditutup_from_dilaporkan(admin_client, db):
    """Cannot go from Dilaporkan directly to Ditutup."""
    trip = _setup_trip(db)
    data = _incident_data(trip)
    admin_client.post("/incidents/create", data=data)
    inc = Incident.query.filter_by(incident_number="INC-TEST").first()

    response = admin_client.post(f"/incidents/{inc.id}/status", data={
        "new_status": "Ditutup",
        "notes": "",
        "resolution_notes": "",
    }, follow_redirects=True)

    assert b"tidak diizinkan" in response.data
    db.session.refresh(inc)
    assert inc.status == "Dilaporkan"


def test_selesai_requires_resolution_notes(admin_client, db):
    """Status Selesai requires resolution_notes."""
    trip = _setup_trip(db)
    data = _incident_data(trip)
    admin_client.post("/incidents/create", data=data)
    inc = Incident.query.filter_by(incident_number="INC-TEST").first()

    # First move to Dalam Penanganan
    admin_client.post(f"/incidents/{inc.id}/status", data={
        "new_status": "Dalam Penanganan", "notes": "Start", "resolution_notes": "",
    })

    # Try Selesai without resolution_notes
    response = admin_client.post(f"/incidents/{inc.id}/status", data={
        "new_status": "Selesai",
        "notes": "",
        "resolution_notes": "",  # Empty!
    }, follow_redirects=True)

    assert b"Catatan penyelesaian wajib" in response.data
    db.session.refresh(inc)
    assert inc.status == "Dalam Penanganan"  # Unchanged


def test_selesai_with_resolution_works(admin_client, db):
    """Status Selesai with resolution_notes succeeds."""
    trip = _setup_trip(db)
    data = _incident_data(trip)
    admin_client.post("/incidents/create", data=data)
    inc = Incident.query.filter_by(incident_number="INC-TEST").first()

    admin_client.post(f"/incidents/{inc.id}/status", data={
        "new_status": "Dalam Penanganan", "notes": "Start", "resolution_notes": "",
    })
    admin_client.post(f"/incidents/{inc.id}/status", data={
        "new_status": "Selesai",
        "notes": "",
        "resolution_notes": "Masalah terselesaikan.",
    })

    db.session.refresh(inc)
    assert inc.status == "Selesai"
    assert inc.resolution_notes == "Masalah terselesaikan."
    assert inc.resolved_at is not None


def test_supervisor_cannot_create(client, db, app):
    """Supervisor cannot create incidents."""
    user = User(full_name="SV Incident", email="sv-inc@railops.local",
                role=User.ROLE_SUPERVISOR, is_active=True)
    user.set_password("Super123!")
    db.session.add(user)
    db.session.commit()

    client.post("/login", data={"email": "sv-inc@railops.local", "password": "Super123!"})
    response = client.get("/incidents/create")
    assert response.status_code == 403


def test_operator_can_create(client, db, app):
    """Operator can create incidents."""
    user = User(full_name="OP Incident", email="op-inc@railops.local",
                role=User.ROLE_OPERATOR, is_active=True)
    user.set_password("Oper123!")
    db.session.add(user)
    db.session.commit()

    trip = _setup_trip(db)

    client.post("/login", data={"email": "op-inc@railops.local", "password": "Oper123!"})
    response = client.get("/incidents/create")
    assert response.status_code == 200


def test_filter_priority(admin_client, db):
    """Priority filter works."""
    trip = _setup_trip(db)
    inc = Incident(
        incident_number="INC-PRIO", trip_id=trip.id,
        incident_type="Gangguan Jalur", location="KM 10",
        occurred_at=datetime.now(timezone.utc), priority="Darurat",
        description="Test prioritas darurat.", status="Dilaporkan",
        reported_by=1,
    )
    db.session.add(inc)
    db.session.commit()

    response = admin_client.get("/incidents?priority=Darurat")
    assert response.status_code == 200
    assert b"INC-PRIO" in response.data


def test_filter_status(admin_client, db):
    """Status filter works."""
    trip = _setup_trip(db)
    inc = Incident(
        incident_number="INC-STAT", trip_id=trip.id,
        incident_type="Gangguan Listrik", location="Stasiun X",
        occurred_at=datetime.now(timezone.utc), priority="Sedang",
        description="Test filter status.", status="Dalam Penanganan",
        reported_by=1,
    )
    db.session.add(inc)
    db.session.commit()

    response = admin_client.get("/incidents?status=Dalam+Penanganan")
    assert response.status_code == 200
    assert b"INC-STAT" in response.data


def test_dashboard_active_incident_count(admin_client, db):
    """Dashboard shows active incident count."""
    trip = _setup_trip(db)
    for i in range(3):
        inc = Incident(
            incident_number=f"INC-DASH-{i}", trip_id=trip.id,
            incident_type="Lainnya", location="Lokasi",
            occurred_at=datetime.now(timezone.utc), priority="Rendah",
            description="Test dashboard count.", status="Dilaporkan",
            reported_by=1,
        )
        db.session.add(inc)
    db.session.commit()

    response = admin_client.get("/dashboard")
    assert response.status_code == 200
    # The stat card should show "3" for gangguan aktif
    assert b"Gangguan Aktif" in response.data


def test_status_history_full_flow(admin_client, db):
    """Full status flow records all history entries."""
    trip = _setup_trip(db)
    data = _incident_data(trip)
    admin_client.post("/incidents/create", data=data)
    inc = Incident.query.filter_by(incident_number="INC-TEST").first()

    # Dilaporkan → Dalam Penanganan
    admin_client.post(f"/incidents/{inc.id}/status", data={
        "new_status": "Dalam Penanganan", "notes": "Mulai", "resolution_notes": "",
    })
    # Dalam Penanganan → Selesai
    admin_client.post(f"/incidents/{inc.id}/status", data={
        "new_status": "Selesai", "notes": "", "resolution_notes": "Done.",
    })
    # Selesai → Ditutup
    admin_client.post(f"/incidents/{inc.id}/status", data={
        "new_status": "Ditutup", "notes": "Closed.", "resolution_notes": "",
    })

    db.session.refresh(inc)
    assert inc.status == "Ditutup"

    history = IncidentStatusHistory.query.filter_by(incident_id=inc.id).all()
    assert len(history) == 4  # create + 3 transitions
