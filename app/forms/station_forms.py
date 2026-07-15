"""Station forms."""

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length

from app.models.station import Station


class StationForm(FlaskForm):
    """Form for creating/editing a station."""

    station_code = StringField(
        "Kode Stasiun",
        validators=[DataRequired(message="Kode stasiun wajib diisi."), Length(max=10)],
    )
    station_name = StringField(
        "Nama Stasiun",
        validators=[DataRequired(message="Nama stasiun wajib diisi."), Length(max=100)],
    )
    city = StringField(
        "Kota",
        validators=[DataRequired(message="Kota wajib diisi."), Length(max=100)],
    )
    province = StringField(
        "Provinsi",
        validators=[DataRequired(message="Provinsi wajib diisi."), Length(max=100)],
    )
    platform_count = IntegerField(
        "Jumlah Peron",
        validators=[
            DataRequired(message="Jumlah peron wajib diisi."),
            NumberRange(min=1, message="Jumlah peron minimal 1."),
        ],
    )
    operational_status = SelectField(
        "Status Operasional",
        choices=[(s, s) for s in Station.STATUS_CHOICES],
        validators=[DataRequired(message="Status wajib dipilih.")],
    )
    submit = SubmitField("Simpan")
