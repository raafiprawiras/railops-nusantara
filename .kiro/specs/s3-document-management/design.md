# Design — S3 Document Management

## S3 Service (app/services/s3_service.py)
- get_s3_client() → boto3 client from app config
- check_health() → bool
- ensure_bucket(name) → idempotent create
- upload_file(bucket, key, file_obj, content_type) → success/error
- download_file(bucket, key) → StreamingBody
- delete_object(bucket, key) → success/error
- list_objects(bucket, prefix) → list
- get_object_metadata(bucket, key) → dict
- list_buckets() → list

## Object Key Structure
- manifests/YYYY/TRIP_NUMBER/uuid_filename
- incidents/YYYY/INCIDENT_NUMBER/uuid_filename
- inspections/YYYY/TRAIN_CODE/uuid_filename
- maintenance/YYYY/TRAIN_CODE/uuid_filename
- miscellaneous/YYYY/uuid_filename

## Document Model
| Field | Type |
|-------|------|
| id | Integer PK |
| trip_id | FK nullable |
| incident_id | FK nullable |
| original_filename | String(255) |
| stored_filename | String(255) |
| bucket_name | String(100) |
| object_key | String(500) |
| content_type | String(100) |
| file_size | Integer |
| document_category | String(50) |
| uploaded_by | FK users.id |
| uploaded_at | DateTime |
| deleted_at | DateTime nullable |

## Routes
| Method | URL | Roles |
|--------|-----|-------|
| GET | /documents | all |
| GET/POST | /documents/upload | admin, operator |
| GET | /documents/<id> | all |
| GET | /documents/<id>/download | all |
| POST | /documents/<id>/delete | admin |
| GET | /cloud/s3 | all |
