"""Seed trip data for development.

Usage:
    python scripts/seed_trip_data.py

Requires trains and stations to exist (run seed_master_data.py first).
"""

import sys
import os
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.train import Train
from app.models.station import Station
from app.models.trip import Trip, TripStatusHistory
from app.models.user import User


def seed():
    """Seed trip data."""
    app = create_app()

    with app.app_context():
        db.create_all()

        trains = Train.query.filter_by(status="Aktif").all()
        stations = Station.query.filter_by(operational_status="Aktif").all()
        admin = User.query.filter_by(role="administrator").first()

        if not trains or not stations:
            print("ERROR: Jalankan seed_master_data.py terlebih dahulu.")
            return

        if len(stations) < 2:
            print("ERROR: Minimal 2 stasiun dibutuhkan.")
            return

        creator_id = admin.id if admin else None
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        trips_data = [
            {
                "trip_number": "TRN-001",
                "train_idx": 0,
                "origin_idx": 0,
                "dest_idx": 3,
                "hour": 6, "min": 0,
                "duration_h": 8,
                "platform": 1,
                "status": "Tiba",
                "delay": 0,
            },
            {
                "trip_number": "TRN-002",
                "train_idx": 1,
                "origin_idx": 0,
                "dest_idx": 2,
                "hour": 7, "min": 30,
                "duration_h": 5,
                "platform": 2,
                "status": "Terlambat",
                "delay": 15,
            },
            {
                "trip_number": "TRN-003",
                "train_idx": 0,
                "origin_idx": 1,
                "dest_idx": 3,
                "hour": 8, "min": 15,
                "duration_h": 6,
                "platform": 3,
                "status": "Dalam Perjalanan",
                "delay": 5,
            },
            {
                "trip_number": "TRN-004",
                "train_idx": 1,
                "origin_idx": 3,
                "dest_idx": 0,
                "hour": 9, "min": 0,
                "duration_h": 8,
                "platform": 2,
                "status": "Berangkat",
                "delay": 0,
            },
            {
                "trip_number": "TRN-005",
                "train_idx": 0,
                "origin_idx": 0,
                "dest_idx": 1,
                "hour": 10, "min": 0,
                "duration_h": 3,
                "platform": 1,
                "status": "Dijadwalkan",
                "delay": 0,
            },
            {
                "trip_number": "TRN-006",
                "train_idx": 1,
                "origin_idx": 2,
                "dest_idx": 4,
                "hour": 14, "min": 0,
                "duration_h": 2,
                "platform": 4,
                "status": "Dibatalkan",
                "delay": 0,
            },
            {
                "trip_number": "TRN-007",
                "train_idx": 0,
                "origin_idx": 5,
                "dest_idx": 0,
                "hour": 16, "min": 30,
                "duration_h": 4,
                "platform": 2,
                "status": "Persiapan",
                "delay": 0,
            },
        ]

        print("Menambahkan jadwal perjalanan...")
        for data in trips_data:
            existing = Trip.query.filter_by(trip_number=data["trip_number"]).first()
            if existing:
                print(f"  Sudah ada: {data['trip_number']}")
                continue

            t_idx = data["train_idx"] % len(trains)
            o_idx = data["origin_idx"] % len(stations)
            d_idx = data["dest_idx"] % len(stations)
            if o_idx == d_idx:
                d_idx = (d_idx + 1) % len(stations)

            departure = today + timedelta(hours=data["hour"], minutes=data["min"])
            arrival = departure + timedelta(hours=data["duration_h"])

            trip = Trip(
                trip_number=data["trip_number"],
                train_id=trains[t_idx].id,
                origin_station_id=stations[o_idx].id,
                destination_station_id=stations[d_idx].id,
                scheduled_departure=departure,
                scheduled_arrival=arrival,
                platform=data["platform"],
                status=data["status"],
                delay_minutes=data["delay"],
                notes="Dibatalkan karena cuaca buruk" if data["status"] == "Dibatalkan" else None,
                created_by=creator_id,
                actual_departure=departure if data["status"] in ("Berangkat", "Dalam Perjalanan", "Tiba", "Terlambat") else None,
                actual_arrival=arrival if data["status"] == "Tiba" else None,
            )
            db.session.add(trip)
            db.session.flush()

            # Add initial history
            history = TripStatusHistory(
                trip_id=trip.id,
                previous_status=None,
                new_status=data["status"],
                delay_minutes=data["delay"],
                changed_by=creator_id,
                notes="Seed data",
            )
            db.session.add(history)
            print(f"  Ditambahkan: {data['trip_number']} ({data['status']})")

        db.session.commit()
        print("\nSelesai!")


if __name__ == "__main__":
    seed()
