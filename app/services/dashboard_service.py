"""Dashboard service — aggregate queries for operational statistics."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, case

from app.extensions import db
from app.models.train import Train
from app.models.trip import Trip
from app.models.incident import Incident
from app.models.document import Document
from app.models.infrastructure import InfrastructureInstance, AuditLog


def get_dashboard_stats() -> dict:
    """Get all dashboard statistics from database."""
    today = datetime.now(timezone.utc).date()
    today_start = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)
    today_end = datetime(today.year, today.month, today.day, 23, 59, 59, tzinfo=timezone.utc)

    kereta_aktif = db.session.query(func.count(Train.id)).filter(
        Train.status == "Aktif"
    ).scalar() or 0

    # Trip stats for today
    trips_today_base = Trip.query.filter(
        Trip.scheduled_departure.between(today_start, today_end)
    )
    perjalanan_hari_ini = trips_today_base.count()
    tepat_waktu = trips_today_base.filter(Trip.status == "Tiba", Trip.delay_minutes == 0).count()
    terlambat = trips_today_base.filter(
        Trip.status.in_(["Terlambat", "Tiba"]), Trip.delay_minutes > 0
    ).count()
    dibatalkan = trips_today_base.filter(Trip.status == "Dibatalkan").count()

    # Punctuality percentage
    completed = tepat_waktu + terlambat
    persen_tepat_waktu = round((tepat_waktu / completed * 100) if completed > 0 else 0, 1)

    # Average delay (all completed trips)
    avg_delay = db.session.query(func.avg(Trip.delay_minutes)).filter(
        Trip.status.in_(["Tiba", "Terlambat"]),
        Trip.delay_minutes > 0,
    ).scalar()
    rata_rata_delay = round(float(avg_delay), 1) if avg_delay else 0

    gangguan_aktif = db.session.query(func.count(Incident.id)).filter(
        Incident.status.in_(["Dilaporkan", "Dalam Penanganan"])
    ).scalar() or 0

    ec2_running = db.session.query(func.count(InfrastructureInstance.id)).filter(
        InfrastructureInstance.state == "running",
        InfrastructureInstance.terminated_at.is_(None),
    ).scalar() or 0

    dokumen_s3 = db.session.query(func.count(Document.id)).filter(
        Document.deleted_at.is_(None)
    ).scalar() or 0

    return {
        "kereta_aktif": kereta_aktif,
        "perjalanan_hari_ini": perjalanan_hari_ini,
        "tepat_waktu": tepat_waktu,
        "terlambat": terlambat,
        "dibatalkan": dibatalkan,
        "gangguan_aktif": gangguan_aktif,
        "ec2_running": ec2_running,
        "dokumen_s3": dokumen_s3,
        "persen_tepat_waktu": persen_tepat_waktu,
        "rata_rata_delay": rata_rata_delay,
    }


def get_trip_chart_data() -> dict:
    """Get chart data: doughnut (status), line (7-day delay), bar (trips/day)."""
    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=6)

    # --- Doughnut: overall trip status breakdown ---
    status_counts = db.session.query(
        Trip.status, func.count(Trip.id)
    ).group_by(Trip.status).all()
    doughnut = {status: count for status, count in status_counts}

    # --- Line: average delay per day (last 7 days) ---
    delay_labels = []
    delay_values = []
    for i in range(7):
        day = (seven_days_ago + timedelta(days=i)).date()
        day_start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
        day_end = datetime(day.year, day.month, day.day, 23, 59, 59, tzinfo=timezone.utc)

        avg = db.session.query(func.avg(Trip.delay_minutes)).filter(
            Trip.scheduled_departure.between(day_start, day_end),
            Trip.delay_minutes > 0,
        ).scalar()

        delay_labels.append(day.strftime("%a"))
        delay_values.append(round(float(avg), 1) if avg else 0)

    # --- Bar: trips per day (last 7 days) ---
    bar_labels = []
    bar_values = []
    for i in range(7):
        day = (seven_days_ago + timedelta(days=i)).date()
        day_start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
        day_end = datetime(day.year, day.month, day.day, 23, 59, 59, tzinfo=timezone.utc)

        count = Trip.query.filter(
            Trip.scheduled_departure.between(day_start, day_end)
        ).count()

        bar_labels.append(day.strftime("%d/%m"))
        bar_values.append(count)

    return {
        "doughnut": doughnut,
        "delay_labels": delay_labels,
        "delay_values": delay_values,
        "bar_labels": bar_labels,
        "bar_values": bar_values,
    }


def get_incident_priority_stats() -> dict:
    """Get incident counts grouped by priority (active incidents)."""
    results = db.session.query(
        Incident.priority, func.count(Incident.id)
    ).filter(
        Incident.status.in_(["Dilaporkan", "Dalam Penanganan"])
    ).group_by(Incident.priority).all()

    return {priority: count for priority, count in results}


def get_recent_trips(limit: int = 5) -> list[dict]:
    """Get recent trips for dashboard table."""
    trips = Trip.query.order_by(Trip.scheduled_departure.desc()).limit(limit).all()
    result = []
    for t in trips:
        if t.status == "Tiba" and t.delay_minutes == 0:
            display_status = "Tepat Waktu"
        elif t.delay_minutes > 0:
            display_status = "Terlambat"
        elif t.status == "Dibatalkan":
            display_status = "Dibatalkan"
        else:
            display_status = t.status
        result.append({
            "train": t.train.train_name if t.train else "?",
            "route": t.route_display,
            "departure": t.scheduled_departure.strftime("%H:%M") if t.scheduled_departure else "-",
            "status": display_status,
        })
    return result


def get_recent_incidents(limit: int = 5) -> list[dict]:
    """Get recent incidents for dashboard table."""
    incidents = Incident.query.order_by(Incident.created_at.desc()).limit(limit).all()
    return [
        {"location": inc.location, "type": inc.incident_type, "priority": inc.priority}
        for inc in incidents
    ]


def get_recent_audit_logs(limit: int = 5) -> list[dict]:
    """Get recent audit logs for dashboard."""
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [
        {
            "action": log.action,
            "resource": log.resource_id,
            "user": log.user.full_name if log.user else "-",
            "time": log.created_at.strftime("%d/%m %H:%M") if log.created_at else "-",
        }
        for log in logs
    ]
