from models import UserRoles, Equipment

def validate_transition(current_status, new_status, user_role):
    """
    Valida si una transición de estado es permitida para un rol dado.
    """
    import unicodedata

    def norm(s):
        if not s: return ""
        # Normalización robusta: minúsculas, sin espacios, sin acentos
        s = str(s).lower().replace(" ", "").strip()
        return "".join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

    curr_norm = norm(current_status)
    next_norm = norm(new_status)
    STATUS = Equipment.Status
    
    # Normalize role
    role_norm = user_role.lower().strip() if user_role else ""

    # === REGLAS PARA ADMIN ===
    if role_norm == UserRoles.ADMIN.lower():
        return True, None

    # RESTRICCIÓN SENIOR: Solo Recepción/Admin pueden mover desde PENDIENTE
    if curr_norm == norm(STATUS.PENDIENTE_APROBACION):
        if role_norm != UserRoles.RECEPCION.lower():
            return False, "Solo el personal de Recepción o Administradores pueden aprobar equipos pendientes."

    # === REGLAS PARA RECEPCION ===
    if role_norm == UserRoles.RECEPCION.lower():
        valid_transitions = {
            norm(STATUS.PENDIENTE_APROBACION): [norm(STATUS.APROBADO)],
            norm(STATUS.SERVICIO_CULMINADO): [norm(STATUS.ENTREGADO)]
        }
        
        # Permitir registro inicial
        if not current_status and next_norm == norm(STATUS.ESPERA_DIAGNOSTICO):
            return True, None
            
        allowed = valid_transitions.get(curr_norm, [])
        if next_norm in allowed:
            return True, None
        
        return False, f"Recepción no puede cambiar de '{current_status}' a '{new_status}'."

    # === REGLAS PARA OPERACIONES ===
    if role_norm == UserRoles.OPERACIONES.lower():
        valid_transitions = {
            norm(STATUS.ESPERA_DIAGNOSTICO): [norm(STATUS.EN_DIAGNOSTICO)],
            norm("Espera Diagnostico"): [norm(STATUS.EN_DIAGNOSTICO)], # Alias without 'de'
            norm(STATUS.EN_DIAGNOSTICO): [
                norm(STATUS.PENDIENTE_APROBACION),
                norm(STATUS.ESPERA_REPUESTO_CONSUMIBLE)
            ],
            'diagnostico': [ # Legacy support
                norm(STATUS.PENDIENTE_APROBACION),
                norm(STATUS.ESPERA_REPUESTO_CONSUMIBLE)
            ],
            norm(STATUS.REPUESTO_ENTREGADO): [norm(STATUS.PENDIENTE_APROBACION)],
            norm(STATUS.APROBADO): [norm(STATUS.INICIO_SERVICIO)],
            norm(STATUS.INICIO_SERVICIO): [norm(STATUS.SERVICIO_CULMINADO), norm(STATUS.ESPERA_REPUESTOS)],
            norm(STATUS.ESPERA_REPUESTOS): [norm(STATUS.EN_SERVICIO)],
            norm(STATUS.EN_SERVICIO): [norm(STATUS.SERVICIO_CULMINADO), norm(STATUS.ESPERA_REPUESTOS)]
        }

        allowed = valid_transitions.get(curr_norm, [])
        if next_norm in allowed:
            return True, None

        return False, f"Operaciones no puede cambiar de '{current_status}' a '{new_status}'."

    # === REGLAS PARA ALMACEN ===
    if role_norm == UserRoles.ALMACEN.lower():
        valid_transitions = {
            norm(STATUS.ESPERA_REPUESTO_CONSUMIBLE): [norm(STATUS.REPUESTO_ENTREGADO)],
            norm(STATUS.ESPERA_REPUESTOS): [norm(STATUS.EN_SERVICIO)]
        }

        allowed = valid_transitions.get(curr_norm, [])
        if next_norm in allowed:
            return True, None
            
        return False, f"Almacén no puede cambiar de '{current_status}' a '{new_status}'."

    return False, "Rol no autorizado o transición desconocida."
