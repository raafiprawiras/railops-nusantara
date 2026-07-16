"""S3 service — all Boto3 operations via LocalStack.

All configuration comes from Flask app config. Never hardcodes
endpoint, region, credentials, or bucket names.
"""

import logging
from typing import Any

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError, EndpointConnectionError, ConnectionClosedError
from flask import current_app

logger = logging.getLogger(__name__)


def get_s3_client():
    """Create an S3 Boto3 client from app config."""
    endpoint_url = current_app.config.get("AWS_ENDPOINT_URL", "")
    if not endpoint_url:
        raise RuntimeError("AWS_ENDPOINT_URL tidak dikonfigurasi.")

    boto_config = BotoConfig(
        connect_timeout=5,
        read_timeout=10,
        retries={"max_attempts": 2},
    )
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=current_app.config["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=current_app.config["AWS_SECRET_ACCESS_KEY"],
        region_name=current_app.config["AWS_DEFAULT_REGION"],
        config=boto_config,
    )


def check_health() -> bool:
    """Check if LocalStack S3 is reachable."""
    try:
        client = get_s3_client()
        client.list_buckets()
        return True
    except (ClientError, EndpointConnectionError, ConnectionClosedError, Exception):
        return False


def ensure_bucket(bucket_name: str) -> dict[str, Any]:
    """Create bucket if it doesn't exist (idempotent)."""
    try:
        client = get_s3_client()
        region = current_app.config["AWS_DEFAULT_REGION"]

        try:
            client.head_bucket(Bucket=bucket_name)
            return {"success": True, "message": "Bucket sudah ada."}
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code in ("404", "NoSuchBucket"):
                client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": region},
                )
                return {"success": True, "message": "Bucket berhasil dibuat."}
            raise

    except (EndpointConnectionError, ConnectionClosedError):
        return {"success": False, "message": "LocalStack tidak tersedia."}
    except ClientError as e:
        return {"success": False, "message": f"Error S3: {e.response['Error']['Message']}"}
    except Exception as e:
        logger.error(f"ensure_bucket error: {e}")
        return {"success": False, "message": "Gagal membuat bucket."}


def list_buckets() -> list[dict]:
    """List all S3 buckets."""
    try:
        client = get_s3_client()
        response = client.list_buckets()
        return response.get("Buckets", [])
    except (EndpointConnectionError, ConnectionClosedError, ClientError):
        return []


def upload_file(bucket_name: str, object_key: str, file_obj, content_type: str) -> dict[str, Any]:
    """Upload a file to S3.

    Returns dict with 'success' bool and 'message' or 'error'.
    """
    try:
        client = get_s3_client()
        client.upload_fileobj(
            file_obj,
            bucket_name,
            object_key,
            ExtraArgs={"ContentType": content_type},
        )
        return {"success": True, "message": "Upload berhasil."}
    except (EndpointConnectionError, ConnectionClosedError):
        return {"success": False, "error": "LocalStack tidak tersedia."}
    except ClientError as e:
        return {"success": False, "error": f"Error S3: {e.response['Error']['Message']}"}
    except Exception as e:
        logger.error(f"upload_file error: {e}")
        return {"success": False, "error": "Gagal mengupload file."}


def download_file(bucket_name: str, object_key: str) -> dict[str, Any]:
    """Download a file from S3.

    Returns dict with 'success' and 'body' (StreamingBody) or 'error'.
    """
    try:
        client = get_s3_client()
        response = client.get_object(Bucket=bucket_name, Key=object_key)
        return {
            "success": True,
            "body": response["Body"],
            "content_type": response.get("ContentType", "application/octet-stream"),
            "content_length": response.get("ContentLength", 0),
        }
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code == "NoSuchKey":
            return {"success": False, "error": "File tidak ditemukan di S3."}
        return {"success": False, "error": f"Error S3: {e.response['Error']['Message']}"}
    except (EndpointConnectionError, ConnectionClosedError):
        return {"success": False, "error": "LocalStack tidak tersedia."}
    except Exception as e:
        logger.error(f"download_file error: {e}")
        return {"success": False, "error": "Gagal mengunduh file."}


def delete_object(bucket_name: str, object_key: str) -> dict[str, Any]:
    """Delete an object from S3."""
    try:
        client = get_s3_client()
        client.delete_object(Bucket=bucket_name, Key=object_key)
        return {"success": True, "message": "Object berhasil dihapus."}
    except (EndpointConnectionError, ConnectionClosedError):
        return {"success": False, "error": "LocalStack tidak tersedia."}
    except ClientError as e:
        return {"success": False, "error": f"Error S3: {e.response['Error']['Message']}"}
    except Exception as e:
        logger.error(f"delete_object error: {e}")
        return {"success": False, "error": "Gagal menghapus object."}


def list_objects(bucket_name: str, prefix: str = "") -> list[dict]:
    """List objects in a bucket, optionally with prefix."""
    try:
        client = get_s3_client()
        kwargs = {"Bucket": bucket_name}
        if prefix:
            kwargs["Prefix"] = prefix

        response = client.list_objects_v2(**kwargs)
        return response.get("Contents", [])
    except (EndpointConnectionError, ConnectionClosedError, ClientError):
        return []


def get_object_metadata(bucket_name: str, object_key: str) -> dict[str, Any] | None:
    """Get object metadata (head_object)."""
    try:
        client = get_s3_client()
        response = client.head_object(Bucket=bucket_name, Key=object_key)
        return {
            "content_type": response.get("ContentType"),
            "content_length": response.get("ContentLength"),
            "last_modified": response.get("LastModified"),
            "etag": response.get("ETag"),
        }
    except (EndpointConnectionError, ConnectionClosedError, ClientError):
        return None


def get_bucket_object_count(bucket_name: str) -> int:
    """Get total object count in a bucket."""
    try:
        client = get_s3_client()
        response = client.list_objects_v2(Bucket=bucket_name)
        return response.get("KeyCount", 0)
    except (EndpointConnectionError, ConnectionClosedError, ClientError):
        return 0
