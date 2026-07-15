"""Authentication forms."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError


def _validate_email_format(form, field):
    """Validate email format without strict deliverability check.

    Allows .local domains for development environments.
    """
    value = field.data.strip() if field.data else ""
    if not value or "@" not in value:
        raise ValidationError("Format email tidak valid.")
    local, _, domain = value.rpartition("@")
    if not local or not domain or "." not in domain:
        raise ValidationError("Format email tidak valid.")


class LoginForm(FlaskForm):
    """Login form with CSRF protection."""

    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email wajib diisi."),
            _validate_email_format,
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password wajib diisi."),
            Length(min=1, max=128),
        ],
    )
    remember = BooleanField("Ingat saya")
    submit = SubmitField("Masuk")
