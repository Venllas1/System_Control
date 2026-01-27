import os
from datetime import timedelta

class Config:
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    db_url = os.environ.get('POSTGRES_URL') or os.environ.get('DATABASE_URL')
    if db_url:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = db_url
    else:
        # Local fallback
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'cabelab.db')
            
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Professional Configuration: Dashboard Roles mapping
    # Defines what each role sees and can do
    DASHBOARD_ROLES = {
        'admin': {
            'can_view_all': True,
            'can_edit': True,
            'stats_visible': True,
            'tables': ['active', 'history'],
            'columns': ['encargado_diagnostico'],
            'actions': ['view', 'edit', 'delete']
        },
        'recepcion': {
            'can_view_all': False,
            'can_edit': True,
            'stats_visible': False,
            'tables': ['relevant', 'history'],
            'columns': ['encargado_diagnostico'],
            'relevant_statuses': [
                'Espera de Diagnostico',
                'Pendiente de aprobacion'
            ],
            'actions': ['view', 'edit']
        },
        'operaciones': {
            'can_view_all': False,
            'can_edit': True,
            'stats_visible': False,
            'tables': ['relevant', 'history'],
            'columns': ['encargado_diagnostico'],
            'relevant_statuses': [
                'Espera de Diagnostico',
                'en Diagnostico',
                'DIAGNOSTICO',
                'espera de repuesto o consumible',
                'Repuesto entregado',
                'Aprobado',
                'Inicio de Servicio',
                'En servicio'
            ],
            'actions': ['view', 'edit']
        },
        'almacen': {
            'can_view_all': False,
            'can_edit': True,
            'stats_visible': False,
            'tables': ['relevant'],
            'columns': ['encargado_diagnostico'],
            'relevant_statuses': [
                'espera de repuestos',
                'espera de repuesto o consumible'
            ],
            'actions': ['view', 'edit']
        },
        'visualizador': {
            'can_view_all': True,
            'can_edit': True,
            'stats_visible': True,
            'tables': ['active', 'history'],
            'columns': [],
            'actions': ['view', 'edit']
        }
    }
