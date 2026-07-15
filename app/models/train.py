"""Train model for railway master data."""

from datetime import datetime, timezone

from app.extensions import db


class Train(db.Model):
    """Railway train/locomotive data."""

    __tablename__ = "trains"

    id = db.Column(db.Integer, primary_key=True)
    train_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    train_name = db.Column(db.String(100), nullable=False)
    train_type = db.Column(db.String(20), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    carriage_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="Aktif")
    last_maintenance_date = db.Column(db.Date, nullable=True)
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
    TYPE_CHOICES = ["Eksekutif", "Bisnis", "Ekonomi", "Komuter", "Barang"]
    STATUS_CHOICES = ["Aktif", "Tidak Aktif", "Dalam Perawatan", "Mengalami Gangguan"]

    def __repr__(self) -> str:
        return f"<Train {self.train_code}>"
