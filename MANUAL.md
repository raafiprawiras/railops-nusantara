# RailOps Nusantara — Manual Lengkap

## 1. Pendahuluan

### Tujuan Aplikasi

RailOps Nusantara adalah aplikasi web internal untuk manajemen operasional kereta api sekaligus simulasi infrastruktur cloud AWS (EC2 dan S3) menggunakan Boto3 dan LocalStack.

### Target Pengguna

- **Administrator** — mengelola seluruh sistem
- **Operator** — operasional harian kereta api
- **Supervisor** — monitoring dan pelaporan

### Fitur Utama

| Modul | Fungsi |
|-------|--------|
| Dashboard | Statistik real-time operasional |
| Data Kereta | CRUD armada kereta api |
| Data Stasiun | CRUD stasiun Indonesia |
| Jadwal Perjalanan | Penjadwalan dan status tracking |
| Monitoring | Pemantauan perjalanan aktif |
| Gangguan | Pelaporan dan penanganan insiden |
| Dokumen S3 | Upload/download dokumen via LocalStack |
| Infrastruktur EC2 | Simulasi lifecycle EC2 |
| Laporan | Report operasional + export CSV |
| Manajemen Pengguna | User CRUD, role, profil |
| Audit Log | Pencatatan operasi infrastruktur |
| Pengaturan | Konfigurasi sistem |


## 2. Arsitektur Sistem

```mermaid
graph TB
    subgraph Browser
        UI[Browser Client]
    end
    subgraph Docker["Docker Compose"]
        APP[Flask App :5000]
        PG[(PostgreSQL :5432)]
        LS[LocalStack :4566]
        SP[StackPort :8080]
    end
    UI -->|HTTP| APP
    UI -->|HTTP| SP
    APP -->|SQLAlchemy| PG
    APP -->|Boto3| LS
    SP -->|AWS SDK| LS
    LS --> S3[(S3 Bucket)]
    LS --> EC2[(EC2 Instances)]
```

| Komponen | Teknologi | Fungsi |
|----------|-----------|--------|
| Frontend | Bootstrap 5, Chart.js | UI responsif |
| Backend | Python 3.11, Flask | API dan logic |
| Database | PostgreSQL 16 | Penyimpanan data |
| Cloud | Boto3 + LocalStack | Simulasi AWS |
| Browser Resource | StackPort | Inspeksi S3/EC2 |

## 3. Persyaratan Sistem

| Persyaratan | Minimum |
|-------------|---------|
| Docker Desktop | v24+ |
| Docker Compose | v2+ |
| Git | v2.30+ |
| RAM | 4 GB |
| Disk | 5 GB |
| Browser | Chrome/Firefox/Edge terbaru |

**Port yang digunakan:**

| Port | Service |
|------|---------|
| 5000 | Flask Application |
| 5432 | PostgreSQL |
| 4566 | LocalStack (S3, EC2) |
| 8080 | StackPort Resource Browser |


## 4. Clone Repository

```bash
git clone <repository-url>
cd railops-nusantara
```

## 5. Konfigurasi Environment

Salin file environment:

```bash
cp .env.example .env
```

### Tabel Variabel Environment

| Variable | Fungsi | Default |
|----------|--------|---------|
| FLASK_APP | Entry point | run.py |
| FLASK_DEBUG | Mode debug | 1 |
| FLASK_ENV | Environment | development |
| SECRET_KEY | Secret sesi | change-this-to-a-random-secret-key |
| DATABASE_URL | Koneksi PostgreSQL | postgresql+psycopg2://railops:railops_secret@postgres:5432/railops_nusantara |
| AWS_ACCESS_KEY_ID | Credential LocalStack | test |
| AWS_SECRET_ACCESS_KEY | Credential LocalStack | test |
| AWS_DEFAULT_REGION | Region AWS | ap-southeast-1 |
| AWS_ENDPOINT_URL | Endpoint LocalStack | http://localstack:4566 |
| S3_BUCKET_NAME | Nama bucket S3 | railops-bucket |
| EC2_IMAGE_ID | AMI ID simulasi | ami-00000000 |
| MAX_CONTENT_LENGTH | Max upload (bytes) | 16777216 (16 MB) |

> **Peringatan:** Jangan gunakan credential AWS asli. Gunakan `test/test` untuk LocalStack.

## 6. Menjalankan Project

### Start Seluruh Stack

```bash
docker compose up --build -d
```

### Cek Status

```bash
docker compose ps
```

Output yang diharapkan:

| Container | Status | Port |
|-----------|--------|------|
| app | Up | 5000 |
| postgres | Up (healthy) | 5432 |
| localstack | Up (healthy) | 4566 |
| stackport | Up | 8080 |

### Melihat Log

```bash
docker compose logs -f app          # Log aplikasi
docker compose logs -f localstack   # Log LocalStack
docker compose logs -f stackport    # Log StackPort
```

### Menghentikan

```bash
docker compose down                 # Stop (data tetap)
docker compose down -v              # Stop + hapus data (HATI-HATI!)
```


## 7. Database Migration

```bash
# Jalankan semua migrasi
docker compose exec app flask db upgrade

# Inisialisasi bucket S3
docker compose exec app python scripts/init_localstack.py

# Seed demo data (idempotent)
docker compose exec app flask seed-demo

# Reset + reseed (development only)
docker compose exec app flask seed-demo --reset
```

Migrasi yang tersedia:
1. `create_users_table`
2. `create_trains_stations_tables`
3. `create_trips_and_status_history`
4. `create_incidents_tables`
5. `create_documents_table`
6. `create_infrastructure_and_audit_tables`

## 8. Login

**URL:** http://localhost:5000/login

### Akun Demo

| Email | Password | Role |
|-------|----------|------|
| admin@railops.local | Admin123! | Administrator |
| budi@railops.local | Operator1! | Operator |
| dewi@railops.local | Operator2! | Operator |
| andi@railops.local | Supervisor1! | Supervisor |

### Perbedaan Role

| Kemampuan | Administrator | Operator | Supervisor |
|-----------|:---:|:---:|:---:|
| Dashboard | ✓ | ✓ | ✓ |
| CRUD Kereta/Stasiun | ✓ | Lihat saja | Lihat saja |
| Buat/Edit Jadwal | ✓ | ✓ | ✗ |
| Hapus Jadwal | ✓ | ✗ | ✗ |
| Update Monitoring | ✓ | ✓ | ✗ |
| Buat Gangguan | ✓ | ✓ | ✗ |
| Tutup Gangguan | ✓ | ✗ | ✓ |
| Upload Dokumen | ✓ | ✓ | ✗ |
| Download Dokumen | ✓ | ✓ | ✓ |
| Hapus Dokumen | ✓ | ✗ | ✗ |
| Create/Terminate EC2 | ✓ | ✗ | ✗ |
| Start/Stop/Reboot EC2 | ✓ | ✓ | ✗ |
| Semua Laporan | ✓ | Sebagian | ✓ |
| Kelola Pengguna | ✓ | ✗ | ✗ |


## 9. Dashboard

**URL:** http://localhost:5000/dashboard

Dashboard menampilkan:

| Card | Data |
|------|------|
| Kereta Aktif | Jumlah kereta berstatus Aktif |
| Perjalanan Hari Ini | Total trip hari ini |
| Tepat Waktu | Trip selesai tanpa delay |
| Gangguan Aktif | Incident berstatus Dilaporkan/Dalam Penanganan |
| EC2 Running | Instance EC2 dalam state running |
| Dokumen S3 | Total dokumen aktif (belum dihapus) |

**Grafik:**
- Doughnut: Status perjalanan (Tepat Waktu/Terlambat/Dibatalkan)
- Line: Keterlambatan rata-rata 7 hari terakhir

**Tabel:**
- Perjalanan terbaru (5 terakhir)
- Gangguan terbaru (5 terakhir)

**Quick Actions:**
- Tambah Jadwal → `/trips/create`
- Lapor Gangguan → `/incidents/create`
- Upload Dokumen → `/documents/upload`

## 10. Data Kereta

**URL:** http://localhost:5000/trains

### Melihat Data
- Pencarian berdasarkan kode atau nama
- Filter berdasarkan status: Aktif, Tidak Aktif, Dalam Perawatan, Mengalami Gangguan

### Menambah Kereta (Administrator)
1. Klik **Tambah Kereta**
2. Isi: Kode, Nama, Jenis, Kapasitas, Gerbong, Status, Tanggal Perawatan
3. Klik **Simpan**

### Jenis Kereta
Eksekutif, Bisnis, Ekonomi, Komuter, Barang

### Status Kereta
- **Aktif** — beroperasi normal
- **Tidak Aktif** — tidak digunakan
- **Dalam Perawatan** — sedang maintenance
- **Mengalami Gangguan** — ada masalah teknis

> **Catatan:** Kereta non-Aktif tidak dapat digunakan untuk jadwal perjalanan baru.

## 11. Data Stasiun

**URL:** http://localhost:5000/stations

Field: Kode Stasiun, Nama, Kota, Provinsi, Jumlah Peron, Status Operasional.

Status: Aktif, Tidak Aktif, Dalam Renovasi.

Operasi CRUD sama dengan Data Kereta.


## 12. Jadwal Perjalanan

**URL:** http://localhost:5000/trips

### Membuat Jadwal
1. Klik **Tambah Jadwal**
2. Pilih kereta (hanya kereta berstatus Aktif)
3. Pilih stasiun asal dan tujuan (harus berbeda)
4. Atur jadwal berangkat dan tiba (tiba harus setelah berangkat)
5. Isi peron dan status awal
6. Klik **Simpan**

### Status Perjalanan
| Status | Deskripsi |
|--------|-----------|
| Dijadwalkan | Belum berangkat |
| Persiapan | Sedang persiapan |
| Berangkat | Sudah meninggalkan stasiun asal |
| Dalam Perjalanan | Di antara stasiun |
| Tiba | Sampai di tujuan |
| Terlambat | Delay > 0 menit |
| Dibatalkan | Perjalanan batal |

### Update Status
Buka detail perjalanan → panel **Update Status** → pilih status baru → isi keterlambatan dan catatan → klik **Update**.

Setiap perubahan status otomatis tercatat di riwayat (TripStatusHistory).

## 13. Monitoring Operasional

**URL:** http://localhost:5000/trips/monitoring

Menampilkan perjalanan aktif (Persiapan, Berangkat, Dalam Perjalanan, Terlambat).

Informasi per perjalanan:
- Nomor trip dan nama kereta
- Rute (Asal — Tujuan)
- Jadwal berangkat — tiba
- Delay (menit)
- Status badge berwarna
- Tombol **Detail & Update**

## 14. Incident Management

**URL:** http://localhost:5000/incidents

### Membuat Laporan
1. Klik **Lapor Gangguan**
2. Isi: Nomor gangguan, perjalanan terkait, jenis, lokasi, waktu, prioritas, deskripsi
3. Assign ke operator (opsional)
4. Klik **Simpan**

### Jenis Gangguan
Gangguan Lokomotif, Gangguan Rangkaian, Gangguan Persinyalan, Gangguan Jalur, Gangguan Listrik, Cuaca Buruk, Gangguan Fasilitas, Lainnya

### Prioritas
Rendah, Sedang, Tinggi, Darurat

### Alur Status
```
Dilaporkan → Dalam Penanganan → Selesai → Ditutup
```

**Aturan:**
- Tidak bisa melompati tahapan
- **Selesai** memerlukan catatan penyelesaian (resolution_notes)
- **Ditutup** hanya oleh Administrator atau Supervisor
- Setiap perubahan tercatat di IncidentStatusHistory


## 15. S3 Documents

**URL:** http://localhost:5000/documents

### Upload File
1. Klik **Upload**
2. Pilih file (format: PDF, PNG, JPG, JPEG, DOCX, XLSX — max 16 MB)
3. Pilih kategori: Manifest, Inspeksi, Perawatan, Laporan Gangguan, Berita Acara, Dokumentasi, Lainnya
4. Pilih Perjalanan atau Gangguan terkait (minimal satu)
5. Klik **Upload**

### Struktur Object Key di S3
```
manifests/2026/TRN-D001/uuid_filename.pdf
incidents/2026/INC-D001/uuid_filename.pdf
inspections/2026/TRN-D001/uuid_filename.pdf
maintenance/2026/TRN-D001/uuid_filename.pdf
miscellaneous/2026/uuid_filename.pdf
```

### Download
Klik ikon download pada daftar dokumen.

### Hapus (Soft Delete)
Administrator klik ikon hapus. Metadata di-set `deleted_at`, object dihapus dari S3.

### Cloud S3 Panel
**URL:** http://localhost:5000/cloud/s3

Menampilkan status LocalStack S3, daftar bucket, dan jumlah object.

### Verifikasi S3 via StackPort
Buka http://localhost:8080 → pilih **S3** → bucket `railops-bucket` tampil dengan semua object.

## 16. EC2 Infrastructure

**URL:** http://localhost:5000/infrastructure/ec2

### Membuat Instance (Administrator)
1. Klik **Create Instance**
2. Pilih nama: RailOps-Web-Server, RailOps-Monitoring-Server, RailOps-Backup-Server, RailOps-Emergency-Server
3. Pilih purpose: Web Application, Monitoring, Backup, Emergency
4. Klik **Create**

### Aksi per State

| State | Aksi Tersedia |
|-------|--------------|
| running | Stop, Reboot, Terminate |
| stopped | Start, Terminate |
| pending | (tunggu) |
| terminated | (tidak ada) |

### Sync
Klik **Sync** untuk menyinkronkan state dari LocalStack.

### Audit Log
Setiap create/start/stop/reboot/terminate tercatat di Audit Log.

### Verifikasi EC2 via StackPort
Buka http://localhost:8080 → pilih **EC2** → instance tampil dengan ID, Name tag, state, type.

> **Catatan:** EC2 LocalStack adalah simulasi. Instance tidak menjalankan VM nyata.


## 17. Reports

**URL:** http://localhost:5000/reports

| Laporan | URL | Role | CSV Export |
|---------|-----|------|:---:|
| Perjalanan | /reports/trips | Semua | ✓ |
| Gangguan | /reports/incidents | Semua | ✓ |
| Ketepatan Waktu | /reports/punctuality | Admin, Supervisor | ✗ |
| Infrastruktur | /reports/infrastructure | Admin, Supervisor | ✓ |
| Dokumen | /reports/documents | Admin, Supervisor | ✗ |

### Filter
- Tanggal mulai dan akhir
- Status
- Kereta (untuk laporan perjalanan)
- Prioritas (untuk laporan gangguan)

### Export CSV
Klik **Export CSV** pada halaman laporan. File terunduh dengan nama berformat `laporan_perjalanan_YYYYMMDD.csv`.

> CSV dilindungi dari formula injection — nilai yang dimulai dengan `=`, `+`, `-`, `@` di-escape otomatis.

## 18. User Management

**URL:** http://localhost:5000/users (Administrator only)

### Fitur
- List pengguna dengan search dan filter
- Tambah pengguna baru
- Edit nama, email, role
- Aktifkan/nonaktifkan akun
- Reset password (generate temporary password, ditampilkan via flash satu kali)

### Profil Sendiri
**URL:** http://localhost:5000/profile
- Lihat informasi akun
- Edit nama
- Ganti password (wajib input password lama)

### Aturan Keamanan
- Tidak bisa menonaktifkan akun sendiri
- Tidak bisa menonaktifkan administrator terakhir
- Password minimal 8 karakter
- Password lama wajib benar untuk ganti password

## 19. Settings

**URL:** http://localhost:5000/profile/settings

Menampilkan:
- **Umum** — Nama aplikasi, versi, tema, bahasa, timezone
- **Akun** — Informasi user yang login
- **Status Sistem** — Database, LocalStack S3, LocalStack EC2, environment
- **Tampilan** — Mode, sidebar, animasi, font
- **StackPort** — Link ke resource browser

## 20. Audit Log

**URL:** http://localhost:5000/audit-logs

Mencatat operasi:
- Create/Start/Stop/Reboot/Terminate EC2 instance
- Create/Edit/Deactivate/Reset password user

Informasi per entry: Waktu, User, Aksi, Resource ID, Deskripsi.


## 21. StackPort Resource Browser

**URL:** http://localhost:8080

StackPort menampilkan resource AWS yang berjalan pada LocalStack.

### Konfigurasi
| Parameter | Nilai |
|-----------|-------|
| Endpoint | http://localstack:4566 (dari container) |
| Region | ap-southeast-1 |
| Access Key | test |
| Secret Key | test |

### Melihat S3
1. Buka http://localhost:8080
2. Pilih **S3** di sidebar
3. Bucket `railops-bucket` tampil
4. Klik bucket untuk melihat objects

### Melihat EC2
1. Buka http://localhost:8080
2. Pilih **EC2** di sidebar
3. Instance tampil dengan ID, Name, State, Type

### Catatan
- StackPort read-only (untuk inspeksi, bukan modifikasi)
- Perubahan dari RailOps langsung terlihat setelah refresh
- Tidak terhubung ke AWS asli

## 22. Struktur Folder Project

```
railops-nusantara/
├── app/
│   ├── __init__.py              # Application factory
│   ├── extensions.py            # Flask extensions
│   ├── commands.py              # CLI commands (flask seed-demo)
│   ├── models/                  # SQLAlchemy models
│   │   ├── user.py
│   │   ├── train.py
│   │   ├── station.py
│   │   ├── trip.py
│   │   ├── incident.py
│   │   ├── document.py
│   │   └── infrastructure.py
│   ├── routes/                  # Blueprint routes
│   │   ├── main.py             # Dashboard, health
│   │   ├── auth_routes.py      # Login, logout
│   │   ├── train_routes.py
│   │   ├── station_routes.py
│   │   ├── trip_routes.py
│   │   ├── incident_routes.py
│   │   ├── document_routes.py
│   │   ├── ec2_routes.py
│   │   ├── report_routes.py
│   │   ├── user_routes.py
│   │   └── profile_routes.py
│   ├── services/                # Business logic
│   │   ├── s3_service.py
│   │   ├── ec2_service.py
│   │   └── dashboard_service.py
│   ├── forms/                   # Flask-WTF forms
│   ├── templates/               # Jinja2 HTML
│   ├── static/                  # CSS, JS, favicon
│   └── utils/                   # Decorators
├── scripts/                     # Seed & init scripts
├── tests/                       # pytest (138 tests)
├── migrations/                  # Alembic (6 migrations)
├── documentation/               # Docs
├── config.py
├── run.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```


## 23. Troubleshooting

### Docker Gagal Build
```bash
# Rebuild tanpa cache
docker compose build --no-cache app
# Jika pip gagal (network), coba ulang
docker compose build app
```

### PostgreSQL Tidak Healthy
```bash
docker compose logs postgres
docker compose restart postgres
# Tunggu 10 detik, lalu:
docker compose exec app flask db upgrade
```

### LocalStack Tidak Tersedia
```bash
docker compose logs localstack
docker compose restart localstack
# Tunggu 15 detik, lalu:
docker compose exec app python scripts/init_localstack.py
```
> Aplikasi tetap berjalan tanpa LocalStack — fitur S3/EC2 menampilkan "Tidak tersedia".

### S3 Bucket Tidak Muncul
```bash
docker compose exec app python scripts/init_localstack.py
```

### EC2 Instance Tidak Muncul
```bash
docker compose exec app python scripts/init_ec2_demo.py
```

### Port Bentrok
Periksa port yang digunakan:
```bash
netstat -ano | findstr :5000
netstat -ano | findstr :5432
netstat -ano | findstr :4566
netstat -ano | findstr :8080
```
Hentikan service yang menggunakan port tersebut atau ubah port di docker-compose.yml.

### Migration Error
```bash
docker compose exec app flask db upgrade
# Jika conflict:
docker compose exec app flask db heads
docker compose exec app flask db current
```

### Login Gagal
| Masalah | Solusi |
|---------|--------|
| Email/password salah | Periksa credential di tabel Akun Demo |
| Akun tidak aktif | Minta administrator mengaktifkan |
| Redirect loop | Hapus cookies browser |

### Permission Denied (403)
Login dengan role yang sesuai. Lihat tabel Role Matrix di Section 8.

### Upload Gagal
- Pastikan LocalStack running
- Periksa format file (PDF, PNG, JPG, DOCX, XLSX saja)
- Periksa ukuran file (max 16 MB)
- Pastikan memilih Trip atau Incident terkait

## 24. FAQ

**Q1: Apakah aplikasi terhubung ke AWS asli?**
Tidak. Seluruh operasi S3 dan EC2 menggunakan LocalStack.

**Q2: Data hilang setelah restart Docker?**
Data PostgreSQL persisten (volume). Data LocalStack hilang setelah `docker compose down -v`.

**Q3: Bagaimana cara reset data development?**
```bash
docker compose exec app flask seed-demo --reset
```

**Q4: Apakah bisa diakses dari komputer lain?**
Ya, ganti `localhost` dengan IP komputer host.

**Q5: Berapa user maksimal?**
Tidak dibatasi oleh aplikasi.

**Q6: Bagaimana menambah role baru?**
Edit `app/models/user.py` → `VALID_ROLES` dan `role_required` decorator.

**Q7: File upload disimpan di mana?**
Di LocalStack S3 bucket `railops-bucket`. Metadata di PostgreSQL tabel `documents`.

**Q8: EC2 instance benar-benar jalan?**
Tidak. LocalStack mensimulasikan API EC2 tanpa VM nyata.

**Q9: Bagaimana backup database?**
```bash
docker compose exec postgres pg_dump -U railops railops_nusantara > backup.sql
```

**Q10: Bagaimana restore database?**
```bash
docker compose exec -T postgres psql -U railops railops_nusantara < backup.sql
```

**Q11: Mengapa tests lambat?**
Boto3 health check timeout saat LocalStack tidak running. Gunakan mock pada unit test.

**Q12: Bagaimana menjalankan tanpa Docker?**
Pastikan PostgreSQL di localhost:5432, lalu: `flask run`

**Q13: Apa itu StackPort?**
Resource browser untuk melihat S3/EC2 di LocalStack via web UI.

**Q14: Bisa ditambah service AWS lain?**
Ya. Tambahkan di `SERVICES` LocalStack dan buat service layer Boto3 baru.

**Q15: Bagaimana deploy ke production?**
Ganti SECRET_KEY, gunakan PostgreSQL managed, jangan gunakan LocalStack di production.


## 25. Security Notes

> **PERINGATAN: Jangan pernah gunakan credential AWS asli pada project ini.**

| Aturan | Detail |
|--------|--------|
| AWS Credential | Selalu `test/test` untuk LocalStack |
| SECRET_KEY | Ganti di production, jangan pakai default |
| .env | Sudah di .gitignore, jangan commit |
| Password | Di-hash dengan Werkzeug (scrypt) |
| CSRF | Aktif pada seluruh form |
| Upload | Validasi extension + MIME type |
| CSV Export | Dilindungi dari formula injection |
| AWS Endpoint | Guard menolak jika kosong |

## 26. Demo Scenario (10-15 menit)

### Persiapan
```bash
docker compose up -d
docker compose exec app flask db upgrade
docker compose exec app python scripts/init_localstack.py
docker compose exec app flask seed-demo
```

### Urutan Demo

| # | Aksi | URL |
|---|------|-----|
| 1 | Login sebagai Administrator | /login |
| 2 | Tunjukkan Dashboard | /dashboard |
| 3 | Buat kereta baru (KA-DEMO) | /trains/create |
| 4 | Tunjukkan stasiun | /stations |
| 5 | Buat jadwal perjalanan | /trips/create |
| 6 | Monitoring — update status | /trips/monitoring |
| 7 | Lapor gangguan | /incidents/create |
| 8 | Upload dokumen S3 | /documents/upload |
| 9 | Buat EC2 instance | /infrastructure/ec2 |
| 10 | Lihat laporan + export CSV | /reports/trips |
| 11 | Lihat audit log | /audit-logs |
| 12 | Buka StackPort | http://localhost:8080 |
| 13 | Logout | Dropdown → Keluar |

## 27. Maintenance Guide

### Update Project
```bash
git pull origin main
docker compose up --build -d
docker compose exec app flask db upgrade
```

### Backup Database
```bash
docker compose exec postgres pg_dump -U railops railops_nusantara > backup_$(date +%Y%m%d).sql
```

### Reset Development
```bash
docker compose down -v
docker compose up --build -d
docker compose exec app flask db upgrade
docker compose exec app python scripts/init_localstack.py
docker compose exec app flask seed-demo
```

### Update Dependency
Edit `requirements.txt` → rebuild:
```bash
docker compose build --no-cache app
docker compose up -d
```

## 28. Changelog

### v1.0.0 (2026-07-16)
- Project Foundation (Flask, Docker, PostgreSQL, LocalStack)
- UI Foundation (Bootstrap 5 enterprise theme)
- Authentication & Role Management
- Railway Master Data (Train + Station CRUD)
- Trip Operations & Monitoring
- Incident Management
- S3 Document Management
- EC2 Infrastructure Management
- Dynamic Dashboard & Reports
- User Administration & Profile
- Integrated Demo Data
- Quality & Security Review
- Documentation & User Manual
- StackPort Integration

---

*Dokumen ini dibuat untuk project RailOps Nusantara — Sistem Manajemen Operasional Kereta Api Cerdas & Infrastruktur Cloud.*
