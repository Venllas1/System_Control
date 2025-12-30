"""
Middleware de seguridad para Flask
Bloquea todas las rutas si la licencia no es válida
"""

from functools import wraps
from flask import redirect, url_for, render_template, session
from datetime import datetime
import logging

from utils.license_manager import LicenseManager

# Logger
logger = logging.getLogger(__name__)


class LicenseMiddleware:
    """
    Middleware que intercepta todas las peticiones
    y verifica la licencia antes de continuar
    """
    
    def __init__(self, app=None):
        self.app = app
        self.manager = LicenseManager()
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa el middleware con la app Flask"""
        
        # Registrar before_request
        @app.before_request
        def check_license():
            # Rutas públicas que no requieren licencia
            public_routes = ['/license/activate', '/license/status', '/static']
            
            # Verificar si es ruta pública
            from flask import request
            if any(request.path.startswith(route) for route in public_routes):
                return None
            
            # Validar licencia
            result = self.manager.validate_license()
            
            if not result['valid']:
                logger.warning(f"Intento de acceso sin licencia válida: {result['message']}")
                return render_template('license_error.html', 
                                     error=result['message'],
                                     hardware_id=self.manager.get_hardware_id())
            
            # Advertencia si está por vencer
            if self.manager.check_expiry_warning():
                session['license_warning'] = result.get('days_remaining', 0)
    
    def require_license(self, f):
        """
        Decorador para proteger rutas específicas
        Uso: @require_license
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = self.manager.validate_license()
            
            if not result['valid']:
                return render_template('license_error.html',
                                     error=result['message'],
                                     hardware_id=self.manager.get_hardware_id()), 403
            
            return f(*args, **kwargs)
        
        return decorated_function


def require_license(f):
    """
    Decorador standalone para proteger rutas
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        manager = LicenseManager()
        result = manager.validate_license()
        
        if not result['valid']:
            logger.warning(f"Acceso bloqueado a {f.__name__}: {result['message']}")
            return render_template('license_error.html',
                                 error=result['message'],
                                 hardware_id=manager.get_hardware_id()), 403
        
        return f(*args, **kwargs)
    
    return decorated_function