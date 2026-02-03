import unicodedata

def normalize_state_key(s):
    if not s: return ""
    # Remove accents and lowercase
    s = str(s).lower()
    return "".join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

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
            'auto_fill': {'hora_inicio_diagnostico': 'now'}
        },
        'espera de repuesto o consumible': {
            'next': ['en Diagnostico'],
            'allowed_roles': ['admin', 'almacen'],
            'requires_decision': False
        },
        'Pendiente de aprobacion': {
            'next': ['Aprobado', 'Entregado - Devolucion', 'Revision'],
            'allowed_roles': ['admin', 'recepcion'],
            'requires_decision': True,
            'enter_prompts': ['numero_informe', 'observaciones_diagnostico']
        },
        'Aprobado': {
            'next': ['En servicio'],
            'allowed_roles': ['admin', 'operaciones'],
            'requires_decision': True,
            'auto_fill': {'hora_aprobacion': 'now'}
        },
        'En servicio': {
            'next': ['espera de repuestos', 'Entregado'],
            'allowed_roles': ['admin', 'operaciones'],
            'requires_decision': True,
            'enter_prompts': ['encargado_mantenimiento'],
            'auto_fill': {'hora_inicio_mantenimiento': 'now'},
            'exit_prompts': ['observaciones_mantenimiento']
        },
        'espera de repuestos': {
            'next': ['En servicio'],
            'allowed_roles': ['admin', 'almacen'],
            'requires_decision': False
        },
        'Revision': {
            'next': ['en Diagnostico', 'Entregado - Devolucion'],
            'allowed_roles': ['admin', 'operaciones'],
            'requires_decision': True
        },
        'Entregado': {
            'next': None,  # Terminal state
            'allowed_roles': [],
            'requires_decision': False,
            'auto_fill': {'hora_entregado': 'now'}
        },
        'Entregado - Devolucion': {
            'next': None,  # Terminal state
            'allowed_roles': [],
            'requires_decision': False,
            'auto_fill': {'hora_entregado': 'now'}
        }
    }
    
    # Pending tasks logic: states that require action from each role
    PENDING_LOGIC = {
        'recepcion': ['Pendiente de aprobacion'],
        'operaciones': ['Espera de Diagnostico', 'en Diagnostico', 
                        'Aprobado', 'En servicio'],
        'almacen': ['espera de repuesto o consumible', 'espera de repuestos'],
        'admin': [],  # Admin sees all but doesn't have specific "pending" states
        'visualizador': []  # Read-only role
    }
    
    @staticmethod
    def _get_state_info_normalized(current_state):
        """Helper to find state info by normalized key."""
        target = normalize_state_key(current_state)
        for key, info in WorkflowEngine.STATE_FLOW.items():
            if normalize_state_key(key) == target:
                return key, info
        return None, None

    @staticmethod
    def get_next_states(current_state):
        """
        Get the next possible state(s) for a given current state.
        
        Args:
            current_state (str): Current equipment state
            
        Returns:
            list or None: List of next possible states, or None if terminal state
        """
        _, state_info = WorkflowEngine._get_state_info_normalized(current_state)
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
        _, state_info = WorkflowEngine._get_state_info_normalized(current_state)
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
        _, state_info = WorkflowEngine._get_state_info_normalized(current_state)
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
        canon_key, state_info = WorkflowEngine._get_state_info_normalized(current_state)
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
        canon_key, current_info = WorkflowEngine._get_state_info_normalized(current_state)
        if not current_info: current_info = {}
        next_states = current_info.get('next')
        
        # Determine prompts needed
        prompt_fields = []
        
        # 1. Exit prompts from current state (only if we are moving)
        if target_state:
            prompt_fields.extend(current_info.get('exit_prompts', []))
            
            # 2. Enter prompts for target state
            _, target_info = WorkflowEngine._get_state_info_normalized(target_state)
            if not target_info: target_info = {}
            prompt_fields.extend(target_info.get('enter_prompts', []))
        
        # If no target state but only one possible next state, we can pre-calculate prompts
        elif next_states and len(next_states) == 1:
            target_state = next_states[0]
            prompt_fields.extend(current_info.get('exit_prompts', []))
            _, target_info = WorkflowEngine._get_state_info_normalized(target_state)
            if not target_info: target_info = {}
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
