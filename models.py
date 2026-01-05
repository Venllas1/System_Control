from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(50), default='recepcion') # Roles: admin, operaciones, recepcion, almacen
    expires_at = db.Column(db.DateTime, nullable=True) # None = Permanente
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    @property
    def is_active(self):
        """Flask-Login checks this. If False, user is logged out."""
        return self.is_approved

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Constantes de Roles
class UserRoles:
    ADMIN = 'admin'
    OPERACIONES = 'operaciones'
    RECEPCION = 'recepcion'
    ALMACEN = 'almacen'
    VISUALIZADOR = 'visualizador'

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fr = db.Column(db.String(255), nullable=True)  # Increased limit
    marca = db.Column(db.String(255)) # Increased limit
    modelo = db.Column(db.String(255)) # Increased limit
    reporte_cliente = db.Column(db.Text)
    estado = db.Column(db.String(255), index=True) # Increased limit
    condicion = db.Column(db.String(255)) # Increased limit
    encargado = db.Column(db.String(255)) # Increased limit
    fecha_ingreso = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Campos adicionales para mantener integridad con el Excel original si es necesario
    observaciones = db.Column(db.Text)

    # Constantes de Estado
    class Status:
        ESPERA_DIAGNOSTICO = 'Espera de Diagnostico'
        EN_DIAGNOSTICO = 'en Diagnostico'
        ESPERA_REPUESTO_CONSUMIBLE = 'espera de repuesto o consumible'
        REPUESTO_ENTREGADO = 'Repuesto entregado'
        PENDIENTE_APROBACION = 'Pendiente de aprobacion'
        APROBADO = 'Aprobado'
        INICIO_SERVICIO = 'Inicio de Servicio'
        ESPERA_REPUESTOS = 'espera de repuestos'
        EN_SERVICIO = 'En servicio'
        SERVICIO_CULMINADO = 'Servicio culminado'
        ENTREGADO = 'Entregado'
    
    def to_dict(self):
        return {
            'FR': self.fr,
            'MARCA': self.marca,
            'MODELO': self.modelo,
            'REPORTE DE CLIENTE': self.reporte_cliente,
            'ESTADO': self.estado,
            'CONDICION': self.condicion,
            'ENCARGADO': self.encargado,
            'FECHA': self.fecha_ingreso.strftime('%Y-%m-%d') if self.fecha_ingreso else None
        }
            'FECHA': self.fecha_ingreso.strftime('%Y-%m-%d') if self.fecha_ingreso else None
        }

class GlobalSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True)
    value = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
