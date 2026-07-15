"""User model for authentication and role management."""

from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class User(db.Model, UserMixin):
    """Application user with role-based access."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="operator")
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Valid roles
    ROLE_ADMINISTRATOR = "administrator"
    ROLE_OPERATOR = "operator"
    ROLE_SUPERVISOR = "supervisor"
    VALID_ROLES = (ROLE_ADMINISTRATOR, ROLE_OPERATOR, ROLE_SUPERVISOR)

    def set_password(self, password: str) -> None:
        """Hash and store password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify password against stored hash."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_administrator(self) -> bool:
        """Check if user has administrator role."""
        return self.role == self.ROLE_ADMINISTRATOR

    @property
    def is_operator(self) -> bool:
        """Check if user has operator role."""
        return self.role == self.ROLE_OPERATOR

    @property
    def is_supervisor(self) -> bool:
        """Check if user has supervisor role."""
        return self.role == self.ROLE_SUPERVISOR

    def get_role_display(self) -> str:
        """Return role name in Indonesian for display."""
        role_labels = {
            self.ROLE_ADMINISTRATOR: "Administrator",
            self.ROLE_OPERATOR: "Operator",
            self.ROLE_SUPERVISOR: "Supervisor",
        }
        return role_labels.get(self.role, self.role.capitalize())

    def __repr__(self) -> str:
        return f"<User {self.email}>"
