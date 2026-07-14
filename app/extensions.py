"""Flask extensions instantiation.

Extensions are created here without binding to a specific app instance,
following the application factory pattern.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
