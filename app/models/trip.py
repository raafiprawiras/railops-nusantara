"""Trip and TripStatusHistory models."""

from datetime import datetime, timezone

from app.extensions import db


class Trip(db.Model):
    """Railway trip/schedule."""

    __tablename__ = "trips"

    id = db.Column(db.Integer, primary_key=True)
    trip_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    train_id = db.Column(db.Integer, db.ForeignKey("trains.id"), nullable=False)
    origin_station_id = db.Column(db.Integer, db.ForeignKey("stations.id"), nullable=False)
    destination_station_id = db.Column(db.Integer, db.ForeignKey("stations.id"), nullable=False)
    scheduled_departure = db.Column(db.DateTime(timezone=True), nullable=False)
    scheduled_arrival = db.Column(db.DateTime(timezone=True), nullable=False)
    actual_departure = db.Column(db.DateTime(timezone=True), nullable=True)
    actual_arrival = db.Column(db.DateTime(timezone=True), nullable=True)
    platform = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="Dijadwalkan")
    delay_minutes = db.Column(db.Integer, nullable=False, default=0)
    last_known_station_id = db.Column(db.Integer, db.ForeignKey("stations.id"), nullable=True)
    notes = db.Column(db.Text, nullable=True)
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

    # Relationships (eager load to avoid N+1)
    train = db.relationship("Train", backref="trips", lazy="joined")
    origin_station = db.relationship("Station", foreign_keys=[origin_station_id], lazy="joined")
    destination_station = db.relationship("Station", foreign_keys=[destination_station_id], lazy="joined")
    last_known_station = db.relationship("Station", foreign_keys=[last_known_station_id], lazy="joined")
    creator = db.relationship("User", foreign_keys=[created_by], lazy="joined")
    status_history = db.relationship(
        "TripStatusHistory", backref="trip", lazy="dynamic", order_by="TripStatusHistory.created_at.desc()"
    )

    # Choices
    STATUS_CHOICES = [
        "Dijadwalkan", "Persiapan", "Berangkat", "Dalam Perjalanan",
        "Tiba", "Terlambat", "Dibatalkan",
    ]

    @property
    def route_display(self) -> str:
        """Format: Origin — Destination."""
        origin = self.origin_station.station_name if self.origin_station else "?"
        dest = self.destination_station.station_name if self.destination_station else "?"
        return f"{origin} — {dest}"

    def __repr__(self) -> str:
        return f"<Trip {self.trip_number}>"


class TripStatusHistory(db.Model):
    """Audit log of trip status changes."""

    __tablename__ = "trip_status_history"

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False, index=True)
    previous_status = db.Column(db.String(30), nullable=True)
    new_status = db.Column(db.String(30), nullable=False)
    station_id = db.Column(db.Integer, db.ForeignKey("stations.id"), nullable=True)
    delay_minutes = db.Column(db.Integer, nullable=False, default=0)
    notes = db.Column(db.Text, nullable=True)
    changed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    station = db.relationship("Station", foreign_keys=[station_id], lazy="joined")
    user = db.relationship("User", foreign_keys=[changed_by], lazy="joined")

    def __repr__(self) -> str:
        return f"<TripStatusHistory {self.trip_id}: {self.previous_status} → {self.new_status}>"
