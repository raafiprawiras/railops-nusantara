"""Profile routes — view and edit own profile, change password."""

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.forms.user_forms import ProfileEditForm, ChangePasswordForm

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.route("")
@login_required
def index():
    """View own profile."""
    return render_template("profile/index.html")


@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    """Edit own name."""
    form = ProfileEditForm(obj=current_user)

    if form.validate_on_submit():
        current_user.full_name = form.full_name.data.strip()
        db.session.commit()
        flash("Profil berhasil diperbarui.", "success")
        return redirect(url_for("profile.index"))

    return render_template("profile/edit.html", form=form)


@profile_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change own password."""
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if not current_user.check_password(form.old_password.data):
            flash("Password lama salah.", "danger")
            return render_template("profile/change_password.html", form=form)

        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash("Password berhasil diganti.", "success")
        return redirect(url_for("profile.index"))

    return render_template("profile/change_password.html", form=form)
