"""Integrated demo data seeder for RailOps Nusantara.

Usage:
    python scripts/seed_demo.py
    python scripts/seed_demo.py --reset   (development only, wipes + reseeds)

Or via Flask CLI:
    flask seed-demo
    flask seed-demo --reset

Safe to run multiple times (idempotent). Never runs in production automatically.
"""

import sys
import os
import io
from datetime import datetime, timedelta, timezone, date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# === DATA DEFINITIONS ===

DEMO_USERS = [
    {"full_name": "Administrator", "email": "admin@railops.local", "role": "administrator", "password": "Admin123!"},
    {"full_name": "Budi Santoso", "email": "budi@railops.local", "role": "operator", "password": "Operator1!"},
    {"full_name": "Dewi Lestari", "email": "dewi@railops.local", "role": "operator", "password": "Operator2!"},
    {"full_name": "Andi Wijaya", "email": "andi@railops.local", "role": "supervisor", "password": "Supervisor1!"},
]

DEMO_TRAINS = [
    {"train_code": "KA-001", "train_name": "Argo Bromo Anggrek", "train_type": "Eksekutif", "capacity": 416, "carriage_number": 8, "status": "Aktif", "last_maintenance_date": date(2026, 6, 15)},
    {"train_code": "KA-002", "train_name": "Taksaka", "train_type": "Eksekutif", "capacity": 320, "carriage_number": 6, "status": "Aktif", "last_maintenance_date": date(2026, 5, 20)},
    {"train_code": "KA-003", "train_name": "Gajayana", "train_type": "Bisnis", "capacity": 480, "carriage_number": 10, "status": "Dalam Perawatan", "last_maintenance_date": date(2026, 7, 1)},
    {"train_code": "KA-004", "train_name": "Argo Parahyangan", "train_type": "Eksekutif", "capacity": 256, "carriage_number": 5, "status": "Aktif", "last_maintenance_date": date(2026, 4, 10)},
    {"train_code": "KA-005", "train_name": "KRL Commuter Line", "train_type": "Komuter", "capacity": 1200, "carriage_number": 12, "status": "Aktif", "last_maintenance_date": date(2026, 7, 5)},
    {"train_code": "KA-006", "train_name": "Barang Kontainer Utara", "train_type": "Barang", "capacity": 2000, "carriage_number": 20, "status": "Mengalami Gangguan", "last_maintenance_date": date(2026, 3, 28)},
    {"train_code": "KA-007", "train_name": "Sembrani", "train_type": "Eksekutif", "capacity": 350, "carriage_number": 7, "status": "Aktif", "last_maintenance_date": date(2026, 6, 1)},
    {"train_code": "KA-008", "train_name": "Ekonomi Lokal Cirebon", "train_type": "Ekonomi", "capacity": 600, "carriage_number": 8, "status": "Aktif", "last_maintenance_date": date(2026, 5, 15)},
]

DEMO_STATIONS = [
    {"station_code": "GMR", "station_name": "Gambir", "city": "Jakarta Pusat", "province": "DKI Jakarta", "platform_count": 5, "operational_status": "Aktif"},
    {"station_code": "BD", "station_name": "Bandung", "city": "Bandung", "province": "Jawa Barat", "platform_count": 4, "operational_status": "Aktif"},
    {"station_code": "YK", "station_name": "Yogyakarta (Tugu)", "city": "Yogyakarta", "province": "DI Yogyakarta", "platform_count": 4, "operational_status": "Aktif"},
    {"station_code": "SGU", "station_name": "Surabaya Gubeng", "city": "Surabaya", "province": "Jawa Timur", "platform_count": 6, "operational_status": "Aktif"},
    {"station_code": "SMT", "station_name": "Semarang Tawang", "city": "Semarang", "province": "Jawa Tengah", "platform_count": 5, "operational_status": "Dalam Renovasi"},
    {"station_code": "CN", "station_name": "Cirebon", "city": "Cirebon", "province": "Jawa Barat", "platform_count": 3, "operational_status": "Aktif"},
    {"station_code": "PSE", "station_name": "Pasar Senen", "city": "Jakarta Pusat", "province": "DKI Jakarta", "platform_count": 4, "operational_status": "Aktif"},
    {"station_code": "ML", "station_name": "Malang", "city": "Malang", "province": "Jawa Timur", "platform_count": 3, "operational_status": "Aktif"},
    {"station_code": "SLO", "station_name": "Solo Balapan", "city": "Surakarta", "province": "Jawa Tengah", "platform_count": 4, "operational_status": "Aktif"},
    {"station_code": "PWK", "station_name": "Purwokerto", "city": "Purwokerto", "province": "Jawa Tengah", "platform_count": 3, "operational_status": "Aktif"},
]


def _get_trip_definitions(today):
    """Generate trip definitions relative to today."""
    trips = []
    statuses_cycle = [
        ("Tiba", 0), ("Tiba", 0), ("Tiba", 5), ("Terlambat", 12),
        ("Tiba", 0), ("Dalam Perjalanan", 3), ("Berangkat", 0),
        ("Dijadwalkan", 0), ("Dibatalkan", 0), ("Persiapan", 0),
    ]
    for i in range(22):
        day_offset = -(i // 4)  # spread across last few days
        hour = 5 + (i * 2) % 18
        dep = today + timedelta(days=day_offset, hours=hour)
        arr = dep + timedelta(hours=3 + (i % 3))
        status, delay = statuses_cycle[i % len(statuses_cycle)]
        trips.append({
            "trip_number": f"TRN-D{i+1:03d}",
            "train_idx": i % 6,  # only use active trains (0-5 but skip idx 2,5)
            "origin_idx": i % 10,
            "dest_idx": (i + 3) % 10,
            "departure": dep,
            "arrival": arr,
            "platform": (i % 5) + 1,
            "status": status,
            "delay": delay,
            "notes": "Dibatalkan karena cuaca buruk." if status == "Dibatalkan" else None,
        })
    return trips


DEMO_INCIDENTS = [
    {"number": "INC-D001", "trip_idx": 3, "type": "Gangguan Persinyalan", "location": "KM 45 Cikampek", "priority": "Tinggi", "status": "Dalam Penanganan"},
    {"number": "INC-D002", "trip_idx": 5, "type": "Gangguan Listrik", "location": "Stasiun Cirebon", "priority": "Sedang", "status": "Dilaporkan"},
    {"number": "INC-D003", "trip_idx": 0, "type": "Cuaca Buruk", "location": "KM 120 Semarang", "priority": "Darurat", "status": "Selesai", "resolution": "Jalur dibersihkan."},
    {"number": "INC-D004", "trip_idx": 1, "type": "Gangguan Lokomotif", "location": "Depo Manggarai", "priority": "Rendah", "status": "Ditutup", "resolution": "Kompresor diganti."},
    {"number": "INC-D005", "trip_idx": 2, "type": "Gangguan Fasilitas", "location": "Stasiun Tegal", "priority": "Rendah", "status": "Dilaporkan"},
    {"number": "INC-D006", "trip_idx": 4, "type": "Gangguan Jalur", "location": "KM 80 Cikampek", "priority": "Tinggi", "status": "Dalam Penanganan"},
    {"number": "INC-D007", "trip_idx": 6, "type": "Gangguan Rangkaian", "location": "Stasiun Gambir", "priority": "Sedang", "status": "Selesai", "resolution": "Coupling diperbaiki."},
    {"number": "INC-D008", "trip_idx": 7, "type": "Lainnya", "location": "Stasiun Bandung", "priority": "Rendah", "status": "Dilaporkan"},
]


def seed_demo(reset: bool = False, app=None):
    """Run the full demo seed."""
    from app.extensions import db
    from app.models.user import User
    from app.models.train import Train
    from app.models.station import Station
    from app.models.trip import Trip, TripStatusHistory
    from app.models.incident import Incident, IncidentStatusHistory
    from app.models.document import Document
    from app.models.infrastructure import InfrastructureInstance, AuditLog

    if app is None:
        from app import create_app
        app = create_app()

    with app.app_context():
        # Production guard
        if not app.debug and not app.testing:
            print("ERROR: Seed demo hanya dapat dijalankan di development/testing.")
            return False

        db.create_all()

        if reset:
            print("RESET: Menghapus data demo...")
            AuditLog.query.delete()
            InfrastructureInstance.query.delete()
            Document.query.delete()
            IncidentStatusHistory.query.delete()
            Incident.query.delete()
            TripStatusHistory.query.delete()
            Trip.query.delete()
            Station.query.delete()
            Train.query.delete()
            User.query.delete()
            db.session.commit()
            print("  Data dihapus.\n")

        now = datetime.now(timezone.utc)
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        created = {"users": 0, "trains": 0, "stations": 0, "trips": 0, "incidents": 0, "ec2": 0, "docs": 0}

        # --- Users ---
        print("Seeding users...")
        admin_id = None
        for u_data in DEMO_USERS:
            existing = User.query.filter_by(email=u_data["email"]).first()
            if existing:
                if u_data["role"] == "administrator":
                    admin_id = existing.id
                continue
            user = User(full_name=u_data["full_name"], email=u_data["email"], role=u_data["role"], is_active=True)
            user.set_password(u_data["password"])
            db.session.add(user)
            db.session.flush()
            if u_data["role"] == "administrator":
                admin_id = user.id
            created["users"] += 1
        db.session.commit()
        if not admin_id:
            admin_id = User.query.filter_by(role="administrator").first().id
        print(f"  Users: {created['users']} baru")

        # --- Trains ---
        print("Seeding trains...")
        for t_data in DEMO_TRAINS:
            if Train.query.filter_by(train_code=t_data["train_code"]).first():
                continue
            db.session.add(Train(**t_data))
            created["trains"] += 1
        db.session.commit()
        trains = Train.query.order_by(Train.train_code).all()
        active_trains = [t for t in trains if t.status == "Aktif"]
        print(f"  Trains: {created['trains']} baru")

        # --- Stations ---
        print("Seeding stations...")
        for s_data in DEMO_STATIONS:
            if Station.query.filter_by(station_code=s_data["station_code"]).first():
                continue
            db.session.add(Station(**s_data))
            created["stations"] += 1
        db.session.commit()
        stations = Station.query.order_by(Station.station_code).all()
        print(f"  Stations: {created['stations']} baru")

        # --- Trips ---
        print("Seeding trips...")
        trip_defs = _get_trip_definitions(today)
        trip_objects = []
        for td in trip_defs:
            if Trip.query.filter_by(trip_number=td["trip_number"]).first():
                trip_objects.append(Trip.query.filter_by(trip_number=td["trip_number"]).first())
                continue
            train = active_trains[td["train_idx"] % len(active_trains)]
            o_idx = td["origin_idx"] % len(stations)
            d_idx = td["dest_idx"] % len(stations)
            if o_idx == d_idx:
                d_idx = (d_idx + 1) % len(stations)

            trip = Trip(
                trip_number=td["trip_number"],
                train_id=train.id,
                origin_station_id=stations[o_idx].id,
                destination_station_id=stations[d_idx].id,
                scheduled_departure=td["departure"],
                scheduled_arrival=td["arrival"],
                platform=td["platform"],
                status=td["status"],
                delay_minutes=td["delay"],
                notes=td["notes"],
                created_by=admin_id,
                actual_departure=td["departure"] if td["status"] in ("Berangkat", "Dalam Perjalanan", "Tiba", "Terlambat") else None,
                actual_arrival=td["arrival"] if td["status"] == "Tiba" else None,
            )
            db.session.add(trip)
            db.session.flush()
            # Status history
            db.session.add(TripStatusHistory(
                trip_id=trip.id, previous_status=None, new_status=td["status"],
                delay_minutes=td["delay"], changed_by=admin_id, notes="Demo seed",
            ))
            trip_objects.append(trip)
            created["trips"] += 1
        db.session.commit()
        print(f"  Trips: {created['trips']} baru")

        # --- Incidents ---
        print("Seeding incidents...")
        for inc_data in DEMO_INCIDENTS:
            if Incident.query.filter_by(incident_number=inc_data["number"]).first():
                continue
            trip = trip_objects[inc_data["trip_idx"] % len(trip_objects)]
            inc = Incident(
                incident_number=inc_data["number"],
                trip_id=trip.id,
                incident_type=inc_data["type"],
                location=inc_data["location"],
                occurred_at=now - timedelta(hours=inc_data["trip_idx"] * 3),
                priority=inc_data["priority"],
                description=f"Demo: {inc_data['type']} di {inc_data['location']}.",
                status=inc_data["status"],
                reported_by=admin_id,
                resolution_notes=inc_data.get("resolution"),
                resolved_at=now if inc_data["status"] in ("Selesai", "Ditutup") else None,
            )
            db.session.add(inc)
            db.session.flush()
            db.session.add(IncidentStatusHistory(
                incident_id=inc.id, previous_status=None, new_status=inc_data["status"],
                notes="Demo seed", changed_by=admin_id,
            ))
            created["incidents"] += 1
        db.session.commit()
        print(f"  Incidents: {created['incidents']} baru")

        # --- EC2 Instances (optional) ---
        print("Seeding EC2 instances...")
        try:
            from app.services import ec2_service
            if ec2_service.check_health():
                ec2_demos = [
                    ("RailOps-Web-Server", "Web Application"),
                    ("RailOps-Monitoring-Server", "Monitoring"),
                ]
                for name, purpose in ec2_demos:
                    if InfrastructureInstance.query.filter_by(instance_name=name, terminated_at=None).first():
                        continue
                    result = ec2_service.run_instance(name=name, purpose=purpose)
                    if result["success"]:
                        inst = result["instance"]
                        db.session.add(InfrastructureInstance(
                            instance_id=inst["instance_id"], instance_name=name,
                            instance_type=inst["instance_type"], image_id=inst["image_id"],
                            state=inst["state"], purpose=purpose, created_by=admin_id,
                        ))
                        created["ec2"] += 1
                db.session.commit()
                print(f"  EC2: {created['ec2']} baru")
            else:
                print("  EC2: LocalStack tidak tersedia (dilewati)")
        except Exception as e:
            print(f"  EC2: Gagal — {e} (dilewati)")

        # --- Documents (optional S3) ---
        print("Seeding documents...")
        try:
            from app.services import s3_service
            bucket = app.config.get("S3_BUCKET_NAME", "railops-bucket")
            s3_available = s3_service.check_health()
            if s3_available:
                s3_service.ensure_bucket(bucket)

            doc_demos = [
                ("manifest_trip_001.pdf", "Manifest", "application/pdf"),
                ("inspeksi_kereta_001.pdf", "Inspeksi", "application/pdf"),
                ("laporan_gangguan_001.pdf", "Laporan Gangguan", "application/pdf"),
            ]
            for filename, category, ctype in doc_demos:
                if Document.query.filter_by(original_filename=filename, deleted_at=None).first():
                    continue
                object_key = f"demo/{now.strftime('%Y')}/{filename}"
                if s3_available:
                    content = f"Demo document: {filename}\nGenerated: {now.isoformat()}\n".encode()
                    s3_service.upload_file(bucket, object_key, io.BytesIO(content), ctype)

                trip_for_doc = trip_objects[0] if trip_objects else None
                db.session.add(Document(
                    trip_id=trip_for_doc.id if trip_for_doc else None,
                    original_filename=filename,
                    stored_filename=filename,
                    bucket_name=bucket,
                    object_key=object_key,
                    content_type=ctype,
                    file_size=1024,
                    document_category=category,
                    uploaded_by=admin_id,
                ))
                created["docs"] += 1
            db.session.commit()
            if not s3_available:
                print(f"  Documents: {created['docs']} metadata (WARNING: S3 tidak tersedia, file tidak diupload)")
            else:
                print(f"  Documents: {created['docs']} baru (uploaded to S3)")
        except Exception as e:
            print(f"  Documents: Gagal — {e} (dilewati)")

        # --- Audit Logs ---
        print("Seeding audit logs...")
        if not AuditLog.query.filter_by(description="Demo seed: system initialized").first():
            db.session.add(AuditLog(
                user_id=admin_id, action="seed_demo", resource_type="system",
                resource_id="demo", description="Demo seed: system initialized",
            ))
            db.session.commit()

        # Summary
        print(f"\n{'='*40}")
        print("SEED DEMO SELESAI")
        print(f"{'='*40}")
        total = sum(created.values())
        print(f"Total record baru: {total}")
        for key, val in created.items():
            print(f"  {key}: {val}")
        print()
        return True


if __name__ == "__main__":
    do_reset = "--reset" in sys.argv
    seed_demo(reset=do_reset)
