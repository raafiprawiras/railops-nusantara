"""Tests for EC2 Infrastructure Management.

Unit tests mock the EC2 service. Integration tests require LocalStack.
"""

from unittest.mock import patch
from datetime import datetime, timezone

from app.models.infrastructure import InfrastructureInstance, AuditLog


def _create_instance(db, state="running", instance_id="i-test123"):
    """Helper to create a tracked instance."""
    infra = InfrastructureInstance(
        instance_id=instance_id,
        instance_name="RailOps-Test-Server",
        instance_type="t2.micro",
        image_id="ami-12345678",
        state=state,
        purpose="Web Application",
        created_by=1,
    )
    db.session.add(infra)
    db.session.commit()
    return infra


# === UNIT TESTS ===

def test_ec2_page_accessible(admin_client, db):
    """EC2 page loads."""
    with patch("app.routes.ec2_routes.ec2_service") as mock_ec2:
        mock_ec2.check_health.return_value = False
        response = admin_client.get("/infrastructure/ec2")
        assert response.status_code == 200


@patch("app.routes.ec2_routes.ec2_service")
def test_create_instance(mock_ec2, admin_client, db):
    """Admin can create an instance."""
    mock_ec2.run_instance.return_value = {
        "success": True,
        "instance": {
            "instance_id": "i-new123",
            "instance_name": "RailOps-Web-Server",
            "instance_type": "t2.micro",
            "image_id": "ami-12345678",
            "state": "pending",
            "purpose": "Web Application",
        },
    }

    response = admin_client.post("/infrastructure/ec2/create", data={
        "instance_name": "RailOps-Web-Server",
        "purpose": "Web Application",
    }, follow_redirects=False)
    assert response.status_code == 302

    infra = InfrastructureInstance.query.filter_by(instance_id="i-new123").first()
    assert infra is not None
    assert infra.instance_name == "RailOps-Web-Server"


@patch("app.routes.ec2_routes.ec2_service")
def test_create_records_audit_log(mock_ec2, admin_client, db):
    """Creating an instance records audit log."""
    mock_ec2.run_instance.return_value = {
        "success": True,
        "instance": {
            "instance_id": "i-audit123",
            "instance_name": "Test",
            "instance_type": "t2.micro",
            "image_id": "ami-12345678",
            "state": "pending",
            "purpose": "Monitoring",
        },
    }

    admin_client.post("/infrastructure/ec2/create", data={
        "instance_name": "RailOps-Monitoring-Server",
        "purpose": "Monitoring",
    })

    log = AuditLog.query.filter_by(resource_id="i-audit123").first()
    assert log is not None
    assert log.action == "create"


@patch("app.routes.ec2_routes.ec2_service")
def test_stop_running_instance(mock_ec2, admin_client, db):
    """Can stop a running instance."""
    infra = _create_instance(db, state="running")
    mock_ec2.stop_instance.return_value = {"success": True, "message": "Stopped."}

    response = admin_client.post(
        f"/infrastructure/ec2/{infra.instance_id}/stop", follow_redirects=False
    )
    assert response.status_code == 302

    db.session.refresh(infra)
    assert infra.state == "stopped"


@patch("app.routes.ec2_routes.ec2_service")
def test_start_stopped_instance(mock_ec2, admin_client, db):
    """Can start a stopped instance."""
    infra = _create_instance(db, state="stopped", instance_id="i-start1")
    mock_ec2.start_instance.return_value = {"success": True, "message": "Started."}

    response = admin_client.post(
        f"/infrastructure/ec2/{infra.instance_id}/start", follow_redirects=False
    )
    assert response.status_code == 302

    db.session.refresh(infra)
    assert infra.state == "running"


@patch("app.routes.ec2_routes.ec2_service")
def test_terminate_instance(mock_ec2, admin_client, db):
    """Admin can terminate an instance."""
    infra = _create_instance(db, state="running", instance_id="i-term1")
    mock_ec2.terminate_instance.return_value = {"success": True, "message": "Terminated."}

    response = admin_client.post(
        f"/infrastructure/ec2/{infra.instance_id}/terminate", follow_redirects=False
    )
    assert response.status_code == 302

    db.session.refresh(infra)
    assert infra.state == "terminated"
    assert infra.terminated_at is not None


def test_invalid_state_action_rejected(admin_client, db):
    """Cannot start an already running instance."""
    infra = _create_instance(db, state="running", instance_id="i-invalid1")

    response = admin_client.post(
        f"/infrastructure/ec2/{infra.instance_id}/start", follow_redirects=True
    )
    assert response.status_code == 200
    assert b"tidak dapat di-start" in response.data


def test_operator_cannot_create(logged_in_client, db):
    """Operator cannot create instances."""
    response = logged_in_client.post("/infrastructure/ec2/create", data={
        "instance_name": "Test", "purpose": "Test",
    })
    assert response.status_code == 403


def test_operator_cannot_terminate(logged_in_client, db):
    """Operator cannot terminate instances."""
    infra = _create_instance(db, state="running", instance_id="i-opterm")
    response = logged_in_client.post(f"/infrastructure/ec2/{infra.instance_id}/terminate")
    assert response.status_code == 403


@patch("app.routes.ec2_routes.ec2_service")
def test_operator_can_stop(mock_ec2, logged_in_client, db, active_user):
    """Operator can stop instances."""
    infra = _create_instance(db, state="running", instance_id="i-opstop")
    mock_ec2.stop_instance.return_value = {"success": True, "message": "ok"}

    response = logged_in_client.post(
        f"/infrastructure/ec2/{infra.instance_id}/stop", follow_redirects=False
    )
    assert response.status_code == 302


@patch("app.routes.ec2_routes.ec2_service")
def test_localstack_unavailable_no_crash(mock_ec2, admin_client, db):
    """If LocalStack is unavailable, create fails gracefully."""
    mock_ec2.run_instance.return_value = {"success": False, "error": "LocalStack tidak tersedia."}

    response = admin_client.post("/infrastructure/ec2/create", data={
        "instance_name": "Test", "purpose": "Backup",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Gagal" in response.data


def test_audit_log_page(admin_client, db):
    """Audit log page loads."""
    response = admin_client.get("/audit-logs")
    assert response.status_code == 200


def test_dashboard_ec2_count(admin_client, db):
    """Dashboard shows EC2 running count from DB."""
    _create_instance(db, state="running", instance_id="i-dash1")
    _create_instance(db, state="stopped", instance_id="i-dash2")

    response = admin_client.get("/dashboard")
    assert response.status_code == 200
    assert b"EC2 Running" in response.data


def test_service_response_normalization(app):
    """EC2 service normalizes Boto3 response."""
    from app.services.ec2_service import _normalize_instance

    raw = {
        "InstanceId": "i-abc123",
        "InstanceType": "t2.micro",
        "ImageId": "ami-12345678",
        "State": {"Name": "running", "Code": 16},
        "Tags": [
            {"Key": "Name", "Value": "TestServer"},
            {"Key": "Purpose", "Value": "Web Application"},
        ],
    }
    result = _normalize_instance(raw)
    assert result["instance_id"] == "i-abc123"
    assert result["instance_name"] == "TestServer"
    assert result["state"] == "running"
    assert result["purpose"] == "Web Application"
