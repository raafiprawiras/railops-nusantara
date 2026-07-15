"""Initialize EC2 demo instances via LocalStack.

Usage:
    python scripts/init_ec2_demo.py

Safe to run multiple times. Creates demo instances if none exist.
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.services import ec2_service
from app.models.infrastructure import InfrastructureInstance

DEMO_INSTANCES = [
    {"name": "RailOps-Web-Server", "purpose": "Web Application"},
    {"name": "RailOps-Monitoring-Server", "purpose": "Monitoring"},
]


def main():
    app = create_app()

    with app.app_context():
        db.create_all()

        print("Inisialisasi EC2 Demo (LocalStack)...")
        print(f"  Endpoint: {app.config['AWS_ENDPOINT_URL']}")
        print()

        # Wait for LocalStack EC2
        print("Menunggu LocalStack EC2...")
        for attempt in range(1, 31):
            if ec2_service.check_health():
                print(f"  EC2 siap (percobaan {attempt}).")
                break
            time.sleep(2)
        else:
            print("  GAGAL: LocalStack EC2 tidak tersedia.")
            sys.exit(1)

        # Create demo instances
        print("\nMembuat instance demo...")
        for data in DEMO_INSTANCES:
            existing = InfrastructureInstance.query.filter_by(
                instance_name=data["name"],
                terminated_at=None,
            ).first()
            if existing:
                print(f"  Sudah ada: {data['name']} ({existing.instance_id})")
                continue

            result = ec2_service.run_instance(name=data["name"], purpose=data["purpose"])
            if result["success"]:
                inst = result["instance"]
                infra = InfrastructureInstance(
                    instance_id=inst["instance_id"],
                    instance_name=data["name"],
                    instance_type=inst["instance_type"],
                    image_id=inst["image_id"],
                    state=inst["state"],
                    purpose=data["purpose"],
                )
                db.session.add(infra)
                print(f"  Dibuat: {data['name']} ({inst['instance_id']})")
            else:
                print(f"  GAGAL: {data['name']} — {result.get('error')}")

        db.session.commit()
        print("\nSelesai!")


if __name__ == "__main__":
    main()
