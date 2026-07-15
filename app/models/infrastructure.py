"""Infrastructure instance and audit log models."""

from datetime import datetime, timezone

from app.extensions import db


class InfrastructureInstance(db.Model):
    """Local tracking of EC2 instances managed via LocalStack."""

    __tablename__ = "infrastructure_instances"

    id = db.Column(db.Integer, primary_key=True)
    instance_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    instance_name = db.Column(db.String(100), nullable=False)
    instance_type = db.Column(db.String(20), nullable=False, default="t2.micro")
    image_id = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(20), nullable=False, default="pending")
    purpose = db.Column(db.String(50), nullable=False, default="")
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    terminated_at = db.Column(db.DateTime(timezone=True), nullable=True)

    creator = db.relationship("User", foreign_keys=[created_by], lazy="joined")

    # Valid actions per state
    STATE_ACTIONS = {
        "running": ["stop", "reboot", "terminate"],
        "stopped": ["start", "terminate"],
        "pending": [],
        "shutting-down": [],
        "terminated": [],
    }

    PURPOSE_CHOICES = ["Web Application", "Monitoring", "Backup", "Emergency"]
    NAME_CHOICES = [
        "RailOps-Web-Server",
        "RailOps-Monitoring-Server",
        "RailOps-Backup-Server",
        "RailOps-Emergency-Server",
    ]

    def get_allowed_actions(self) -> list[str]:
        """Return allowed actions for current state."""
        return self.STATE_ACTIONS.get(self.state, [])

    def can_perform(self, action: str) -> bool:
        """Check if action is valid for current state."""
        return action in self.get_allowed_actions()

    def __repr__(self) -> str:
        return f"<InfrastructureInstance {self.instance_id}>"


class AuditLog(db.Model):
    """Audit log for infrastructure actions."""

    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    action = db.Column(db.String(50), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    metadata_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship("User", foreign_keys=[user_id], lazy="joined")

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} {self.resource_type}/{self.resource_id}>"
