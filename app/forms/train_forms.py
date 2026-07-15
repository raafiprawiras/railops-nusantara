"""Train forms."""

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length, Optional

from app.models.train import Train


class TrainForm(FlaskForm):
    """Form for creating/editing a train."""

    train_code = StringField(
        "Kode Kereta",
        validators=[DataRequired(message="Kode kereta wajib diisi."), Length(max=20)],
    )
    train_name = StringField(
        "Nama Kereta",
        validators=[DataRequired(message="Nama kereta wajib diisi."), Length(max=100)],
    )
    train_type = SelectField(
        "Jenis Kereta",
        choices=[(t, t) for t in Train.TYPE_CHOICES],
        validators=[DataRequired(message="Jenis kereta wajib dipilih.")],
    )
    capacity = IntegerField(
        "Kapasitas",
        validators=[
            DataRequired(message="Kapasitas wajib diisi."),
            NumberRange(min=1, message="Kapasitas harus lebih dari 0."),
        ],
    )
    carriage_number = IntegerField(
        "Jumlah Gerbong",
        validators=[
            DataRequired(message="Jumlah gerbong wajib diisi."),
            NumberRange(min=1, message="Jumlah gerbong minimal 1."),
        ],
    )
    status = SelectField(
        "Status",
        choices=[(s, s) for s in Train.STATUS_CHOICES],
        validators=[DataRequired(message="Status wajib dipilih.")],
    )
    last_maintenance_date = DateField(
        "Tanggal Perawatan Terakhir",
        validators=[Optional()],
        format="%Y-%m-%d",
    )
    submit = SubmitField("Simpan")
