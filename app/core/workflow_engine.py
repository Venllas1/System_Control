"""
Workflow Engine - State Machine for Equipment Flow
Defines state transitions and role-based permissions for equipment workflow.
"""

class WorkflowEngine:
    """
    Centralized state machine for equipment workflow.
    Defines valid transitions and role permissions.
    """
    
    # State flow definition with transitions and permissions
    STATE_FLOW = {
        'Espera de Diagnostico': {
            'next': ['en Diagnostico'],
            'allowed_roles': ['admin', 'operaciones'],
            'requires_decision': False
        },
        'en Diagnostico': {
            'next': ['espera de repuesto o consumible', 'Pendiente de aprobacion'],
            'allowed_roles': ['admin', 'operaciones'],
            'requires_decision': True,
            'enter_prompts': ['encargado_diagnostico'],
            'exit_prompts': ['numero_informe'],
            'auto_fill': {'hora_inicio_diagnostico': 'now'}
        },
        'espera de repuesto o consumible': {
            'next': ['Repuesto entregado'],
            'allowed_roles': ['admin', 'almacen'],
            'requires_decision': False
        },
        'Repuesto entregado': {
            'next': ['Aprobado'],
            'allowed_roles': ['admin', 'operaciones'],
            'requires_decision': False
        },
        'Pendiente de aprobacion': {
            'next': ['Aprobado'],
            'allowed_roles': ['admin', 'recepcion'],
            'requires_decision': False
        },
        'Aprobado': {
            'next': ['Inicio de Servicio'],
            'allowed_roles': ['admin', 'operaciones'],
            'requires_decision': False
        },
        'Inicio de Servicio': {
            'next': ['En servicio'],
            'allowed_roles': ['admin', 'operaciones'],
            'requires_decision': False,
            'enter_prompts': ['encargado_mantenimiento'], # Prompt when entering
            'auto_fill': {'hora_inicio_mantenimiento': 'now'} # Auto-fill timestamp
        },
        'En servicio': {
            'next': ['espera de repuestos', 'Servicio culminado'],
            'allowed_roles': ['admin', 'operaciones'],
            'requires_decision': True
        },
        'espera de repuestos': {
            'next': ['En servicio'],
            'allowed_roles': ['admin', 'almacen'],
            'requires_decision': False
        },
        'Servicio culminado': {
            'next': ['Entregado'],
            'allowed_roles': ['admin', 'recepcion'],
            'requires_decision': False
        },
        'Entregado': {
            'next': None,  # Terminal state
            'allowed_roles': [],
            'requires_decision': False
        }
    }
    
    # Pending tasks logic: states that require action from each role
    PENDING_LOGIC = {
        'recepcion': ['Pendiente de aprobacion', 'Servicio culminado'],
        'operaciones': ['Espera de Diagnostico', 'en Diagnostico', 'Repuesto entregado', 
                        'Aprobado', 'Inicio de Servicio', 'En servicio'],
        'almacen': ['espera de repuesto o consumible', 'espera de repuestos'],
        'admin': [],  # Admin sees all but doesn't have specific "pending" states
        'visualizador': []  # Read-only role
    }
    
    @staticmethod
    def get_next_states(current_state):
        """
        Get the next possible state(s) for a given current state.
        
        Args:
            current_state (str): Current equipment state
            
        Returns:
            list or None: List of next possible states, or None if terminal state
        """
        state_info = WorkflowEngine.STATE_FLOW.get(current_state)
        if not state_info:
            return None
        return state_info.get('next')
    
    @staticmethod
    def can_advance(current_state, user_role):
        """
        Check if a user role can advance from the current state.
        
        Args:
            current_state (str): Current equipment state
            user_role (str): User's role
            
        Returns:
            bool: True if user can advance, False otherwise
        """
        state_info = WorkflowEngine.STATE_FLOW.get(current_state)
        if not state_info:
            return False
        
        # Terminal state cannot be advanced
        if state_info.get('next') is None:
            return False
        
        allowed_roles = state_info.get('allowed_roles', [])
        return user_role.lower() in allowed_roles
    
    @staticmethod
    def requires_decision(current_state):
        """
        Check if advancing from current state requires user decision.
        
        Args:
            current_state (str): Current equipment state
            
        Returns:
            bool: True if user must choose between multiple options
        """
        state_info = WorkflowEngine.STATE_FLOW.get(current_state)
        if not state_info:
            return False
        return state_info.get('requires_decision', False)
    
    @staticmethod
    def validate_transition(current_state, new_state, user_role):
        """
        Validate if a state transition is allowed.
        
        Args:
            current_state (str): Current equipment state
            new_state (str): Desired new state
            user_role (str): User's role
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        # Get state info
        state_info = WorkflowEngine.STATE_FLOW.get(current_state)
        if not state_info:
            return False, f"Estado actual '{current_state}' no reconocido en el flujo"
        
        # Check if terminal state
        next_states = state_info.get('next')
        if next_states is None:
            return False, "El equipo ya está en estado terminal (Entregado)"
        
        # Check if new_state is in allowed next states
        if new_state not in next_states:
            return False, f"Transición no permitida: '{current_state}' → '{new_state}'"
        
        # Check role permissions
        allowed_roles = state_info.get('allowed_roles', [])
        if user_role.lower() not in allowed_roles:
            return False, f"Tu rol ({user_role}) no puede avanzar equipos desde '{current_state}'"
        
        return True, None
    
    @staticmethod
    def get_pending_states_for_role(role):
        """
        Get states that are considered "pending" for a specific role.
        
        Args:
            role (str): User's role
            
        Returns:
            list: List of states that require action from this role
        """
        return WorkflowEngine.PENDING_LOGIC.get(role.lower(), [])

    @staticmethod
    def get_state_info(current_state, user_role, target_state=None):
        """
        Get comprehensive information about a state for a specific user.
        
        Args:
            current_state (str): Current equipment state
            user_role (str): User's role
            target_state (str, optional): Potential next state
            
        Returns:
            dict: State information including next states, permissions, etc.
        """
        current_info = WorkflowEngine.STATE_FLOW.get(current_state, {})
        next_states = current_info.get('next')
        
        # Determine prompts needed
        prompt_fields = []
        
        # 1. Exit prompts from current state (only if we are moving)
        if target_state:
            prompt_fields.extend(current_info.get('exit_prompts', []))
            
            # 2. Enter prompts for target state
            target_info = WorkflowEngine.STATE_FLOW.get(target_state, {})
            prompt_fields.extend(target_info.get('enter_prompts', []))
        
        # If no target state but only one possible next state, we can pre-calculate prompts
        elif next_states and len(next_states) == 1:
            target_state = next_states[0]
            prompt_fields.extend(current_info.get('exit_prompts', []))
            target_info = WorkflowEngine.STATE_FLOW.get(target_state, {})
            prompt_fields.extend(target_info.get('enter_prompts', []))

        return {
            'current_state': current_state,
            'next_states': next_states if next_states else [],
            'can_advance': WorkflowEngine.can_advance(current_state, user_role),
            'requires_decision': WorkflowEngine.requires_decision(current_state),
            'is_terminal': next_states is None,
            'allowed_roles': current_info.get('allowed_roles', []),
            'prompt_fields': list(set(prompt_fields)) # Unique fields
        }
