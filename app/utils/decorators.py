"""Custom decorators for access control."""

from functools import wraps

from flask import abort
from flask_login import current_user


def role_required(*roles: str):
    """Decorator that restricts access to users with specified roles.

    Args:
        *roles: Allowed role strings (e.g., 'administrator', 'operator').

    Usage:
        @role_required('administrator')
        def admin_panel():
            ...

        @role_required('administrator', 'supervisor')
        def reports():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
