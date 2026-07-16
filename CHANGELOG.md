# Changelog — RailOps Nusantara

## [1.0.0] — 2026-07-16

### Added
- Project foundation: Flask app factory, Docker Compose, PostgreSQL, LocalStack
- UI Foundation: Bootstrap 5 dark navy dashboard, sidebar, responsive layout
- Authentication: Login/logout, Flask-Login, CSRF, password hashing, role management
- Railway Master Data: Train and Station CRUD with search, filter, pagination
- Trip Operations: Scheduling, monitoring, status tracking with history
- Incident Management: Reporting, status workflow, timeline, resolution tracking
- S3 Document Management: Upload/download/delete via LocalStack, metadata tracking
- EC2 Infrastructure: Lifecycle simulation (create/start/stop/reboot/terminate), audit log
- Dynamic Dashboard: Real-time stats from database, Chart.js charts
- Operational Reports: Trip, incident, punctuality reports with CSV export
- User Administration: User CRUD, profile editing, password change
- Integrated Demo Data: Single-command seed (flask seed-demo)
- Quality & Security Review: SECRET_KEY guard, AWS endpoint guard, sanitization
- Documentation: README, architecture, database schema, routes, user manual, troubleshooting

### Security
- Production SECRET_KEY validation
- AWS_ENDPOINT_URL empty guard (prevents real AWS connection)
- Content-Disposition header sanitization
- CSRF protection on all forms
- Password hashing (Werkzeug scrypt/pbkdf2)
- Role-based access control
- Open redirect prevention
- File upload validation (extension + MIME)
- Path traversal protection
- CSV injection prevention

### Infrastructure
- Docker Compose: app + postgres:16 + localstack
- 6 database migrations
- 138 automated tests
- 11 Flask blueprints, 60 routes
