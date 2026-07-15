"""User administration and profile forms."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, ValidationError, EqualTo

from app.models.user import User


class UserCreateForm(FlaskForm):
    """Form for creating a new user (admin)."""

    full_name = StringField(
        "Nama Lengkap",
        validators=[DataRequired(message="Nama wajib diisi."), Length(max=150)],
    )
    email = StringField(
        "Email",
        validators=[DataRequired(message="Email wajib diisi."), Length(max=254)],
    )
    role = SelectField(
        "Role",
        choices=[(r, r.capitalize()) for r in User.VALID_ROLES],
        validators=[DataRequired(message="Role wajib dipilih.")],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password wajib diisi."),
            Length(min=8, message="Password minimal 8 karakter."),
        ],
    )
    confirm_password = PasswordField(
        "Konfirmasi Password",
        validators=[
            DataRequired(message="Konfirmasi password wajib diisi."),
            EqualTo("password", message="Password dan konfirmasi tidak sama."),
        ],
    )
    submit = SubmitField("Simpan")


class UserEditForm(FlaskForm):
    """Form for editing a user (admin)."""

    full_name = StringField(
        "Nama Lengkap",
        validators=[DataRequired(message="Nama wajib diisi."), Length(max=150)],
    )
    email = StringField(
        "Email",
        validators=[DataRequired(message="Email wajib diisi."), Length(max=254)],
    )
    role = SelectField(
        "Role",
        choices=[(r, r.capitalize()) for r in User.VALID_ROLES],
        validators=[DataRequired(message="Role wajib dipilih.")],
    )
    submit = SubmitField("Simpan")


class ProfileEditForm(FlaskForm):
    """Form for editing own profile."""

    full_name = StringField(
        "Nama Lengkap",
        validators=[DataRequired(message="Nama wajib diisi."), Length(max=150)],
    )
    submit = SubmitField("Simpan")


class ChangePasswordForm(FlaskForm):
    """Form for changing own password."""

    old_password = PasswordField(
        "Password Lama",
        validators=[DataRequired(message="Password lama wajib diisi.")],
    )
    new_password = PasswordField(
        "Password Baru",
        validators=[
            DataRequired(message="Password baru wajib diisi."),
            Length(min=8, message="Password baru minimal 8 karakter."),
        ],
    )
    confirm_password = PasswordField(
        "Konfirmasi Password Baru",
        validators=[
            DataRequired(message="Konfirmasi wajib diisi."),
            EqualTo("new_password", message="Password baru dan konfirmasi tidak sama."),
        ],
    )
    submit = SubmitField("Ganti Password")
