# Requirements — User Administration & Profile

## FR-1: Admin User Management (admin only)
- List users: search, filter role, filter status, pagination
- Create user: name, email, role, password
- Detail user
- Edit user: name, email, role, status
- Toggle activate/deactivate
- Reset password (generates temp password, flash once)
- Last active admin cannot be deactivated
- Email must be unique
- Audit log every important change

## FR-2: Profile (all users)
- View own profile (name, email, role, last_login, created_at)
- Edit own name
- Change password (old password required, min 8 chars, confirm match)
- Cannot change own role or deactivate self

## FR-3: Security
- CSRF on all forms
- No plain text password storage
- Password hash never exposed
- Temp reset password shown via flash only once
