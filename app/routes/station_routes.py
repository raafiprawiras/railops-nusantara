"""Station routes — CRUD with search, filter, pagination."""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required

from app.extensions import db
from app.models.station import Station
from app.forms.station_forms import StationForm
from app.utils.decorators import role_required

stations_bp = Blueprint("stations", __name__, url_prefix="/stations")

PER_PAGE = 10


@stations_bp.route("")
@login_required
def index():
    """List stations with search, filter, pagination."""
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "", type=str).strip()
    status = request.args.get("status", "", type=str).strip()

    query = Station.query

    if search:
        query = query.filter(
            db.or_(
                Station.station_code.ilike(f"%{search}%"),
                Station.station_name.ilike(f"%{search}%"),
                Station.city.ilike(f"%{search}%"),
            )
        )

    if status:
        query = query.filter(Station.operational_status == status)

    query = query.order_by(Station.station_code.asc())
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)

    return render_template(
        "stations/list.html",
        stations=pagination.items,
        pagination=pagination,
        search=search,
        status=status,
        status_choices=Station.STATUS_CHOICES,
    )


@stations_bp.route("/create", methods=["GET", "POST"])
@login_required
@role_required("administrator")
def create():
    """Create a new station."""
    form = StationForm()

    if form.validate_on_submit():
        existing = Station.query.filter_by(station_code=form.station_code.data.strip()).first()
        if existing:
            flash("Kode stasiun sudah digunakan.", "danger")
            return render_template("stations/form.html", form=form, title="Tambah Stasiun")

        station = Station(
            station_code=form.station_code.data.strip(),
            station_name=form.station_name.data.strip(),
            city=form.city.data.strip(),
            province=form.province.data.strip(),
            platform_count=form.platform_count.data,
            operational_status=form.operational_status.data,
        )
        db.session.add(station)
        db.session.commit()
        flash("Stasiun berhasil ditambahkan.", "success")
        return redirect(url_for("stations.index"))

    return render_template("stations/form.html", form=form, title="Tambah Stasiun")


@stations_bp.route("/<int:id>")
@login_required
def detail(id):
    """Show station detail."""
    station = db.session.get(Station, id) or abort(404)
    return render_template("stations/detail.html", station=station)


@stations_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
@role_required("administrator")
def edit(id):
    """Edit an existing station."""
    station = db.session.get(Station, id) or abort(404)
    form = StationForm(obj=station)

    if form.validate_on_submit():
        existing = Station.query.filter(
            Station.station_code == form.station_code.data.strip(),
            Station.id != station.id,
        ).first()
        if existing:
            flash("Kode stasiun sudah digunakan.", "danger")
            return render_template("stations/form.html", form=form, title="Edit Stasiun", station=station)

        station.station_code = form.station_code.data.strip()
        station.station_name = form.station_name.data.strip()
        station.city = form.city.data.strip()
        station.province = form.province.data.strip()
        station.platform_count = form.platform_count.data
        station.operational_status = form.operational_status.data
        db.session.commit()
        flash("Stasiun berhasil diperbarui.", "success")
        return redirect(url_for("stations.detail", id=station.id))

    return render_template("stations/form.html", form=form, title="Edit Stasiun", station=station)


@stations_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
@role_required("administrator")
def delete(id):
    """Delete a station."""
    station = db.session.get(Station, id) or abort(404)
    db.session.delete(station)
    db.session.commit()
    flash(f"Stasiun {station.station_name} berhasil dihapus.", "success")
    return redirect(url_for("stations.index"))
