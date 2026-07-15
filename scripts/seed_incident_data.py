"""Seed incident data for development.

Usage:
    python scripts/seed_incident_data.py

Requires trips to exist (run seed_trip_data.py first).
"""

import sys
import os
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.trip import Trip
from app.models.user import User
from app.models.incident import Incident, IncidentStatusHistory


def seed():
    """Seed incident data."""
    app = create_app()

    with app.app_context():
        db.create_all()

        trips = Trip.query.all()
        admin = User.query.filter_by(role="administrator").first()

        if not trips:
            print("ERROR: Jalankan seed_trip_data.py terlebih dahulu.")
            return

        reporter_id = admin.id if admin else None
        now = datetime.now(timezone.utc)

        incidents_data = [
            {
                "incident_number": "INC-001",
                "trip_idx": 0,
                "incident_type": "Gangguan Persinyalan",
                "location": "KM 45 Cikampek",
                "occurred_at": now - timedelta(hours=6),
                "priority": "Tinggi",
                "description": "Sinyal di KM 45 tidak berfungsi normal, kereta harus berjalan pelan.",
                "status": "Dalam Penanganan",
            },
            {
                "incident_number": "INC-002",
                "trip_idx": 1,
                "incident_type": "Gangguan Listrik",
                "location": "Stasiun Cirebon",
                "occurred_at": now - timedelta(hours=3),
                "priority": "Sedang",
                "description": "Listrik overhead contact system mengalami gangguan intermiten.",
                "status": "Dilaporkan",
            },
            {
                "incident_number": "INC-003",
                "trip_idx": 2,
                "incident_type": "Cuaca Buruk",
                "location": "KM 120 Semarang",
                "occurred_at": now - timedelta(days=1),
                "priority": "Darurat",
                "description": "Banjir merendam jalur setinggi 30cm, perjalanan dialihkan.",
                "status": "Selesai",
                "resolution_notes": "Jalur sudah dibersihkan dan aman dilalui.",
            },
            {
                "incident_number": "INC-004",
                "trip_idx": 0,
                "incident_type": "Gangguan Lokomotif",
                "location": "Depo Manggarai",
                "occurred_at": now - timedelta(days=2),
                "priority": "Rendah",
                "description": "Lokomotif CC206 mengalami overheat pada kompresor udara.",
                "status": "Ditutup",
                "resolution_notes": "Kompresor sudah diganti dan diuji coba.",
            },
            {
                "incident_number": "INC-005",
                "trip_idx": 1,
                "incident_type": "Gangguan Fasilitas",
                "location": "Stasiun Tegal",
                "occurred_at": now - timedelta(hours=1),
                "priority": "Rendah",
                "description": "AC di ruang tunggu VIP tidak berfungsi.",
                "status": "Dilaporkan",
            },
        ]

        print("Menambahkan data gangguan...")
        for data in incidents_data:
            existing = Incident.query.filter_by(incident_number=data["incident_number"]).first()
            if existing:
                print(f"  Sudah ada: {data['incident_number']}")
                continue

            trip = trips[data["trip_idx"] % len(trips)]

            incident = Incident(
                incident_number=data["incident_number"],
                trip_id=trip.id,
                incident_type=data["incident_type"],
                location=data["location"],
                occurred_at=data["occurred_at"],
                priority=data["priority"],
                description=data["description"],
                status=data["status"],
                reported_by=reporter_id,
                resolution_notes=data.get("resolution_notes"),
                resolved_at=now if data["status"] in ("Selesai", "Ditutup") else None,
            )
            db.session.add(incident)
            db.session.flush()

            history = IncidentStatusHistory(
                incident_id=incident.id,
                previous_status=None,
                new_status=data["status"],
                notes="Seed data",
                changed_by=reporter_id,
            )
            db.session.add(history)
            print(f"  Ditambahkan: {data['incident_number']} ({data['status']})")

        db.session.commit()
        print("\nSelesai!")


if __name__ == "__main__":
    seed()
