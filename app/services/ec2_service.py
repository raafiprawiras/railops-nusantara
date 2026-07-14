"""EC2 service — operations via LocalStack."""

from app.services import get_boto3_client


def list_instances() -> list[dict]:
    """List all EC2 instances."""
    client = get_boto3_client("ec2")
    response = client.describe_instances()
    instances = []
    for reservation in response.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            instances.append(instance)
    return instances


def run_instance(image_id: str = "ami-12345678", instance_type: str = "t2.micro") -> dict:
    """Launch a new EC2 instance."""
    client = get_boto3_client("ec2")
    response = client.run_instances(
        ImageId=image_id,
        InstanceType=instance_type,
        MinCount=1,
        MaxCount=1,
    )
    return response["Instances"][0]


def stop_instance(instance_id: str) -> dict:
    """Stop a running EC2 instance."""
    client = get_boto3_client("ec2")
    return client.stop_instances(InstanceIds=[instance_id])


def start_instance(instance_id: str) -> dict:
    """Start a stopped EC2 instance."""
    client = get_boto3_client("ec2")
    return client.start_instances(InstanceIds=[instance_id])


def terminate_instance(instance_id: str) -> dict:
    """Terminate an EC2 instance."""
    client = get_boto3_client("ec2")
    return client.terminate_instances(InstanceIds=[instance_id])
