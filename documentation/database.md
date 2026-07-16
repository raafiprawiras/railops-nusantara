# Database Schema — RailOps Nusantara

## Overview

Database: PostgreSQL 16
ORM: SQLAlchemy via Flask-SQLAlchemy
Migrations: Alembic via Flask-Migrate

## Tables

### users
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PK, auto |
| full_name | String(150) | NOT NULL |
| email | String(254) | UNIQUE, NOT NULL, indexed |
| password_hash | String(256) | NOT NULL |
| role | String(20) | NOT NULL, default 'operator' |
| is_active | Boolean | NOT NULL, default true |
| last_login_at | DateTime(tz) | nullable |
| created_at | DateTime(tz) | NOT NULL, auto |
| updated_at | DateTime(tz) | NOT NULL, auto |

**Role values:** administrator, operator, supervisor

### trains
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PK |
| train_code | String(20) | UNIQUE, NOT NULL, indexed |
| train_name | String(100) | NOT NULL |
| train_type | String(20) | NOT NULL |
| capacity | Integer | NOT NULL |
| carriage_number | Integer | NOT NULL |
| status | String(30) | NOT NULL, default 'Aktif' |
| last_maintenance_date | Date | nullable |
| created_at | DateTime(tz) | NOT NULL |
| updated_at | DateTime(tz) | NOT NULL |

**train_type:** Eksekutif, Bisnis, Ekonomi, Komuter, Barang
**status:** Aktif, Tidak Aktif, Dalam Perawatan, Mengalami Gangguan

### stations
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PK |
| station_code | String(10) | UNIQUE, NOT NULL, indexed |
| station_name | String(100) | NOT NULL |
| city | String(100) | NOT NULL |
| province | String(100) | NOT NULL |
| platform_count | Integer | NOT NULL, default 1 |
| operational_status | String(30) | NOT NULL, default 'Aktif' |
| created_at | DateTime(tz) | NOT NULL |
| updated_at | DateTime(tz) | NOT NULL |

**operational_status:** Aktif, Tidak Aktif, Dalam Renovasi

### trips
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PK |
| trip_number | String(30) | UNIQUE, NOT NULL, indexed |
| train_id | Integer | FK trains.id, NOT NULL |
| origin_station_id | Integer | FK stations.id, NOT NULL |
| destination_station_id | Integer | FK stations.id, NOT NULL |
| scheduled_departure | DateTime(tz) | NOT NULL |
| scheduled_arrival | DateTime(tz) | NOT NULL |
| actual_departure | DateTime(tz) | nullable |
| actual_arrival | DateTime(tz) | nullable |
| platform | Integer | NOT NULL |
| status | String(30) | NOT NULL, default 'Dijadwalkan' |
| delay_minutes | Integer | NOT NULL, default 0 |
| last_known_station_id | Integer | FK stations.id, nullable |
| notes | Text | nullable |
| created_by | Integer | FK users.id |
| created_at | DateTime(tz) | NOT NULL |
| updated_at | DateTime(tz) | NOT NULL |

**status:** Dijadwalkan, Persiapan, Berangkat, Dalam Perjalanan, Tiba, Terlambat, Dibatalkan

### trip_status_history
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PK |
| trip_id | Integer | FK trips.id, NOT NULL, indexed |
| previous_status | String(30) | nullable |
| new_status | String(30) | NOT NULL |
| station_id | Integer | FK stations.id, nullable |
| delay_minutes | Integer | NOT NULL, default 0 |
| notes | Text | nullable |
| changed_by | Integer | FK users.id |
| created_at | DateTime(tz) | NOT NULL |

### incidents
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PK |
| incident_number | String(30) | UNIQUE, NOT NULL, indexed |
| trip_id | Integer | FK trips.id, NOT NULL |
| incident_type | String(50) | NOT NULL |
| location | String(200) | NOT NULL |
| occurred_at | DateTime(tz) | NOT NULL |
| priority | String(20) | NOT NULL |
| description | Text | NOT NULL |
| status | String(30) | NOT NULL, default 'Dilaporkan' |
| reported_by | Integer | FK users.id, NOT NULL |
| assigned_to | Integer | FK users.id, nullable |
| resolved_at | DateTime(tz) | nullable |
| resolution_notes | Text | nullable |
| created_at | DateTime(tz) | NOT NULL |
| updated_at | DateTime(tz) | NOT NULL |

**incident_type:** Gangguan Lokomotif, Gangguan Rangkaian, Gangguan Persinyalan, Gangguan Jalur, Gangguan Listrik, Cuaca Buruk, Gangguan Fasilitas, Lainnya
**priority:** Rendah, Sedang, Tinggi, Darurat
**status:** Dilaporkan, Dalam Penanganan, Selesai, Ditutup

### incident_status_history
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PK |
| incident_id | Integer | FK incidents.id, NOT NULL, indexed |
| previous_status | String(30) | nullable |
| new_status | String(30) | NOT NULL |
| notes | Text | nullable |
| changed_by | Integer | FK users.id |
| created_at | DateTime(tz) | NOT NULL |

### documents
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PK |
| trip_id | Integer | FK trips.id, nullable |
| incident_id | Integer | FK incidents.id, nullable |
| original_filename | String(255) | NOT NULL |
| stored_filename | String(255) | NOT NULL |
| bucket_name | String(100) | NOT NULL |
| object_key | String(500) | NOT NULL |
| content_type | String(100) | NOT NULL |
| file_size | Integer | NOT NULL |
| document_category | String(50) | NOT NULL |
| uploaded_by | Integer | FK users.id, NOT NULL |
| uploaded_at | DateTime(tz) | NOT NULL |
| deleted_at | DateTime(tz) | nullable (soft delete) |

**document_category:** Manifest, Inspeksi, Perawatan, Laporan Gangguan, Berita Acara, Dokumentasi, Lainnya

### infrastructure_instances
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PK |
| instance_id | String(30) | UNIQUE, NOT NULL, indexed |
| instance_name | String(100) | NOT NULL |
| instance_type | String(20) | NOT NULL, default 't2.micro' |
| image_id | String(50) | NOT NULL |
| state | String(20) | NOT NULL, default 'pending' |
| purpose | String(50) | NOT NULL |
| created_by | Integer | FK users.id |
| created_at | DateTime(tz) | NOT NULL |
| updated_at | DateTime(tz) | NOT NULL |
| terminated_at | DateTime(tz) | nullable |

**state:** pending, running, stopped, shutting-down, terminated

### audit_logs
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PK |
| user_id | Integer | FK users.id |
| action | String(50) | NOT NULL |
| resource_type | String(50) | NOT NULL |
| resource_id | String(100) | NOT NULL |
| description | Text | NOT NULL |
| metadata_json | Text | nullable |
| created_at | DateTime(tz) | NOT NULL |

## Migration History

1. `47851b64d0c5` — create_users_table
2. `de74356fb0dc` — create_trains_stations_tables
3. `9914c0b3cf2d` — create_trips_and_status_history
4. `1d2c96d48121` — create_incidents_tables
5. `153caba72246` — create_documents_table
6. `f6800a7a8ef7` — create_infrastructure_and_audit_tables
