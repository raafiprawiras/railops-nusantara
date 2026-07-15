# Design — Trip Operations & Monitoring

## Models

### Trip
| Field | Type | Constraints |
|-------|------|-------------|
| id | Integer | PK |
| trip_number | String(30) | unique, not null |
| train_id | Integer | FK trains.id, not null |
| origin_station_id | Integer | FK stations.id, not null |
| destination_station_id | Integer | FK stations.id, not null |
| scheduled_departure | DateTime | not null |
| scheduled_arrival | DateTime | not null |
| actual_departure | DateTime | nullable |
| actual_arrival | DateTime | nullable |
| platform | Integer | not null, > 0 |
| status | String(30) | not null, default Dijadwalkan |
| delay_minutes | Integer | default 0, >= 0 |
| last_known_station_id | Integer | FK stations.id, nullable |
| notes | Text | nullable |
| created_by | Integer | FK users.id |
| created_at | DateTime | auto |
| updated_at | DateTime | auto |

### TripStatusHistory
| Field | Type |
|-------|------|
| id | Integer PK |
| trip_id | FK trips.id |
| previous_status | String(30) |
| new_status | String(30) |
| station_id | FK nullable |
| delay_minutes | Integer |
| notes | Text nullable |
| changed_by | FK users.id |
| created_at | DateTime auto |

## Routes
| Method | URL | Roles |
|--------|-----|-------|
| GET | /trips | all |
| GET/POST | /trips/create | admin, operator |
| GET | /trips/<id> | all |
| GET/POST | /trips/<id>/edit | admin, operator |
| POST | /trips/<id>/delete | admin |
| GET | /monitoring | all |
| POST | /trips/<id>/status | admin, operator |

## Status Flow
Dijadwalkan → Persiapan → Berangkat → Dalam Perjalanan → Tiba
                                                        → Terlambat → Tiba
Any → Dibatalkan
