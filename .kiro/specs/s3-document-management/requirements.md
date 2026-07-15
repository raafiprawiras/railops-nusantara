# Requirements — S3 Document Management

## FR-1: S3 Service
- Client init from config (never hardcoded)
- Health check, create bucket idempotent, list buckets
- Upload, list objects, get metadata, download, delete
- Handle ClientError/EndpointConnectionError gracefully

## FR-2: Document Model
- Metadata in PostgreSQL, file in S3
- Linked to Trip or Incident (at least one)
- Soft delete (deleted_at)
- Structured object keys

## FR-3: Upload
- Sanitize filename, UUID stored name
- Validate extension (pdf,png,jpg,jpeg,docx,xlsx)
- Validate MIME type
- Validate size (MAX_CONTENT_LENGTH)
- Save metadata only after S3 success
- Rollback S3 object if metadata save fails

## FR-4: Download
- Safe, prevent path traversal
- Stream from S3

## FR-5: Delete
- Soft delete metadata + remove from S3
- Admin only for delete

## FR-6: Cloud S3 Panel
- LocalStack status
- Bucket list with object count
- Object summary

## FR-7: Authorization
- admin: upload, download, delete
- operator: upload, download
- supervisor: download only
