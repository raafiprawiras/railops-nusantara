"""Wait for PostgreSQL and LocalStack to be ready before starting the app."""

import os
import sys
import time

import psycopg2
import boto3
from botocore.exceptions import ClientError, EndpointConnectionError


MAX_RETRIES = 30
RETRY_INTERVAL = 2  # seconds


def wait_for_postgres() -> bool:
    """Wait for PostgreSQL to accept connections."""
    database_url = os.environ.get("DATABASE_URL", "")
    print("Menunggu PostgreSQL...")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            conn = psycopg2.connect(database_url)
            conn.close()
            print(f"  PostgreSQL siap (percobaan {attempt}).")
            return True
        except psycopg2.OperationalError:
            time.sleep(RETRY_INTERVAL)

    print("  GAGAL: PostgreSQL tidak tersedia.")
    return False


def wait_for_localstack() -> bool:
    """Wait for LocalStack to respond."""
    endpoint_url = os.environ.get("AWS_ENDPOINT_URL", "http://localhost:4566")
    print("Menunggu LocalStack...")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            client = boto3.client(
                "sts",
                endpoint_url=endpoint_url,
                aws_access_key_id="test",
                aws_secret_access_key="test",
                region_name="ap-southeast-1",
            )
            client.get_caller_identity()
            print(f"  LocalStack siap (percobaan {attempt}).")
            return True
        except (ClientError, EndpointConnectionError, Exception):
            time.sleep(RETRY_INTERVAL)

    print("  GAGAL: LocalStack tidak tersedia.")
    return False


if __name__ == "__main__":
    pg_ok = wait_for_postgres()
    ls_ok = wait_for_localstack()

    if pg_ok and ls_ok:
        print("\nSemua service siap!")
        sys.exit(0)
    else:
        print("\nBeberapa service gagal. Periksa konfigurasi.")
        sys.exit(1)
