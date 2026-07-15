"""Create default administrator account for development.

Usage:
    python scripts/create_admin.py

Default credentials (development only):
    Email: admin@railops.local
    Password: Admin123!
    Role: administrator
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.user import User


def create_admin():
    """Create admin user if not exists."""
    app = create_app()

    with app.app_context():
        db.create_all()

        email = "admin@railops.local"
        existing = User.query.filter_by(email=email).first()

        if existing:
            print(f"Admin user sudah ada: {email}")
            return

        admin = User(
            full_name="Administrator",
            email=email,
            role=User.ROLE_ADMINISTRATOR,
            is_active=True,
        )
        admin.set_password("Admin123!")

        db.session.add(admin)
        db.session.commit()

        print(f"Admin user berhasil dibuat:")
        print(f"  Email:    {email}")
        print(f"  Password: Admin123!")
        print(f"  Role:     administrator")
        print()
        print("PENTING: Ganti password setelah login pertama kali!")


if __name__ == "__main__":
    create_admin()
