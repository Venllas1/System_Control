from datetime import datetime, timedelta
from sqlalchemy import or_, func
from app.extensions import db
from app.models.equipment import Equipment, StatusHistory
from app.core.config import Config
from app.core.workflow_engine import WorkflowEngine

class EquipmentService:
    @staticmethod
    def get_dashboard_config(user):
        role = user.role.lower()
        return Config.DASHBOARD_ROLES.get(role, Config.DASHBOARD_ROLES['visualizador'])

    @staticmethod
    def get_equipment_by_role(user, include_delivered=False):
        config = EquipmentService.get_dashboard_config(user)
        query = Equipment.query

        if config.get('can_view_all'):
            # Admin and Visualizador see everything active
            # If include_delivered is True (for panel_estados), include all equipment
            if include_delivered:
                return query.order_by(Equipment.fecha_ingreso.desc()).all()
            else:
                return query.filter(~Equipment.estado.ilike('%entregado%')).order_by(Equipment.fecha_ingreso.desc()).all()
        
        # Others see relevant statuses defined in config
        relevant_statuses = config.get('relevant_statuses', [])
        
        # If include_delivered, also add delivered equipment
        if include_delivered:
            # Use or_ to combine: either in relevant_statuses OR is delivered
            from sqlalchemy import or_
            return query.filter(
                or_(
                    Equipment.estado.in_(relevant_statuses),
                    Equipment.estado.ilike('%entregado%')
                )
            ).order_by(Equipment.fecha_ingreso.desc()).all()
        
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
    def _update_status_internal(equipment_id, new_status, user_name, encargado=None):
        """
        Internal method to update equipment status and log history.
        WARNING: This method does NOT validate transitions.
        Use advance_to_next_state() for validated state changes.
        """
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
                fecha_ingreso=datetime.strptime(data['fecha_ingreso'], '%Y-%m-%d') if data.get('fecha_ingreso') else datetime.now(),
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

    @staticmethod
    def get_pending_tasks(user):
        """
        Get equipment that requires action from the user's role.
        Returns equipment in states that are pending for the user's role,
        ordered by oldest first (priority).
        """
        role = user.role.lower()
        pending_states = WorkflowEngine.get_pending_states_for_role(role)
        
        if not pending_states:
            return []
        
        # Get active equipment (not delivered) in pending states
        return Equipment.query.filter(
            Equipment.estado.in_(pending_states),
            ~Equipment.estado.ilike('%entregado%')
        ).order_by(Equipment.fecha_ingreso.asc()).all()
    
    @staticmethod
    def get_next_state_info(equipment_id, user):
        """
        Get information about the next possible state(s) for an equipment.
        
        Returns:
            dict: Information about current state, next states, and permissions
        """
        equipment = Equipment.query.get(equipment_id)
        if not equipment:
            return None
        
        role = user.role.lower()
        state_info = WorkflowEngine.get_state_info(equipment.estado, role)
        
        return {
            'equipment_id': equipment_id,
            'current_state': equipment.estado,
            'next_states': state_info['next_states'],
            'can_advance': state_info['can_advance'],
            'requires_decision': state_info['requires_decision'],
            'is_terminal': state_info['is_terminal']
        }
    
    @staticmethod
    def advance_to_next_state(equipment_id, user, next_state=None):
        """
        Advance equipment to the next state in the workflow.
        Validates transitions and role permissions.
        
        Args:
            equipment_id: ID of the equipment
            user: User object performing the action
            next_state: Specific next state (required if multiple options exist)
            
        Returns:
            tuple: (success: bool, message: str, new_state: str or None)
        """
        equipment = Equipment.query.get(equipment_id)
        if not equipment:
            return False, "Equipo no encontrado", None
        
        current_state = equipment.estado
        role = user.role.lower()
        
        # Get possible next states
        next_states = WorkflowEngine.get_next_states(current_state)
        
        if next_states is None:
            return False, "El equipo ya está en estado terminal (Entregado)", None
        
        # Check if user can advance from current state
        if not WorkflowEngine.can_advance(current_state, role):
            return False, f"Tu rol ({user.role}) no puede avanzar equipos desde '{current_state}'", None
        
        # Determine the target state
        if len(next_states) == 1:
            # Only one option, use it
            target_state = next_states[0]
        elif len(next_states) > 1:
            # Multiple options, user must specify
            if not next_state:
                return False, "Debes seleccionar el siguiente estado", None
            if next_state not in next_states:
                return False, f"Estado '{next_state}' no es una opción válida desde '{current_state}'", None
            target_state = next_state
        else:
            return False, "No hay estados siguientes definidos", None
        
        # Validate the transition
        is_valid, error_msg = WorkflowEngine.validate_transition(current_state, target_state, role)
        if not is_valid:
            return False, error_msg, None
        
        # Perform the state change (internal method without validation)
        success, message = EquipmentService._update_status_internal(
            equipment_id,
            target_state,
            user.username
        )
        
        if success:
            return True, f"Equipo avanzado de '{current_state}' a '{target_state}'", target_state
        else:
            return False, message, None

    @staticmethod
    def update_equipment_data(equipment_id, data):
        """
        Update general equipment data without changing status.
        Ignores 'estado' field to ensure workflow integrity.
        """
        try:
            eq = Equipment.query.get(equipment_id)
            if not eq:
                return False, "Equipo no encontrado"

            # Helper to handle empty/trimmed strings
            def get_val(key):
                val = data.get(key)
                if val is None: return None
                val = val.strip()
                return val if val != "" else None

            # Update uppercase fields
            if 'fr' in data: 
                val = get_val('fr')
                eq.fr = val.upper() if val else None
            if 'marca' in data: 
                val = get_val('marca')
                eq.marca = val.upper() if val else None
            if 'modelo' in data: 
                val = get_val('modelo')
                eq.modelo = val.upper() if val else None
            if 'cliente' in data: 
                val = get_val('cliente')
                eq.cliente = val.upper() if val else None
            if 'serie' in data: 
                val = get_val('serie')
                eq.serie = val.upper() if val else None
            if 'accesorios' in data: 
                val = get_val('accesorios')
                eq.accesorios = val.upper() if val else None
            if 'reporte_cliente' in data: 
                val = get_val('reporte_cliente')
                eq.reporte_cliente = val.upper() if val else None
            if 'observaciones' in data: 
                val = get_val('observaciones')
                eq.observaciones = val.upper() if val else None
            
            if 'condicion' in data: eq.condicion = get_val('condicion')
            if 'numero_informe' in data: eq.numero_informe = get_val('numero_informe')
            
            # New Excel Fields (handled as strings, but we format the 'T' from datetime-local)
            if 'encargado_mantenimiento' in data: eq.encargado_mantenimiento = get_val('encargado_mantenimiento')
            
            if 'hora_inicio_diagnostico' in data:
                val = get_val('hora_inicio_diagnostico')
                if val: val = val.replace('T', ' ')
                eq.hora_inicio_diagnostico = val
            
            if 'observaciones_diagnostico' in data: eq.observaciones_diagnostico = get_val('observaciones_diagnostico')
            
            if 'hora_inicio_mantenimiento' in data:
                val = get_val('hora_inicio_mantenimiento')
                if val: val = val.replace('T', ' ')
                eq.hora_inicio_mantenimiento = val
            
            if 'observaciones_mantenimiento' in data: eq.observaciones_mantenimiento = get_val('observaciones_mantenimiento')
            
            # Encargado can be updated here
            if 'encargado' in data: eq.encargado = get_val('encargado')

            db.session.commit()
            return True, "Datos actualizados correctamente"
        except Exception as e:
            db.session.rollback()
            return False, str(e)

