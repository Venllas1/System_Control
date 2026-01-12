from datetime import datetime, timedelta
from sqlalchemy import or_, func
from app.extensions import db
from app.models.equipment import Equipment, StatusHistory
from app.core.config import Config

class EquipmentService:
    @staticmethod
    def get_dashboard_config(user):
        role = user.role.lower()
        return Config.DASHBOARD_ROLES.get(role, Config.DASHBOARD_ROLES['visualizador'])

    @staticmethod
    def get_equipment_by_role(user):
        config = EquipmentService.get_dashboard_config(user)
        query = Equipment.query

        if config.get('can_view_all'):
            # Admin and Visualizador see everything active
            return query.filter(~Equipment.estado.ilike('%entregado%')).order_by(Equipment.fecha_ingreso.desc()).all()
        
        # Others see relevant statuses defined in config
        relevant_statuses = config.get('relevant_statuses', [])
        return query.filter(Equipment.estado.in_(relevant_statuses)).order_by(Equipment.fecha_ingreso.desc()).all()

    @staticmethod
    def get_history():
        # Entregados history is visible to most roles (except Almacen as per user preference)
        return Equipment.query.filter(Equipment.estado.ilike('%entregado%')).order_by(Equipment.fecha_ingreso.desc()).all()

    @staticmethod
    def get_admin_stats():
        now = datetime.now()
        fecha_limite = now - timedelta(days=5)
        fecha_30_dias = now - timedelta(days=30)

        stats = {
            'total': Equipment.query.count(),
            'activos': Equipment.query.filter(~Equipment.estado.ilike('%entregado%')).count(),
            'atrasados': Equipment.query.filter(
                ~Equipment.estado.ilike('%entregado%'),
                Equipment.fecha_ingreso < fecha_limite
            ).count(),
            'ultima_actualizacion': now.strftime('%d/%m/%Y %H:%M:%S')
        }

        # Tiempo promedio (30 days)
        recientes = Equipment.query.filter(
            Equipment.estado.ilike('%entregado%'),
            Equipment.fecha_ingreso >= fecha_30_dias
        ).all()
        
        if recientes:
            tiempos = [(now - eq.fecha_ingreso).days for eq in recientes]
            stats['tiempo_promedio'] = round(sum(tiempos) / len(tiempos), 1)
        else:
            stats['tiempo_promedio'] = 0

        return stats

    @staticmethod
    def update_status(equipment_id, new_status, user_name, encargado=None):
        equipment = Equipment.query.get(equipment_id)
        if not equipment:
            return False, "Equipo no encontrado"

        prev_status = equipment.estado
        equipment.estado = new_status
        if encargado:
            equipment.encargado = encargado

        # Log History
        history = StatusHistory(
            equipment_id=equipment.id,
            previous_status=prev_status,
            new_status=new_status,
            changed_by=user_name
        )
        db.session.add(history)
        db.session.commit()
        return True, "Estado actualizado"

    @staticmethod
    def create_equipment(data):
        try:
            new_eq = Equipment(
                fr=data.get('fr', '').upper(),
                marca=data.get('marca', '').upper(),
                modelo=data.get('modelo', '').upper(),
                reporte_cliente=data.get('reporte_cliente', '').upper(),
                observaciones=data.get('observaciones', '').upper(),
                encargado=data.get('encargado', 'No asignado'),
                cliente=data.get('cliente', '').upper(),
                serie=data.get('serie', '').upper(),
                accesorios=data.get('accesorios', '').upper(),
                fecha_ingreso=datetime.now(),
                estado=Equipment.Status.ESPERA_DIAGNOSTICO
            )
            db.session.add(new_eq)
            db.session.commit()
            return True, new_eq
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def search(search_query):
        search_pattern = f"%{search_query}%"
        return Equipment.query.filter(or_(
            Equipment.fr.ilike(search_pattern),
            Equipment.marca.ilike(search_pattern),
            Equipment.modelo.ilike(search_pattern),
            Equipment.encargado.ilike(search_pattern),
            Equipment.cliente.ilike(search_pattern)
        )).limit(100).all()

    @staticmethod
    def delete_equipment(equipment_id):
        eq = Equipment.query.get(equipment_id)
        if eq:
            db.session.delete(eq)
            db.session.commit()
            return True
        return False
