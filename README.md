# RailOps Nusantara

Sistem Manajemen Operasional Kereta Api & Simulasi Infrastruktur Cloud.

## Deskripsi

RailOps Nusantara adalah aplikasi web internal untuk manajemen operasional kereta api sekaligus simulasi AWS EC2 dan S3 menggunakan Boto3 dan LocalStack.

## Technology Stack

- Python 3.12, Flask
- PostgreSQL 16
- Bootstrap 5, Chart.js
- Boto3 + LocalStack (EC2, S3)
- Docker & Docker Compose
- pytest

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

# Jalankan migration
docker-compose exec app flask db upgrade

# Inisialisasi LocalStack bucket
docker-compose exec app python scripts/init_localstack.py

# Seed demo data
docker-compose exec app flask seed-demo
```

Aplikasi berjalan di: http://localhost:5000

### Akun Demo

| Email | Password | Role |
|-------|----------|------|
| admin@railops.local | Admin123! | Administrator |
| budi@railops.local | Operator1! | Operator |
| dewi@railops.local | Operator2! | Operator |
| andi@railops.local | Supervisor1! | Supervisor |

### Health Check

```bash
curl http://localhost:5000/health
```

## Development (Lokal tanpa Docker)

```bash
# Buat virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Jalankan migration
flask db upgrade

# Seed demo data
flask seed-demo

# Jalankan aplikasi
flask run
```

### Seed Demo Data

```bash
# Seed data (idempotent, aman dijalankan berulang kali)
flask seed-demo

# Reset dan seed ulang (development only)
flask seed-demo --reset

# Atau via script langsung
python scripts/seed_demo.py
python scripts/seed_demo.py --reset
```

### Menjalankan Tests

```bash
pytest
```

## Struktur Project

```
app/          — Flask application (factory, routes, models, services, templates)
scripts/      — Operational & seed scripts
tests/        — Automated tests
documentation/ — Project documentation
.kiro/        — Kiro steering & specs
```

## Fitur Utama

- Dashboard operasional real-time
- Manajemen kereta dan stasiun
- Penjadwalan perjalanan + monitoring
- Pelaporan gangguan + penanganan
- Manajemen dokumen S3 (LocalStack)
- Simulasi infrastruktur EC2 (LocalStack)
- Laporan operasional + export CSV
- Manajemen pengguna + role-based access
- Audit log

## Environment Variables

Lihat `.env.example` untuk daftar lengkap variabel yang diperlukan.

## License

Internal use only.
