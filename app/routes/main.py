"""Main blueprint — dashboard, login, health check."""

from datetime import date

from flask import Blueprint, jsonify, redirect, render_template, url_for, current_app
from sqlalchemy import text

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Root redirect to dashboard."""
    return redirect(url_for("main.dashboard"))


@main_bp.route("/dashboard")
def dashboard():
    """Dashboard with static operational statistics."""
    stats = {
        "kereta_aktif": 12,
        "perjalanan_hari_ini": 35,
        "tepat_waktu": 27,
        "terlambat": 6,
        "dibatalkan": 2,
        "gangguan_aktif": 3,
        "ec2_running": 2,
        "dokumen_s3": 48,
    }

    recent_trips = [
        {"train": "Argo Bromo", "route": "Jakarta — Surabaya", "departure": "06:00", "status": "Tepat Waktu"},
        {"train": "Taksaka", "route": "Jakarta — Yogyakarta", "departure": "07:30", "status": "Terlambat"},
        {"train": "Gajayana", "route": "Jakarta — Malang", "departure": "08:15", "status": "Tepat Waktu"},
        {"train": "Sembrani", "route": "Surabaya — Jakarta", "departure": "09:00", "status": "Dibatalkan"},
        {"train": "Argo Parahyangan", "route": "Jakarta — Bandung", "departure": "10:00", "status": "Tepat Waktu"},
    ]

    recent_incidents = [
        {"location": "Stasiun Cirebon", "type": "Sinyal", "priority": "Tinggi"},
        {"location": "KM 120 Semarang", "type": "Rel", "priority": "Sedang"},
        {"location": "Stasiun Tegal", "type": "Listrik", "priority": "Rendah"},
    ]

    delay_labels = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
    delay_values = [12, 8, 15, 6, 10, 4, 7]

    return render_template(
        "dashboard.html",
        stats=stats,
        recent_trips=recent_trips,
        recent_incidents=recent_incidents,
        delay_labels=delay_labels,
        delay_values=delay_values,
    )


@main_bp.route("/login")
def login():
    """Login page (UI only, no authentication logic)."""
    return render_template("login.html")


@main_bp.route("/health")
def health():
    """Health check endpoint.

    Returns JSON with status of application, database, and LocalStack.
    Never crashes — returns degraded status if dependencies are unavailable.
    """
    result = {
        "application": "healthy",
        "database": _check_database(),
        "localstack": _check_localstack(),
    }

    if result["database"] == "healthy" and result["localstack"] == "healthy":
        result["status"] = "healthy"
    else:
        result["status"] = "degraded"

    return jsonify(result)


def _check_database() -> str:
    """Check PostgreSQL connectivity."""
    try:
        from app.extensions import db

        db.session.execute(text("SELECT 1"))
        db.session.rollback()
        return "healthy"
    except Exception:
        return "unhealthy"


def _check_localstack() -> str:
    """Check LocalStack connectivity via STS."""
    try:
        from botocore.config import Config as BotoConfig
        import boto3

        endpoint_url = current_app.config.get("AWS_ENDPOINT_URL")
        boto_config = BotoConfig(
            connect_timeout=3,
            read_timeout=3,
            retries={"max_attempts": 1},
        )
        client = boto3.client(
            "sts",
            endpoint_url=endpoint_url,
            aws_access_key_id=current_app.config.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=current_app.config.get("AWS_SECRET_ACCESS_KEY"),
            region_name=current_app.config.get("AWS_DEFAULT_REGION"),
            config=boto_config,
        )
        client.get_caller_identity()
        return "healthy"
    except Exception:
        return "unhealthy"
