"""Services package — business logic and AWS interactions."""

import boto3
from flask import current_app


def get_boto3_client(service_name: str):
    """Create a Boto3 client configured for LocalStack.

    Args:
        service_name: AWS service name (e.g., 's3', 'ec2', 'sts').

    Returns:
        Configured boto3 client pointing to LocalStack endpoint.
    """
    return boto3.client(
        service_name,
        endpoint_url=current_app.config["AWS_ENDPOINT_URL"],
        aws_access_key_id=current_app.config["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=current_app.config["AWS_SECRET_ACCESS_KEY"],
        region_name=current_app.config["AWS_DEFAULT_REGION"],
    )
