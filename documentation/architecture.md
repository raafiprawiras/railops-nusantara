# Architecture — RailOps Nusantara

## Overview

RailOps Nusantara menggunakan arsitektur monolitik modular berbasis Flask:

- **Application Factory** — `create_app()` untuk fleksibilitas konfigurasi.
- **Blueprint-based routing** — setiap modul memiliki blueprint sendiri.
- **Service layer** — logika bisnis terpisah dari route handler.
- **LocalStack** — simulasi AWS tanpa koneksi ke cloud asli.

## Component Diagram

```
┌────────────────────────────────────────────┐
│                 Browser                     │
└─────────────────────┬──────────────────────┘
                      │ HTTP
┌─────────────────────▼──────────────────────┐
│              Flask Application              │
│  ┌─────────┐  ┌─────────┐  ┌───────────┐  │
│  │ Routes  │→ │Services │→ │  Models    │  │
│  └─────────┘  └────┬────┘  └─────┬─────┘  │
│                     │             │         │
└─────────────────────┼─────────────┼─────────┘
                      │             │
         ┌────────────▼──┐   ┌─────▼──────┐
         │  LocalStack   │   │ PostgreSQL  │
         │  (S3 + EC2)   │   │     16      │
         └───────────────┘   └────────────┘
```

## Directory Responsibilities

| Directory       | Responsibility                              |
|-----------------|---------------------------------------------|
| `app/routes/`   | HTTP handling, request/response only        |
| `app/services/` | Business logic, Boto3 interactions          |
| `app/models/`   | Database models (SQLAlchemy)                |
| `app/forms/`    | Form validation (Flask-WTF)                 |
| `app/templates/`| Jinja2 HTML templates                       |
| `app/static/`   | CSS, JS, images                             |
| `app/utils/`    | Shared helper functions                     |
| `scripts/`      | Operational scripts                         |
| `tests/`        | Automated tests                             |
