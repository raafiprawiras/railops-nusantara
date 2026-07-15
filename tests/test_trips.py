"""Tests for Trip Operations & Monitoring."""

from datetime import datetime, timedelta, timezone

from app.models.trip import Trip, TripStatusHistory
from app.models.train import Train
from app.models.station import Station


# --- Fixtures local to this module ---

def _create_train(db, status="Aktif", code="KA-TRIP"):
    """Helper to create a train."""
    train = Train(
        train_code=code, train_name="Trip Test Train",
        train_type="Eksekutif", capacity=200, carriage_number=5, status=status,
    )
    db.session.add(train)
    db.session.commit()
    return train


def _create_stations(db):
    """Helper to create two stations."""
    s1 = Station(station_code="ORI", station_name="Stasiun Asal",
                 city="Jakarta", province="DKI Jakarta", platform_count=3, operational_status="Aktif")
    s2 = Station(station_code="DST", station_name="Stasiun Tujuan",
                 city="Bandung", province="Jawa Barat", platform_count=4, operational_status="Aktif")
    db.session.add_all([s1, s2])
    db.session.commit()
    return s1, s2


def _trip_data(train, s1, s2, trip_number="TRN-TEST"):
    """Standard trip form data."""
    dep = datetime.now(timezone.utc) + timedelta(hours=1)
    arr = dep + timedelta(hours=3)
    return {
        "trip_number": trip_number,
        "train_id": str(train.id),
        "origin_station_id": str(s1.id),
        "destination_station_id": str(s2.id),
        "scheduled_departure": dep.strftime("%Y-%m-%dT%H:%M"),
        "scheduled_arrival": arr.strftime("%Y-%m-%dT%H:%M"),
        "platform": "1",
        "status": "Dijadwalkan",
        "notes": "",
    }


# === TESTS ===

def test_trip_list_accessible(admin_client, db):
    """Trip list page accessible."""
    _create_train(db)
    response = admin_client.get("/trips")
    assert response.status_code == 200


def test_admin_can_create_trip(admin_client, db):
    """Admin can create a trip."""
    train = _create_train(db)
    s1, s2 = _create_stations(db)
    data = _trip_data(train, s1, s2)

    response = admin_client.post("/trips/create", data=data, follow_redirects=False)
    assert response.status_code == 302

    trip = Trip.query.filter_by(trip_number="TRN-TEST").first()
    assert trip is not None
    assert trip.origin_station_id == s1.id
    assert trip.destination_station_id == s2.id


def test_origin_must_differ_from_destination(admin_client, db):
    """Origin and destination must be different stations."""
    train = _create_train(db)
    s1, s2 = _create_stations(db)
    data = _trip_data(train, s1, s2)
    data["destination_station_id"] = str(s1.id)  # Same as origin

    response = admin_client.post("/trips/create", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"berbeda" in response.data


def test_arrival_must_be_after_departure(admin_client, db):
    """Arrival must be after departure."""
    train = _create_train(db)
    s1, s2 = _create_stations(db)
    data = _trip_data(train, s1, s2)
    # Set arrival before departure
    dep = datetime.now(timezone.utc) + timedelta(hours=5)
    data["scheduled_departure"] = dep.strftime("%Y-%m-%dT%H:%M")
    data["scheduled_arrival"] = (dep - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")

    response = admin_client.post("/trips/create", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"setelah" in response.data


def test_inactive_train_cannot_be_used(admin_client, db):
    """Train with status Tidak Aktif cannot be used."""
    train = _create_train(db, status="Tidak Aktif", code="KA-INAC")
    s1, s2 = _create_stations(db)
    data = _trip_data(train, s1, s2)

    response = admin_client.post("/trips/create", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Tidak Aktif" in response.data


def test_maintenance_train_cannot_be_used(admin_client, db):
    """Train in maintenance cannot be used."""
    train = _create_train(db, status="Dalam Perawatan", code="KA-MNT")
    s1, s2 = _create_stations(db)
    data = _trip_data(train, s1, s2)

    response = admin_client.post("/trips/create", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Perawatan" in response.data


def test_status_history_recorded(admin_client, db):
    """Creating a trip should record initial status history."""
    train = _create_train(db)
    s1, s2 = _create_stations(db)
    data = _trip_data(train, s1, s2)

    admin_client.post("/trips/create", data=data)
    trip = Trip.query.filter_by(trip_number="TRN-TEST").first()
    assert trip is not None

    history = TripStatusHistory.query.filter_by(trip_id=trip.id).all()
    assert len(history) == 1
    assert history[0].new_status == "Dijadwalkan"


def test_status_update_records_history(admin_client, db):
    """Status update should add a history record."""
    train = _create_train(db)
    s1, s2 = _create_stations(db)
    data = _trip_data(train, s1, s2)
    admin_client.post("/trips/create", data=data)

    trip = Trip.query.filter_by(trip_number="TRN-TEST").first()

    # Update status
    admin_client.post(f"/trips/{trip.id}/status", data={
        "new_status": "Berangkat",
        "delay_minutes": "0",
        "station_id": "0",
        "notes": "Berangkat tepat waktu",
    })

    db.session.refresh(trip)
    assert trip.status == "Berangkat"

    history = TripStatusHistory.query.filter_by(trip_id=trip.id).order_by(
        TripStatusHistory.created_at.desc()
    ).all()
    assert len(history) == 2
    assert history[0].new_status == "Berangkat"
    assert history[0].previous_status == "Dijadwalkan"


def test_supervisor_cannot_create_trip(client, db, app):
    """Supervisor cannot create trips."""
    from app.models.user import User

    user = User(full_name="Super Visor", email="sv@railops.local",
                role=User.ROLE_SUPERVISOR, is_active=True)
    user.set_password("Super123!")
    db.session.add(user)
    db.session.commit()

    client.post("/login", data={"email": "sv@railops.local", "password": "Super123!"})
    response = client.get("/trips/create")
    assert response.status_code == 403


def test_supervisor_cannot_delete_trip(client, db, app):
    """Supervisor cannot delete trips."""
    from app.models.user import User

    user = User(full_name="Super Visor", email="sv2@railops.local",
                role=User.ROLE_SUPERVISOR, is_active=True)
    user.set_password("Super123!")
    db.session.add(user)
    db.session.commit()

    train = _create_train(db)
    s1, s2 = _create_stations(db)
    trip = Trip(trip_number="TRN-DEL", train_id=train.id,
                origin_station_id=s1.id, destination_station_id=s2.id,
                scheduled_departure=datetime.now(timezone.utc),
                scheduled_arrival=datetime.now(timezone.utc) + timedelta(hours=2),
                platform=1, status="Dijadwalkan")
    db.session.add(trip)
    db.session.commit()

    client.post("/login", data={"email": "sv2@railops.local", "password": "Super123!"})
    response = client.post(f"/trips/{trip.id}/delete")
    assert response.status_code == 403


def test_trip_search(admin_client, db):
    """Search by trip number works."""
    train = _create_train(db)
    s1, s2 = _create_stations(db)
    trip = Trip(trip_number="SEARCH-001", train_id=train.id,
                origin_station_id=s1.id, destination_station_id=s2.id,
                scheduled_departure=datetime.now(timezone.utc),
                scheduled_arrival=datetime.now(timezone.utc) + timedelta(hours=2),
                platform=1, status="Dijadwalkan")
    db.session.add(trip)
    db.session.commit()

    response = admin_client.get("/trips?search=SEARCH-001")
    assert response.status_code == 200
    assert b"SEARCH-001" in response.data


def test_trip_status_filter(admin_client, db):
    """Status filter works."""
    train = _create_train(db)
    s1, s2 = _create_stations(db)
    trip = Trip(trip_number="FILTER-001", train_id=train.id,
                origin_station_id=s1.id, destination_station_id=s2.id,
                scheduled_departure=datetime.now(timezone.utc),
                scheduled_arrival=datetime.now(timezone.utc) + timedelta(hours=2),
                platform=1, status="Terlambat", delay_minutes=10)
    db.session.add(trip)
    db.session.commit()

    response = admin_client.get("/trips?status=Terlambat")
    assert response.status_code == 200
    assert b"FILTER-001" in response.data


def test_dashboard_counts(admin_client, db):
    """Dashboard counts trips from database."""
    response = admin_client.get("/dashboard")
    assert response.status_code == 200
    # Should render without error even with no trips
    assert b"Perjalanan Hari Ini" in response.data


def test_monitoring_page(admin_client, db):
    """Monitoring page accessible."""
    response = admin_client.get("/trips/monitoring")
    assert response.status_code == 200
