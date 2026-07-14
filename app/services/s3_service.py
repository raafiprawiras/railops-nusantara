"""S3 service — operations via LocalStack."""

from flask import current_app

from app.services import get_boto3_client


def list_buckets() -> list[dict]:
    """List all S3 buckets."""
    client = get_boto3_client("s3")
    response = client.list_buckets()
    return response.get("Buckets", [])


def create_bucket(bucket_name: str) -> dict:
    """Create an S3 bucket."""
    client = get_boto3_client("s3")
    region = current_app.config["AWS_DEFAULT_REGION"]
    return client.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={"LocationConstraint": region},
    )


def list_objects(bucket_name: str) -> list[dict]:
    """List objects in a bucket."""
    client = get_boto3_client("s3")
    response = client.list_objects_v2(Bucket=bucket_name)
    return response.get("Contents", [])


def upload_file(bucket_name: str, file_obj, object_key: str) -> None:
    """Upload a file to S3."""
    client = get_boto3_client("s3")
    client.upload_fileobj(file_obj, bucket_name, object_key)


def delete_object(bucket_name: str, object_key: str) -> dict:
    """Delete an object from S3."""
    client = get_boto3_client("s3")
    return client.delete_object(Bucket=bucket_name, Key=object_key)
