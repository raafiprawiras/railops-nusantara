# RailOps Nusantara

**Sistem Manajemen Operasional Kereta Api Cerdas & Infrastruktur Cloud**

## Deskripsi

RailOps Nusantara adalah aplikasi web internal untuk manajemen operasional kereta api sekaligus simulasi infrastruktur cloud AWS (EC2 dan S3) menggunakan Boto3 dan LocalStack. Dibangun sebagai tugas besar mata kuliah dengan arsitektur modular dan profesional.

## Tujuan

- Simulasi sistem manajemen operasional kereta api modern
- Demonstrasi integrasi AWS (S3, EC2) melalui LocalStack tanpa koneksi AWS asli
- Implementasi role-based access control, audit logging, dan pelaporan
- Penerapan best practices: application factory, Blueprint, service layer, CSRF, password hashing

## Fitur

| Modul | Deskripsi |
|-------|-----------|
| Dashboard | Statistik real-time, grafik Chart.js, ringkasan operasional |
| Data Kereta | CRUD kereta dengan pencarian, filter, pagination |
| Data Stasiun | CRUD stasiun Indonesia |
| Jadwal Perjalanan | Penjadwalan, monitoring, pelacakan status |
| Gangguan | Pelaporan dan penanganan gangguan dengan alur kerja status |
| Dokumen S3 | Upload/download dokumen via LocalStack S3 |
| Infrastruktur EC2 | Simulasi siklus hidup EC2 (buat/mulai/hentikan/terminasi) |
| Laporan | Laporan operasional dengan ekspor CSV |
| Pengguna | Manajemen pengguna, profil, kontrol akses berbasis role |
| Audit Log | Pencatatan seluruh operasi infrastruktur |
| Autentikasi | Login/logout, ingat saya, hashing password |

## Tumpukan Teknologi

| Lapisan | Teknologi |
|---------|-----------|
| Backend | Python 3.12, Flask |
| Database | PostgreSQL 16 |
| ORM | Flask-SQLAlchemy, Flask-Migrate (Alembic) |
| Autentikasi | Flask-Login, Flask-WTF (CSRF) |
| Frontend | Bootstrap 5, Bootstrap Icons, Chart.js |
| Cloud | Boto3, LocalStack (S3, EC2) |
| Container | Docker, Docker Compose |
| Pengujian | pytest |

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
- **Route tipis** — hanya penanganan HTTP

## Struktur Folder

```
railops-nusantara/
├── app/
│   ├── __init__.py          # Application factory
│   ├── extensions.py        # Ekstensi Flask
│   ├── commands.py          # Perintah CLI Flask
│   ├── models/              # Model SQLAlchemy
│   ├── routes/              # Route Blueprint
│   ├── services/            # Logika bisnis + AWS
│   ├── forms/               # Form Flask-WTF
│   ├── templates/           # Template Jinja2
│   ├── static/              # CSS, JS, gambar
│   └── utils/               # Decorator, helper
├── scripts/                 # Script seed & inisialisasi
├── tests/                   # Tes pytest
├── migrations/              # Migrasi Alembic
├── documentation/           # Dokumentasi project
├── .kiro/                   # Kiro steering & specs
├── config.py                # Kelas konfigurasi
├── run.py                   # Titik masuk aplikasi
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Prasyarat

- Docker & Docker Compose
- Python 3.12+ (untuk development lokal)
- Git

## Instalasi & Menjalankan

### Docker (Direkomendasikan)

```bash
git clone <repository-url>
cd railops-nusantara

# Salin variabel lingkungan
cp .env.example .env

# Jalankan seluruh stack
docker-compose up --build -d

# Jalankan migrasi database
docker-compose exec app flask db upgrade

# Inisialisasi bucket LocalStack S3
docker-compose exec app python scripts/init_localstack.py

# Isi data demo
docker-compose exec app flask seed-demo
```

Aplikasi tersedia di: http://localhost:5000

### Development Lokal (tanpa Docker)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt

# Pastikan PostgreSQL berjalan di localhost:5432
flask db upgrade
flask seed-demo
flask run
```

## Variabel Lingkungan

| Variabel | Deskripsi | Default |
|----------|-----------|---------|
| FLASK_APP | Titik masuk | run.py |
| FLASK_DEBUG | Mode debug | 1 |
| SECRET_KEY | Secret sesi | dev-secret-key |
| DATABASE_URL | Koneksi PostgreSQL | postgresql://railops:railops_secret@localhost:5432/railops_nusantara |
| AWS_ACCESS_KEY_ID | Credential LocalStack | test |
| AWS_SECRET_ACCESS_KEY | Credential LocalStack | test |
| AWS_DEFAULT_REGION | Region | ap-southeast-1 |
| AWS_ENDPOINT_URL | Endpoint LocalStack | http://localhost:4566 |
| S3_BUCKET_NAME | Nama bucket S3 | railops-bucket |
| MAX_CONTENT_LENGTH | Ukuran upload maksimal (byte) | 16777216 |
| EC2_IMAGE_ID | ID AMI untuk simulasi | ami-12345678 |

## Layanan Docker Compose

| Layanan | Image | Port | Deskripsi |
|---------|-------|------|-----------|
| app | Build dari Dockerfile | 5000 | Aplikasi Flask |
| postgres | postgres:16 | 5432 | Database utama |
| localstack | localstack/localstack | 4566 | Simulasi AWS (S3, EC2) |

## Migrasi Database

```bash
flask db upgrade          # Jalankan semua migrasi
flask db migrate -m "msg" # Generate migrasi baru
flask db downgrade        # Rollback satu langkah
```

## Data Seed

```bash
flask seed-demo           # Isi data demo (idempotent, aman dijalankan berulang)
flask seed-demo --reset   # Reset + isi ulang (khusus development)
```

## Akun Demo

| Email | Password | Role |
|-------|----------|------|
| admin@railops.local | Admin123! | Administrator |
| budi@railops.local | Operator1! | Operator |
| dewi@railops.local | Operator2! | Operator |
| andi@railops.local | Supervisor1! | Supervisor |

## Menjalankan Tes

```bash
pytest                           # Semua tes
pytest tests/test_auth.py -v     # Tes spesifik
pytest -k "security" -v          # Berdasarkan kata kunci
```

## LocalStack S3

```bash
# Inisialisasi bucket
python scripts/init_localstack.py

# Bucket akan dibuat otomatis saat upload jika belum ada
```

## LocalStack EC2

```bash
# Inisialisasi instance demo
python scripts/init_ec2_demo.py
```

## Matriks Role

| Fitur | Administrator | Operator | Supervisor |
|-------|:---:|:---:|:---:|
| Dashboard | ✓ | ✓ | ✓ |
| Data Kereta/Stasiun (lihat) | ✓ | ✓ | ✓ |
| Data Kereta/Stasiun (CRUD) | ✓ | ✗ | ✗ |
| Jadwal (lihat) | ✓ | ✓ | ✓ |
| Jadwal (buat/edit) | ✓ | ✓ | ✗ |
| Jadwal (hapus) | ✓ | ✗ | ✗ |
| Monitoring & Update Status | ✓ | ✓ | ✗ |
| Gangguan (buat/edit) | ✓ | ✓ | ✗ |
| Gangguan (tutup) | ✓ | ✗ | ✓ |
| Dokumen (upload) | ✓ | ✓ | ✗ |
| Dokumen (download) | ✓ | ✓ | ✓ |
| Dokumen (hapus) | ✓ | ✗ | ✗ |
| EC2 (buat/terminasi) | ✓ | ✗ | ✗ |
| EC2 (mulai/hentikan/reboot) | ✓ | ✓ | ✗ |
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
- Proteksi CSRF pada seluruh form
- Pencegahan open redirect
- Upload file: validasi ekstensi + tipe MIME
- Proteksi path traversal pada download
- Pencegahan CSV injection pada ekspor
- Validasi SECRET_KEY di production
- Guard AWS_ENDPOINT_URL — menolak operasi jika kosong
- Sanitasi header Content-Disposition
- Kontrol akses berbasis role
- Audit logging

## Keterbatasan

- Simulasi AWS — tidak terhubung ke AWS asli
- Layanan email tidak tersedia (reset password via flash message)
- Ekspor PDF belum diimplementasi (gunakan HTML print-friendly)
- LocalStack free tier: data tidak persisten setelah restart container
- Deployment single-node (tidak High Availability)

## Pemecahan Masalah

Lihat `documentation/troubleshooting.md` untuk panduan lengkap.

## Lisensi

Hanya untuk penggunaan internal — Tugas Besar.

## Informasi Tugas Akademik

| Item | Detail |
|------|--------|
| Nama Project | RailOps Nusantara |
| Tipe | Sistem Manajemen Operasional Kereta Api Cerdas & Infrastruktur Cloud |
| Stack Utama | Python, Flask, PostgreSQL, Boto3, LocalStack, Docker |
| Simulasi Cloud | AWS EC2 + S3 via LocalStack |
| Arsitektur | Monolitik Modular (Flask Application Factory + Blueprint) |
