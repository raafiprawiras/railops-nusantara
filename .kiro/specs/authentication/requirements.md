# Requirements — Authentication & Role Management

## Functional Requirements

### FR-1: User Model
- Fields: id, full_name, email (unique), password_hash, role, is_active, last_login_at, created_at, updated_at
- Roles: administrator, operator, supervisor
- Password hashed with Werkzeug (never plain text)

### FR-2: Login
- `GET /login` — render login form (redirect to dashboard if already logged in)
- `POST /login` — authenticate user, set session, update last_login_at
- CSRF protection via Flask-WTF
- Remember me support
- Flash messages in Bahasa Indonesia
- Validate `next` URL to prevent open redirect

### FR-3: Logout
- `POST /logout` — clear session, redirect to login
- CSRF protected

### FR-4: Access Control
- Dashboard requires login (redirect to login if unauthenticated)
- Inactive accounts cannot login
- `role_required` decorator for role-based access
- 403 page for unauthorized access

### FR-5: Role Definitions
- administrator: full access
- operator: operational access
- supervisor: read and report access

### FR-6: Development Scripts
- `create_admin.py` — create default admin account
- `seed_users.py` — seed sample users for development
- Default: admin@railops.local / Admin123! / administrator

## Non-Functional Requirements

### NFR-1: Security
- No plain text passwords
- No credentials hardcoded in app code (only in dev scripts)
- CSRF on all forms
- Validate redirect URLs

### NFR-2: UX
- Flash messages in Bahasa Indonesia
- Show user name + role in sidebar/navbar
- Logout in navbar
