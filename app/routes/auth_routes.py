"""Authentication routes — login, logout."""

from datetime import datetime, timezone
from urllib.parse import urlparse

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user, login_required

from app.extensions import db
from app.forms.auth_forms import LoginForm
from app.models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    # Already logged in → redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()

        if user is None or not user.check_password(form.password.data):
            flash("Email atau password salah.", "danger")
            return render_template("login.html", form=form)

        if not user.is_active:
            flash("Akun Anda tidak aktif. Hubungi administrator.", "warning")
            return render_template("login.html", form=form)

        # Login successful
        login_user(user, remember=form.remember.data)

        # Update last_login_at
        user.last_login_at = datetime.now(timezone.utc)
        db.session.commit()

        flash(f"Selamat datang, {user.full_name}!", "success")

        # Safe redirect (prevent open redirect)
        next_page = request.args.get("next")
        if next_page and _is_safe_url(next_page):
            return redirect(next_page)

        return redirect(url_for("main.dashboard"))

    return render_template("login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash("Anda telah berhasil keluar.", "info")
    return redirect(url_for("auth.login"))


def _is_safe_url(target: str) -> bool:
    """Validate redirect URL to prevent open redirect attacks."""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(target)
    # Allow relative URLs and same-host URLs only
    return test_url.scheme in ("", "http", "https") and ref_url.netloc == (test_url.netloc or ref_url.netloc)
