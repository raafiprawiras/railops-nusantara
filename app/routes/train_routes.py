"""Train routes — CRUD with search, filter, pagination."""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required

from app.extensions import db
from app.models.train import Train
from app.forms.train_forms import TrainForm
from app.utils.decorators import role_required

trains_bp = Blueprint("trains", __name__, url_prefix="/trains")

PER_PAGE = 10


@trains_bp.route("")
@login_required
def index():
    """List trains with search, filter, pagination."""
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "", type=str).strip()
    status = request.args.get("status", "", type=str).strip()

    query = Train.query

    if search:
        query = query.filter(
            db.or_(
                Train.train_code.ilike(f"%{search}%"),
                Train.train_name.ilike(f"%{search}%"),
            )
        )

    if status:
        query = query.filter(Train.status == status)

    query = query.order_by(Train.train_code.asc())
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)

    return render_template(
        "trains/list.html",
        trains=pagination.items,
        pagination=pagination,
        search=search,
        status=status,
        status_choices=Train.STATUS_CHOICES,
    )


@trains_bp.route("/create", methods=["GET", "POST"])
@login_required
@role_required("administrator")
def create():
    """Create a new train."""
    form = TrainForm()

    if form.validate_on_submit():
        existing = Train.query.filter_by(train_code=form.train_code.data.strip()).first()
        if existing:
            flash("Kode kereta sudah digunakan.", "danger")
            return render_template("trains/form.html", form=form, title="Tambah Kereta")

        train = Train(
            train_code=form.train_code.data.strip(),
            train_name=form.train_name.data.strip(),
            train_type=form.train_type.data,
            capacity=form.capacity.data,
            carriage_number=form.carriage_number.data,
            status=form.status.data,
            last_maintenance_date=form.last_maintenance_date.data,
        )
        db.session.add(train)
        db.session.commit()
        flash("Kereta berhasil ditambahkan.", "success")
        return redirect(url_for("trains.index"))

    return render_template("trains/form.html", form=form, title="Tambah Kereta")


@trains_bp.route("/<int:id>")
@login_required
def detail(id):
    """Show train detail."""
    train = db.session.get(Train, id) or abort(404)
    return render_template("trains/detail.html", train=train)


@trains_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
@role_required("administrator")
def edit(id):
    """Edit an existing train."""
    train = db.session.get(Train, id) or abort(404)
    form = TrainForm(obj=train)

    if form.validate_on_submit():
        # Check unique code (exclude self)
        existing = Train.query.filter(
            Train.train_code == form.train_code.data.strip(),
            Train.id != train.id,
        ).first()
        if existing:
            flash("Kode kereta sudah digunakan.", "danger")
            return render_template("trains/form.html", form=form, title="Edit Kereta", train=train)

        train.train_code = form.train_code.data.strip()
        train.train_name = form.train_name.data.strip()
        train.train_type = form.train_type.data
        train.capacity = form.capacity.data
        train.carriage_number = form.carriage_number.data
        train.status = form.status.data
        train.last_maintenance_date = form.last_maintenance_date.data
        db.session.commit()
        flash("Kereta berhasil diperbarui.", "success")
        return redirect(url_for("trains.detail", id=train.id))

    return render_template("trains/form.html", form=form, title="Edit Kereta", train=train)


@trains_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
@role_required("administrator")
def delete(id):
    """Delete a train."""
    train = db.session.get(Train, id) or abort(404)
    db.session.delete(train)
    db.session.commit()
    flash(f"Kereta {train.train_name} berhasil dihapus.", "success")
    return redirect(url_for("trains.index"))
