# Tasks — Authentication & Role Management

## Task List

- [x] 1. Buat spec files
- [x] 2. Buat User model (app/models/user.py)
- [x] 3. Buat auth forms (app/forms/auth_forms.py)
- [x] 4. Buat role_required decorator
- [x] 5. Buat auth routes (app/routes/auth_routes.py)
- [x] 6. Update app factory (user_loader, blueprint, 403)
- [x] 7. Update main route (login_required on dashboard)
- [x] 8. Update templates (login, sidebar, navbar, 403)
- [x] 9. Buat scripts (create_admin.py, seed_users.py)
- [x] 10. Buat tests/test_auth.py
- [x] 11. Buat migration
- [x] 12. Verifikasi

## Acceptance Criteria

- Login correct → redirect dashboard
- Login wrong → flash error
- Inactive user → cannot login
- Dashboard without login → redirect /login
- Logout → redirect /login
- Password stored as hash
- role_required rejects wrong role (403)
- No credentials in .env.example
