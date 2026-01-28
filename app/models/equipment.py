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
    encargado_diagnostico = db.Column(db.String(255))
    fecha_ingreso = db.Column(db.DateTime, default=datetime.utcnow)
    observaciones = db.Column(db.Text)
    cliente = db.Column(db.String(255))
    serie = db.Column(db.String(255))
    accesorios = db.Column(db.Text)
    numero_informe = db.Column(db.String(255))
    
    # New Fields for Excel View
    encargado_mantenimiento = db.Column(db.String(255))
    hora_inicio_diagnostico = db.Column(db.DateTime)
    observaciones_diagnostico = db.Column(db.Text)
    hora_inicio_mantenimiento = db.Column(db.DateTime)
    hora_aprobacion = db.Column(db.DateTime)
    observaciones_mantenimiento = db.Column(db.Text)

    class Status:
        ESPERA_DIAGNOSTICO = 'Espera de Diagnostico'
        EN_DIAGNOSTICO = 'en Diagnostico'
        ESPERA_REPUESTO_CONSUMIBLE = 'espera de repuesto o consumible'
        REPUESTO_ENTREGADO = 'Repuesto entregado'
        PENDIENTE_APROBACION = 'Pendiente de aprobacion'
        APROBADO = 'Aprobado'

        ESPERA_REPUESTOS = 'espera de repuestos'
        EN_SERVICIO = 'En servicio'
        ENTREGADO = 'Entregado'
        ENTREGADO_DEVOLUCION = 'Entregado - Devolucion'
        RECHAZADO = 'Rechazado'
        REVISION = 'Revision'

    def to_dict(self):
        def parse_date(dt):
            if not dt: return None
            if isinstance(dt, str): return dt
            if isinstance(dt, datetime):
                # Format: DD/MM/YYYY HH:MM AM/PM
                return dt.strftime('%d/%m/%Y %I:%M %p')
            return str(dt)

        return {
            'id': self.id,
            'fr': self.fr,
            'marca': self.marca,
            'modelo': self.modelo,
            'estado': self.estado,
            'cliente': self.cliente,
            'fecha_ingreso': parse_date(self.fecha_ingreso),
            'encargado_diagnostico': self.encargado_diagnostico,
            'reporte_cliente': self.reporte_cliente,
            'observaciones': self.observaciones,
            'serie': self.serie,
            'accesorios': self.accesorios,
            'condicion': self.condicion,
            'numero_informe': self.numero_informe,
            'encargado_mantenimiento': self.encargado_mantenimiento,
            'hora_inicio_diagnostico': parse_date(self.hora_inicio_diagnostico),
            'observaciones_diagnostico': self.observaciones_diagnostico,
            'hora_inicio_mantenimiento': parse_date(self.hora_inicio_mantenimiento),
            'hora_aprobacion': parse_date(self.hora_aprobacion),
            'observaciones_mantenimiento': self.observaciones_mantenimiento
        }

class StatusHistory(db.Model):
    __tablename__ = 'status_history'
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    previous_status = db.Column(db.String(255))
    new_status = db.Column(db.String(255))
    changed_by = db.Column(db.String(80))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    equipment = db.relationship('Equipment', backref=db.backref('history', lazy=True, cascade='all, delete-orphan'))
