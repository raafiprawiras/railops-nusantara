# Project Structure — RailOps Nusantara

```
railops-nusantara/
├── app/
│   ├── __init__.py            # Application factory (create_app)
│   ├── extensions.py          # Flask extensions (db, migrate, login_manager)
│   ├── models/
│   │   └── __init__.py
│   ├── routes/
│   │   ├── __init__.py        # Register all blueprints
│   │   └── main.py            # Main blueprint (health, index)
│   ├── services/
│   │   ├── __init__.py        # get_boto3_client helper
│   │   ├── ec2_service.py     # EC2 operations via LocalStack
│   │   └── s3_service.py      # S3 operations via LocalStack
│   ├── forms/
│   │   └── __init__.py
│   ├── templates/
│   │   └── layouts/
│   │       └── base.html      # Base template with Bootstrap 5
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── app.js
│   │   └── images/
│   └── utils/
│       └── __init__.py
├── scripts/
│   └── wait_for_services.py   # Wait for PostgreSQL & LocalStack readiness
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # pytest fixtures
│   └── test_health.py         # Health endpoint tests
├── documentation/
│   └── architecture.md
├── .kiro/
│   ├── steering/
│   │   ├── product.md
│   │   ├── tech.md
│   │   └── structure.md
│   └── specs/
│       └── project-foundation/
│           ├── requirements.md
│           ├── design.md
│           └── tasks.md
├── .env.example
├── .gitignore
├── config.py
├── docker-compose.yml
├── Dockerfile
├── README.md
├── requirements.txt
└── run.py
```

## Konvensi Penamaan

| Item              | Convention          | Contoh                    |
|-------------------|---------------------|---------------------------|
| File Python       | snake_case          | `ec2_service.py`          |
| Class             | PascalCase          | `TrainSchedule`           |
| Function          | snake_case          | `get_all_trains()`        |
| Template          | snake_case          | `train_list.html`         |
| Blueprint         | snake_case          | `main_bp`                 |
| Route URL         | kebab-case          | `/api/train-schedules`    |
| Environment Var   | UPPER_SNAKE_CASE    | `DATABASE_URL`            |

## Module Responsibilities

- **routes/**: HTTP request handling saja. Tipis.
- **services/**: Logika bisnis, interaksi AWS/Boto3.
- **models/**: SQLAlchemy model definitions.
- **forms/**: Flask-WTF form classes.
- **templates/**: Jinja2 HTML templates.
- **utils/**: Helper functions dan utilities.
- **scripts/**: Operational scripts (bukan bagian dari app).
