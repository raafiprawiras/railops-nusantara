"""Incident and IncidentStatusHistory models."""

from datetime import datetime, timezone

from app.extensions import db


class Incident(db.Model):
    """Railway incident/disruption record."""

    __tablename__ = "incidents"

    id = db.Column(db.Integer, primary_key=True)
    incident_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False)
    incident_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    occurred_at = db.Column(db.DateTime(timezone=True), nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="Dilaporkan")
    reported_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    resolved_at = db.Column(db.DateTime(timezone=True), nullable=True)
    resolution_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    trip = db.relationship("Trip", backref="incidents", lazy="joined")
    reporter = db.relationship("User", foreign_keys=[reported_by], lazy="joined")
    assignee = db.relationship("User", foreign_keys=[assigned_to], lazy="joined")
    status_history = db.relationship(
        "IncidentStatusHistory", backref="incident", lazy="dynamic",
        order_by="IncidentStatusHistory.created_at.desc()",
    )

    # Choices
    TYPE_CHOICES = [
        "Gangguan Lokomotif", "Gangguan Rangkaian", "Gangguan Persinyalan",
        "Gangguan Jalur", "Gangguan Listrik", "Cuaca Buruk",
        "Gangguan Fasilitas", "Lainnya",
    ]
    PRIORITY_CHOICES = ["Rendah", "Sedang", "Tinggi", "Darurat"]
    STATUS_CHOICES = ["Dilaporkan", "Dalam Penanganan", "Selesai", "Ditutup"]

    # Valid transitions: current_status -> [allowed next statuses]
    VALID_TRANSITIONS = {
        "Dilaporkan": ["Dalam Penanganan"],
        "Dalam Penanganan": ["Selesai"],
        "Selesai": ["Ditutup"],
        "Ditutup": [],
    }

    def can_transition_to(self, new_status: str) -> bool:
        """Check if transition to new_status is valid."""
        allowed = self.VALID_TRANSITIONS.get(self.status, [])
        return new_status in allowed

    def __repr__(self) -> str:
        return f"<Incident {self.incident_number}>"


class IncidentStatusHistory(db.Model):
    """Audit log of incident status changes."""

    __tablename__ = "incident_status_history"

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey("incidents.id"), nullable=False, index=True)
    previous_status = db.Column(db.String(30), nullable=True)
    new_status = db.Column(db.String(30), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    changed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship("User", foreign_keys=[changed_by], lazy="joined")

    def __repr__(self) -> str:
        return f"<IncidentStatusHistory {self.incident_id}: {self.previous_status} → {self.new_status}>"
