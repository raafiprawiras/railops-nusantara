"""Initialize LocalStack S3 — create bucket if not exists.

Usage:
    python scripts/init_localstack.py

Safe to run multiple times (idempotent).
Waits for LocalStack to be ready before creating bucket.
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MAX_RETRIES = 30
RETRY_INTERVAL = 2


def main():
    from app import create_app
    from app.services import s3_service

    app = create_app()

    with app.app_context():
        bucket_name = app.config["S3_BUCKET_NAME"]
        endpoint = app.config["AWS_ENDPOINT_URL"]

        print(f"Inisialisasi LocalStack S3...")
        print(f"  Endpoint: {endpoint}")
        print(f"  Bucket:   {bucket_name}")
        print()

        # Wait for LocalStack to be ready
        print("Menunggu LocalStack...")
        for attempt in range(1, MAX_RETRIES + 1):
            if s3_service.check_health():
                print(f"  LocalStack siap (percobaan {attempt}).")
                break
            time.sleep(RETRY_INTERVAL)
        else:
            print("  GAGAL: LocalStack tidak tersedia setelah 60 detik.")
            sys.exit(1)

        # Create bucket
        print(f"\nMembuat bucket '{bucket_name}'...")
        result = s3_service.ensure_bucket(bucket_name)
        if result["success"]:
            print(f"  {result['message']}")
        else:
            print(f"  GAGAL: {result['message']}")
            sys.exit(1)

        print("\nInisialisasi selesai!")


if __name__ == "__main__":
    main()
