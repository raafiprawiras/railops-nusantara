# Design — S3 Document Management

## Overview

Modul S3 Document Management menyediakan pengelolaan dokumen operasional kereta api dengan penyimpanan file di LocalStack S3 dan metadata di PostgreSQL. Seluruh operasi Boto3 berada di service layer, tidak pernah terhubung ke AWS asli.

## Architecture

```
Browser → Route (document_routes.py) → S3 Service (s3_service.py) → LocalStack S3
                                     → SQLAlchemy (Document model) → PostgreSQL
```

- **Route layer**: HTTP handling, form validation, authorization
- **Service layer**: Boto3 client creation, upload/download/delete, health check
- **Model layer**: Document metadata (PostgreSQL), soft-delete support

## Components and Interfaces

### S3 Service (`app/services/s3_service.py`)
- `get_s3_client()` — create Boto3 client from config (with endpoint guard)
- `check_health()` → bool
- `ensure_bucket(name)` → dict (idempotent create)
- `upload_file(bucket, key, file_obj, content_type)` → dict
- `download_file(bucket, key)` → dict (with StreamingBody)
- `delete_object(bucket, key)` → dict
- `list_objects(bucket, prefix)` → list
- `get_object_metadata(bucket, key)` → dict | None
- `list_buckets()` → list
- `get_bucket_object_count(bucket)` → int

### Document Routes (`app/routes/document_routes.py`)
- `GET /documents` — list with category filter, pagination
- `GET/POST /documents/upload` — upload form + processing
- `GET /documents/<id>` — detail metadata
- `GET /documents/<id>/download` — stream from S3
- `POST /documents/<id>/delete` — soft-delete + S3 removal
- `GET /cloud/s3` — LocalStack status panel

### Authorization
- administrator: upload, download, delete
- operator: upload, download
- supervisor: download only

## Data Models

### Document
| Field | Type | Constraints |
|-------|------|-------------|
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
| uploaded_at | DateTime(tz) | NOT NULL, auto |
| deleted_at | DateTime(tz) | nullable (soft delete) |

**Categories:** Manifest, Inspeksi, Perawatan, Laporan Gangguan, Berita Acara, Dokumentasi, Lainnya

**Allowed extensions:** pdf, png, jpg, jpeg, docx, xlsx

### Object Key Structure
```
manifests/YYYY/TRIP_NUMBER/uuid_filename
incidents/YYYY/INCIDENT_NUMBER/uuid_filename
inspections/YYYY/TRIP_NUMBER/uuid_filename
maintenance/YYYY/TRIP_NUMBER/uuid_filename
miscellaneous/YYYY/uuid_filename
```

## Correctness Properties

- Document must be linked to at least one Trip or Incident
- Metadata saved to PostgreSQL only after S3 upload succeeds
- If metadata save fails, uploaded S3 object is deleted (rollback)
- Soft-delete sets deleted_at + removes object from S3
- Filename sanitized via `secure_filename()` + UUID prefix
- Object key cannot contain `..` or start with `/`
- Content-Disposition header sanitized on download

## Error Handling

- `EndpointConnectionError` / `ConnectionClosedError` → graceful failure message
- `ClientError` → user-friendly error extracted from response
- S3 unavailable → dashboard/panel shows "Tidak tersedia", app doesn't crash
- Upload failure → no metadata orphan in database
- Download of deleted document → 404

## Testing Strategy

- **Unit tests (mocked S3):** upload valid/invalid, authorization, metadata storage, download, delete, S3 unavailable
- **Integration tests (LocalStack required):** real upload/download cycle, bucket creation
- Mock applied via `@patch("app.routes.document_routes.s3_service")`
- 12 tests in `tests/test_s3_documents.py`
