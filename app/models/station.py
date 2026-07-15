"""Station model for railway master data."""

from datetime import datetime, timezone

from app.extensions import db


class Station(db.Model):
    """Railway station data."""

    __tablename__ = "stations"

    id = db.Column(db.Integer, primary_key=True)
    station_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    station_name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(100), nullable=False)
    platform_count = db.Column(db.Integer, nullable=False, default=1)
    operational_status = db.Column(db.String(30), nullable=False, default="Aktif")
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Choices
    STATUS_CHOICES = ["Aktif", "Tidak Aktif", "Dalam Renovasi"]

    def __repr__(self) -> str:
        return f"<Station {self.station_code}>"
