
import os

class Config:
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Database
    if os.environ.get('VERCEL'):
        # Vercel: Use writable /tmp directory
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/cabelab.db'
    else:
        # Local: Use project root
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join(BASE_DIR, 'cabelab.db')
            
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuración de ruta Excel (para migración histórica solamente)
    # Configuración de ruta Excel (para migración histórica solamente)
    EXCEL_PATH_LEGACY = r"G:\.shortcut-targets-by-id\1xDetM5Ublhlwkhbm90gGSrkvIPJ8k0Nn\AREA TECNICA\01. SEDE CABELAB\04. CONTROL DE EQUIPOS\Copia de CONTROL DE EQUIPOS CABELAB(Recuperado automáticamente).xlsx"
    
    # Columnas (Restored)
    COLUMNAS_PRINCIPALES = ['FR', 'MARCA', 'MODELO', 'REPORTE DE CLIENTE', 'ESTADO', 'CONDICION']
    COLUMNAS_SERVICIO = ['FR', 'MARCA', 'MODELO', 'ENCARGADO']
    COLUMNAS_DETALLE = ['FR', 'MARCA', 'MODELO', 'REPORTE DE CLIENTE', 'ESTADO', 'CONDICION', 'ENCARGADO', 'FECHA']
    
    # Estados permitidos (para validación)
    ESTADOS = {
        'DIAGNOSTICO': 'DIAGNOSTICO',
        'APROBADO': 'APROBADO',
        'PENDIENTE': ['PENDIENTE DE APROBACION', 'PENDIENTE DE APROBACIÓN', 'PENDIENTE']
    }
    
    # Flask
    DEBUG = False # Set to False for production
    HOST = '0.0.0.0'
    PORT = 5000