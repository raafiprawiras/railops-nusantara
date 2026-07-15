"""Seed sample users for development.

Usage:
    python scripts/seed_users.py

Creates sample users with different roles for testing purposes.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.user import User


SEED_USERS = [
    {
        "full_name": "Administrator",
        "email": "admin@railops.local",
        "password": "Admin123!",
        "role": User.ROLE_ADMINISTRATOR,
    },
    {
        "full_name": "Budi Operator",
        "email": "budi@railops.local",
        "password": "Operator123!",
        "role": User.ROLE_OPERATOR,
    },
    {
        "full_name": "Siti Supervisor",
        "email": "siti@railops.local",
        "password": "Supervisor123!",
        "role": User.ROLE_SUPERVISOR,
    },
]


def seed_users():
    """Seed development users."""
    app = create_app()

    with app.app_context():
        db.create_all()

        created = 0
        for user_data in SEED_USERS:
            existing = User.query.filter_by(email=user_data["email"]).first()
            if existing:
                print(f"  Sudah ada: {user_data['email']}")
                continue

            user = User(
                full_name=user_data["full_name"],
                email=user_data["email"],
                role=user_data["role"],
                is_active=True,
            )
            user.set_password(user_data["password"])
            db.session.add(user)
            created += 1
            print(f"  Dibuat: {user_data['email']} ({user_data['role']})")

        db.session.commit()
        print(f"\nSelesai. {created} user baru ditambahkan.")


if __name__ == "__main__":
    seed_users()
