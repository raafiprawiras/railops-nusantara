"""EC2 Infrastructure routes — lifecycle management and audit log."""

import json
from datetime import datetime, timezone

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models.infrastructure import InfrastructureInstance, AuditLog
from app.services import ec2_service
from app.utils.decorators import role_required

ec2_bp = Blueprint("ec2", __name__)

PER_PAGE = 10


def _log_action(action: str, resource_id: str, description: str, metadata: dict = None):
    """Record an audit log entry."""
    log = AuditLog(
        user_id=current_user.id,
        action=action,
        resource_type="ec2_instance",
        resource_id=resource_id,
        description=description,
        metadata_json=json.dumps(metadata) if metadata else None,
    )
    db.session.add(log)


@ec2_bp.route("/infrastructure/ec2")
@login_required
def index():
    """EC2 instances overview."""
    ec2_healthy = ec2_service.check_health()
    instances = InfrastructureInstance.query.filter(
        InfrastructureInstance.terminated_at.is_(None)
    ).order_by(InfrastructureInstance.created_at.desc()).all()

    return render_template(
        "ec2/index.html",
        instances=instances,
        ec2_healthy=ec2_healthy,
        name_choices=InfrastructureInstance.NAME_CHOICES,
        purpose_choices=InfrastructureInstance.PURPOSE_CHOICES,
    )


@ec2_bp.route("/infrastructure/ec2/create", methods=["POST"])
@login_required
@role_required("administrator")
def create():
    """Create a new EC2 instance."""
    name = request.form.get("instance_name", "").strip()
    purpose = request.form.get("purpose", "").strip()

    if not name or not purpose:
        flash("Nama dan purpose wajib diisi.", "danger")
        return redirect(url_for("ec2.index"))

    result = ec2_service.run_instance(name=name, purpose=purpose)
    if not result["success"]:
        flash(f"Gagal membuat instance: {result.get('error')}", "danger")
        return redirect(url_for("ec2.index"))

    inst_data = result["instance"]

    # Save to DB
    infra = InfrastructureInstance(
        instance_id=inst_data["instance_id"],
        instance_name=name,
        instance_type=inst_data["instance_type"],
        image_id=inst_data["image_id"],
        state=inst_data["state"],
        purpose=purpose,
        created_by=current_user.id,
    )
    db.session.add(infra)
    _log_action("create", inst_data["instance_id"], f"Instance {name} dibuat.", {"purpose": purpose})
    db.session.commit()

    flash(f"Instance {name} berhasil dibuat.", "success")
    return redirect(url_for("ec2.index"))


@ec2_bp.route("/infrastructure/ec2/<instance_id>/start", methods=["POST"])
@login_required
@role_required("administrator", "operator")
def start(instance_id):
    """Start a stopped instance."""
    infra = InfrastructureInstance.query.filter_by(instance_id=instance_id).first() or abort(404)

    if not infra.can_perform("start"):
        flash(f"Instance dalam status '{infra.state}' tidak dapat di-start.", "danger")
        return redirect(url_for("ec2.index"))

    result = ec2_service.start_instance(instance_id)
    if not result["success"]:
        flash(f"Gagal: {result.get('error')}", "danger")
        return redirect(url_for("ec2.index"))

    infra.state = "running"
    _log_action("start", instance_id, f"Instance {infra.instance_name} di-start.")
    db.session.commit()

    flash(f"Instance {infra.instance_name} berhasil di-start.", "success")
    return redirect(url_for("ec2.index"))


@ec2_bp.route("/infrastructure/ec2/<instance_id>/stop", methods=["POST"])
@login_required
@role_required("administrator", "operator")
def stop(instance_id):
    """Stop a running instance."""
    infra = InfrastructureInstance.query.filter_by(instance_id=instance_id).first() or abort(404)

    if not infra.can_perform("stop"):
        flash(f"Instance dalam status '{infra.state}' tidak dapat di-stop.", "danger")
        return redirect(url_for("ec2.index"))

    result = ec2_service.stop_instance(instance_id)
    if not result["success"]:
        flash(f"Gagal: {result.get('error')}", "danger")
        return redirect(url_for("ec2.index"))

    infra.state = "stopped"
    _log_action("stop", instance_id, f"Instance {infra.instance_name} di-stop.")
    db.session.commit()

    flash(f"Instance {infra.instance_name} berhasil di-stop.", "success")
    return redirect(url_for("ec2.index"))


@ec2_bp.route("/infrastructure/ec2/<instance_id>/reboot", methods=["POST"])
@login_required
@role_required("administrator", "operator")
def reboot(instance_id):
    """Reboot a running instance."""
    infra = InfrastructureInstance.query.filter_by(instance_id=instance_id).first() or abort(404)

    if not infra.can_perform("reboot"):
        flash(f"Instance dalam status '{infra.state}' tidak dapat di-reboot.", "danger")
        return redirect(url_for("ec2.index"))

    result = ec2_service.reboot_instance(instance_id)
    if not result["success"]:
        flash(f"Gagal: {result.get('error')}", "danger")
        return redirect(url_for("ec2.index"))

    _log_action("reboot", instance_id, f"Instance {infra.instance_name} di-reboot.")
    db.session.commit()

    flash(f"Instance {infra.instance_name} berhasil di-reboot.", "success")
    return redirect(url_for("ec2.index"))


@ec2_bp.route("/infrastructure/ec2/<instance_id>/terminate", methods=["POST"])
@login_required
@role_required("administrator")
def terminate(instance_id):
    """Terminate an instance."""
    infra = InfrastructureInstance.query.filter_by(instance_id=instance_id).first() or abort(404)

    if not infra.can_perform("terminate"):
        flash(f"Instance dalam status '{infra.state}' tidak dapat di-terminate.", "danger")
        return redirect(url_for("ec2.index"))

    result = ec2_service.terminate_instance(instance_id)
    if not result["success"]:
        flash(f"Gagal: {result.get('error')}", "danger")
        return redirect(url_for("ec2.index"))

    infra.state = "terminated"
    infra.terminated_at = datetime.now(timezone.utc)
    _log_action("terminate", instance_id, f"Instance {infra.instance_name} di-terminate.")
    db.session.commit()

    flash(f"Instance {infra.instance_name} berhasil di-terminate.", "success")
    return redirect(url_for("ec2.index"))


@ec2_bp.route("/infrastructure/ec2/sync", methods=["POST"])
@login_required
@role_required("administrator", "operator")
def sync():
    """Sync local DB state with LocalStack."""
    live_instances = ec2_service.list_instances()
    if not live_instances:
        flash("Tidak dapat sync — LocalStack tidak tersedia atau tidak ada instance.", "warning")
        return redirect(url_for("ec2.index"))

    synced = 0
    for live in live_instances:
        infra = InfrastructureInstance.query.filter_by(instance_id=live["instance_id"]).first()
        if infra:
            if infra.state != live["state"]:
                infra.state = live["state"]
                if live["state"] == "terminated" and not infra.terminated_at:
                    infra.terminated_at = datetime.now(timezone.utc)
                synced += 1

    db.session.commit()
    flash(f"Sync selesai. {synced} instance diperbarui.", "success")
    return redirect(url_for("ec2.index"))


# --- Audit Log ---

@ec2_bp.route("/audit-logs")
@login_required
def audit_logs():
    """View audit log."""
    page = request.args.get("page", 1, type=int)
    query = AuditLog.query.order_by(AuditLog.created_at.desc())
    pagination = query.paginate(page=page, per_page=20, error_out=False)

    return render_template("ec2/audit_logs.html", logs=pagination.items, pagination=pagination)
