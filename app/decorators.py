from functools import wraps
from flask import abort
from flask.ext.login import current_user
from .models import Permission

def permission_required(permission):
    """
    Check if current user has a permission to perform action.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """
    Check if current user is administrator.
    """
    return permission_required(Permission.ADMINISTER)(f)
