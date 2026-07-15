# Requirements — Admin UI Foundation

## Functional Requirements

### FR-1: Dashboard Page (`GET /dashboard`)
- Menampilkan statistik operasional statis:
  - Kereta Aktif: 12
  - Perjalanan Hari Ini: 35
  - Tepat Waktu: 27, Terlambat: 6, Dibatalkan: 2
  - Gangguan Aktif: 3
  - EC2 Running: 2
  - Dokumen S3: 48
- Grafik doughnut status perjalanan (Chart.js)
- Grafik line keterlambatan harian (Chart.js)
- Tabel perjalanan terbaru
- Tabel gangguan terbaru
- Badge status berwarna

### FR-2: Index Redirect (`GET /`)
- Redirect ke `/dashboard`

### FR-3: Login Page (`GET /login`)
- Halaman login UI saja (belum ada autentikasi)
- Form email/password dengan styling Bootstrap

### FR-4: Error Pages
- 404 Not Found — halaman custom
- 500 Internal Server Error — halaman custom

### FR-5: Shared Layout
- base.html — kerangka utama
- sidebar.html — navigasi samping
- navbar.html — top navbar dengan tanggal
- footer.html — footer
- flash_messages.html — alert dismissible

### FR-6: Sidebar Navigation
Menu: Dashboard, Data Kereta, Data Stasiun, Jadwal Perjalanan, Monitoring,
Gangguan, Dokumen S3, Infrastruktur EC2, Laporan, Audit Log, Pengguna, Profil, Pengaturan

### FR-7: Mobile Responsive
- Sidebar toggle pada mobile
- Layout responsif

## Non-Functional Requirements

### NFR-1: Theme
- Primary dark navy: #0B1F3A
- Sidebar gelap, konten background abu muda
- Card putih, aksen biru, status hijau/oranye/merah
- Bootstrap Icons (CDN)
- Tidak ada Tailwind atau font berlisensi khusus

### NFR-2: No Authentication Logic
- Halaman login hanya UI, tanpa proses autentikasi

### NFR-3: Static Data
- Semua data dari Python dict di route, bukan hardcode di HTML

### NFR-4: No New Dependencies
- Tidak menambahkan dependency Python baru
