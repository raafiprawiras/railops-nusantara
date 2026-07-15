# Design — Operational Dashboard & Reports

## Dashboard Service
```python
def get_dashboard_stats() -> dict
def get_trip_chart_data() -> dict  # doughnut + 7-day line + bar
def get_recent_trips(limit=5) -> list
def get_recent_incidents(limit=5) -> list
def get_recent_audit_logs(limit=5) -> list
def get_incident_priority_stats() -> dict
```

## CSV Export Helper
```python
def escape_csv_value(val) -> str  # prevent injection
def generate_csv(headers, rows) -> Response
```

## Routes
| URL | Method | Description |
|-----|--------|-------------|
| /reports | GET | Report index |
| /reports/trips | GET | Trip report |
| /reports/trips/csv | GET | Trip CSV |
| /reports/incidents | GET | Incident report |
| /reports/incidents/csv | GET | Incident CSV |
| /reports/punctuality | GET | Punctuality analysis |
| /reports/infrastructure | GET | Infra audit report |
| /reports/infrastructure/csv | GET | Infra audit CSV |
| /reports/documents | GET | Document report |
