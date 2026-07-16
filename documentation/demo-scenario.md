# Demo Scenario — RailOps Nusantara

Durasi: 10–15 menit

## Persiapan

```bash
docker-compose up -d
docker-compose exec app flask db upgrade
docker-compose exec app python scripts/init_localstack.py
docker-compose exec app flask seed-demo
```

Buka: http://localhost:5000

---

## Langkah Demo

### 1. Login sebagai Administrator (1 menit)
- Buka /login
- Email: admin@railops.local
- Password: Admin123!
- Tunjukkan dashboard dengan statistik real-time

### 2. Dashboard (1 menit)
- Tunjukkan stat cards (kereta aktif, perjalanan, gangguan, EC2, S3)
- Tunjukkan grafik doughnut status perjalanan
- Tunjukkan grafik line keterlambatan 7 hari
- Tunjukkan tabel perjalanan dan gangguan terbaru

### 3. CRUD Kereta (2 menit)
- Buka Data Kereta
- Tunjukkan list dengan search dan filter
- Tambah kereta baru:
  - Kode: KA-DEMO
  - Nama: Demo Express
  - Jenis: Eksekutif
  - Kapasitas: 300
  - Gerbong: 6
- Edit kereta yang baru dibuat
- Tunjukkan detail

### 4. CRUD Stasiun (1 menit)
- Buka Data Stasiun
- Tunjukkan data yang sudah ada
- Tunjukkan filter status

### 5. Jadwal Perjalanan (2 menit)
- Buka Jadwal Perjalanan
- Tunjukkan list dengan filter
- Buat jadwal baru:
  - Pilih kereta aktif
  - Pilih stasiun asal dan tujuan berbeda
  - Atur waktu
- Buka detail dan update status:
  - Dijadwalkan → Persiapan → Berangkat

### 6. Monitoring (1 menit)
- Buka Monitoring
- Tunjukkan perjalanan aktif
- Tunjukkan update status dari monitoring

### 7. Incident Management (2 menit)
- Buka Gangguan
- Lapor gangguan baru:
  - Pilih perjalanan terkait
  - Jenis: Gangguan Persinyalan
  - Prioritas: Tinggi
- Ubah status: Dilaporkan → Dalam Penanganan
- Tunjukkan timeline penanganan

### 8. Upload Dokumen S3 (1 menit)
- Buka Dokumen S3
- Upload file PDF
- Tunjukkan metadata
- Tunjukkan Cloud S3 panel (bucket, object count)
- Download file yang diupload

### 9. EC2 Infrastructure (2 menit)
- Buka Infrastruktur EC2
- Tunjukkan status LocalStack
- Buat instance baru: RailOps-Backup-Server
- Stop instance
- Start instance kembali
- Tunjukkan audit log

### 10. Laporan & Export (1 menit)
- Buka Laporan
- Tunjukkan laporan perjalanan dengan filter tanggal
- Export CSV
- Tunjukkan laporan ketepatan waktu

### 11. Manajemen User (1 menit)
- Buka Pengguna
- Tunjukkan list user
- Tunjukkan role matrix
- Login sebagai operator (tab baru) untuk menunjukkan perbedaan akses

### 12. Penutup
- Logout
- Tunjukkan health check: `curl http://localhost:5000/health`
- Tunjukkan bahwa semua menggunakan LocalStack, bukan AWS asli

---

## Tips Presentasi

- Gunakan 2 tab browser: satu admin, satu operator (untuk demo role)
- Seed data sebelum demo agar dashboard tidak kosong
- Jika LocalStack lambat, refresh halaman EC2/S3
- Health check endpoint bisa digunakan untuk menunjukkan status semua service
