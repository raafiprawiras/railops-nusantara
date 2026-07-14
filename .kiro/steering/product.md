# Product Context — RailOps Nusantara

## Deskripsi Produk

RailOps Nusantara adalah aplikasi web internal untuk manajemen operasional kereta api
sekaligus simulasi infrastruktur cloud AWS (EC2 dan S3) menggunakan LocalStack.

## Target Pengguna

- Operator kereta api internal
- Administrator sistem
- Tim DevOps yang mempelajari AWS

## Fitur Utama

1. **Manajemen Kereta & Jadwal** — CRUD kereta, stasiun, jadwal perjalanan.
2. **Simulasi EC2** — Membuat, memulai, menghentikan, dan menghapus instance EC2 via LocalStack.
3. **Simulasi S3** — Membuat bucket, upload/download objek, manajemen file via LocalStack.
4. **Dashboard** — Visualisasi statistik operasional dan infrastruktur.
5. **Autentikasi** — Login/logout dengan role-based access.

## Batasan Produk

- Aplikasi ini TIDAK terhubung ke AWS asli; semua interaksi AWS melalui LocalStack.
- UI menggunakan Bahasa Indonesia.
- Tidak ada frontend framework (React/Vue/Angular); hanya server-side rendering dengan Jinja2.
- Aplikasi bersifat internal, tidak untuk publik.

## Metrik Keberhasilan

- Semua endpoint berfungsi tanpa error.
- Health check mengembalikan status semua dependensi.
- Docker Compose dapat menjalankan seluruh stack dalam satu perintah.
