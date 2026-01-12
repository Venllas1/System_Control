from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
from app.core.config import Config

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role.lower() not in [r.lower() for r in roles]:
                flash('No tienes permisos para realizar esta acción.', 'danger')
                return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def can_perform_action(user, action):
    role_config = Config.DASHBOARD_ROLES.get(user.role.lower(), Config.DASHBOARD_ROLES['visualizador'])
    allowed_actions = role_config.get('actions', [])
    return action in allowed_actions
