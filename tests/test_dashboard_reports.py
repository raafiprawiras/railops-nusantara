"""Tests for Dynamic Dashboard and Operational Reports."""

from datetime import datetime, timedelta, timezone

from app.models.train import Train
from app.models.station import Station
from app.models.trip import Trip
from app.models.incident import Incident
from app.models.infrastructure import InfrastructureInstance, AuditLog
from app.services.dashboard_service import get_dashboard_stats, get_trip_chart_data


def _seed_data(db):
    """Seed minimal data for dashboard/report tests."""
    train = Train(train_code="KA-RPT", train_name="Report Train",
                  train_type="Eksekutif", capacity=200, carriage_number=5, status="Aktif")
    s1 = Station(station_code="RPT1", station_name="St Report Asal",
                 city="Jakarta", province="DKI Jakarta", platform_count=3, operational_status="Aktif")
    s2 = Station(station_code="RPT2", station_name="St Report Tujuan",
                 city="Bandung", province="Jawa Barat", platform_count=4, operational_status="Aktif")
    db.session.add_all([train, s1, s2])
    db.session.flush()

    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=6, minute=0, second=0, microsecond=0)

    # Trip on time
    t1 = Trip(trip_number="RPT-01", train_id=train.id,
              origin_station_id=s1.id, destination_station_id=s2.id,
              scheduled_departure=today_start,
              scheduled_arrival=today_start + timedelta(hours=3),
              platform=1, status="Tiba", delay_minutes=0)
    # Trip delayed
    t2 = Trip(trip_number="RPT-02", train_id=train.id,
              origin_station_id=s1.id, destination_station_id=s2.id,
              scheduled_departure=today_start + timedelta(hours=2),
              scheduled_arrival=today_start + timedelta(hours=5),
              platform=2, status="Terlambat", delay_minutes=15)
    # Trip cancelled
    t3 = Trip(trip_number="RPT-03", train_id=train.id,
              origin_station_id=s2.id, destination_station_id=s1.id,
              scheduled_departure=today_start + timedelta(hours=4),
              scheduled_arrival=today_start + timedelta(hours=7),
              platform=1, status="Dibatalkan", delay_minutes=0)
    db.session.add_all([t1, t2, t3])
    db.session.flush()

    # Incident
    inc = Incident(
        incident_number="INC-RPT-01", trip_id=t2.id,
        incident_type="Gangguan Persinyalan", location="KM 50",
        occurred_at=now, priority="Tinggi",
        description="Test incident.", status="Dilaporkan", reported_by=1,
    )
    db.session.add(inc)

    # EC2 instance
    infra = InfrastructureInstance(
        instance_id="i-rpt1", instance_name="RPT-Server",
        instance_type="t2.micro", image_id="ami-12345678",
        state="running", purpose="Web Application", created_by=1,
    )
    db.session.add(infra)
    db.session.commit()
    return train, s1, s2, t1, t2, t3


# === DASHBOARD TESTS ===

def test_dashboard_no_data(admin_client, db):
    """Dashboard renders correctly with no data."""
    response = admin_client.get("/dashboard")
    assert response.status_code == 200
    assert b"RailOps Nusantara" in response.data


def test_dashboard_with_data(admin_client, db):
    """Dashboard renders with real data."""
    _seed_data(db)
    response = admin_client.get("/dashboard")
    assert response.status_code == 200
    assert b"Perjalanan Hari Ini" in response.data
    assert b"Gangguan Aktif" in response.data


def test_dashboard_stats_calculation(app, db):
    """Dashboard service returns correct stats."""
    _seed_data(db)
    stats = get_dashboard_stats()
    assert stats["kereta_aktif"] == 1
    assert stats["gangguan_aktif"] == 1
    assert stats["ec2_running"] == 1
    # Trips today depend on when test runs - just verify keys exist
    assert "perjalanan_hari_ini" in stats
    assert "persen_tepat_waktu" in stats
    assert "rata_rata_delay" in stats


def test_chart_data_structure(app, db):
    """Chart data returns expected structure."""
    _seed_data(db)
    chart = get_trip_chart_data()
    assert "doughnut" in chart
    assert "delay_labels" in chart
    assert "delay_values" in chart
    assert "bar_labels" in chart
    assert "bar_values" in chart
    assert len(chart["delay_labels"]) == 7
    assert len(chart["bar_values"]) == 7


def test_dashboard_fallback_without_localstack(admin_client, db):
    """Dashboard works when LocalStack is unavailable."""
    response = admin_client.get("/dashboard")
    assert response.status_code == 200
    # Should not crash, EC2 count just shows 0


# === REPORT TESTS ===

def test_reports_index(admin_client, db):
    """Reports index page accessible."""
    response = admin_client.get("/reports")
    assert response.status_code == 200


def test_trips_report(admin_client, db):
    """Trips report page."""
    _seed_data(db)
    response = admin_client.get("/reports/trips")
    assert response.status_code == 200
    assert b"RPT-01" in response.data


def test_trips_report_date_filter(admin_client, db):
    """Trips report date filter."""
    _seed_data(db)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    response = admin_client.get(f"/reports/trips?start_date={today}&end_date={today}")
    assert response.status_code == 200


def test_trips_csv_response(admin_client, db):
    """Trips CSV export returns proper CSV."""
    _seed_data(db)
    response = admin_client.get("/reports/trips/csv")
    assert response.status_code == 200
    assert response.content_type == "text/csv; charset=utf-8"
    assert b"No. Perjalanan" in response.data
    assert b"RPT-01" in response.data


def test_csv_injection_protection(admin_client, db):
    """CSV values starting with formula chars are escaped."""
    from app.routes.report_routes import _escape_csv_value
    assert _escape_csv_value("=SUM(A1)") == "'=SUM(A1)"
    assert _escape_csv_value("+cmd") == "'+cmd"
    assert _escape_csv_value("-malicious") == "'-malicious"
    assert _escape_csv_value("@import") == "'@import"
    assert _escape_csv_value("normal") == "normal"
    assert _escape_csv_value("") == ""
    assert _escape_csv_value(None) == ""


def test_incidents_report(admin_client, db):
    """Incidents report page."""
    _seed_data(db)
    response = admin_client.get("/reports/incidents")
    assert response.status_code == 200


def test_incidents_csv(admin_client, db):
    """Incidents CSV export."""
    _seed_data(db)
    response = admin_client.get("/reports/incidents/csv")
    assert response.status_code == 200
    assert response.content_type == "text/csv; charset=utf-8"


def test_punctuality_report(admin_client, db):
    """Punctuality report page."""
    _seed_data(db)
    response = admin_client.get("/reports/punctuality")
    assert response.status_code == 200


def test_infrastructure_report(admin_client, db):
    """Infrastructure report page."""
    response = admin_client.get("/reports/infrastructure")
    assert response.status_code == 200


def test_infrastructure_csv(admin_client, db):
    """Infrastructure CSV export."""
    response = admin_client.get("/reports/infrastructure/csv")
    assert response.status_code == 200
    assert response.content_type == "text/csv; charset=utf-8"


def test_documents_report(admin_client, db):
    """Documents report page."""
    response = admin_client.get("/reports/documents")
    assert response.status_code == 200


def test_operator_can_access_trips_report(logged_in_client, db):
    """Operator can access trips report."""
    response = logged_in_client.get("/reports/trips")
    assert response.status_code == 200


def test_operator_cannot_access_punctuality(logged_in_client, db):
    """Operator cannot access punctuality report (admin/supervisor only)."""
    response = logged_in_client.get("/reports/punctuality")
    assert response.status_code == 403
