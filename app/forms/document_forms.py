"""Document upload forms."""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired, Optional

from app.models.document import Document


class DocumentUploadForm(FlaskForm):
    """Form for uploading a document to S3."""

    file = FileField(
        "File",
        validators=[
            FileRequired(message="File wajib dipilih."),
            FileAllowed(
                list(Document.ALLOWED_EXTENSIONS),
                message="Tipe file tidak diizinkan. Hanya: pdf, png, jpg, jpeg, docx, xlsx.",
            ),
        ],
    )
    document_category = SelectField(
        "Kategori Dokumen",
        choices=[(c, c) for c in Document.CATEGORY_CHOICES],
        validators=[DataRequired(message="Kategori wajib dipilih.")],
    )
    trip_id = SelectField(
        "Perjalanan Terkait",
        coerce=int,
        validators=[Optional()],
    )
    incident_id = SelectField(
        "Gangguan Terkait",
        coerce=int,
        validators=[Optional()],
    )
    submit = SubmitField("Upload")
