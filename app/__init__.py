"""Flask application factory."""

import os

from flask import Flask

from config import config_by_name, Config


def create_app(config_class: type[Config] | None = None) -> Flask:
    """Create and configure the Flask application.

    Args:
        config_class: Configuration class to use. Defaults to environment-based selection.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)

    # Load configuration
    if config_class is None:
        env = os.environ.get("FLASK_ENV", "development")
        config_class = config_by_name.get(env, config_by_name["development"])

    app.config.from_object(config_class)

    # Initialize extensions
    _register_extensions(app)

    # Register blueprints
    _register_blueprints(app)

    return app


def _register_extensions(app: Flask) -> None:
    """Initialize Flask extensions."""
    from app.extensions import db, migrate, login_manager

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Silakan login untuk mengakses halaman ini."
    login_manager.login_message_category = "warning"


def _register_blueprints(app: Flask) -> None:
    """Register all application blueprints."""
    from app.routes import register_blueprints

    register_blueprints(app)
