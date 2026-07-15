"""Main blueprint — dashboard, health check."""

from flask import Blueprint, jsonify, redirect, render_template, url_for, current_app
from flask_login import login_required
from sqlalchemy import text

from app.extensions import db

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Root redirect to dashboard."""
    return redirect(url_for("main.dashboard"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Dashboard with real operational statistics from database."""
    from app.services import dashboard_service

    stats = dashboard_service.get_dashboard_stats()
    chart_data = dashboard_service.get_trip_chart_data()
    incident_priority = dashboard_service.get_incident_priority_stats()
    recent_trips = dashboard_service.get_recent_trips(5)
    recent_incidents = dashboard_service.get_recent_incidents(5)
    recent_audit = dashboard_service.get_recent_audit_logs(5)

    return render_template(
        "dashboard.html",
        stats=stats,
        recent_trips=recent_trips,
        recent_incidents=recent_incidents,
        recent_audit=recent_audit,
        chart_data=chart_data,
        incident_priority=incident_priority,
        delay_labels=chart_data["delay_labels"],
        delay_values=chart_data["delay_values"],
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
