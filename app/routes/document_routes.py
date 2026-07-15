"""Document routes — upload, download, delete, list, cloud S3 panel."""

import os
import uuid
import mimetypes
from datetime import datetime, timezone

from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, abort,
    Response, stream_with_context, current_app,
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.document import Document
from app.models.trip import Trip
from app.models.incident import Incident
from app.forms.document_forms import DocumentUploadForm
from app.services import s3_service
from app.utils.decorators import role_required

documents_bp = Blueprint("documents", __name__)

PER_PAGE = 10

# Category → key prefix mapping
CATEGORY_PREFIX = {
    "Manifest": "manifests",
    "Inspeksi": "inspections",
    "Perawatan": "maintenance",
    "Laporan Gangguan": "incidents",
    "Berita Acara": "miscellaneous",
    "Dokumentasi": "miscellaneous",
    "Lainnya": "miscellaneous",
}


def _build_object_key(category: str, original_filename: str,
                      trip=None, incident=None) -> str:
    """Build structured S3 object key."""
    year = datetime.now(timezone.utc).strftime("%Y")
    prefix = CATEGORY_PREFIX.get(category, "miscellaneous")
    ext = os.path.splitext(original_filename)[1].lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"

    if trip and prefix in ("manifests",):
        return f"{prefix}/{year}/{trip.trip_number}/{unique_name}"
    elif incident and prefix == "incidents":
        return f"{prefix}/{year}/{incident.incident_number}/{unique_name}"
    elif trip:
        return f"{prefix}/{year}/{trip.trip_number}/{unique_name}"
    else:
        return f"{prefix}/{year}/{unique_name}"


def _validate_mimetype(file) -> str | None:
    """Validate file MIME type. Returns content_type or None if invalid."""
    content_type = file.content_type
    if not content_type:
        content_type = mimetypes.guess_type(file.filename)[0] or ""

    if content_type in Document.ALLOWED_MIMETYPES:
        return content_type

    # Also check by extension as fallback
    ext = os.path.splitext(file.filename)[1].lower().lstrip(".")
    if ext in Document.ALLOWED_EXTENSIONS:
        guessed = mimetypes.guess_type(f"file.{ext}")[0]
        if guessed and guessed in Document.ALLOWED_MIMETYPES:
            return guessed

    return None


def _populate_form_choices(form):
    """Populate trip and incident choices."""
    trips = Trip.query.order_by(Trip.trip_number.desc()).limit(50).all()
    incidents = Incident.query.order_by(Incident.incident_number.desc()).limit(50).all()

    form.trip_id.choices = [(0, "— Tidak Ada —")] + [
        (t.id, f"{t.trip_number} — {t.route_display}") for t in trips
    ]
    form.incident_id.choices = [(0, "— Tidak Ada —")] + [
        (i.id, f"{i.incident_number} — {i.incident_type}") for i in incidents
    ]


@documents_bp.route("/documents")
@login_required
def index():
    """List documents with filters and pagination."""
    page = request.args.get("page", 1, type=int)
    category = request.args.get("category", "", type=str).strip()

    query = Document.query.filter(Document.deleted_at.is_(None))

    if category:
        query = query.filter(Document.document_category == category)

    query = query.order_by(Document.uploaded_at.desc())
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)

    return render_template(
        "documents/list.html",
        documents=pagination.items,
        pagination=pagination,
        category=category,
        category_choices=Document.CATEGORY_CHOICES,
    )


@documents_bp.route("/documents/upload", methods=["GET", "POST"])
@login_required
@role_required("administrator", "operator")
def upload():
    """Upload a document to S3."""
    form = DocumentUploadForm()
    _populate_form_choices(form)

    if form.validate_on_submit():
        file = form.file.data

        # Validate MIME type
        content_type = _validate_mimetype(file)
        if not content_type:
            flash("Tipe file tidak diizinkan.", "danger")
            return render_template("documents/upload.html", form=form)

        # Validate file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        max_size = current_app.config.get("MAX_CONTENT_LENGTH", 16777216)
        if file_size > max_size:
            flash(f"File terlalu besar. Maksimal {max_size // (1024*1024)} MB.", "danger")
            return render_template("documents/upload.html", form=form)

        # Sanitize filename
        original_filename = secure_filename(file.filename) or "unnamed"
        stored_filename = f"{uuid.uuid4().hex}_{original_filename}"

        # Resolve related objects
        trip = db.session.get(Trip, form.trip_id.data) if form.trip_id.data else None
        incident = db.session.get(Incident, form.incident_id.data) if form.incident_id.data else None

        if not trip and not incident:
            flash("Dokumen harus terkait dengan Perjalanan atau Gangguan.", "danger")
            return render_template("documents/upload.html", form=form)

        # Build object key
        bucket_name = current_app.config["S3_BUCKET_NAME"]
        object_key = _build_object_key(form.document_category.data, original_filename, trip, incident)

        # Ensure bucket exists
        s3_service.ensure_bucket(bucket_name)

        # Upload to S3
        result = s3_service.upload_file(bucket_name, object_key, file, content_type)
        if not result["success"]:
            flash(f"Gagal upload ke S3: {result.get('error', 'Unknown error')}", "danger")
            return render_template("documents/upload.html", form=form)

        # Save metadata to DB
        try:
            doc = Document(
                trip_id=trip.id if trip else None,
                incident_id=incident.id if incident else None,
                original_filename=original_filename,
                stored_filename=stored_filename,
                bucket_name=bucket_name,
                object_key=object_key,
                content_type=content_type,
                file_size=file_size,
                document_category=form.document_category.data,
                uploaded_by=current_user.id,
            )
            db.session.add(doc)
            db.session.commit()
            flash("Dokumen berhasil diupload.", "success")
            return redirect(url_for("documents.index"))
        except Exception:
            # Rollback: remove uploaded S3 object
            db.session.rollback()
            s3_service.delete_object(bucket_name, object_key)
            flash("Gagal menyimpan metadata. Upload dibatalkan.", "danger")
            return render_template("documents/upload.html", form=form)

    return render_template("documents/upload.html", form=form)


@documents_bp.route("/documents/<int:id>")
@login_required
def detail(id):
    """Document detail with metadata."""
    doc = db.session.get(Document, id) or abort(404)
    if doc.is_deleted:
        abort(404)
    return render_template("documents/detail.html", document=doc)


@documents_bp.route("/documents/<int:id>/download")
@login_required
def download(id):
    """Download a document from S3."""
    doc = db.session.get(Document, id) or abort(404)
    if doc.is_deleted:
        abort(404)

    # Prevent path traversal
    if ".." in doc.object_key or doc.object_key.startswith("/"):
        abort(400)

    result = s3_service.download_file(doc.bucket_name, doc.object_key)
    if not result["success"]:
        flash(f"Gagal mengunduh: {result.get('error', 'Unknown error')}", "danger")
        return redirect(url_for("documents.detail", id=doc.id))

    def generate():
        body = result["body"]
        while True:
            chunk = body.read(8192)
            if not chunk:
                break
            yield chunk

    return Response(
        stream_with_context(generate()),
        content_type=result["content_type"],
        headers={
            "Content-Disposition": f'attachment; filename="{doc.original_filename}"',
            "Content-Length": str(result.get("content_length", "")),
        },
    )


@documents_bp.route("/documents/<int:id>/delete", methods=["POST"])
@login_required
@role_required("administrator")
def delete(id):
    """Soft-delete document metadata and remove from S3."""
    doc = db.session.get(Document, id) or abort(404)
    if doc.is_deleted:
        abort(404)

    # Delete from S3
    s3_service.delete_object(doc.bucket_name, doc.object_key)

    # Soft delete metadata
    doc.deleted_at = datetime.now(timezone.utc)
    db.session.commit()

    flash(f"Dokumen {doc.original_filename} berhasil dihapus.", "success")
    return redirect(url_for("documents.index"))


# --- Cloud S3 Panel ---

@documents_bp.route("/cloud/s3")
@login_required
def cloud_s3():
    """Cloud S3 panel — LocalStack status, buckets, objects."""
    s3_healthy = s3_service.check_health()
    buckets = []
    if s3_healthy:
        raw_buckets = s3_service.list_buckets()
        for b in raw_buckets:
            name = b.get("Name", "")
            count = s3_service.get_bucket_object_count(name)
            buckets.append({"name": name, "created": b.get("CreationDate"), "object_count": count})

    return render_template(
        "documents/cloud_s3.html",
        s3_healthy=s3_healthy,
        buckets=buckets,
    )
