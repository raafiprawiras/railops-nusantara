"""Tests for Railway Master Data — Trains and Stations."""

from app.models.train import Train
from app.models.station import Station


# === TRAIN TESTS ===

def test_train_list_accessible(logged_in_client):
    """Authenticated user can access train list."""
    response = logged_in_client.get("/trains")
    assert response.status_code == 200


def test_admin_can_create_train(admin_client, db):
    """Administrator can create a train."""
    response = admin_client.post("/trains/create", data={
        "train_code": "KA-TEST",
        "train_name": "Test Express",
        "train_type": "Eksekutif",
        "capacity": "200",
        "carriage_number": "5",
        "status": "Aktif",
    }, follow_redirects=False)
    assert response.status_code == 302

    train = Train.query.filter_by(train_code="KA-TEST").first()
    assert train is not None
    assert train.train_name == "Test Express"


def test_operator_cannot_create_train(logged_in_client):
    """Operator cannot access create train page."""
    response = logged_in_client.get("/trains/create")
    assert response.status_code == 403


def test_operator_cannot_delete_train(logged_in_client, db, sample_train):
    """Operator cannot delete a train."""
    response = logged_in_client.post(f"/trains/{sample_train.id}/delete")
    assert response.status_code == 403


def test_admin_can_edit_train(admin_client, db, sample_train):
    """Administrator can edit a train."""
    response = admin_client.post(f"/trains/{sample_train.id}/edit", data={
        "train_code": sample_train.train_code,
        "train_name": "Updated Name",
        "train_type": "Bisnis",
        "capacity": "300",
        "carriage_number": "6",
        "status": "Aktif",
    }, follow_redirects=False)
    assert response.status_code == 302

    db.session.refresh(sample_train)
    assert sample_train.train_name == "Updated Name"


def test_admin_can_delete_train(admin_client, db, sample_train):
    """Administrator can delete a train via POST."""
    train_id = sample_train.id
    response = admin_client.post(f"/trains/{train_id}/delete", follow_redirects=False)
    assert response.status_code == 302

    assert db.session.get(Train, train_id) is None


def test_train_unique_code_validation(admin_client, db, sample_train):
    """Creating a train with duplicate code should fail."""
    response = admin_client.post("/trains/create", data={
        "train_code": sample_train.train_code,
        "train_name": "Another Train",
        "train_type": "Ekonomi",
        "capacity": "100",
        "carriage_number": "4",
        "status": "Aktif",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"sudah digunakan" in response.data


def test_train_search(admin_client, db, sample_train):
    """Search filter works on train list."""
    response = admin_client.get(f"/trains?search={sample_train.train_name}")
    assert response.status_code == 200
    assert sample_train.train_name.encode() in response.data


def test_train_status_filter(admin_client, db, sample_train):
    """Status filter works on train list."""
    response = admin_client.get(f"/trains?status={sample_train.status}")
    assert response.status_code == 200
    assert sample_train.train_code.encode() in response.data


def test_train_delete_uses_post(logged_in_client, sample_train):
    """GET request to delete should return 405."""
    response = logged_in_client.get(f"/trains/{sample_train.id}/delete")
    assert response.status_code == 405


# === STATION TESTS ===

def test_station_list_accessible(logged_in_client):
    """Authenticated user can access station list."""
    response = logged_in_client.get("/stations")
    assert response.status_code == 200


def test_admin_can_create_station(admin_client, db):
    """Administrator can create a station."""
    response = admin_client.post("/stations/create", data={
        "station_code": "TST",
        "station_name": "Stasiun Test",
        "city": "Jakarta",
        "province": "DKI Jakarta",
        "platform_count": "3",
        "operational_status": "Aktif",
    }, follow_redirects=False)
    assert response.status_code == 302

    station = Station.query.filter_by(station_code="TST").first()
    assert station is not None
    assert station.station_name == "Stasiun Test"


def test_operator_cannot_create_station(logged_in_client):
    """Operator cannot access create station page."""
    response = logged_in_client.get("/stations/create")
    assert response.status_code == 403


def test_station_unique_code_validation(admin_client, db, sample_station):
    """Creating a station with duplicate code should fail."""
    response = admin_client.post("/stations/create", data={
        "station_code": sample_station.station_code,
        "station_name": "Another Station",
        "city": "Bandung",
        "province": "Jawa Barat",
        "platform_count": "2",
        "operational_status": "Aktif",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"sudah digunakan" in response.data


def test_station_search(admin_client, db, sample_station):
    """Search filter works on station list."""
    response = admin_client.get(f"/stations?search={sample_station.station_name}")
    assert response.status_code == 200
    assert sample_station.station_name.encode() in response.data


def test_station_status_filter(admin_client, db, sample_station):
    """Status filter works on station list."""
    response = admin_client.get(f"/stations?status={sample_station.operational_status}")
    assert response.status_code == 200
    assert sample_station.station_code.encode() in response.data
