"""Blueprint registration."""

from flask import Flask


def register_blueprints(app: Flask) -> None:
    """Register all application blueprints."""
    from app.routes.main import main_bp

    app.register_blueprint(main_bp)
