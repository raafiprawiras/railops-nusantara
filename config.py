"""Application configuration loaded from environment variables."""

import os


class Config:
    """Base configuration."""

    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL", "postgresql://railops:railops_secret@localhost:5432/railops_nusantara"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # AWS / LocalStack
    AWS_ACCESS_KEY_ID: str = os.environ.get("AWS_ACCESS_KEY_ID", "test")
    AWS_SECRET_ACCESS_KEY: str = os.environ.get("AWS_SECRET_ACCESS_KEY", "test")
    AWS_DEFAULT_REGION: str = os.environ.get("AWS_DEFAULT_REGION", "ap-southeast-1")
    AWS_ENDPOINT_URL: str = os.environ.get("AWS_ENDPOINT_URL", "http://localhost:4566")

    # S3
    S3_BUCKET_NAME: str = os.environ.get("S3_BUCKET_NAME", "railops-bucket")

    # Upload
    MAX_CONTENT_LENGTH: int = int(os.environ.get("MAX_CONTENT_LENGTH", 16777216))


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG: bool = True


class TestingConfig(Config):
    """Testing configuration.

    Uses SQLite in-memory by default for fast local tests.
    Set TEST_DATABASE_URL to use PostgreSQL for integration tests.
    """

    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "TEST_DATABASE_URL", "sqlite:///:memory:"
    )
    WTF_CSRF_ENABLED: bool = False


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG: bool = False


config_by_name: dict[str, type[Config]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
