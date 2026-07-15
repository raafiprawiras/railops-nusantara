"""Seed railway master data for development.

Usage:
    python scripts/seed_master_data.py

Creates sample trains and stations for demo purposes.
"""

import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.train import Train
from app.models.station import Station


TRAINS = [
    {
        "train_code": "KA-001",
        "train_name": "Argo Bromo Anggrek",
        "train_type": "Eksekutif",
        "capacity": 416,
        "carriage_number": 8,
        "status": "Aktif",
        "last_maintenance_date": date(2026, 6, 15),
    },
    {
        "train_code": "KA-002",
        "train_name": "Taksaka",
        "train_type": "Eksekutif",
        "capacity": 320,
        "carriage_number": 6,
        "status": "Aktif",
        "last_maintenance_date": date(2026, 5, 20),
    },
    {
        "train_code": "KA-003",
        "train_name": "Gajayana",
        "train_type": "Bisnis",
        "capacity": 480,
        "carriage_number": 10,
        "status": "Dalam Perawatan",
        "last_maintenance_date": date(2026, 7, 1),
    },
    {
        "train_code": "KA-004",
        "train_name": "Argo Parahyangan",
        "train_type": "Eksekutif",
        "capacity": 256,
        "carriage_number": 5,
        "status": "Aktif",
        "last_maintenance_date": date(2026, 4, 10),
    },
    {
        "train_code": "KA-005",
        "train_name": "KRL Commuter Line",
        "train_type": "Komuter",
        "capacity": 1200,
        "carriage_number": 12,
        "status": "Aktif",
        "last_maintenance_date": date(2026, 7, 5),
    },
    {
        "train_code": "KA-006",
        "train_name": "Barang Kontainer Utara",
        "train_type": "Barang",
        "capacity": 2000,
        "carriage_number": 20,
        "status": "Mengalami Gangguan",
        "last_maintenance_date": date(2026, 3, 28),
    },
]

STATIONS = [
    {
        "station_code": "GMR",
        "station_name": "Gambir",
        "city": "Jakarta Pusat",
        "province": "DKI Jakarta",
        "platform_count": 5,
        "operational_status": "Aktif",
    },
    {
        "station_code": "BD",
        "station_name": "Bandung",
        "city": "Bandung",
        "province": "Jawa Barat",
        "platform_count": 4,
        "operational_status": "Aktif",
    },
    {
        "station_code": "YK",
        "station_name": "Yogyakarta (Tugu)",
        "city": "Yogyakarta",
        "province": "DI Yogyakarta",
        "platform_count": 4,
        "operational_status": "Aktif",
    },
    {
        "station_code": "SGU",
        "station_name": "Surabaya Gubeng",
        "city": "Surabaya",
        "province": "Jawa Timur",
        "platform_count": 6,
        "operational_status": "Aktif",
    },
    {
        "station_code": "SMT",
        "station_name": "Semarang Tawang",
        "city": "Semarang",
        "province": "Jawa Tengah",
        "platform_count": 5,
        "operational_status": "Dalam Renovasi",
    },
    {
        "station_code": "CN",
        "station_name": "Cirebon",
        "city": "Cirebon",
        "province": "Jawa Barat",
        "platform_count": 3,
        "operational_status": "Aktif",
    },
    {
        "station_code": "PSE",
        "station_name": "Pasar Senen",
        "city": "Jakarta Pusat",
        "province": "DKI Jakarta",
        "platform_count": 4,
        "operational_status": "Aktif",
    },
    {
        "station_code": "ML",
        "station_name": "Malang",
        "city": "Malang",
        "province": "Jawa Timur",
        "platform_count": 3,
        "operational_status": "Aktif",
    },
]


def seed():
    """Seed master data."""
    app = create_app()

    with app.app_context():
        db.create_all()

        # Seed trains
        print("Menambahkan data kereta...")
        for data in TRAINS:
            existing = Train.query.filter_by(train_code=data["train_code"]).first()
            if existing:
                print(f"  Sudah ada: {data['train_code']}")
                continue
            train = Train(**data)
            db.session.add(train)
            print(f"  Ditambahkan: {data['train_code']} — {data['train_name']}")

        # Seed stations
        print("\nMenambahkan data stasiun...")
        for data in STATIONS:
            existing = Station.query.filter_by(station_code=data["station_code"]).first()
            if existing:
                print(f"  Sudah ada: {data['station_code']}")
                continue
            station = Station(**data)
            db.session.add(station)
            print(f"  Ditambahkan: {data['station_code']} — {data['station_name']}")

        db.session.commit()
        print("\nSelesai!")


if __name__ == "__main__":
    seed()
