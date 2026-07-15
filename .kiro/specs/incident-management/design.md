# Design — Incident Management

## Models

### Incident
| Field | Type | Constraints |
|-------|------|-------------|
| id | Integer | PK |
| incident_number | String(30) | unique, not null |
| trip_id | FK trips.id | not null |
| incident_type | String(50) | not null |
| location | String(200) | not null |
| occurred_at | DateTime | not null |
| priority | String(20) | not null |
| description | Text | not null |
| status | String(30) | default Dilaporkan |
| reported_by | FK users.id | not null |
| assigned_to | FK users.id | nullable |
| resolved_at | DateTime | nullable |
| resolution_notes | Text | nullable |
| created_at | DateTime | auto |
| updated_at | DateTime | auto |

### IncidentStatusHistory
| Field | Type |
|-------|------|
| id | Integer PK |
| incident_id | FK incidents.id |
| previous_status | String(30) nullable |
| new_status | String(30) |
| notes | Text nullable |
| changed_by | FK users.id |
| created_at | DateTime auto |

## Status Flow
```
Dilaporkan → Dalam Penanganan → Selesai → Ditutup
```
Invalid: Dilaporkan → Selesai, Dilaporkan → Ditutup, Dalam Penanganan → Ditutup

## Routes
| Method | URL | Roles |
|--------|-----|-------|
| GET | /incidents | all |
| GET/POST | /incidents/create | admin, operator |
| GET | /incidents/<id> | all |
| GET/POST | /incidents/<id>/edit | admin, operator |
| POST | /incidents/<id>/status | admin, operator, supervisor(close only) |
