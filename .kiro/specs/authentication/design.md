# Design — Authentication & Role Management

## User Model

```python
class User(db.Model, UserMixin):
    id: int (PK, auto)
    full_name: str (not null)
    email: str (unique, not null)
    password_hash: str (not null)
    role: str (not null, default='operator')
    is_active: bool (default=True)
    last_login_at: datetime (nullable)
    created_at: datetime (auto)
    updated_at: datetime (auto)
```

## Auth Flow

```
GET /login → already logged in? → redirect /dashboard
                                → render login form

POST /login → validate form → check email → check password → check is_active
           → success: login_user(), update last_login_at, redirect next/dashboard
           → fail: flash error, re-render form

POST /logout → logout_user() → redirect /login
```

## Route Structure

```
auth_bp (prefix: /auth or root)
├── GET  /login
├── POST /login
└── POST /logout
```

## Decorator

```python
def role_required(*roles):
    """Decorator: requires user to have one of the specified roles."""
```

## Template Changes

- login.html → connected to backend (form action, CSRF, field errors)
- sidebar.html → user profile section at bottom
- navbar.html → user dropdown with logout
- errors/403.html → new page

## File Layout

```
app/models/user.py
app/forms/auth_forms.py
app/routes/auth_routes.py
app/utils/decorators.py
app/templates/errors/403.html
scripts/create_admin.py
scripts/seed_users.py
```
