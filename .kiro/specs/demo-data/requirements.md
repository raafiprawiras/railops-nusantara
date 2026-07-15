# Requirements — Integrated Demo Data

## FR-1: Seed Script
- Single command to populate full consistent demo dataset
- Idempotent (safe to run multiple times, no duplicates)
- Uses transactions
- Concise output
- Works in Docker
- Never auto-runs in production
- Optional --reset with development-only guard

## FR-2: Demo Data
- 4 users (1 admin, 2 operators, 1 supervisor)
- 8 trains
- 10 stations
- 20+ trips (all statuses, realistic delays, dates around today)
- 8+ incidents (mixed types, priorities, statuses)
- Status history for trips and incidents
- Document metadata (S3 upload if LocalStack available, warning if not)
- EC2 instances (if LocalStack available)
- Audit logs

## FR-3: Flask CLI
- `flask seed-demo` — seed data
- `flask seed-demo --reset` — wipe + reseed (development only)

## FR-4: README
- Migration command, seed command, demo accounts, how to run
