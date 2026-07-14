# Design — Project Foundation

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   Docker Compose                     │
├──────────────┬──────────────┬───────────────────────┤
│  Flask App   │  PostgreSQL  │     LocalStack        │
│  (port 5000) │  (port 5432) │     (port 4566)       │
├──────────────┴──────────────┴───────────────────────┤
│                  Docker Network                      │
└─────────────────────────────────────────────────────┘
```

## Application Structure

### Application Factory (`app/__init__.py`)

```python
def create_app(config_class=None):
    app = Flask(__name__)
    app.config.from_object(config_class or Config)
    _register_extensions(app)
    _register_blueprints(app)
    return app
```

### Configuration (`config.py`)

- `Config` — base configuration from env vars
- `DevelopmentConfig` — debug enabled
- `TestingConfig` — testing flag, separate DB, short timeouts
- `ProductionConfig` — production settings

### Health Check Design

`GET /health` returns:

```json
{
    "application": "healthy",
    "database": "healthy | unhealthy",
    "localstack": "healthy | unhealthy",
    "status": "healthy | degraded"
}
```

Logic:
- `application`: always "healthy" jika endpoint merespons.
- `database`: cek koneksi dengan `SELECT 1`.
- `localstack`: cek koneksi dengan `sts.get_caller_identity()` (timeout 3s).
- `status`: "healthy" jika semua ok, "degraded" jika ada yang gagal.

### Blueprint Structure

```
routes/
├── __init__.py     # register_blueprints(app)
└── main.py         # main_bp: /, /health
```

### Services Layer

```
services/
├── __init__.py     # get_boto3_client(service_name)
├── ec2_service.py
└── s3_service.py
```

## Docker Compose Services

| Service     | Image              | Port  | Depends On |
|-------------|--------------------|-------|------------|
| app         | Build from .       | 5000  | postgres, localstack |
| postgres    | postgres:16        | 5432  | -          |
| localstack  | localstack/localstack | 4566 | -       |

## Data Flow

1. Request masuk ke Flask route (tipis).
2. Route memanggil service layer.
3. Service berinteraksi dengan DB (via SQLAlchemy) atau AWS (via Boto3 + LocalStack).
4. Response dikembalikan ke client.
