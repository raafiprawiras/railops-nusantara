# Design — Admin UI Foundation

## Layout Architecture

```
┌──────────────────────────────────────────────────────────┐
│  base.html                                               │
│  ┌─────────┬────────────────────────────────────────┐    │
│  │         │  navbar.html (top bar + date)           │    │
│  │ sidebar │  ┌──────────────────────────────────┐   │    │
│  │  .html  │  │  flash_messages.html             │   │    │
│  │         │  │  {% block content %}             │   │    │
│  │         │  │                                  │   │    │
│  │         │  └──────────────────────────────────┘   │    │
│  │         │  footer.html                            │    │
│  └─────────┴────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

## Color Palette

| Token              | Value     | Usage                     |
|--------------------|-----------|---------------------------|
| --railops-navy     | #0B1F3A   | Sidebar bg, primary dark  |
| --railops-navy-light| #132D50  | Sidebar hover             |
| --railops-blue     | #2E86DE   | Accent, links             |
| --railops-bg       | #F4F6F9   | Content background        |
| --railops-card     | #FFFFFF   | Card backgrounds          |
| --railops-success  | #27AE60   | Status sukses             |
| --railops-warning  | #F39C12   | Status peringatan         |
| --railops-danger   | #E74C3C   | Status bahaya             |

## Route Design

| Route       | Method | Response          |
|-------------|--------|-------------------|
| /           | GET    | Redirect /dashboard |
| /dashboard  | GET    | render dashboard.html with stats dict |
| /login      | GET    | render login.html  |

## Template Hierarchy

```
templates/
├── layouts/
│   ├── base.html
│   ├── base_auth.html      (for login, no sidebar)
│   └── partials/
│       ├── sidebar.html
│       ├── navbar.html
│       ├── footer.html
│       └── flash_messages.html
├── dashboard.html
├── login.html
└── errors/
    ├── 404.html
    └── 500.html
```

## Dashboard Data Structure (Python)

```python
stats = {
    "kereta_aktif": 12,
    "perjalanan_hari_ini": 35,
    "tepat_waktu": 27,
    "terlambat": 6,
    "dibatalkan": 2,
    "gangguan_aktif": 3,
    "ec2_running": 2,
    "dokumen_s3": 48,
}
```

## Chart.js Integration

- Doughnut: Tepat Waktu / Terlambat / Dibatalkan
- Line: Keterlambatan harian (7 hari statis)

## JavaScript Files

- `app.js` — sidebar toggle, active nav state
- `dashboard.js` — Chart.js initialization (only on dashboard page)
