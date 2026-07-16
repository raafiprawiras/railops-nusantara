# Project Structure — RailOps Nusantara v1.0.0

```
railops-nusantara/
├── app/
│   ├── __init__.py                    # Application factory
│   ├── extensions.py                  # Flask extensions (db, migrate, login, csrf)
│   ├── commands.py                    # Flask CLI commands (seed-demo)
│   ├── models/
│   │   ├── __init__.py                # Model imports
│   │   ├── user.py                    # User model
│   │   ├── train.py                   # Train model
│   │   ├── station.py                 # Station model
│   │   ├── trip.py                    # Trip + TripStatusHistory
│   │   ├── incident.py               # Incident + IncidentStatusHistory
│   │   ├── document.py               # Document model (S3 metadata)
│   │   └── infrastructure.py         # InfrastructureInstance + AuditLog
│   ├── routes/
│   │   ├── __init__.py                # Blueprint registration
│   │   ├── main.py                    # Dashboard, health
│   │   ├── auth_routes.py            # Login, logout
│   │   ├── train_routes.py           # Train CRUD
│   │   ├── station_routes.py         # Station CRUD
│   │   ├── trip_routes.py            # Trip CRUD + monitoring
│   │   ├── incident_routes.py        # Incident CRUD + status
│   │   ├── document_routes.py        # Document upload/download + S3 panel
│   │   ├── ec2_routes.py             # EC2 lifecycle + audit log
│   │   ├── report_routes.py          # Reports + CSV export
│   │   ├── user_routes.py            # User administration
│   │   └── profile_routes.py         # Profile + password change
│   ├── services/
│   │   ├── __init__.py                # get_boto3_client (with guard)
│   │   ├── s3_service.py             # S3 operations via LocalStack
│   │   ├── ec2_service.py            # EC2 operations via LocalStack
│   │   └── dashboard_service.py      # Dashboard aggregate queries
│   ├── forms/
│   │   ├── __init__.py
│   │   ├── auth_forms.py             # Login form
│   │   ├── train_forms.py            # Train form
│   │   ├── station_forms.py          # Station form
│   │   ├── trip_forms.py             # Trip + status forms
│   │   ├── incident_forms.py         # Incident + status forms
│   │   ├── document_forms.py         # Upload form
│   │   └── user_forms.py             # User admin + profile forms
│   ├── templates/
│   │   ├── layouts/
│   │   │   ├── base.html             # Main layout (sidebar + navbar)
│   │   │   ├── base_auth.html        # Auth layout (no sidebar)
│   │   │   └── partials/
│   │   │       ├── sidebar.html
│   │   │       ├── navbar.html
│   │   │       ├── footer.html
│   │   │       └── flash_messages.html
│   │   ├── dashboard.html
│   │   ├── login.html
│   │   ├── errors/ (403, 404, 500)
│   │   ├── trains/ (list, detail, form)
│   │   ├── stations/ (list, detail, form)
│   │   ├── trips/ (list, detail, form, monitoring, _status_badge)
│   │   ├── incidents/ (list, detail, form)
│   │   ├── documents/ (list, detail, upload, cloud_s3)
│   │   ├── ec2/ (index, audit_logs)
│   │   ├── reports/ (index, trips, incidents, punctuality, infrastructure, documents)
│   │   ├── users/ (list, detail, form, edit)
│   │   └── profile/ (index, edit, change_password)
│   ├── static/
│   │   ├── css/style.css              # Dark navy theme
│   │   ├── js/app.js                  # Sidebar toggle, nav state
│   │   ├── js/dashboard.js           # Chart.js charts
│   │   └── images/
│   └── utils/
│       ├── __init__.py
│       └── decorators.py              # role_required
├── scripts/
│   ├── seed_demo.py                   # Full integrated demo seeder
│   ├── create_admin.py                # Create admin user
│   ├── seed_users.py                  # Seed sample users
│   ├── seed_master_data.py            # Seed trains + stations
│   ├── seed_trip_data.py              # Seed trips
│   ├── seed_incident_data.py          # Seed incidents
│   ├── init_localstack.py             # Initialize S3 bucket
│   ├── init_ec2_demo.py               # Initialize EC2 demo instances
│   └── wait_for_services.py           # Wait for PostgreSQL + LocalStack
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # Fixtures (app, db, clients, sample data)
│   ├── test_auth.py                   # Authentication tests (10)
│   ├── test_health.py                 # Health endpoint tests (4)
│   ├── test_ui.py                     # UI foundation tests (5)
│   ├── test_master_data.py            # Train + station tests (16)
│   ├── test_trips.py                  # Trip tests (14)
│   ├── test_incidents.py              # Incident tests (13)
│   ├── test_s3_documents.py           # S3 document tests (12)
│   ├── test_ec2.py                    # EC2 tests (14)
│   ├── test_dashboard_reports.py      # Dashboard + report tests (18)
│   ├── test_users_profile.py          # User admin + profile tests (15)
│   ├── test_seed_demo.py              # Seed idempotency tests (7)
│   └── test_security.py              # Security tests (10)
├── migrations/
│   ├── versions/
│   │   ├── 47851b64d0c5_create_users_table.py
│   │   ├── de74356fb0dc_create_trains_stations_tables.py
│   │   ├── 9914c0b3cf2d_create_trips_and_status_history.py
│   │   ├── 1d2c96d48121_create_incidents_tables.py
│   │   ├── 153caba72246_create_documents_table.py
│   │   └── f6800a7a8ef7_create_infrastructure_and_audit_tables.py
│   ├── env.py
│   └── alembic.ini
├── documentation/
│   ├── architecture.md                # Mermaid diagrams
│   ├── database.md                    # Schema reference
│   ├── api-and-routes.md              # Route list
│   ├── user-manual.md                 # Manual (Bahasa Indonesia)
│   ├── demo-scenario.md               # Demo presentation guide
│   ├── troubleshooting.md             # Problem resolution
│   ├── project-structure.md           # This file
│   └── CONVERT-TO-PDF.md             # PDF conversion instructions
├── .kiro/
│   ├── steering/ (product, tech, structure)
│   └── specs/ (10 spec folders)
├── config.py                          # Configuration classes
├── run.py                             # Entry point
├── Dockerfile                         # Python 3.12-slim + gunicorn
├── docker-compose.yml                 # app + postgres + localstack
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment template
├── .gitignore
├── README.md                          # Comprehensive README
├── CHANGELOG.md                       # Version history
├── RELEASE_CHECKLIST.md               # Release verification
└── VERSION                            # 1.0.0
```

## Statistics

| Metric | Count |
|--------|-------|
| Python files | 55+ |
| Templates | 40+ |
| Blueprints | 11 |
| Routes | 60 |
| Models | 9 (User, Train, Station, Trip, TripStatusHistory, Incident, IncidentStatusHistory, Document, InfrastructureInstance, AuditLog) |
| Migrations | 6 |
| Tests | 138 |
| Documentation files | 8 |
