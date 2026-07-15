# Design — Railway Master Data

## Models

### Train
| Field | Type | Constraints |
|-------|------|-------------|
| id | Integer | PK |
| train_code | String(20) | unique, not null |
| train_name | String(100) | not null |
| train_type | String(20) | not null |
| capacity | Integer | not null, > 0 |
| carriage_number | Integer | not null |
| status | String(30) | not null |
| last_maintenance_date | Date | nullable |
| created_at | DateTime | auto |
| updated_at | DateTime | auto |

### Station
| Field | Type | Constraints |
|-------|------|-------------|
| id | Integer | PK |
| station_code | String(10) | unique, not null |
| station_name | String(100) | not null |
| city | String(100) | not null |
| province | String(100) | not null |
| platform_count | Integer | not null, >= 1 |
| operational_status | String(30) | not null |
| created_at | DateTime | auto |
| updated_at | DateTime | auto |

## Routes

### Trains
| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| GET | /trains | all | List |
| GET | /trains/create | admin | Form |
| POST | /trains/create | admin | Create |
| GET | /trains/<id> | all | Detail |
| GET | /trains/<id>/edit | admin | Edit form |
| POST | /trains/<id>/edit | admin | Update |
| POST | /trains/<id>/delete | admin | Delete |

### Stations
| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| GET | /stations | all | List |
| GET | /stations/create | admin | Form |
| POST | /stations/create | admin | Create |
| GET | /stations/<id> | all | Detail |
| GET | /stations/<id>/edit | admin | Edit form |
| POST | /stations/<id>/edit | admin | Update |
| POST | /stations/<id>/delete | admin | Delete |

## Files
```
app/models/train.py
app/models/station.py
app/forms/train_forms.py
app/forms/station_forms.py
app/routes/train_routes.py
app/routes/station_routes.py
app/templates/trains/list.html
app/templates/trains/detail.html
app/templates/trains/form.html
app/templates/stations/list.html
app/templates/stations/detail.html
app/templates/stations/form.html
scripts/seed_master_data.py
tests/test_master_data.py
```
