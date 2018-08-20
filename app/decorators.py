from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission


def permission_required(permission):
    def decorate(f):
        @wraps(f)
        def decrated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decrated_function
    return decorate


def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)

