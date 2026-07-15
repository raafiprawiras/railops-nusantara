"""Trip routes — CRUD, monitoring, status updates."""

from datetime import datetime, timezone, date

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models.train import Train
from app.models.station import Station
from app.models.trip import Trip, TripStatusHistory
from app.forms.trip_forms import TripForm, TripStatusForm
from app.utils.decorators import role_required

trips_bp = Blueprint("trips", __name__, url_prefix="/trips")

PER_PAGE = 10


def _populate_form_choices(form):
    """Populate select fields with train/station choices."""
    trains = Train.query.filter(Train.status == "Aktif").order_by(Train.train_name).all()
    stations = Station.query.filter(Station.operational_status == "Aktif").order_by(Station.station_name).all()

    form.train_id.choices = [(t.id, f"{t.train_code} — {t.train_name}") for t in trains]
    form.origin_station_id.choices = [(s.id, f"{s.station_code} — {s.station_name}") for s in stations]
    form.destination_station_id.choices = [(s.id, f"{s.station_code} — {s.station_name}") for s in stations]


def _populate_status_form_choices(form):
    """Populate station choices for status form."""
    stations = Station.query.order_by(Station.station_name).all()
    form.station_id.choices = [(0, "— Pilih Stasiun —")] + [
        (s.id, f"{s.station_code} — {s.station_name}") for s in stations
    ]


def _validate_train_availability(train_id: int) -> str | None:
    """Check if train is available. Returns error message or None."""
    train = db.session.get(Train, train_id)
    if not train:
        return "Kereta tidak ditemukan."
    if train.status == "Tidak Aktif":
        return "Kereta berstatus Tidak Aktif tidak dapat digunakan."
    if train.status == "Dalam Perawatan":
        return "Kereta sedang Dalam Perawatan, tidak dapat digunakan."
    if train.status == "Mengalami Gangguan":
        return "Kereta Mengalami Gangguan, tidak dapat digunakan."
    return None


def _record_status_change(trip: Trip, new_status: str, station_id: int | None,
                          delay_minutes: int, notes: str | None, user_id: int):
    """Record a status change in history and update the trip."""
    history = TripStatusHistory(
        trip_id=trip.id,
        previous_status=trip.status,
        new_status=new_status,
        station_id=station_id if station_id and station_id > 0 else None,
        delay_minutes=delay_minutes,
        notes=notes,
        changed_by=user_id,
    )
    db.session.add(history)

    trip.status = new_status
    trip.delay_minutes = delay_minutes
    if station_id and station_id > 0:
        trip.last_known_station_id = station_id

    now = datetime.now(timezone.utc)

    # Auto-fill actual times based on status
    if new_status in ("Berangkat", "Dalam Perjalanan") and not trip.actual_departure:
        trip.actual_departure = now

    if new_status == "Tiba":
        if not trip.actual_arrival:
            trip.actual_arrival = now
        if not trip.actual_departure:
            trip.actual_departure = trip.scheduled_departure


@trips_bp.route("")
@login_required
def index():
    """List trips with search, filter, pagination."""
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "", type=str).strip()
    status = request.args.get("status", "", type=str).strip()
    train_id = request.args.get("train_id", 0, type=int)
    date_filter = request.args.get("date", "", type=str).strip()

    query = Trip.query

    if search:
        query = query.filter(Trip.trip_number.ilike(f"%{search}%"))

    if status:
        query = query.filter(Trip.status == status)

    if train_id:
        query = query.filter(Trip.train_id == train_id)

    if date_filter:
        try:
            d = datetime.strptime(date_filter, "%Y-%m-%d").date()
            start = datetime(d.year, d.month, d.day, tzinfo=timezone.utc)
            end = datetime(d.year, d.month, d.day, 23, 59, 59, tzinfo=timezone.utc)
            query = query.filter(Trip.scheduled_departure.between(start, end))
        except ValueError:
            pass

    query = query.order_by(Trip.scheduled_departure.desc())
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)

    trains = Train.query.order_by(Train.train_name).all()

    return render_template(
        "trips/list.html",
        trips=pagination.items,
        pagination=pagination,
        search=search,
        status=status,
        train_id=train_id,
        date_filter=date_filter,
        status_choices=Trip.STATUS_CHOICES,
        trains=trains,
    )


@trips_bp.route("/create", methods=["GET", "POST"])
@login_required
@role_required("administrator", "operator")
def create():
    """Create a new trip."""
    form = TripForm()
    _populate_form_choices(form)

    if form.validate_on_submit():
        # Check unique trip number
        existing = Trip.query.filter_by(trip_number=form.trip_number.data.strip()).first()
        if existing:
            flash("Nomor perjalanan sudah digunakan.", "danger")
            return render_template("trips/form.html", form=form, title="Tambah Jadwal")

        # Validate train availability
        error = _validate_train_availability(form.train_id.data)
        if error:
            flash(error, "danger")
            return render_template("trips/form.html", form=form, title="Tambah Jadwal")

        trip = Trip(
            trip_number=form.trip_number.data.strip(),
            train_id=form.train_id.data,
            origin_station_id=form.origin_station_id.data,
            destination_station_id=form.destination_station_id.data,
            scheduled_departure=form.scheduled_departure.data,
            scheduled_arrival=form.scheduled_arrival.data,
            platform=form.platform.data,
            status=form.status.data,
            notes=form.notes.data,
            created_by=current_user.id,
        )
        db.session.add(trip)
        db.session.flush()

        # Record initial status
        history = TripStatusHistory(
            trip_id=trip.id,
            previous_status=None,
            new_status=trip.status,
            changed_by=current_user.id,
            notes="Jadwal dibuat",
        )
        db.session.add(history)
        db.session.commit()

        flash("Jadwal perjalanan berhasil ditambahkan.", "success")
        return redirect(url_for("trips.index"))

    return render_template("trips/form.html", form=form, title="Tambah Jadwal")


@trips_bp.route("/<int:id>")
@login_required
def detail(id):
    """Show trip detail with status history timeline."""
    trip = db.session.get(Trip, id) or abort(404)
    history = TripStatusHistory.query.filter_by(trip_id=trip.id).order_by(
        TripStatusHistory.created_at.desc()
    ).all()
    return render_template("trips/detail.html", trip=trip, history=history)


@trips_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
@role_required("administrator", "operator")
def edit(id):
    """Edit an existing trip."""
    trip = db.session.get(Trip, id) or abort(404)
    form = TripForm(obj=trip)
    _populate_form_choices(form)

    if form.validate_on_submit():
        # Check unique trip_number (exclude self)
        existing = Trip.query.filter(
            Trip.trip_number == form.trip_number.data.strip(),
            Trip.id != trip.id,
        ).first()
        if existing:
            flash("Nomor perjalanan sudah digunakan.", "danger")
            return render_template("trips/form.html", form=form, title="Edit Jadwal", trip=trip)

        error = _validate_train_availability(form.train_id.data)
        if error:
            flash(error, "danger")
            return render_template("trips/form.html", form=form, title="Edit Jadwal", trip=trip)

        old_status = trip.status
        trip.trip_number = form.trip_number.data.strip()
        trip.train_id = form.train_id.data
        trip.origin_station_id = form.origin_station_id.data
        trip.destination_station_id = form.destination_station_id.data
        trip.scheduled_departure = form.scheduled_departure.data
        trip.scheduled_arrival = form.scheduled_arrival.data
        trip.platform = form.platform.data
        trip.notes = form.notes.data

        # If status changed via edit, record it
        if form.status.data != old_status:
            _record_status_change(
                trip, form.status.data, None, trip.delay_minutes,
                "Status diubah melalui edit", current_user.id,
            )
        else:
            trip.status = form.status.data

        db.session.commit()
        flash("Jadwal perjalanan berhasil diperbarui.", "success")
        return redirect(url_for("trips.detail", id=trip.id))

    return render_template("trips/form.html", form=form, title="Edit Jadwal", trip=trip)


@trips_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
@role_required("administrator")
def delete(id):
    """Delete a trip."""
    trip = db.session.get(Trip, id) or abort(404)
    TripStatusHistory.query.filter_by(trip_id=trip.id).delete()
    db.session.delete(trip)
    db.session.commit()
    flash(f"Jadwal {trip.trip_number} berhasil dihapus.", "success")
    return redirect(url_for("trips.index"))


@trips_bp.route("/<int:id>/status", methods=["POST"])
@login_required
@role_required("administrator", "operator")
def update_status(id):
    """Update trip status with history tracking."""
    trip = db.session.get(Trip, id) or abort(404)
    form = TripStatusForm()
    _populate_status_form_choices(form)

    if form.validate_on_submit():
        new_status = form.new_status.data
        notes = form.notes.data
        delay = form.delay_minutes.data or 0
        station_id = form.station_id.data

        # Validate: Dibatalkan requires notes
        if new_status == "Dibatalkan" and not notes:
            flash("Status Dibatalkan memerlukan catatan alasan.", "danger")
            return redirect(url_for("trips.detail", id=trip.id))

        _record_status_change(trip, new_status, station_id, delay, notes, current_user.id)

        if notes:
            trip.notes = notes

        db.session.commit()
        flash(f"Status berhasil diubah menjadi {new_status}.", "success")
    else:
        flash("Data tidak valid.", "danger")

    return redirect(url_for("trips.detail", id=trip.id))


# --- Monitoring View ---

@trips_bp.route("/monitoring")
@login_required
def monitoring():
    """Monitoring view for active trips."""
    active_statuses = ["Persiapan", "Berangkat", "Dalam Perjalanan", "Terlambat"]
    trips = Trip.query.filter(Trip.status.in_(active_statuses)).order_by(
        Trip.scheduled_departure.asc()
    ).all()

    status_form = TripStatusForm()
    _populate_status_form_choices(status_form)

    return render_template(
        "trips/monitoring.html",
        trips=trips,
        status_form=status_form,
    )
