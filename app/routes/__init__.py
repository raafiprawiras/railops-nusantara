"""Blueprint registration."""

from flask import Flask


def register_blueprints(app: Flask) -> None:
    """Register all application blueprints."""
    from app.routes.main import main_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.train_routes import trains_bp
    from app.routes.station_routes import stations_bp
    from app.routes.trip_routes import trips_bp
    from app.routes.incident_routes import incidents_bp
    from app.routes.document_routes import documents_bp
    from app.routes.ec2_routes import ec2_bp
    from app.routes.report_routes import reports_bp
    from app.routes.user_routes import users_bp
    from app.routes.profile_routes import profile_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(trains_bp)
    app.register_blueprint(stations_bp)
    app.register_blueprint(trips_bp)
    app.register_blueprint(incidents_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(ec2_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(profile_bp)
