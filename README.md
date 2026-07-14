# RailOps Nusantara

Sistem Manajemen Operasional Kereta Api & Simulasi Infrastruktur Cloud.

## Deskripsi

RailOps Nusantara adalah aplikasi web internal untuk manajemen operasional kereta api sekaligus simulasi AWS EC2 dan S3 menggunakan Boto3 dan LocalStack.

## Technology Stack

- Python 3.12, Flask
- PostgreSQL 16
- Bootstrap 5, Chart.js
- Boto3 + LocalStack
- Docker & Docker Compose

## Quick Start

### Prasyarat

- Docker & Docker Compose
- Git

### Menjalankan Project

```bash
# Clone repository
git clone <repository-url>
cd railops-nusantara

# Salin environment variables
cp .env.example .env

# Jalankan seluruh stack
docker-compose up --build
```

Aplikasi berjalan di: http://localhost:5000

### Health Check

```bash
curl http://localhost:5000/health
```

Response:
```json
{
    "application": "healthy",
    "database": "healthy",
    "localstack": "healthy",
    "status": "healthy"
}
```

## Development

### Tanpa Docker (lokal)

```bash
# Buat virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Jalankan aplikasi
flask run
```

### Menjalankan Tests

```bash
pytest
```

## Struktur Project

```
app/          — Flask application
scripts/      — Operational scripts
tests/        — Automated tests
documentation/ — Project documentation
.kiro/        — Kiro steering & specs
```

## Environment Variables

Lihat `.env.example` untuk daftar lengkap variabel yang diperlukan.

## License

Internal use only.
