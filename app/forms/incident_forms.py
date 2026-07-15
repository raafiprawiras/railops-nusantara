"""Incident forms."""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, SelectField, TextAreaField, DateTimeLocalField, SubmitField,
)
from wtforms.validators import DataRequired, Length, Optional

from app.models.incident import Incident


class IncidentForm(FlaskForm):
    """Form for creating/editing an incident."""

    incident_number = StringField(
        "Nomor Gangguan",
        validators=[DataRequired(message="Nomor gangguan wajib diisi."), Length(max=30)],
    )
    trip_id = SelectField(
        "Perjalanan Terkait",
        coerce=int,
        validators=[DataRequired(message="Perjalanan wajib dipilih.")],
    )
    incident_type = SelectField(
        "Jenis Gangguan",
        choices=[(t, t) for t in Incident.TYPE_CHOICES],
        validators=[DataRequired(message="Jenis gangguan wajib dipilih.")],
    )
    location = StringField(
        "Lokasi",
        validators=[DataRequired(message="Lokasi wajib diisi."), Length(max=200)],
    )
    occurred_at = DateTimeLocalField(
        "Waktu Kejadian",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired(message="Waktu kejadian wajib diisi.")],
    )
    priority = SelectField(
        "Prioritas",
        choices=[(p, p) for p in Incident.PRIORITY_CHOICES],
        validators=[DataRequired(message="Prioritas wajib dipilih.")],
    )
    description = TextAreaField(
        "Deskripsi",
        validators=[DataRequired(message="Deskripsi wajib diisi."), Length(max=2000)],
    )
    assigned_to = SelectField(
        "Ditugaskan Kepada",
        coerce=int,
        validators=[Optional()],
    )
    submit = SubmitField("Simpan")


class IncidentStatusForm(FlaskForm):
    """Form for updating incident status."""

    new_status = SelectField(
        "Status Baru",
        choices=[(s, s) for s in Incident.STATUS_CHOICES],
        validators=[DataRequired(message="Status wajib dipilih.")],
    )
    notes = TextAreaField("Catatan", validators=[Optional(), Length(max=1000)])
    resolution_notes = TextAreaField("Catatan Penyelesaian", validators=[Optional(), Length(max=2000)])
    submit = SubmitField("Update Status")
