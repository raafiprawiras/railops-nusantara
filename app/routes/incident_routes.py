"""Incident routes — CRUD, status updates, timeline."""

from datetime import datetime, timezone

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models.trip import Trip
from app.models.user import User
from app.models.incident import Incident, IncidentStatusHistory
from app.forms.incident_forms import IncidentForm, IncidentStatusForm
from app.utils.decorators import role_required

incidents_bp = Blueprint("incidents", __name__, url_prefix="/incidents")

PER_PAGE = 10


def _populate_form_choices(form):
    """Populate select fields."""
    trips = Trip.query.order_by(Trip.trip_number.desc()).all()
    form.trip_id.choices = [(t.id, f"{t.trip_number} — {t.route_display}") for t in trips]

    operators = User.query.filter(
        User.is_active == True,
        User.role.in_([User.ROLE_ADMINISTRATOR, User.ROLE_OPERATOR]),
    ).order_by(User.full_name).all()
    form.assigned_to.choices = [(0, "— Belum Ditugaskan —")] + [
        (u.id, u.full_name) for u in operators
    ]


@incidents_bp.route("")
@login_required
def index():
    """List incidents with filters and pagination."""
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "", type=str).strip()
    status = request.args.get("status", "", type=str).strip()
    priority = request.args.get("priority", "", type=str).strip()
    incident_type = request.args.get("type", "", type=str).strip()

    query = Incident.query

    if search:
        query = query.filter(Incident.incident_number.ilike(f"%{search}%"))
    if status:
        query = query.filter(Incident.status == status)
    if priority:
        query = query.filter(Incident.priority == priority)
    if incident_type:
        query = query.filter(Incident.incident_type == incident_type)

    query = query.order_by(Incident.created_at.desc())
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)

    return render_template(
        "incidents/list.html",
        incidents=pagination.items,
        pagination=pagination,
        search=search,
        status=status,
        priority=priority,
        incident_type=incident_type,
        status_choices=Incident.STATUS_CHOICES,
        priority_choices=Incident.PRIORITY_CHOICES,
        type_choices=Incident.TYPE_CHOICES,
    )


@incidents_bp.route("/create", methods=["GET", "POST"])
@login_required
@role_required("administrator", "operator")
def create():
    """Create a new incident."""
    form = IncidentForm()
    _populate_form_choices(form)

    if form.validate_on_submit():
        existing = Incident.query.filter_by(incident_number=form.incident_number.data.strip()).first()
        if existing:
            flash("Nomor gangguan sudah digunakan.", "danger")
            return render_template("incidents/form.html", form=form, title="Lapor Gangguan")

        assigned = form.assigned_to.data if form.assigned_to.data and form.assigned_to.data > 0 else None

        incident = Incident(
            incident_number=form.incident_number.data.strip(),
            trip_id=form.trip_id.data,
            incident_type=form.incident_type.data,
            location=form.location.data.strip(),
            occurred_at=form.occurred_at.data,
            priority=form.priority.data,
            description=form.description.data.strip(),
            status="Dilaporkan",
            reported_by=current_user.id,
            assigned_to=assigned,
        )
        db.session.add(incident)
        db.session.flush()

        history = IncidentStatusHistory(
            incident_id=incident.id,
            previous_status=None,
            new_status="Dilaporkan",
            notes="Laporan gangguan dibuat",
            changed_by=current_user.id,
        )
        db.session.add(history)
        db.session.commit()

        flash("Laporan gangguan berhasil dibuat.", "success")
        return redirect(url_for("incidents.index"))

    return render_template("incidents/form.html", form=form, title="Lapor Gangguan")


@incidents_bp.route("/<int:id>")
@login_required
def detail(id):
    """Show incident detail with status timeline."""
    incident = db.session.get(Incident, id) or abort(404)
    history = IncidentStatusHistory.query.filter_by(incident_id=incident.id).order_by(
        IncidentStatusHistory.created_at.desc()
    ).all()

    status_form = IncidentStatusForm()

    return render_template("incidents/detail.html", incident=incident, history=history, status_form=status_form)


@incidents_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
@role_required("administrator", "operator")
def edit(id):
    """Edit an existing incident."""
    incident = db.session.get(Incident, id) or abort(404)
    form = IncidentForm(obj=incident)
    _populate_form_choices(form)

    if form.validate_on_submit():
        existing = Incident.query.filter(
            Incident.incident_number == form.incident_number.data.strip(),
            Incident.id != incident.id,
        ).first()
        if existing:
            flash("Nomor gangguan sudah digunakan.", "danger")
            return render_template("incidents/form.html", form=form, title="Edit Gangguan", incident=incident)

        incident.incident_number = form.incident_number.data.strip()
        incident.trip_id = form.trip_id.data
        incident.incident_type = form.incident_type.data
        incident.location = form.location.data.strip()
        incident.occurred_at = form.occurred_at.data
        incident.priority = form.priority.data
        incident.description = form.description.data.strip()
        incident.assigned_to = form.assigned_to.data if form.assigned_to.data and form.assigned_to.data > 0 else None

        db.session.commit()
        flash("Laporan gangguan berhasil diperbarui.", "success")
        return redirect(url_for("incidents.detail", id=incident.id))

    return render_template("incidents/form.html", form=form, title="Edit Gangguan", incident=incident)


@incidents_bp.route("/<int:id>/status", methods=["POST"])
@login_required
def update_status(id):
    """Update incident status with transition validation."""
    incident = db.session.get(Incident, id) or abort(404)
    form = IncidentStatusForm()

    if not form.validate_on_submit():
        flash("Data tidak valid.", "danger")
        return redirect(url_for("incidents.detail", id=incident.id))

    new_status = form.new_status.data
    notes = form.notes.data
    resolution_notes = form.resolution_notes.data

    # Check role authorization for specific transitions
    if new_status == "Ditutup" and current_user.role not in ("administrator", "supervisor"):
        flash("Hanya administrator atau supervisor yang dapat menutup laporan.", "danger")
        return redirect(url_for("incidents.detail", id=incident.id))

    if new_status != "Ditutup" and current_user.role == "supervisor":
        flash("Supervisor hanya dapat menutup laporan yang sudah selesai.", "danger")
        return redirect(url_for("incidents.detail", id=incident.id))

    # Validate transition
    if not incident.can_transition_to(new_status):
        flash(
            f"Perubahan status dari '{incident.status}' ke '{new_status}' tidak diizinkan.",
            "danger",
        )
        return redirect(url_for("incidents.detail", id=incident.id))

    # Selesai requires resolution_notes
    if new_status == "Selesai" and not resolution_notes:
        flash("Catatan penyelesaian wajib diisi untuk status Selesai.", "danger")
        return redirect(url_for("incidents.detail", id=incident.id))

    # Record history
    history = IncidentStatusHistory(
        incident_id=incident.id,
        previous_status=incident.status,
        new_status=new_status,
        notes=notes or resolution_notes,
        changed_by=current_user.id,
    )
    db.session.add(history)

    # Update incident
    incident.status = new_status
    if new_status == "Selesai":
        incident.resolved_at = datetime.now(timezone.utc)
        incident.resolution_notes = resolution_notes

    db.session.commit()
    flash(f"Status berhasil diubah menjadi {new_status}.", "success")
    return redirect(url_for("incidents.detail", id=incident.id))
