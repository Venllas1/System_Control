
import os

class Config:
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Database
    # Vercel Postgres usually sets POSTGRES_URL or DATABASE_URL
    db_url = os.environ.get('POSTGRES_URL') or os.environ.get('DATABASE_URL')
    
    if db_url:
        # Fix for SQLAlchemy: Vercel/Neon provides 'postgres://', we need 'postgresql://'
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = db_url
    elif os.environ.get('VERCEL'):
        # Fallback to tmp sqlite if no Postgres connected yet
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/cabelab.db'
    else:
        # Local
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'cabelab.db')
            
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    

    
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