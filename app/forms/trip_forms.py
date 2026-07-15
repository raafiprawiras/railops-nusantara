"""Trip forms."""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, SelectField, IntegerField, DateTimeLocalField,
    TextAreaField, SubmitField,
)
from wtforms.validators import DataRequired, NumberRange, Length, Optional, ValidationError

from app.models.trip import Trip


class TripForm(FlaskForm):
    """Form for creating/editing a trip."""

    trip_number = StringField(
        "Nomor Perjalanan",
        validators=[DataRequired(message="Nomor perjalanan wajib diisi."), Length(max=30)],
    )
    train_id = SelectField(
        "Kereta",
        coerce=int,
        validators=[DataRequired(message="Kereta wajib dipilih.")],
    )
    origin_station_id = SelectField(
        "Stasiun Asal",
        coerce=int,
        validators=[DataRequired(message="Stasiun asal wajib dipilih.")],
    )
    destination_station_id = SelectField(
        "Stasiun Tujuan",
        coerce=int,
        validators=[DataRequired(message="Stasiun tujuan wajib dipilih.")],
    )
    scheduled_departure = DateTimeLocalField(
        "Jadwal Berangkat",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired(message="Jadwal berangkat wajib diisi.")],
    )
    scheduled_arrival = DateTimeLocalField(
        "Jadwal Tiba",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired(message="Jadwal tiba wajib diisi.")],
    )
    platform = IntegerField(
        "Peron",
        validators=[
            DataRequired(message="Peron wajib diisi."),
            NumberRange(min=1, message="Peron harus lebih dari 0."),
        ],
    )
    status = SelectField(
        "Status",
        choices=[(s, s) for s in Trip.STATUS_CHOICES],
        validators=[DataRequired(message="Status wajib dipilih.")],
    )
    notes = TextAreaField("Catatan", validators=[Optional(), Length(max=500)])
    submit = SubmitField("Simpan")

    def validate_destination_station_id(self, field):
        """Origin and destination must differ."""
        if field.data and self.origin_station_id.data:
            if field.data == self.origin_station_id.data:
                raise ValidationError("Stasiun tujuan harus berbeda dari stasiun asal.")

    def validate_scheduled_arrival(self, field):
        """Arrival must be after departure."""
        if field.data and self.scheduled_departure.data:
            if field.data <= self.scheduled_departure.data:
                raise ValidationError("Jadwal tiba harus setelah jadwal berangkat.")


class TripStatusForm(FlaskForm):
    """Form for updating trip status."""

    new_status = SelectField(
        "Status Baru",
        choices=[(s, s) for s in Trip.STATUS_CHOICES],
        validators=[DataRequired(message="Status wajib dipilih.")],
    )
    station_id = SelectField(
        "Stasiun Saat Ini",
        coerce=int,
        validators=[Optional()],
    )
    delay_minutes = IntegerField(
        "Keterlambatan (menit)",
        default=0,
        validators=[NumberRange(min=0, message="Keterlambatan tidak boleh negatif.")],
    )
    notes = TextAreaField("Catatan", validators=[Optional(), Length(max=500)])
    submit = SubmitField("Update Status")
