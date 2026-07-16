# Troubleshooting — RailOps Nusantara

## Docker Gagal Start

**Gejala:** `docker-compose up` error atau container restart loop

**Solusi:**
```bash
# Periksa status container
docker-compose ps

# Periksa log
docker-compose logs app
docker-compose logs postgres
docker-compose logs localstack

# Rebuild jika ada perubahan Dockerfile
docker-compose up --build -d
```

## Port Bentrok

**Gejala:** `port already in use`

**Solusi:**
```bash
# Periksa port yang digunakan
# Windows:
netstat -ano | findstr :5000
netstat -ano | findstr :5432
netstat -ano | findstr :4566

# Hentikan service yang menggunakan port tersebut atau ubah port di docker-compose.yml
```

Port default:
- 5000: Flask app
- 5432: PostgreSQL
- 4566: LocalStack

## PostgreSQL Belum Sehat

**Gejala:** App error "connection refused" atau healthcheck gagal

**Solusi:**
```bash
# Periksa status PostgreSQL
docker-compose exec postgres pg_isready -U railops

# Tunggu sampai healthy
docker-compose ps  # Lihat kolom Status

# Restart jika stuck
docker-compose restart postgres
sleep 10
docker-compose exec app flask db upgrade
```

## LocalStack Tidak Tersedia

**Gejala:** Upload gagal, EC2 panel offline, health check "unhealthy"

**Solusi:**
```bash
# Periksa status LocalStack
docker-compose logs localstack

# Restart LocalStack
docker-compose restart localstack
sleep 15

# Re-inisialisasi bucket
docker-compose exec app python scripts/init_localstack.py
```

**Catatan:** Aplikasi tetap berjalan tanpa LocalStack. Fitur S3 dan EC2 akan menampilkan status "Tidak tersedia" tapi tidak crash.

## Migration Error

**Gejala:** `alembic.util.exc.CommandError` atau tabel tidak ditemukan

**Solusi:**
```bash
# Jalankan semua migration pending
docker-compose exec app flask db upgrade

# Jika revision conflict
docker-compose exec app flask db heads
docker-compose exec app flask db current

# Reset total (development only - HAPUS DATA!)
docker-compose down -v
docker-compose up -d
docker-compose exec app flask db upgrade
docker-compose exec app flask seed-demo
```

## Bucket Tidak Ada

**Gejala:** Upload gagal dengan error "NoSuchBucket"

**Solusi:**
```bash
# Inisialisasi bucket (idempotent)
docker-compose exec app python scripts/init_localstack.py
```

## EC2 Action Error

**Gejala:** "Instance dalam status 'X' tidak dapat di-Y"

**Penjelasan:** State machine:
- `running` → stop, reboot, terminate
- `stopped` → start, terminate
- `pending` → tunggu
- `terminated` → tidak ada aksi

**Solusi:**
- Pastikan instance dalam state yang benar
- Klik **Sync** untuk menyinkronkan status dari LocalStack

## Permission / Role Error

**Gejala:** 403 Forbidden

**Penjelasan:**
| Aksi | Role yang Diizinkan |
|------|-------------------|
| CRUD Kereta/Stasiun | administrator |
| Create jadwal | administrator, operator |
| Delete jadwal | administrator |
| Create EC2 | administrator |
| Start/Stop EC2 | administrator, operator |
| Upload dokumen | administrator, operator |
| Delete dokumen | administrator |
| Manajemen user | administrator |

**Solusi:** Login dengan akun yang memiliki role sesuai.

## Reset Volume Development

**Peringatan:** Ini menghapus SEMUA data!

```bash
# Stop semua container dan hapus volume
docker-compose down -v

# Start ulang
docker-compose up -d

# Tunggu PostgreSQL healthy
docker-compose exec app flask db upgrade
docker-compose exec app python scripts/init_localstack.py
docker-compose exec app flask seed-demo
```

## Login Gagal

| Masalah | Solusi |
|---------|--------|
| "Email atau password salah" | Periksa kembali credential |
| "Akun tidak aktif" | Minta administrator mengaktifkan akun |
| Halaman redirect loop | Hapus cookies browser |

## Seed Data Gagal

```bash
# Pastikan database kosong atau gunakan --reset
docker-compose exec app flask seed-demo --reset

# Periksa log untuk detail error
docker-compose exec app flask seed-demo 2>&1
```

## Performance Lambat

- Periksa resource Docker (RAM, CPU)
- LocalStack mungkin memerlukan waktu startup (15-30 detik)
- Pertama kali `docker-compose up --build` lebih lambat (download images)
