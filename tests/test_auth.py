"""Tests for authentication and role management."""

from app.models.user import User


def test_login_correct_credentials(client, active_user):
    """Login with correct credentials should redirect to dashboard."""
    response = client.post("/login", data={
        "email": "test@railops.local",
        "password": "TestPass123!",
    }, follow_redirects=False)

    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]


def test_login_wrong_password(client, active_user):
    """Login with wrong password should show error."""
    response = client.post("/login", data={
        "email": "test@railops.local",
        "password": "WrongPassword!",
    }, follow_redirects=True)

    assert response.status_code == 200
    assert "Email atau password salah" in response.data.decode()


def test_login_nonexistent_user(client):
    """Login with non-existent email should show error."""
    response = client.post("/login", data={
        "email": "noone@railops.local",
        "password": "Whatever123!",
    }, follow_redirects=True)

    assert response.status_code == 200
    assert "Email atau password salah" in response.data.decode()


def test_inactive_user_cannot_login(client, inactive_user):
    """Inactive user should not be able to login."""
    response = client.post("/login", data={
        "email": "inactive@railops.local",
        "password": "Inactive123!",
    }, follow_redirects=True)

    assert response.status_code == 200
    assert "tidak aktif" in response.data.decode()


def test_dashboard_requires_login(client):
    """Dashboard without login should redirect to login page."""
    response = client.get("/dashboard", follow_redirects=False)

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_logout(logged_in_client):
    """Logout should redirect to login."""
    response = logged_in_client.post("/logout", follow_redirects=False)

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

    # Verify dashboard is no longer accessible
    response = logged_in_client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_password_stored_as_hash(app, db):
    """Password should be stored as hash, not plain text."""
    user = User(
        full_name="Hash Test",
        email="hash@railops.local",
        role=User.ROLE_OPERATOR,
        is_active=True,
    )
    user.set_password("MyPlainPassword!")
    db.session.add(user)
    db.session.commit()

    assert user.password_hash != "MyPlainPassword!"
    assert user.password_hash.startswith("scrypt:") or user.password_hash.startswith("pbkdf2:")
    assert user.check_password("MyPlainPassword!")
    assert not user.check_password("WrongPassword!")


def test_role_decorator_rejects_wrong_role(client, active_user, app):
    """Role decorator should return 403 for unauthorized role."""
    from app.utils.decorators import role_required
    from flask import Blueprint
    from flask_login import login_required

    # Create a test-only route with role restriction
    test_bp = Blueprint("test_role", __name__)

    @test_bp.route("/test-admin-only")
    @login_required
    @role_required("administrator")
    def admin_only():
        return "OK"

    app.register_blueprint(test_bp)

    # Login as operator
    client.post("/login", data={
        "email": "test@railops.local",
        "password": "TestPass123!",
    })

    # Try to access admin-only route
    response = client.get("/test-admin-only")
    assert response.status_code == 403


def test_login_page_redirects_if_authenticated(logged_in_client):
    """Already authenticated user should be redirected from login page."""
    response = logged_in_client.get("/login", follow_redirects=False)

    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]


def test_login_updates_last_login(client, active_user, db):
    """Successful login should update last_login_at."""
    assert active_user.last_login_at is None

    client.post("/login", data={
        "email": "test@railops.local",
        "password": "TestPass123!",
    })

    db.session.refresh(active_user)
    assert active_user.last_login_at is not None
