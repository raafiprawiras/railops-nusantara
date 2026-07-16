# Manual Penggunaan — RailOps Nusantara

## 1. Pendahuluan

RailOps Nusantara adalah sistem manajemen operasional kereta api berbasis web yang dilengkapi simulasi infrastruktur cloud AWS. Aplikasi ini dirancang untuk operator, administrator, dan supervisor.

## 2. Persyaratan Sistem

- Browser modern (Chrome, Firefox, Edge)
- Docker & Docker Compose (untuk deployment)
- Koneksi jaringan lokal

## 3. Instalasi

```bash
# Clone repository
git clone <repository-url>
cd railops-nusantara

# Salin konfigurasi
cp .env.example .env

# Jalankan stack
docker-compose up --build -d

# Jalankan migration database
docker-compose exec app flask db upgrade

# Inisialisasi LocalStack
docker-compose exec app python scripts/init_localstack.py

# Seed data demo
docker-compose exec app flask seed-demo
```

## 4. Menjalankan Aplikasi

Buka browser dan akses: **http://localhost:5000**

## 5. Login

[Screenshot: Halaman Login]

1. Buka halaman login di http://localhost:5000/login
2. Masukkan email dan password
3. Centang "Ingat saya" jika diperlukan
4. Klik tombol **Masuk**

Akun demo:
- Administrator: admin@railops.local / Admin123!
- Operator: budi@railops.local / Operator1!
- Supervisor: andi@railops.local / Supervisor1!

## 6. Dashboard

[Screenshot: Dashboard]

Dashboard menampilkan:
- **Stat Cards** — Kereta aktif, perjalanan hari ini, tepat waktu, terlambat, dibatalkan, gangguan, EC2, dokumen
- **Grafik Doughnut** — Status perjalanan
- **Grafik Line** — Keterlambatan harian 7 hari
- **Tabel Perjalanan Terbaru**
- **Tabel Gangguan Terbaru**

## 7. Data Kereta

[Screenshot: List Kereta]

### Melihat Data
1. Klik menu **Data Kereta** di sidebar
2. Gunakan kolom pencarian untuk mencari berdasarkan kode/nama
3. Filter berdasarkan status
4. Klik ikon mata untuk melihat detail

### Menambah Kereta (Administrator)
1. Klik tombol **Tambah Kereta**
2. Isi form: kode, nama, jenis, kapasitas, gerbong, status
3. Klik **Simpan**

### Edit/Hapus (Administrator)
- Klik ikon pensil untuk edit
- Klik ikon tempat sampah dan konfirmasi untuk hapus

## 8. Data Stasiun

[Screenshot: List Stasiun]

Operasi sama dengan Data Kereta:
- List dengan search dan filter
- Detail stasiun
- Tambah/edit/hapus (administrator only)

## 9. Jadwal Perjalanan

[Screenshot: Jadwal Perjalanan]

### Melihat Jadwal
1. Klik **Jadwal Perjalanan** di sidebar
2. Filter berdasarkan status, kereta, atau tanggal
3. Klik detail untuk melihat informasi lengkap dan riwayat status

### Membuat Jadwal (Administrator/Operator)
1. Klik **Tambah Jadwal**
2. Pilih kereta (harus berstatus Aktif)
3. Pilih stasiun asal dan tujuan (harus berbeda)
4. Atur jadwal berangkat dan tiba (tiba harus setelah berangkat)
5. Isi peron dan status awal
6. Klik **Simpan**

### Update Status
1. Buka detail jadwal
2. Di panel **Update Status**, pilih status baru
3. Isi keterlambatan dan catatan jika ada
4. Klik **Update**

## 10. Monitoring

[Screenshot: Monitoring]

1. Klik **Monitoring** di sidebar
2. Tampil semua perjalanan aktif (Persiapan, Berangkat, Dalam Perjalanan, Terlambat)
3. Klik **Detail & Update** untuk mengubah status

## 11. Gangguan

[Screenshot: Gangguan]

### Melaporkan Gangguan (Administrator/Operator)
1. Klik **Gangguan** > **Lapor Gangguan**
2. Isi nomor gangguan, pilih perjalanan terkait
3. Pilih jenis, prioritas, lokasi, deskripsi
4. Klik **Simpan**

### Alur Penanganan
```
Dilaporkan → Dalam Penanganan → Selesai → Ditutup
```
- **Selesai** memerlukan catatan penyelesaian
- **Ditutup** hanya oleh administrator/supervisor
- Tidak bisa melewati tahapan

### Timeline
Setiap perubahan status tercatat di riwayat penanganan.

## 12. Dokumen S3

[Screenshot: Dokumen S3]

### Upload Dokumen (Administrator/Operator)
1. Klik **Dokumen S3** > **Upload**
2. Pilih file (PDF, PNG, JPG, DOCX, XLSX — maks 16 MB)
3. Pilih kategori dokumen
4. Pilih perjalanan atau gangguan terkait (minimal salah satu)
5. Klik **Upload**

### Download
- Klik ikon download pada daftar dokumen

### Panel Cloud S3
- Klik **Dokumen S3** di sidebar
- Akses **/cloud/s3** untuk melihat status LocalStack dan daftar bucket

## 13. Infrastruktur EC2

[Screenshot: EC2]

### Membuat Instance (Administrator)
1. Klik **Infrastruktur EC2**
2. Klik **Buat Instance**
3. Pilih nama dan purpose
4. Klik **Buat**

### Aksi Instance
| State | Aksi Tersedia |
|-------|--------------|
| running | Stop, Reboot, Terminate |
| stopped | Start, Terminate |
| pending | (tunggu) |

### Sync
Klik **Sync** untuk menyinkronkan status dari LocalStack.

### Terminate
Memerlukan konfirmasi. Hanya administrator.

## 14. Laporan

[Screenshot: Laporan]

1. Klik **Laporan** di sidebar
2. Pilih jenis laporan:
   - Perjalanan — filter tanggal, status, kereta
   - Gangguan — filter tanggal, status, prioritas
   - Ketepatan Waktu — analisis performa
   - Infrastruktur — audit log EC2
   - Dokumen — laporan dokumen

### Export CSV
Klik tombol **Export CSV** pada halaman laporan terkait.

## 15. Pengguna dan Profil

### Manajemen Pengguna (Administrator)
[Screenshot: Pengguna]

1. Klik **Pengguna** di sidebar
2. Tambah, edit, aktifkan/nonaktifkan, reset password

### Profil Sendiri
[Screenshot: Profil]

1. Klik **Profil** di sidebar
2. Edit nama atau ganti password

## 16. Audit Log

[Screenshot: Audit Log]

1. Klik **Audit Log** di sidebar
2. Lihat seluruh catatan operasi infrastruktur dan pengguna

## 17. Logout

1. Klik nama pengguna di navbar kanan atas
2. Klik **Keluar**

## 18. Troubleshooting

| Masalah | Solusi |
|---------|--------|
| Tidak bisa login | Periksa email/password, pastikan akun aktif |
| Dashboard kosong | Jalankan `flask seed-demo` |
| Upload gagal | Periksa status LocalStack di /cloud/s3 |
| EC2 offline | Pastikan container localstack running |
| Akses ditolak | Periksa role akun Anda |

Lihat `documentation/troubleshooting.md` untuk panduan lengkap.

## 19. Penutup

RailOps Nusantara menyediakan simulasi lengkap operasional kereta api dan infrastruktur cloud. Seluruh fitur telah diuji dan dapat diakses sesuai role masing-masing pengguna.
