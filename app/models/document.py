"""Document model for S3 file metadata."""

from datetime import datetime, timezone

from app.extensions import db


class Document(db.Model):
    """Metadata for files stored in S3."""

    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=True)
    incident_id = db.Column(db.Integer, db.ForeignKey("incidents.id"), nullable=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    bucket_name = db.Column(db.String(100), nullable=False)
    object_key = db.Column(db.String(500), nullable=False)
    content_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    document_category = db.Column(db.String(50), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    uploaded_at = db.Column(
        db.DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Relationships
    trip = db.relationship("Trip", backref="documents", lazy="joined")
    incident = db.relationship("Incident", backref="documents", lazy="joined")
    uploader = db.relationship("User", foreign_keys=[uploaded_by], lazy="joined")

    # Choices
    CATEGORY_CHOICES = [
        "Manifest", "Inspeksi", "Perawatan", "Laporan Gangguan",
        "Berita Acara", "Dokumentasi", "Lainnya",
    ]

    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "docx", "xlsx"}

    ALLOWED_MIMETYPES = {
        "application/pdf",
        "image/png",
        "image/jpeg",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @property
    def file_size_display(self) -> str:
        """Human-readable file size."""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"

    def __repr__(self) -> str:
        return f"<Document {self.original_filename}>"
