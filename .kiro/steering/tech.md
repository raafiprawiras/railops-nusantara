# Technical Standards — RailOps Nusantara

## Technology Stack

| Layer         | Technology                          |
|---------------|-------------------------------------|
| Language      | Python 3.12                         |
| Framework     | Flask                               |
| ORM           | Flask-SQLAlchemy                    |
| Migrations    | Flask-Migrate (Alembic)             |
| Auth          | Flask-Login                         |
| Forms         | Flask-WTF                           |
| Database      | PostgreSQL 16                       |
| Frontend      | Bootstrap 5, Bootstrap Icons, JS    |
| Charts        | Chart.js                            |
| Cloud Sim     | Boto3 + LocalStack                  |
| Container     | Docker, Docker Compose              |
| Testing       | pytest                              |

## Coding Standards

- Nama variabel, fungsi, class dalam **Bahasa Inggris**.
- UI text, label, pesan error dalam **Bahasa Indonesia**.
- Gunakan type hints di Python.
- Gunakan docstrings untuk fungsi publik.
- Ikuti PEP 8.
- Maksimum 120 karakter per baris.

## Architecture Rules

- Flask application factory pattern (`create_app()`).
- Blueprint per modul fungsional.
- Route harus tipis — logika bisnis di `app/services/`.
- Semua konfigurasi dari environment variables, tidak hardcode.
- Boto3 client WAJIB menggunakan `endpoint_url` dari environment (LocalStack).
- Tidak boleh ada koneksi ke AWS asli.

## Database

- PostgreSQL 16 (bukan SQLite).
- Migrasi menggunakan Flask-Migrate.
- Model di `app/models/`.

## Testing

- Framework: pytest.
- Test files di folder `tests/`.
- Naming: `test_<module>.py`.

## Security

- Jangan hardcode credentials.
- Secret key dari environment variable.
- CSRF protection via Flask-WTF.
- Password hashing menggunakan Werkzeug.

## Forbidden

- React, Vue, Angular, Svelte.
- Tailwind CSS.
- Node.js, npm, yarn, webpack, vite.
- Koneksi AWS asli.
- SQLite sebagai database utama.
