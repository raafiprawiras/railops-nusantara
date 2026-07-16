# RailOps Nusantara

**Smart Railway Operations & Cloud Infrastructure Management System**

## Deskripsi

RailOps Nusantara adalah aplikasi web internal untuk manajemen operasional kereta api sekaligus simulasi infrastruktur cloud AWS (EC2 dan S3) menggunakan Boto3 dan LocalStack. Dibangun sebagai tugas besar mata kuliah dengan arsitektur modular dan profesional.

## Tujuan

- Simulasi sistem manajemen operasional kereta api modern
- Demonstrasi integrasi AWS (S3, EC2) melalui LocalStack tanpa koneksi AWS asli
- Implementasi role-based access control, audit logging, dan reporting
- Penerapan best practices: application factory, Blueprint, service layer, CSRF, password hashing

## Fitur

| Modul | Deskripsi |
|-------|-----------|
| Dashboard | Statistik real-time, grafik Chart.js, ringkasan operasional |
| Data Kereta | CRUD kereta dengan search, filter, pagination |
| Data Stasiun | CRUD stasiun Indonesia |
| Jadwal Perjalanan | Penjadwalan, monitoring, status tracking |
| Gangguan | Pelaporan dan penanganan gangguan dengan workflow status |
| Dokumen S3 | Upload/download dokumen via LocalStack S3 |
| Infrastruktur EC2 | Simulasi lifecycle EC2 (create/start/stop/terminate) |
| Laporan | Report operasional dengan export CSV |
| Pengguna | Manajemen user, profil, role-based access |
| Audit Log | Pencatatan seluruh operasi infrastruktur |
| Autentikasi | Login/logout, remember me, password hashing |

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, Flask |
| Database | PostgreSQL 16 |
| ORM | Flask-SQLAlchemy, Flask-Migrate (Alembic) |
| Auth | Flask-Login, Flask-WTF (CSRF) |
| Frontend | Bootstrap 5, Bootstrap Icons, Chart.js |
| Cloud | Boto3, LocalStack (S3, EC2) |
| Container | Docker, Docker Compose |
| Testing | pytest |

## Arsitektur

```
┌────────────────────────────────────────────────────┐
│                  Docker Compose                     │
├──────────────┬──────────────┬──────────────────────┤
│  Flask App   │  PostgreSQL  │    LocalStack        │
│  (port 5000) │  (port 5432) │    (port 4566)       │
│              │              │    S3 + EC2          │
├──────────────┴──────────────┴──────────────────────┤
│                Docker Network                       │
└────────────────────────────────────────────────────┘
```

Arsitektur internal menggunakan:
- **Application Factory** (`create_app()`)
- **Blueprint** per modul
- **Service Layer** untuk logika bisnis dan AWS
- **Route tipis** — hanya HTTP handling

## Struktur Folder

```
railops-nusantara/
├── app/
│   ├── __init__.py          # Application factory
│   ├── extensions.py        # Flask extensions
│   ├── commands.py          # Flask CLI commands
│   ├── models/              # SQLAlchemy models
│   ├── routes/              # Blueprint routes
│   ├── services/            # Business logic + AWS
│   ├── forms/               # Flask-WTF forms
│   ├── templates/           # Jinja2 templates
│   ├── static/              # CSS, JS, images
│   └── utils/               # Decorators, helpers
├── scripts/                 # Seed & init scripts
├── tests/                   # pytest tests
├── migrations/              # Alembic migrations
├── documentation/           # Project documentation
├── .kiro/                   # Kiro steering & specs
├── config.py                # Configuration classes
├── run.py                   # Entry point
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Requirements

- Docker & Docker Compose
- Python 3.12+ (untuk development lokal)
- Git

## Instalasi & Menjalankan

### Docker (Recommended)

```bash
git clone <repository-url>
cd railops-nusantara

# Salin environment variables
cp .env.example .env

# Jalankan seluruh stack
docker-compose up --build -d

# Jalankan migration
docker-compose exec app flask db upgrade

# Inisialisasi LocalStack S3 bucket
docker-compose exec app python scripts/init_localstack.py

# Seed demo data
docker-compose exec app flask seed-demo
```

Aplikasi: http://localhost:5000

### Development Lokal (tanpa Docker)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt

# Pastikan PostgreSQL running di localhost:5432
flask db upgrade
flask seed-demo
flask run
```

## Environment Variables

| Variable | Deskripsi | Default |
|----------|-----------|---------|
| FLASK_APP | Entry point | run.py |
| FLASK_DEBUG | Debug mode | 1 |
| SECRET_KEY | Session secret | dev-secret-key |
| DATABASE_URL | PostgreSQL connection | postgresql://railops:railops_secret@localhost:5432/railops_nusantara |
| AWS_ACCESS_KEY_ID | LocalStack credential | test |
| AWS_SECRET_ACCESS_KEY | LocalStack credential | test |
| AWS_DEFAULT_REGION | Region | ap-southeast-1 |
| AWS_ENDPOINT_URL | LocalStack endpoint | http://localhost:4566 |
| S3_BUCKET_NAME | S3 bucket name | railops-bucket |
| MAX_CONTENT_LENGTH | Max upload size (bytes) | 16777216 |
| EC2_IMAGE_ID | AMI ID untuk simulasi | ami-12345678 |

## Docker Compose Services

| Service | Image | Port | Deskripsi |
|---------|-------|------|-----------|
| app | Build dari Dockerfile | 5000 | Flask application |
| postgres | postgres:16 | 5432 | Database utama |
| localstack | localstack/localstack | 4566 | Simulasi AWS (S3, EC2) |

## Migration

```bash
flask db upgrade          # Jalankan semua migration
flask db migrate -m "msg" # Generate migration baru
flask db downgrade        # Rollback satu langkah
```

## Seed Data

```bash
flask seed-demo           # Seed data demo (idempotent)
flask seed-demo --reset   # Reset + reseed (development only)
```

## Akun Demo

| Email | Password | Role |
|-------|----------|------|
| admin@railops.local | Admin123! | Administrator |
| budi@railops.local | Operator1! | Operator |
| dewi@railops.local | Operator2! | Operator |
| andi@railops.local | Supervisor1! | Supervisor |

## Menjalankan Test

```bash
pytest                           # Semua test
pytest tests/test_auth.py -v     # Test spesifik
pytest -k "security" -v          # By keyword
```

## LocalStack S3

```bash
# Inisialisasi bucket
python scripts/init_localstack.py

# Bucket akan dibuat otomatis saat upload jika belum ada
```

## LocalStack EC2

```bash
# Inisialisasi demo instances
python scripts/init_ec2_demo.py
```

## Role Matrix

| Fitur | Administrator | Operator | Supervisor |
|-------|:---:|:---:|:---:|
| Dashboard | ✓ | ✓ | ✓ |
| Data Kereta/Stasiun (view) | ✓ | ✓ | ✓ |
| Data Kereta/Stasiun (CRUD) | ✓ | ✗ | ✗ |
| Jadwal (view) | ✓ | ✓ | ✓ |
| Jadwal (create/edit) | ✓ | ✓ | ✗ |
| Jadwal (delete) | ✓ | ✗ | ✗ |
| Monitoring & Status Update | ✓ | ✓ | ✗ |
| Gangguan (create/edit) | ✓ | ✓ | ✗ |
| Gangguan (close) | ✓ | ✗ | ✓ |
| Dokumen (upload) | ✓ | ✓ | ✗ |
| Dokumen (download) | ✓ | ✓ | ✓ |
| Dokumen (delete) | ✓ | ✗ | ✗ |
| EC2 (create/terminate) | ✓ | ✗ | ✗ |
| EC2 (start/stop/reboot) | ✓ | ✓ | ✗ |
| Laporan | ✓ | ✓* | ✓ |
| Manajemen Pengguna | ✓ | ✗ | ✗ |
| Audit Log | ✓ | ✓ | ✓ |

*Operator: hanya laporan perjalanan dan gangguan

## Endpoint Utama

| URL | Deskripsi |
|-----|-----------|
| / | Redirect ke dashboard |
| /dashboard | Dashboard operasional |
| /login | Halaman login |
| /trains | Data kereta |
| /stations | Data stasiun |
| /trips | Jadwal perjalanan |
| /trips/monitoring | Monitoring aktif |
| /incidents | Laporan gangguan |
| /documents | Dokumen S3 |
| /cloud/s3 | Panel Cloud S3 |
| /infrastructure/ec2 | Infrastruktur EC2 |
| /reports | Laporan operasional |
| /audit-logs | Audit log |
| /users | Manajemen pengguna |
| /profile | Profil sendiri |
| /health | Health check (JSON) |

## Keamanan

- Password di-hash dengan Werkzeug (scrypt/pbkdf2)
- CSRF protection pada seluruh form
- Open redirect prevention
- File upload: validasi extension + MIME type
- Path traversal protection pada download
- CSV injection prevention pada export
- SECRET_KEY validation di production
- AWS_ENDPOINT_URL guard — menolak operasi jika kosong
- Content-Disposition header sanitization
- Role-based access control
- Audit logging

## Limitations

- Simulasi AWS — tidak terhubung ke AWS asli
- Email service tidak tersedia (reset password via flash)
- PDF export belum implementasi (gunakan print-friendly HTML)
- LocalStack free tier: data non-persistent setelah restart container
- Single-node deployment (tidak HA)

## Troubleshooting

Lihat `documentation/troubleshooting.md` untuk panduan lengkap.

## Lisensi

Internal use only — Tugas Besar.

## Informasi Tugas Akademik

| Item | Detail |
|------|--------|
| Nama Project | RailOps Nusantara |
| Tipe | Smart Railway Operations & Cloud Infrastructure Management System |
| Stack Utama | Python, Flask, PostgreSQL, Boto3, LocalStack, Docker |
| Simulasi Cloud | AWS EC2 + S3 via LocalStack |
| Arsitektur | Monolithic Modular (Flask Application Factory + Blueprint) |
