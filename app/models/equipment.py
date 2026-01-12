from app.extensions import db
from datetime import datetime

class Equipment(db.Model):
    __tablename__ = 'equipment'
    id = db.Column(db.Integer, primary_key=True)
    fr = db.Column(db.String(255), nullable=True)
    marca = db.Column(db.String(255))
    modelo = db.Column(db.String(255))
    reporte_cliente = db.Column(db.Text)
    estado = db.Column(db.String(255), index=True)
    condicion = db.Column(db.String(255))
    encargado = db.Column(db.String(255))
    fecha_ingreso = db.Column(db.DateTime, default=datetime.utcnow)
    observaciones = db.Column(db.Text)
    cliente = db.Column(db.String(255))
    serie = db.Column(db.String(255))
    accesorios = db.Column(db.Text)
    numero_informe = db.Column(db.String(255))

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
            'id': self.id,
            'fr': self.fr,
            'marca': self.marca,
            'modelo': self.modelo,
            'estado': self.estado,
            'cliente': self.cliente,
            'fecha_ingreso': self.fecha_ingreso.strftime('%Y-%m-%d') if self.fecha_ingreso else None,
            'encargado': self.encargado,
            'reporte_cliente': self.reporte_cliente,
            'observaciones': self.observaciones,
            'serie': self.serie,
            'accesorios': self.accesorios,
            'condicion': self.condicion,
            'numero_informe': self.numero_informe
        }

class StatusHistory(db.Model):
    __tablename__ = 'status_history'
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    previous_status = db.Column(db.String(255))
    new_status = db.Column(db.String(255))
    changed_by = db.Column(db.String(80))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    equipment = db.relationship('Equipment', backref=db.backref('history', lazy=True))
