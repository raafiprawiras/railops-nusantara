# Design — User Administration & Profile

## Routes
| Method | URL | Roles |
|--------|-----|-------|
| GET | /users | admin |
| GET/POST | /users/create | admin |
| GET | /users/<id> | admin |
| GET/POST | /users/<id>/edit | admin |
| POST | /users/<id>/toggle-status | admin |
| POST | /users/<id>/reset-password | admin |
| GET | /profile | all |
| GET/POST | /profile/edit | all |
| GET/POST | /profile/change-password | all |

## Forms
- UserCreateForm: full_name, email, role, password, confirm_password
- UserEditForm: full_name, email, role, is_active
- ProfileEditForm: full_name
- ChangePasswordForm: old_password, new_password, confirm_password
