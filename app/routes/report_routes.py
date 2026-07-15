"""Report routes — operational reports with CSV export."""

import csv
import io
from datetime import datetime, timezone

from flask import Blueprint, render_template, request, Response
from flask_login import login_required
from sqlalchemy import func

from app.extensions import db
from app.models.trip import Trip
from app.models.train import Train
from app.models.station import Station
from app.models.incident import Incident
from app.models.document import Document
from app.models.infrastructure import AuditLog
from app.utils.decorators import role_required

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")

PER_PAGE = 20


def _escape_csv_value(val) -> str:
    """Escape CSV values to prevent formula injection."""
    s = str(val) if val is not None else ""
    if s and s[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + s
    return s


def _csv_response(headers: list, rows: list, filename: str) -> Response:
    """Generate CSV response with proper headers."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in rows:
        writer.writerow([_escape_csv_value(v) for v in row])

    response = Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
    return response


def _parse_date(date_str: str):
    """Parse date string to datetime or None."""
    if not date_str:
        return None
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return d.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


@reports_bp.route("")
@login_required
@role_required("administrator", "supervisor", "operator")
def index():
    """Reports index page."""
    return render_template("reports/index.html")


@reports_bp.route("/trips")
@login_required
@role_required("administrator", "supervisor", "operator")
def trips_report():
    """Trip report with filters."""
    page = request.args.get("page", 1, type=int)
    status = request.args.get("status", "", type=str).strip()
    train_id = request.args.get("train_id", 0, type=int)
    start_date = request.args.get("start_date", "", type=str).strip()
    end_date = request.args.get("end_date", "", type=str).strip()

    query = Trip.query
    if status:
        query = query.filter(Trip.status == status)
    if train_id:
        query = query.filter(Trip.train_id == train_id)
    if start_date:
        sd = _parse_date(start_date)
        if sd:
            query = query.filter(Trip.scheduled_departure >= sd)
    if end_date:
        ed = _parse_date(end_date)
        if ed:
            query = query.filter(Trip.scheduled_departure <= ed.replace(hour=23, minute=59, second=59))

    total = query.count()
    on_time = query.filter(Trip.status == "Tiba", Trip.delay_minutes == 0).count()
    delayed = query.filter(Trip.delay_minutes > 0).count()

    query = query.order_by(Trip.scheduled_departure.desc())
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    trains = Train.query.order_by(Train.train_name).all()

    return render_template(
        "reports/trips.html",
        trips=pagination.items, pagination=pagination,
        total=total, on_time=on_time, delayed=delayed,
        status=status, train_id=train_id, start_date=start_date, end_date=end_date,
        status_choices=Trip.STATUS_CHOICES, trains=trains,
    )


@reports_bp.route("/trips/csv")
@login_required
@role_required("administrator", "supervisor", "operator")
def trips_csv():
    """Export trips as CSV."""
    status = request.args.get("status", "", type=str).strip()
    start_date = request.args.get("start_date", "", type=str).strip()
    end_date = request.args.get("end_date", "", type=str).strip()

    query = Trip.query
    if status:
        query = query.filter(Trip.status == status)
    if start_date:
        sd = _parse_date(start_date)
        if sd:
            query = query.filter(Trip.scheduled_departure >= sd)
    if end_date:
        ed = _parse_date(end_date)
        if ed:
            query = query.filter(Trip.scheduled_departure <= ed.replace(hour=23, minute=59, second=59))

    trips = query.order_by(Trip.scheduled_departure.desc()).all()
    headers = ["No. Perjalanan", "Kereta", "Asal", "Tujuan", "Berangkat", "Tiba", "Status", "Delay (min)"]
    rows = []
    for t in trips:
        rows.append([
            t.trip_number,
            t.train.train_name if t.train else "",
            t.origin_station.station_name if t.origin_station else "",
            t.destination_station.station_name if t.destination_station else "",
            t.scheduled_departure.strftime("%Y-%m-%d %H:%M") if t.scheduled_departure else "",
            t.scheduled_arrival.strftime("%Y-%m-%d %H:%M") if t.scheduled_arrival else "",
            t.status,
            t.delay_minutes,
        ])

    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    return _csv_response(headers, rows, f"laporan_perjalanan_{today}.csv")


@reports_bp.route("/incidents")
@login_required
@role_required("administrator", "supervisor", "operator")
def incidents_report():
    """Incident report."""
    page = request.args.get("page", 1, type=int)
    status = request.args.get("status", "", type=str).strip()
    priority = request.args.get("priority", "", type=str).strip()
    start_date = request.args.get("start_date", "", type=str).strip()
    end_date = request.args.get("end_date", "", type=str).strip()

    query = Incident.query
    if status:
        query = query.filter(Incident.status == status)
    if priority:
        query = query.filter(Incident.priority == priority)
    if start_date:
        sd = _parse_date(start_date)
        if sd:
            query = query.filter(Incident.occurred_at >= sd)
    if end_date:
        ed = _parse_date(end_date)
        if ed:
            query = query.filter(Incident.occurred_at <= ed.replace(hour=23, minute=59, second=59))

    total = query.count()
    query_ordered = query.order_by(Incident.occurred_at.desc())
    pagination = query_ordered.paginate(page=page, per_page=PER_PAGE, error_out=False)

    return render_template(
        "reports/incidents.html",
        incidents=pagination.items, pagination=pagination, total=total,
        status=status, priority=priority, start_date=start_date, end_date=end_date,
        status_choices=Incident.STATUS_CHOICES, priority_choices=Incident.PRIORITY_CHOICES,
    )


@reports_bp.route("/incidents/csv")
@login_required
@role_required("administrator", "supervisor", "operator")
def incidents_csv():
    """Export incidents as CSV."""
    query = Incident.query.order_by(Incident.occurred_at.desc())
    incidents = query.all()

    headers = ["No. Gangguan", "Jenis", "Lokasi", "Prioritas", "Status", "Waktu Kejadian", "Deskripsi"]
    rows = []
    for inc in incidents:
        rows.append([
            inc.incident_number, inc.incident_type, inc.location,
            inc.priority, inc.status,
            inc.occurred_at.strftime("%Y-%m-%d %H:%M") if inc.occurred_at else "",
            inc.description[:100] if inc.description else "",
        ])

    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    return _csv_response(headers, rows, f"laporan_gangguan_{today}.csv")


@reports_bp.route("/punctuality")
@login_required
@role_required("administrator", "supervisor")
def punctuality_report():
    """Punctuality analysis report."""
    completed_trips = Trip.query.filter(Trip.status.in_(["Tiba", "Terlambat"])).all()
    total = len(completed_trips)
    on_time = sum(1 for t in completed_trips if t.delay_minutes == 0)
    delayed = sum(1 for t in completed_trips if t.delay_minutes > 0)
    cancelled = Trip.query.filter(Trip.status == "Dibatalkan").count()
    avg_delay = sum(t.delay_minutes for t in completed_trips if t.delay_minutes > 0)
    avg_delay = round(avg_delay / delayed, 1) if delayed > 0 else 0
    pct = round((on_time / total * 100) if total > 0 else 0, 1)

    # Worst trains by delay
    worst_trains = db.session.query(
        Train.train_name, func.avg(Trip.delay_minutes).label("avg_delay")
    ).join(Trip, Trip.train_id == Train.id).filter(
        Trip.delay_minutes > 0
    ).group_by(Train.train_name).order_by(func.avg(Trip.delay_minutes).desc()).limit(5).all()

    # Worst routes by delay
    origin = db.aliased(Station)
    dest = db.aliased(Station)
    worst_routes = db.session.query(
        origin.station_name, dest.station_name, func.avg(Trip.delay_minutes).label("avg_delay")
    ).join(origin, Trip.origin_station_id == origin.id
    ).join(dest, Trip.destination_station_id == dest.id
    ).filter(Trip.delay_minutes > 0
    ).group_by(origin.station_name, dest.station_name
    ).order_by(func.avg(Trip.delay_minutes).desc()).limit(5).all()

    return render_template(
        "reports/punctuality.html",
        total=total, on_time=on_time, delayed=delayed, cancelled=cancelled,
        avg_delay=avg_delay, pct=pct,
        worst_trains=worst_trains, worst_routes=worst_routes,
    )


@reports_bp.route("/infrastructure")
@login_required
@role_required("administrator", "supervisor")
def infrastructure_report():
    """Infrastructure audit log report."""
    page = request.args.get("page", 1, type=int)
    query = AuditLog.query.order_by(AuditLog.created_at.desc())
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)

    return render_template("reports/infrastructure.html", logs=pagination.items, pagination=pagination)


@reports_bp.route("/infrastructure/csv")
@login_required
@role_required("administrator", "supervisor")
def infrastructure_csv():
    """Export infrastructure audit log as CSV."""
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).all()
    headers = ["Waktu", "User", "Aksi", "Resource Type", "Resource ID", "Deskripsi"]
    rows = []
    for log in logs:
        rows.append([
            log.created_at.strftime("%Y-%m-%d %H:%M") if log.created_at else "",
            log.user.full_name if log.user else "",
            log.action, log.resource_type, log.resource_id, log.description,
        ])

    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    return _csv_response(headers, rows, f"laporan_infrastruktur_{today}.csv")


@reports_bp.route("/documents")
@login_required
@role_required("administrator", "supervisor")
def documents_report():
    """Document report."""
    page = request.args.get("page", 1, type=int)
    category = request.args.get("category", "", type=str).strip()

    query = Document.query.filter(Document.deleted_at.is_(None))
    if category:
        query = query.filter(Document.document_category == category)

    query = query.order_by(Document.uploaded_at.desc())
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    total = Document.query.filter(Document.deleted_at.is_(None)).count()

    return render_template(
        "reports/documents.html",
        documents=pagination.items, pagination=pagination, total=total,
        category=category, category_choices=Document.CATEGORY_CHOICES,
    )
