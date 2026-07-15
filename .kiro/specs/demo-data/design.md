# Design — Integrated Demo Data

## Architecture
```
scripts/seed_demo.py        ← standalone script
app/commands.py             ← Flask CLI commands (registered in factory)
```

## Seed Order (respects FK)
1. Users
2. Trains
3. Stations
4. Trips + TripStatusHistory
5. Incidents + IncidentStatusHistory
6. Documents (S3 optional)
7. EC2 Instances (optional)
8. Audit Logs

## Idempotency Strategy
- Check by unique field (email, train_code, station_code, trip_number, incident_number)
- Skip if exists
- Count created vs skipped

## Reset Strategy
- Only if FLASK_ENV == development or FLASK_DEBUG == 1
- Deletes all seeded data in reverse FK order
- Requires --reset flag
