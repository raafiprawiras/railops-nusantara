# Requirements — Project Foundation

## Functional Requirements

### FR-1: Health Check Endpoint
- **Endpoint**: `GET /health`
- **Response**: JSON object containing status of application, database, and LocalStack.
- **Behavior**: Jika PostgreSQL atau LocalStack tidak tersedia, endpoint tetap merespons JSON tanpa crash.
- **Fields**: `application`, `database`, `localstack`, `status`

### FR-2: Application Factory
- Flask app dibuat menggunakan `create_app()` factory pattern.
- Mendukung konfigurasi berbeda per environment (development, testing, production).

### FR-3: Docker Compose Stack
- Seluruh stack (app, postgres, localstack) dapat dijalankan dengan satu perintah `docker-compose up`.
- PostgreSQL memiliki healthcheck.
- LocalStack menyediakan service S3 dan EC2.

### FR-4: Database Connection
- Menggunakan PostgreSQL 16 via SQLAlchemy.
- Konfigurasi koneksi dari environment variable `DATABASE_URL`.

### FR-5: LocalStack Integration
- Semua Boto3 client menggunakan endpoint LocalStack (`AWS_ENDPOINT_URL`).
- Tidak ada koneksi ke AWS asli.

## Non-Functional Requirements

### NFR-1: Configuration
- Semua konfigurasi dari environment variables.
- Tidak ada credential yang di-hardcode.

### NFR-2: Modularity
- Blueprint-based routing.
- Separation of concerns: routes tipis, logika di services.

### NFR-3: Language
- Kode dalam Bahasa Inggris.
- UI dalam Bahasa Indonesia.

### NFR-4: Containerization
- Dockerfile single-stage untuk development.
- Docker Compose orchestration.
