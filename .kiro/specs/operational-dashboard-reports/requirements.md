# Requirements — Operational Dashboard & Reports

## FR-1: Dynamic Dashboard
- All data from DB queries (no fake data)
- Stats: kereta_aktif, trips today, on-time, delayed, cancelled, incidents, EC2, docs
- Percentage punctuality, average delay
- Charts: doughnut trip status, line 7-day delay, bar trips per day, incident priority
- Tables: recent trips, recent incidents, recent audit log
- Graceful fallback when cloud unavailable (show "N/A" not fake numbers)

## FR-2: Dashboard Service
- app/services/dashboard_service.py
- Efficient aggregate queries
- No N+1
- Service called by route (route stays thin)

## FR-3: Reports
- /reports — index
- /reports/trips — trip report with filters, CSV export
- /reports/incidents — incident report with filters, CSV export
- /reports/punctuality — punctuality analysis
- /reports/infrastructure — EC2 audit log report, CSV export
- /reports/documents — document report

## FR-4: CSV Export
- Date in filename
- Escape formula injection (=, +, -, @, \t, \r prefix with ')
- Content-Disposition attachment

## FR-5: Authorization
- admin, supervisor: all reports
- operator: basic operational reports (trips, incidents)

## FR-6: Filters
- start_date, end_date, status, train, station, priority
