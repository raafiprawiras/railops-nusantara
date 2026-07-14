"""Main blueprint — health check and index."""

from flask import Blueprint, jsonify, current_app
from sqlalchemy import text

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Landing page."""
    return jsonify({
        "message": "Selamat datang di RailOps Nusantara",
        "version": "0.1.0",
    })


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
