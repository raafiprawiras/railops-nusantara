# Design — Quality & Security Review

## Fix 1: SECRET_KEY Production Guard
Add validation in ProductionConfig that raises if SECRET_KEY is the default dev value.

## Fix 2: AWS_ENDPOINT_URL Guard
In services/__init__.py get_boto3_client and in s3/ec2 service, validate that
AWS_ENDPOINT_URL is non-empty before creating clients. If empty, raise or return
failure gracefully.

## Fix 3: Content-Disposition Sanitization
Sanitize filename in download header to remove quotes, newlines, and non-ASCII.
