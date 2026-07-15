"""User administration routes — admin only."""

import json
import secrets
from datetime import datetime, timezone

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models.user import User
from app.models.infrastructure import AuditLog
from app.forms.user_forms import UserCreateForm, UserEditForm
from app.utils.decorators import role_required

users_bp = Blueprint("users", __name__, url_prefix="/users")

PER_PAGE = 10


def _audit(action: str, resource_id: str, description: str):
    """Record audit log."""
    log = AuditLog(
        user_id=current_user.id,
        action=action,
        resource_type="user",
        resource_id=resource_id,
        description=description,
    )
    db.session.add(log)


@users_bp.route("")
@login_required
@role_required("administrator")
def index():
    """List users with search, filter, pagination."""
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "", type=str).strip()
    role = request.args.get("role", "", type=str).strip()
    status = request.args.get("status", "", type=str).strip()

    query = User.query

    if search:
        query = query.filter(
            db.or_(
                User.full_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
            )
        )
    if role:
        query = query.filter(User.role == role)
    if status == "active":
        query = query.filter(User.is_active == True)
    elif status == "inactive":
        query = query.filter(User.is_active == False)

    query = query.order_by(User.full_name.asc())
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)

    return render_template(
        "users/list.html",
        users=pagination.items,
        pagination=pagination,
        search=search,
        role=role,
        status=status,
        role_choices=User.VALID_ROLES,
    )


@users_bp.route("/create", methods=["GET", "POST"])
@login_required
@role_required("administrator")
def create():
    """Create a new user."""
    form = UserCreateForm()

    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if existing:
            flash("Email sudah terdaftar.", "danger")
            return render_template("users/form.html", form=form, title="Tambah Pengguna")

        user = User(
            full_name=form.full_name.data.strip(),
            email=form.email.data.strip().lower(),
            role=form.role.data,
            is_active=True,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()
        _audit("create_user", str(user.id), f"User {user.email} dibuat dengan role {user.role}.")
        db.session.commit()

        flash(f"Pengguna {user.full_name} berhasil ditambahkan.", "success")
        return redirect(url_for("users.index"))

    return render_template("users/form.html", form=form, title="Tambah Pengguna")


@users_bp.route("/<int:id>")
@login_required
@role_required("administrator")
def detail(id):
    """Show user detail."""
    user = db.session.get(User, id) or abort(404)
    return render_template("users/detail.html", user=user)


@users_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
@role_required("administrator")
def edit(id):
    """Edit user details."""
    user = db.session.get(User, id) or abort(404)
    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        # Check unique email
        existing = User.query.filter(
            User.email == form.email.data.strip().lower(),
            User.id != user.id,
        ).first()
        if existing:
            flash("Email sudah terdaftar oleh pengguna lain.", "danger")
            return render_template("users/edit.html", form=form, user=user)

        user.full_name = form.full_name.data.strip()
        user.email = form.email.data.strip().lower()
        user.role = form.role.data
        _audit("edit_user", str(user.id), f"User {user.email} diperbarui.")
        db.session.commit()

        flash("Data pengguna berhasil diperbarui.", "success")
        return redirect(url_for("users.detail", id=user.id))

    return render_template("users/edit.html", form=form, user=user)


@users_bp.route("/<int:id>/toggle-status", methods=["POST"])
@login_required
@role_required("administrator")
def toggle_status(id):
    """Activate or deactivate a user."""
    user = db.session.get(User, id) or abort(404)

    # Cannot deactivate self
    if user.id == current_user.id:
        flash("Anda tidak dapat menonaktifkan akun sendiri.", "danger")
        return redirect(url_for("users.detail", id=user.id))

    # Cannot deactivate last active admin
    if user.is_active and user.role == User.ROLE_ADMINISTRATOR:
        active_admins = User.query.filter_by(role=User.ROLE_ADMINISTRATOR, is_active=True).count()
        if active_admins <= 1:
            flash("Tidak dapat menonaktifkan administrator terakhir yang aktif.", "danger")
            return redirect(url_for("users.detail", id=user.id))

    user.is_active = not user.is_active
    action = "activate_user" if user.is_active else "deactivate_user"
    status_text = "diaktifkan" if user.is_active else "dinonaktifkan"
    _audit(action, str(user.id), f"User {user.email} {status_text}.")
    db.session.commit()

    flash(f"Pengguna {user.full_name} berhasil {status_text}.", "success")
    return redirect(url_for("users.detail", id=user.id))


@users_bp.route("/<int:id>/reset-password", methods=["POST"])
@login_required
@role_required("administrator")
def reset_password(id):
    """Reset user password to a temporary random password."""
    user = db.session.get(User, id) or abort(404)

    # Generate secure temporary password
    temp_password = secrets.token_urlsafe(12)
    user.set_password(temp_password)
    _audit("reset_password", str(user.id), f"Password user {user.email} di-reset oleh admin.")
    db.session.commit()

    # Flash the temp password once (development only approach)
    flash(
        f"Password {user.full_name} telah di-reset. Password sementara: {temp_password} "
        f"— Berikan kepada pengguna secara aman.",
        "warning",
    )
    return redirect(url_for("users.detail", id=user.id))
