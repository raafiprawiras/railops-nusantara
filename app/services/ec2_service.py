"""EC2 service — all Boto3 EC2 operations via LocalStack.

All configuration from Flask app config. Never connects to real AWS.
"""

import json
import logging
from typing import Any

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError, EndpointConnectionError, ConnectionClosedError
from flask import current_app

logger = logging.getLogger(__name__)


def get_ec2_client():
    """Create EC2 Boto3 client from app config."""
    boto_config = BotoConfig(
        connect_timeout=5,
        read_timeout=10,
        retries={"max_attempts": 2},
    )
    return boto3.client(
        "ec2",
        endpoint_url=current_app.config["AWS_ENDPOINT_URL"],
        aws_access_key_id=current_app.config["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=current_app.config["AWS_SECRET_ACCESS_KEY"],
        region_name=current_app.config["AWS_DEFAULT_REGION"],
        config=boto_config,
    )


def check_health() -> bool:
    """Check if LocalStack EC2 is reachable."""
    try:
        client = get_ec2_client()
        client.describe_instances(MaxResults=5)
        return True
    except (ClientError, EndpointConnectionError, ConnectionClosedError, Exception):
        return False


def _normalize_instance(instance: dict) -> dict:
    """Normalize Boto3 instance dict to simple format."""
    # Extract Name tag
    name = ""
    for tag in instance.get("Tags", []):
        if tag.get("Key") == "Name":
            name = tag.get("Value", "")
            break

    # Extract Purpose tag
    purpose = ""
    for tag in instance.get("Tags", []):
        if tag.get("Key") == "Purpose":
            purpose = tag.get("Value", "")
            break

    return {
        "instance_id": instance.get("InstanceId", ""),
        "instance_name": name,
        "instance_type": instance.get("InstanceType", ""),
        "image_id": instance.get("ImageId", ""),
        "state": instance.get("State", {}).get("Name", "unknown"),
        "purpose": purpose,
        "launch_time": instance.get("LaunchTime"),
    }


def list_instances() -> list[dict]:
    """List all EC2 instances (normalized)."""
    try:
        client = get_ec2_client()
        response = client.describe_instances()
        instances = []
        for reservation in response.get("Reservations", []):
            for inst in reservation.get("Instances", []):
                instances.append(_normalize_instance(inst))
        return instances
    except (EndpointConnectionError, ConnectionClosedError):
        return []
    except ClientError as e:
        logger.error(f"list_instances error: {e}")
        return []


def get_instance_state(instance_id: str) -> str | None:
    """Get current state of a specific instance."""
    try:
        client = get_ec2_client()
        response = client.describe_instances(InstanceIds=[instance_id])
        for res in response.get("Reservations", []):
            for inst in res.get("Instances", []):
                return inst.get("State", {}).get("Name")
        return None
    except (ClientError, EndpointConnectionError, ConnectionClosedError):
        return None


def run_instance(name: str, purpose: str, image_id: str = None,
                 instance_type: str = "t2.micro") -> dict[str, Any]:
    """Launch a new EC2 instance.

    Returns dict with 'success' and 'instance' or 'error'.
    """
    if image_id is None:
        image_id = current_app.config.get("EC2_IMAGE_ID", "ami-12345678")

    try:
        client = get_ec2_client()
        response = client.run_instances(
            ImageId=image_id,
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": [
                        {"Key": "Name", "Value": name},
                        {"Key": "Purpose", "Value": purpose},
                        {"Key": "ManagedBy", "Value": "RailOps"},
                    ],
                }
            ],
        )
        instance = response["Instances"][0]
        return {"success": True, "instance": _normalize_instance(instance)}
    except (EndpointConnectionError, ConnectionClosedError):
        return {"success": False, "error": "LocalStack tidak tersedia."}
    except ClientError as e:
        return {"success": False, "error": f"Error EC2: {e.response['Error']['Message']}"}
    except Exception as e:
        logger.error(f"run_instance error: {e}")
        return {"success": False, "error": "Gagal membuat instance."}


def start_instance(instance_id: str) -> dict[str, Any]:
    """Start a stopped instance."""
    try:
        client = get_ec2_client()
        client.start_instances(InstanceIds=[instance_id])
        return {"success": True, "message": "Instance berhasil di-start."}
    except (EndpointConnectionError, ConnectionClosedError):
        return {"success": False, "error": "LocalStack tidak tersedia."}
    except ClientError as e:
        return {"success": False, "error": f"Error EC2: {e.response['Error']['Message']}"}


def stop_instance(instance_id: str) -> dict[str, Any]:
    """Stop a running instance."""
    try:
        client = get_ec2_client()
        client.stop_instances(InstanceIds=[instance_id])
        return {"success": True, "message": "Instance berhasil di-stop."}
    except (EndpointConnectionError, ConnectionClosedError):
        return {"success": False, "error": "LocalStack tidak tersedia."}
    except ClientError as e:
        return {"success": False, "error": f"Error EC2: {e.response['Error']['Message']}"}


def reboot_instance(instance_id: str) -> dict[str, Any]:
    """Reboot a running instance."""
    try:
        client = get_ec2_client()
        client.reboot_instances(InstanceIds=[instance_id])
        return {"success": True, "message": "Instance berhasil di-reboot."}
    except (EndpointConnectionError, ConnectionClosedError):
        return {"success": False, "error": "LocalStack tidak tersedia."}
    except ClientError as e:
        return {"success": False, "error": f"Error EC2: {e.response['Error']['Message']}"}


def terminate_instance(instance_id: str) -> dict[str, Any]:
    """Terminate an instance."""
    try:
        client = get_ec2_client()
        client.terminate_instances(InstanceIds=[instance_id])
        return {"success": True, "message": "Instance berhasil di-terminate."}
    except (EndpointConnectionError, ConnectionClosedError):
        return {"success": False, "error": "LocalStack tidak tersedia."}
    except ClientError as e:
        return {"success": False, "error": f"Error EC2: {e.response['Error']['Message']}"}
