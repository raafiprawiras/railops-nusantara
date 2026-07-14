# Tasks — Project Foundation

## Task List

- [x] 1. Buat struktur folder project
- [x] 2. Buat file steering (.kiro/steering/)
- [x] 3. Buat file spec (.kiro/specs/project-foundation/)
- [x] 4. Buat .gitignore
- [x] 5. Buat .env.example
- [x] 6. Buat requirements.txt
- [x] 7. Buat config.py (konfigurasi dari env vars)
- [x] 8. Buat run.py (entry point)
- [x] 9. Buat Dockerfile
- [x] 10. Buat docker-compose.yml (app, postgres, localstack)
- [x] 11. Buat Flask application factory (app/__init__.py)
- [x] 12. Buat extensions.py (db, migrate, login_manager)
- [x] 13. Buat Blueprint dasar + GET /health
- [x] 14. Buat base template (Bootstrap 5)
- [x] 15. Buat README.md
- [x] 16. Buat tests/ dengan test health endpoint
- [x] 17. Verifikasi syntax dan docker-compose

## Acceptance Criteria

- `docker-compose config` valid tanpa error.
- `python -c "from app import create_app"` berhasil.
- `GET /health` mengembalikan JSON dengan field yang benar.
- Tidak ada hardcoded credentials.
- Tidak ada koneksi ke AWS asli.
