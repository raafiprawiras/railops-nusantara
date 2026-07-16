"""Flask application factory."""

import os
from datetime import date

from flask import Flask, render_template

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

    # Validate production config
    if hasattr(config_class, "validate"):
        config_class.validate()

    app.config.from_object(config_class)

    # Initialize extensions
    _register_extensions(app)

    # Register blueprints
    _register_blueprints(app)

    # Register error handlers
    _register_error_handlers(app)

    # Context processors
    _register_context_processors(app)

    # CLI commands
    _register_commands(app)

    return app


def _register_extensions(app: Flask) -> None:
    """Initialize Flask extensions."""
    from app.extensions import db, migrate, login_manager, csrf
    from app.models.user import User

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Silakan login untuk mengakses halaman ini."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id: str):
        """Load user by ID from database."""
        return db.session.get(User, int(user_id))


def _register_blueprints(app: Flask) -> None:
    """Register all application blueprints."""
    from app.routes import register_blueprints

    register_blueprints(app)


def _register_error_handlers(app: Flask) -> None:
    """Register custom error pages."""

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("errors/500.html"), 500


def _register_context_processors(app: Flask) -> None:
    """Register Jinja2 context processors."""

    @app.context_processor
    def inject_globals():
        today = date.today()
        return {
            "current_date": today.strftime("%A, %d %B %Y"),
        }


def _register_commands(app: Flask) -> None:
    """Register custom CLI commands."""
    from app.commands import register_commands

    register_commands(app)
