# API & Routes — RailOps Nusantara

## Authentication

| Method | URL | Role | Deskripsi |
|--------|-----|------|-----------|
| GET/POST | /login | public | Halaman login |
| POST | /logout | authenticated | Logout |

## Main

| Method | URL | Role | Deskripsi |
|--------|-----|------|-----------|
| GET | / | public | Redirect ke /dashboard |
| GET | /dashboard | authenticated | Dashboard operasional |
| GET | /health | public | Health check (JSON) |

## Trains

| Method | URL | Role | Deskripsi |
|--------|-----|------|-----------|
| GET | /trains | authenticated | List kereta |
| GET/POST | /trains/create | administrator | Tambah kereta |
| GET | /trains/\<id\> | authenticated | Detail kereta |
| GET/POST | /trains/\<id\>/edit | administrator | Edit kereta |
| POST | /trains/\<id\>/delete | administrator | Hapus kereta |

## Stations

| Method | URL | Role | Deskripsi |
|--------|-----|------|-----------|
| GET | /stations | authenticated | List stasiun |
| GET/POST | /stations/create | administrator | Tambah stasiun |
| GET | /stations/\<id\> | authenticated | Detail stasiun |
| GET/POST | /stations/\<id\>/edit | administrator | Edit stasiun |
| POST | /stations/\<id\>/delete | administrator | Hapus stasiun |

## Trips

| Method | URL | Role | Deskripsi |
|--------|-----|------|-----------|
| GET | /trips | authenticated | List jadwal |
| GET/POST | /trips/create | administrator, operator | Tambah jadwal |
| GET | /trips/\<id\> | authenticated | Detail jadwal |
| GET/POST | /trips/\<id\>/edit | administrator, operator | Edit jadwal |
| POST | /trips/\<id\>/delete | administrator | Hapus jadwal |
| POST | /trips/\<id\>/status | administrator, operator | Update status |
| GET | /trips/monitoring | authenticated | Monitoring aktif |

## Incidents

| Method | URL | Role | Deskripsi |
|--------|-----|------|-----------|
| GET | /incidents | authenticated | List gangguan |
| GET/POST | /incidents/create | administrator, operator | Lapor gangguan |
| GET | /incidents/\<id\> | authenticated | Detail gangguan |
| GET/POST | /incidents/\<id\>/edit | administrator, operator | Edit gangguan |
| POST | /incidents/\<id\>/status | admin, operator, supervisor* | Update status |

*Supervisor hanya dapat menutup (Selesai → Ditutup)

## Documents

| Method | URL | Role | Deskripsi |
|--------|-----|------|-----------|
| GET | /documents | authenticated | List dokumen |
| GET/POST | /documents/upload | administrator, operator | Upload dokumen |
| GET | /documents/\<id\> | authenticated | Detail dokumen |
| GET | /documents/\<id\>/download | authenticated | Download file |
| POST | /documents/\<id\>/delete | administrator | Hapus dokumen |
| GET | /cloud/s3 | authenticated | Panel Cloud S3 |

## EC2 Infrastructure

| Method | URL | Role | Deskripsi |
|--------|-----|------|-----------|
| GET | /infrastructure/ec2 | authenticated | List instances |
| POST | /infrastructure/ec2/create | administrator | Create instance |
| POST | /infrastructure/ec2/\<id\>/start | administrator, operator | Start |
| POST | /infrastructure/ec2/\<id\>/stop | administrator, operator | Stop |
| POST | /infrastructure/ec2/\<id\>/reboot | administrator, operator | Reboot |
| POST | /infrastructure/ec2/\<id\>/terminate | administrator | Terminate |
| POST | /infrastructure/ec2/sync | administrator, operator | Sync state |
| GET | /audit-logs | authenticated | Audit log |

## Reports

| Method | URL | Role | Deskripsi |
|--------|-----|------|-----------|
| GET | /reports | admin, supervisor, operator | Index laporan |
| GET | /reports/trips | admin, supervisor, operator | Laporan perjalanan |
| GET | /reports/trips/csv | admin, supervisor, operator | Export CSV |
| GET | /reports/incidents | admin, supervisor, operator | Laporan gangguan |
| GET | /reports/incidents/csv | admin, supervisor, operator | Export CSV |
| GET | /reports/punctuality | administrator, supervisor | Ketepatan waktu |
| GET | /reports/infrastructure | administrator, supervisor | Audit infra |
| GET | /reports/infrastructure/csv | administrator, supervisor | Export CSV |
| GET | /reports/documents | administrator, supervisor | Laporan dokumen |

## Users

| Method | URL | Role | Deskripsi |
|--------|-----|------|-----------|
| GET | /users | administrator | List pengguna |
| GET/POST | /users/create | administrator | Tambah pengguna |
| GET | /users/\<id\> | administrator | Detail pengguna |
| GET/POST | /users/\<id\>/edit | administrator | Edit pengguna |
| POST | /users/\<id\>/toggle-status | administrator | Aktifkan/nonaktifkan |
| POST | /users/\<id\>/reset-password | administrator | Reset password |

## Profile

| Method | URL | Role | Deskripsi |
|--------|-----|------|-----------|
| GET | /profile | authenticated | Profil sendiri |
| GET/POST | /profile/edit | authenticated | Edit nama |
| GET/POST | /profile/change-password | authenticated | Ganti password |
