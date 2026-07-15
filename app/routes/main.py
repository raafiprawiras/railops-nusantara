"""Main blueprint — dashboard, health check."""

from datetime import datetime, timezone

from flask import Blueprint, jsonify, redirect, render_template, url_for, current_app
from flask_login import login_required
from sqlalchemy import text, func

from app.extensions import db

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Root redirect to dashboard."""
    return redirect(url_for("main.dashboard"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Dashboard with operational statistics from database."""
    from app.models.train import Train
    from app.models.trip import Trip

    # Counts from database
    kereta_aktif = Train.query.filter_by(status="Aktif").count()

    today = datetime.now(timezone.utc).date()
    today_start = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)
    today_end = datetime(today.year, today.month, today.day, 23, 59, 59, tzinfo=timezone.utc)

    trips_today_query = Trip.query.filter(
        Trip.scheduled_departure.between(today_start, today_end)
    )
    perjalanan_hari_ini = trips_today_query.count()
    tepat_waktu = trips_today_query.filter(Trip.status == "Tiba", Trip.delay_minutes == 0).count()
    terlambat = trips_today_query.filter(
        Trip.status.in_(["Terlambat", "Tiba"]), Trip.delay_minutes > 0
    ).count()
    dibatalkan = trips_today_query.filter(Trip.status == "Dibatalkan").count()

    gangguan_aktif = Train.query.filter_by(status="Mengalami Gangguan").count()

    stats = {
        "kereta_aktif": kereta_aktif,
        "perjalanan_hari_ini": perjalanan_hari_ini,
        "tepat_waktu": tepat_waktu,
        "terlambat": terlambat,
        "dibatalkan": dibatalkan,
        "gangguan_aktif": gangguan_aktif,
        "ec2_running": 2,
        "dokumen_s3": 48,
    }

    # Recent trips (last 5)
    recent_trips_db = Trip.query.order_by(Trip.scheduled_departure.desc()).limit(5).all()
    recent_trips = []
    for t in recent_trips_db:
        if t.status == "Tiba" and t.delay_minutes == 0:
            display_status = "Tepat Waktu"
        elif t.delay_minutes > 0:
            display_status = "Terlambat"
        elif t.status == "Dibatalkan":
            display_status = "Dibatalkan"
        else:
            display_status = t.status
        recent_trips.append({
            "train": t.train.train_name if t.train else "?",
            "route": t.route_display,
            "departure": t.scheduled_departure.strftime("%H:%M") if t.scheduled_departure else "-",
            "status": display_status,
        })

    # Fallback static data if no trips exist
    if not recent_trips:
        recent_trips = [
            {"train": "Argo Bromo", "route": "Jakarta — Surabaya", "departure": "06:00", "status": "Tepat Waktu"},
            {"train": "Taksaka", "route": "Jakarta — Yogyakarta", "departure": "07:30", "status": "Terlambat"},
            {"train": "Gajayana", "route": "Jakarta — Malang", "departure": "08:15", "status": "Tepat Waktu"},
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


@main_bp.route("/health")
def health():
    """Health check endpoint."""
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
