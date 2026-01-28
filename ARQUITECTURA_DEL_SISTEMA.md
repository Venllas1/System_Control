# ARQUITECTURA DEL SISTEMA - Sistema de Control de Equipos CABELAB
 
 ## 📋 Visión General del Sistema
 
 ### Propósito
 Sistema web de gestión y seguimiento de equipos de motosoldadoras que permite coordinar el flujo operativo entre diferentes áreas de la empresa (recepción, operaciones, almacén, administración). El sistema registra equipos, gestiona sus estados a lo largo del ciclo de servicio, y proporciona visibilidad diferenciada según el rol del usuario.
 
 ### Problema que Resuelve
 - **Coordinación entre áreas**: Elimina la descoordinación entre recepción, técnicos, almacén y administración
 - **Trazabilidad**: Mantiene historial completo de cambios de estado de cada equipo
 - **Control de acceso**: Diferentes roles ven solo la información relevante a su función
 - **Seguimiento temporal**: Identifica equipos atrasados y calcula tiempos promedio de servicio
 - **Gestión de usuarios**: Sistema de permisos temporales y permanentes con aprobación administrativa
 
 ### Tecnologías Principales
 - **Backend**: Flask 3.0.0 (Python)
 - **ORM**: Flask-SQLAlchemy 3.1.1
 - **Autenticación**: Flask-Login 0.6.3
 - **Base de datos**: PostgreSQL (producción) / SQLite (desarrollo)
 - **Procesamiento de datos**: Pandas, OpenPyXL
 - **Frontend**: HTML, CSS, JavaScript (vanilla)
 
 ---
 
 ## 🏗️ Arquitectura General
 
 ### Patrón Arquitectónico
 **Arquitectura modular basada en Blueprints de Flask** con separación clara de responsabilidades:
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                      │
│  Templates (Jinja2) + Static (CSS/JS)                       │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  CAPA DE CONTROLADORES                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐              │
│  │   Auth   │  │   API    │  │  Dashboard   │              │
│  │Blueprint │  │Blueprint │  │  Blueprint   │              │
│  └──────────┘  └──────────┘  └──────────────┘              │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   CAPA DE SERVICIOS                          │
│  ┌────────────────────────────────────────────┐             │
│  │      EquipmentService (Lógica de Negocio)  │             │
│  └────────────────────────────────────────────┘             │
│  ┌────────────────────────────────────────────┐             │
│  │   WorkflowEngine (Validación de Estados)   │ ⚡ CRÍTICO  │
│  └────────────────────────────────────────────┘             │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                    CAPA DE MODELOS                           │
│  ┌──────────────┐  ┌────────────────┐                       │
│  │  Equipment   │  │  User          │                       │
│  │  (Equipos)   │  │  (Usuarios)    │                       │
│  └──────────────┘  └────────────────┘                       │
│  ┌──────────────────────────────────┐                       │
│  │  StatusHistory (Historial)       │                       │
│  └──────────────────────────────────┘                       │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                 CAPA DE PERSISTENCIA                         │
│  PostgreSQL (Producción) / SQLite (Desarrollo)              │
└─────────────────────────────────────────────────────────────┘
### Estructura de Carpetas
Pizarra Virtual/
├── app/                          # Aplicación principal
│   ├── __init__.py              # Factory de aplicación Flask
│   ├── extensions.py            # Inicialización de extensiones (db, login_manager)
│   │
│   ├── blueprints/              # Módulos de rutas
│   │   ├── __init__.py
│   │   ├── auth/                # Autenticación y gestión de usuarios
│   │   │   └── routes.py        # Login, registro, admin de usuarios
│   │   ├── api/                 # Endpoints REST
│   │   │   └── routes.py        # CRUD equipos, búsqueda, exportación
│   │   └── dashboard/           # Vistas principales
│   │       └── routes.py        # Dashboard, panel de estados, gestión general
│   │
│   ├── models/                  # Modelos de datos (ORM)
│   │   ├── __init__.py
│   │   ├── equipment.py         # Modelo Equipment + StatusHistory
│   │   └── user.py              # Modelo User + UserRoles
│   │
│   ├── services/                # Lógica de negocio
│   │   └── equipment_service.py # Servicio principal de equipos
│   │
│   ├── core/                    # Configuración y utilidades
│   │   ├── config.py            # Configuración por roles (DASHBOARD_ROLES)
│   │   ├── permissions.py       # Decoradores de permisos
│   │   └── workflow_engine.py   # Motor de flujo de trabajo (máquina de estados)
│   │
│   ├── templates/               # Plantillas HTML (Jinja2)
│   │   ├── base.html            # Plantilla base
│   │   ├── dashboard.html       # Dashboard principal
│   │   ├── panel_estados.html   # Panel de estados
│   │   ├── dashboard_modals.html # Modales de edición
│   │   ├── gestion_general.html # Panel de gestión general
│   │   ├── gestion_excel.html   # Panel de gestión Excel
│   │   ├── auth/                # Plantillas de autenticación
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   │   ├── admin_users.html
│   │   │   └── change_password.html
│   │   └── macros/              # Macros reutilizables
│   │
│   └── static/                  # Recursos estáticos
│       ├── css/                 # Estilos
│       ├── js/                  # Scripts JavaScript
│       └── img/                 # Imágenes
│
├── scripts/                     # Scripts de utilidad
│   ├── add_missing_columns.py   # Script de migración de columnas
│   └── migrate_to_timestamp.py  # Script de migración de timestamps
│
├── manage.py                    # Punto de entrada para desarrollo local
├── wsgi.py                      # Entrada para servidores WSGI (Vercel)
├── requirements.txt             # Dependencias Python
├── vercel.json                  # Configuración de despliegue Vercel
├── diagnostico_vercel.py        # Script de diagnóstico
├── ARQUITECTURA_DEL_SISTEMA.md  # Este documento
├── README.md                    # Documentación principal
├── DEPLOY_GUIA.md              # Guía de despliegue
├── GUIA_DESARROLLO.md          # Guía de desarrollo
└── cabelab.db                   # Base de datos SQLite (solo desarrollo local)
---

## ⚡ WorkflowEngine - Motor de Flujo de Trabajo

### Propósito
**Componente crítico** que implementa una máquina de estados para validar transiciones de equipos y controlar permisos por rol. Garantiza la integridad del flujo operativo impidiendo cambios de estado inválidos.

### Ubicación
`app/core/workflow_engine.py`

### Responsabilidades
1. **Definir transiciones válidas** entre estados de equipos
2. **Validar permisos por rol** para cada transición
3. **Identificar estados pendientes** para cada rol
4. **Detectar estados terminales** que no permiten más cambios
5. **Manejar decisiones** cuando hay múltiples opciones de transición

### Componentes Principales

#### 1. STATE_FLOW - Grafo de Transiciones

Define el flujo completo de estados con transiciones permitidas y roles autorizados:

```python
STATE_FLOW = {
    'Espera de Diagnostico': {
        'next': ['en Diagnostico'],
        'allowed_roles': ['admin', 'operaciones'],
        'requires_decision': False
    },
    'en Diagnostico': {
        'next': ['espera de repuesto o consumible', 'Pendiente de aprobacion'],
        'allowed_roles': ['admin', 'operaciones'],
        'requires_decision': True  # Usuario elige entre dos caminos
    },
    # ... 11 estados en total
}
```

**Estructura de cada estado**:
- `next`: Lista de estados siguientes permitidos (None si es terminal)
- `allowed_roles`: Roles que pueden avanzar desde este estado
- `requires_decision`: True si hay múltiples opciones (usuario debe elegir)

#### 2. PENDING_LOGIC - Estados Pendientes por Rol

Define qué estados requieren acción de cada rol:

```python
PENDING_LOGIC = {
    'recepcion': ['Pendiente de aprobacion', 'Servicio culminado'],
    'operaciones': ['Espera de Diagnostico', 'en Diagnostico', 'Repuesto entregado', 
                    'Aprobado', 'Inicio de Servicio', 'En servicio'],
    'almacen': ['espera de repuesto o consumible', 'espera de repuestos'],
    'admin': [],  # Admin ve todo pero no tiene estados "pendientes" específicos
    'visualizador': []  # Solo lectura
}
```

### Métodos Principales

#### validate_transition(current_state, new_state, user_role)
**Propósito**: Valida si una transición de estado es permitida.

**Validaciones**:
1. ✅ Estado actual existe en el flujo
2. ✅ Estado actual no es terminal
3. ✅ Nuevo estado está en las transiciones permitidas
4. ✅ Rol del usuario tiene permisos para la transición

**Retorna**: `(is_valid: bool, error_message: str or None)`

**Ejemplo**:
```python
is_valid, error = WorkflowEngine.validate_transition(
    'en Diagnostico', 
    'Aprobado',  # Transición inválida (debe pasar por otros estados)
    'operaciones'
)
# is_valid = False
# error = "Transición no permitida: 'en Diagnostico' → 'Aprobado'"
```

#### can_advance(current_state, user_role)
**Propósito**: Verifica si un rol puede avanzar desde un estado.

**Retorna**: `bool`

#### get_next_states(current_state)
**Propósito**: Obtiene los estados siguientes posibles.

**Retorna**: `list` de estados o `None` si es terminal

#### get_pending_states_for_role(role)
**Propósito**: Obtiene estados que requieren acción del rol.

**Retorna**: `list` de estados pendientes

#### get_state_info(current_state, user_role)
**Propósito**: Información completa sobre un estado para un usuario.

**Retorna**:
```python
{
    'current_state': str,
    'next_states': list,
    'can_advance': bool,
    'requires_decision': bool,
    'is_terminal': bool,
    'allowed_roles': list
}
```

### Integración con EquipmentService

El `WorkflowEngine` es utilizado por `EquipmentService.advance_to_next_state()`:

```python
# 1. Obtener estados siguientes
next_states = WorkflowEngine.get_next_states(current_state)

# 2. Verificar permisos
if not WorkflowEngine.can_advance(current_state, user.role):
    return False, "No tienes permisos"

# 3. Validar transición
is_valid, error = WorkflowEngine.validate_transition(
    current_state, target_state, user.role
)

# 4. Si es válida, ejecutar cambio
if is_valid:
    _update_status_internal(equipment_id, target_state, user.username)
```

### Reglas de Negocio Implementadas

1. **Transiciones Unidireccionales**: No se puede retroceder en el flujo
2. **Estado Terminal**: "Entregado" no permite más cambios
3. **Decisiones Operativas**: 
   - Desde "en Diagnostico" → requiere repuesto O aprobación
   - Desde "En servicio" → requiere más repuestos O está culminado
4. **Separación de Responsabilidades**:
   - Recepción: Aprobaciones y entregas
   - Operaciones: Diagnóstico y servicio
   - Almacén: Entrega de repuestos

### Ejemplo de Flujo Validado

```
Usuario: Operaciones
Equipo actual: "Espera de Diagnostico"

1. Intenta avanzar a "en Diagnostico"
   ✅ Transición válida
   ✅ Rol tiene permiso
   → Cambio ejecutado

2. Intenta avanzar a "Servicio culminado"
   ❌ Transición no permitida (debe pasar por estados intermedios)
   → Cambio rechazado

3. Intenta avanzar a "espera de repuesto o consumible"
   ✅ Transición válida
   ✅ Rol tiene permiso
   → Cambio ejecutado

Usuario: Almacén
Equipo actual: "espera de repuesto o consumible"

4. Intenta avanzar a "Repuesto entregado"
   ✅ Transición válida
   ✅ Rol tiene permiso
   → Cambio ejecutado
```

---
 
 ## 📊 Modelos de Datos
 
 ### 1. Equipment (Equipos)
 
 **Propósito**: Representa un equipo de motosoldadora en servicio.
 
 **Campos principales**:
 - id: Identificador único
 - fr: Código FR del equipo (identificador de negocio)
 - marca, modelo: Información del equipo
 - estado: Estado actual en el flujo operativo ⚠️ **CAMPO CRÍTICO**
 - encargado: Técnico responsable
 - cliente: Propietario del equipo
 - fecha_ingreso: Fecha de registro (para cálculo de atrasos)
 - reporte_cliente: Descripción del problema reportado
 - observaciones: Notas adicionales
 - serie, accesorios: Información complementaria
 - numero_informe: Número de diagnóstico asignado
 - condicion: Estado físico del equipo
 
 **Relaciones**:
 - history: Relación 1:N con StatusHistory (historial de cambios)
 
 ### 2. StatusHistory (Historial de Estados)
 
 **Propósito**: Auditoría de cambios de estado de equipos.
 
 **Campos**:
 - equipment_id: FK a Equipment
 - previous_status: Estado anterior
 - new_status: Estado nuevo
 - changed_by: Usuario que realizó el cambio
 - timestamp: Momento del cambio
 
 ### 3. User (Usuarios)
 
 **Propósito**: Gestión de usuarios y control de acceso.
 
 **Campos**:
 - username: Nombre de usuario único
 - password_hash: Contraseña encriptada (Werkzeug)
 - is_admin: Bandera de administrador
 - role: Rol operativo ⚠️ **CAMPO CRÍTICO** (determina permisos)
 - is_approved: Estado de aprobación (usuarios nuevos requieren aprobación)
 - expires_at: Fecha de expiración de acceso (nullable para acceso permanente)
 - created_at: Fecha de creación
 
 **Método importante**:
 - is_active: Property que retorna is_approved (integración con Flask-Login)
 
 ---
 
 ## 🔄 Flujo de Estados de Equipos
 
 ### Estados Definidos (Equipment.Status)
 
 El sistema maneja **11 estados posibles** en el ciclo de vida de un equipo:
 
 1. **Espera de Diagnostico** ← Estado inicial al crear equipo
 2. **en Diagnostico** ← Técnico está evaluando
 3. **espera de repuesto o consumible** ← Requiere materiales
 4. **Repuesto entregado** ← Almacén entregó materiales
 5. **Pendiente de aprobacion** ← Esperando aprobación del cliente
 6. **Aprobado** ← Cliente aprobó el servicio
 7. **Inicio de Servicio** ← Comienza reparación
 8. **espera de repuestos** ← Requiere más repuestos
 9. **En servicio** ← Reparación en curso
 10. **Servicio culminado** ← Reparación completada
 11. **Entregado** ← Equipo devuelto al cliente ⚠️ **ESTADO TERMINAL**
 
 ### Diagrama de Flujo Típico
┌─────────────────────────┐
│  INGRESO DEL EQUIPO     │
│  (Recepción registra)   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Espera de Diagnostico   │ ← Estado inicial
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   en Diagnostico        │ ← Operaciones evalúa
└───────────┬─────────────┘
            │
            ├──────────────────────────────┐
            │                              │
            ▼                              ▼
┌─────────────────────────┐    ┌─────────────────────────┐
│ espera de repuesto o    │    │ Pendiente de aprobacion │
│ consumible              │    │ (cotización al cliente) │
└───────────┬─────────────┘    └───────────┬─────────────┘
            │                              │
            ▼                              ▼
┌─────────────────────────┐    ┌─────────────────────────┐
│ Repuesto entregado      │    │      Aprobado           │
└───────────┬─────────────┘    └───────────┬─────────────┘
            │                              │
            └──────────┬───────────────────┘
                       │
                       ▼
            ┌─────────────────────────┐
            │  Inicio de Servicio     │
            └───────────┬─────────────┘
                        │
                        ▼
            ┌─────────────────────────┐
            │    En servicio          │
            └───────────┬─────────────┘
                        │
                        ├──────────────────┐
                        │                  │
                        ▼                  ▼
            ┌─────────────────────────┐   │
            │ espera de repuestos     │   │
            └───────────┬─────────────┘   │
                        │                  │
                        └──────────────────┘
                        │
                        ▼
            ┌─────────────────────────┐
            │  Servicio culminado     │
            └───────────┬─────────────┘
                        │
                        ▼
            ┌─────────────────────────┐
            │     Entregado           │ ← Estado final
            └─────────────────────────┘
### Reglas de Transición
 
 ✅ **VALIDACIÓN IMPLEMENTADA**: El sistema valida todas las transiciones de estado a través del `WorkflowEngine`. Solo se permiten transiciones válidas según el flujo definido y los permisos del rol del usuario.
 
 **Características del Sistema de Validación**:
 - ✅ **Transiciones Controladas**: Solo se permiten cambios a estados siguientes válidos
 - ✅ **Permisos por Rol**: Cada transición requiere un rol específico
 - ✅ **Estados Terminales**: El estado "Entregado" no permite más cambios
 - ✅ **Decisiones Guiadas**: Cuando hay múltiples opciones, el usuario debe elegir
 - ✅ **Auditoría Completa**: Todos los cambios se registran en StatusHistory
 
 **Validaciones Aplicadas**:
 1. Estado actual debe existir en el flujo
 2. Estado actual no puede ser terminal
 3. Nuevo estado debe estar en las transiciones permitidas
 4. Rol del usuario debe tener permisos para la transición
 
 **Ejemplo de Validación**:
 ```
 Estado actual: "en Diagnostico"
 Intento de cambio: "Servicio culminado"
 Resultado: ❌ RECHAZADO
 Razón: "Transición no permitida: 'en Diagnostico' → 'Servicio culminado'"
 
 Estado actual: "en Diagnostico"
 Intento de cambio: "espera de repuesto o consumible"
 Rol: operaciones
 Resultado: ✅ PERMITIDO
 ```
 
 ---
 
 ## 👥 Sistema de Roles y Permisos
 
 ### Roles Definidos (UserRoles)
 
 1. **admin** - Administrador total
 2. **operaciones** - Técnicos de servicio
 3. **recepcion** - Personal de recepción
 4. **almacen** - Personal de almacén
 5. **visualizador** - Solo lectura
 
 ### Configuración de Permisos (Config.DASHBOARD_ROLES)
 
 Cada rol tiene una configuración específica en app/core/config.py:
 
 #### **admin**
python
{
    'can_view_all': True,           # Ve todos los equipos
    'can_edit': True,               # Puede editar cualquier equipo
    'stats_visible': True,          # Ve estadísticas del dashboard
    'tables': ['active', 'history'], # Ve equipos activos e historial
    'actions': ['view', 'edit', 'delete']  # Todas las acciones
}
#### **recepcion**
python
{
    'can_view_all': False,          # Solo ve estados relevantes
    'can_edit': True,               # Puede editar
    'stats_visible': False,         # No ve estadísticas
    'tables': ['relevant', 'history'],
    'relevant_statuses': [
        'Espera de Diagnostico',    # Equipos recién ingresados
        'Pendiente de aprobacion',  # Requiere contactar cliente
        'Servicio culminado'        # Listos para entregar
    ],
    'actions': ['view', 'edit']
}
#### **operaciones**
python
{
    'can_view_all': False,
    'can_edit': True,
    'stats_visible': False,
    'tables': ['relevant', 'history'],
    'relevant_statuses': [
        'Espera de Diagnostico',
        'en Diagnostico',
        'DIAGNOSTICO',              # Variante del estado
        'espera de repuesto o consumible',
        'Repuesto entregado',
        'Aprobado',
        'Inicio de Servicio',
        'En servicio'               # Estados de trabajo técnico
    ],
    'actions': ['view', 'edit']
}
#### **almacen**
python
{
    'can_view_all': False,
    'can_edit': True,
    'stats_visible': False,
    'tables': ['relevant'],         # NO ve historial de entregados
    'relevant_statuses': [
        'espera de repuestos',
        'espera de repuesto o consumible'  # Solo equipos que requieren materiales
    ],
    'actions': ['view', 'edit']
}
#### **visualizador**
python
{
    'can_view_all': True,           # Ve todo
    'can_edit': False,              # Solo lectura
    'stats_visible': True,
    'tables': ['active', 'history'],
    'actions': ['view']             # Solo visualización
}
### Lógica de Filtrado por Rol
 
 **Implementado en**: EquipmentService.get_equipment_by_role()
python
# Pseudocódigo del filtrado
if user.role tiene 'can_view_all':
    return todos_los_equipos (excepto entregados si no se solicita)
else:
    return equipos WHERE estado IN relevant_statuses del rol
**Casos especiales**:
 - include_delivered=True: Incluye equipos entregados (usado en panel de estados)
 - Almacén NO ve historial de entregados por preferencia del usuario
 - Admin y Visualizador ven todo por defecto
 
 ---
 
 ## 🔐 Sistema de Autenticación y Autorización
 
 ### Flujo de Registro y Aprobación
 
 1. **Registro** (/auth/register):
 - Usuario se registra con username/password
 - Se crea con is_approved=False
 - No puede acceder hasta aprobación
 
 2. **Aprobación** (Admin):
 - Admin accede a /auth/admin/users
 - Puede:
 - Aprobar con acceso temporal (horas o meses)
 - Aprobar con acceso permanente
 - Bloquear usuario
 - Asignar rol operativo
 - Otorgar permisos de admin
 
 3. **Login** (/auth/login):
 - Valida credenciales
 - Verifica is_approved=True
 - Verifica que expires_at no haya pasado (si existe)
 - Crea sesión con Flask-Login
 
 ### Permisos Temporales
 
 **Opciones de acceso**:
 - BLOCK: Bloquea usuario (is_approved=False)
 - PERMANENT: Acceso permanente (expires_at=None)
 - <N>h: N horas de acceso (ej: 24h)
 - <N>: N meses de acceso (ej: 6)
 
 **Implementación**:
python
# En auth/routes.py - set_access()
if meses == 'BLOCK':
    user.is_approved = False
    user.expires_at = None
elif meses == 'PERMANENT':
    user.is_approved = True
    user.expires_at = None
elif meses.endswith('h'):
    hours = int(meses[:-1])
    user.expires_at = datetime.utcnow() + relativedelta(hours=hours)
else:
    months = int(meses)
    user.expires_at = datetime.utcnow() + relativedelta(months=months)
### Protección de Rutas
 
 **Decoradores utilizados**:
 - @login_required: Requiere autenticación (Flask-Login)
 - @role_required(*roles): Requiere rol específico (custom)
 
 **Validación de acciones**:
python
# En api/routes.py
if not can_perform_action(current_user, 'edit'):
    return jsonify({'error': 'Permiso denegado'}), 403
### Usuarios Protegidos
 
 ⚠️ **Usuarios que NO se pueden eliminar**:
 - Venllas (super administrador)
 - El usuario actual (no puede auto-eliminarse)
 
 ---
 
 ## 🛠️ Servicios y Lógica de Negocio
 
 ### EquipmentService
 
 **Ubicación**: app/services/equipment_service.py
 
 **Responsabilidades**:
 1. Filtrado de equipos por rol
 2. Cálculo de estadísticas
 3. Actualización de estados con historial
 4. Creación de equipos
 5. Búsqueda
 6. Eliminación
 
 #### Métodos Principales
 
 ##### get_dashboard_config(user)
 Retorna la configuración de permisos del rol del usuario.
 
 ##### get_equipment_by_role(user, include_delivered=False)
 **Lógica crítica de filtrado**:
 - Si can_view_all=True: Retorna todos (excepto entregados si include_delivered=False)
 - Si can_view_all=False: Filtra por relevant_statuses del rol
 - Ordena por fecha_ingreso DESC
 
 ##### get_admin_stats()
 Calcula estadísticas para el dashboard:
 - total: Total de equipos
 - activos: Equipos no entregados
 - atrasados: Equipos con más de 5 días sin entregar
 - tiempo_promedio: Promedio de días de servicio (últimos 30 días)
 
 **Cálculo de atrasos**:
python
fecha_limite = now - timedelta(days=5)
atrasados = Equipment.query.filter(
    ~Equipment.estado.ilike('%entregado%'),
    Equipment.fecha_ingreso < fecha_limite
).count()
##### _update_status_internal(equipment_id, new_status, user_name, encargado=None)
 **⚠️ Método Interno**: No debe llamarse directamente. Usar `advance_to_next_state()`.
 
 **Flujo**:
 1. Busca equipo por ID
 2. Guarda estado anterior
 3. Actualiza estado (y encargado si se proporciona)
 4. Crea registro en StatusHistory
 5. Commit a base de datos
 
 **NO valida transiciones**: Solo actualiza la base de datos.
 
 ##### advance_to_next_state(equipment_id, user, next_state=None)
 **⚡ Método Principal para Cambios de Estado**
 
 **Flujo**:
 1. Obtiene estado actual del equipo
 2. Obtiene estados siguientes posibles del WorkflowEngine
 3. Verifica que el usuario puede avanzar desde el estado actual
 4. Determina el estado destino (automático si solo hay uno, requiere selección si hay múltiples)
 5. Valida la transición con WorkflowEngine.validate_transition()
 6. Si es válida, ejecuta el cambio con _update_status_internal()
 
 **Retorna**: `(success: bool, message: str, new_state: str or None)`
 
 **Validaciones**:
 - ✅ Estado actual existe en el flujo
 - ✅ No es estado terminal
 - ✅ Transición es permitida
 - ✅ Usuario tiene permisos
 
 ##### get_pending_tasks(user)
 Obtiene equipos que requieren acción del rol del usuario.
 
 **Flujo**:
 1. Obtiene estados pendientes del rol desde WorkflowEngine
 2. Filtra equipos en esos estados (excluyendo entregados)
 3. Ordena por fecha_ingreso ASC (más antiguos primero)
 
 **Retorna**: Lista de equipos pendientes
 
 ##### get_next_state_info(equipment_id, user)
 Obtiene información sobre los siguientes estados posibles para un equipo.
 
 **Retorna**:
 ```python
 {
     'equipment_id': int,
     'current_state': str,
     'next_states': list,
     'can_advance': bool,
     'requires_decision': bool,
     'is_terminal': bool
 }
 ```
 
 ##### create_equipment(data)
 **Flujo**:
 1. Convierte todos los campos a MAYÚSCULAS (.upper())
 2. Asigna estado inicial: Equipment.Status.ESPERA_DIAGNOSTICO
 3. Asigna encargado por defecto: 'No asignado'
 4. Inserta en base de datos
 
 ##### search(search_query)
 Búsqueda por coincidencia parcial (LIKE) en:
 - fr
 - marca
 - modelo
 - encargado
 - cliente
 
 Límite: 100 resultados.
 
 ---
 
 ## 🌐 Blueprints (Controladores)
 
 ### 1. auth_bp (Autenticación)
 
 **Prefix**: /auth
 
 **Rutas principales**:
 
 | Ruta | Método | Descripción |
 |------|--------|-------------|
 | /login | GET, POST | Login de usuarios |
 | /register | GET, POST | Registro de nuevos usuarios |
 | /logout | GET | Cierre de sesión |
 | /admin/users | GET | Panel de gestión de usuarios (admin) |
 | /admin/users/set_access/<id> | POST | Asignar permisos temporales |
 | /admin/users/set_role/<id> | POST | Cambiar rol de usuario |
 | /admin/users/toggle_admin/<id> | GET | Alternar permisos de admin |
 | /admin/users/delete/<id> | POST | Eliminar usuario |
 | /change_password | GET, POST | Cambio de contraseña |
 
 **Reglas de negocio**:
 - Usuarios nuevos requieren aprobación (is_approved=False)
 - Login verifica aprobación y expiración
 - Admin puede otorgar acceso temporal (horas/meses) o permanente
 - No se puede eliminar a Venllas ni al usuario actual
 
 ### 2. api_bp (API REST)
 
 **Prefix**: /api
 
 **Rutas principales**:
 
 | Ruta | Método | Descripción | Permisos |
 |------|--------|-------------|----------|
 | /stats | GET | Estadísticas del dashboard | Login |
 | /equipment/<id>/update_status | POST | Cambiar estado con validación de workflow ⚡ | can_edit |
 | /equipment/create | POST | Crear nuevo equipo | can_edit |
 | /equipment/<id>/details | GET | Detalles de equipo | Login |
 | /equipment/<id>/delete | POST | Eliminar equipo | Admin |
 | /search?q=<query> | GET | Búsqueda de equipos | Login |
 | /export/<formato> | GET | Exportar datos (CSV/Excel) | Login |
 | /pending_tasks | GET | Tareas pendientes del usuario | Login |
 | /equipment/<id>/next_state | GET | Info de siguiente estado posible | Login |
 
 **Formato de respuesta**:
json
{
    "success": true/false,
    "data": {...},      // En caso de éxito
    "error": "..."      // En caso de error
}
**Exportación**:
 - Formatos: csv, xlsx
 - Filtro opcional: ?estado=<estado>
 - Usa Pandas para generar archivos
 - Archivos guardados en carpeta exports/
 
 ### 3. dashboard_bp (Vistas)
 
 **Prefix**: / (raíz)
 
 **Rutas principales**:
 
 | Ruta | Método | Descripción |
 |------|--------|-------------|
 | / | GET | Dashboard principal |
 | /panel | GET | Panel de estados |
 | /general | GET | Panel de gestión general |
 | /excel | GET | Panel de gestión Excel |
 | /admin/db/backup | GET | Descargar backup de BD (admin) |
 | /admin/import_informes | POST | Importar números de informe desde CSV (admin) |
 
 **Lógica del Dashboard** (/):
 - Visualizadores y Admin son redirigidos a /panel
 - Carga equipos según rol del usuario
 - Muestra estadísticas si stats_visible=True
 - Muestra historial si 'history' in tables
 - Pasa configuración de permisos al template
 
 **Lógica del Panel** (/panel):
 - Carga equipos con include_delivered=True
 - Convierte a JSON para manipulación en frontend
 - Permite filtrado dinámico por estado en JavaScript
 
 **Panel de Gestión General** (/general):
 - Vista de gestión general del sistema
 - Accesible para usuarios autenticados
 
 **Panel de Gestión Excel** (/excel):
 - Vista de gestión de datos Excel
 - Accesible para usuarios autenticados
 
 **Importación de informes**:
 - Formato CSV con delimitador ;
 - Columnas: FR, No DIAG
 - Actualiza campo numero_informe de equipos existentes
 - Búsqueda case-insensitive por FR
 
 ---
 
 ## 🗄️ Persistencia de Datos
 
 ### Configuración de Base de Datos
 
 **Ubicación**: app/core/config.py
 
 **Estrategia**:
python
# Prioridad:
# 1. Variable de entorno POSTGRES_URL o DATABASE_URL (producción)
# 2. SQLite local (desarrollo)

db_url = os.environ.get('POSTGRES_URL') or os.environ.get('DATABASE_URL')
if db_url:
    # Corrige formato de Vercel (postgres:// → postgresql://)
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = db_url
else:
    # Fallback local
    SQLALCHEMY_DATABASE_URI = 'sqlite:///cabelab.db'
### Inicialización Automática
 
 **Ubicación**: app/__init__.py - ensure_db()
 
 **Flujo** (ejecutado en cada request):
 1. Verifica si ya se inicializó (app._db_initialized)
 2. Si no:
 - Ejecuta db.create_all() (crea tablas si no existen)
 - Crea usuario admin si no existe (password: admin123)
 - Crea usuario Venllas si no existe (password: Venllas2025)
 - Marca como inicializado
 
 ⚠️ **IMPORTANTE**: Esto se ejecuta en CADA request hasta que se complete exitosamente. Puede causar overhead en el primer request.
 
 ### Migraciones
 
 **Estado actual**: NO hay sistema de migraciones (Alembic no configurado).
 
 **Implicaciones**:
 - Cambios en modelos requieren recrear la base de datos
 - En producción, cambios de esquema deben hacerse manualmente en PostgreSQL
 - No hay versionado de esquema
 
 ---
 
 ## 🎨 Frontend
 
 ### Tecnologías
 - **Templates**: Jinja2
 - **CSS**: Vanilla CSS (sin frameworks)
 - **JavaScript**: Vanilla JS (sin frameworks)
 
 ### Plantillas Principales
 
 #### base.html
 Plantilla base con:
 - Navbar con logo y menú de usuario
 - Sidebar con navegación (dashboard, panel, admin)
 - Sistema de mensajes flash (Bootstrap alerts)
 - Carga de CSS/JS comunes
 
 #### dashboard.html
 Dashboard principal con:
 - Tarjetas de estadísticas (si stats_visible)
 - Tabla de equipos activos
 - Tabla de historial (si 'history' in tables)
 - Modales de edición (incluidos desde dashboard_modals.html)
 
 #### panel_estados.html
 Panel de estados con:
 - Pestañas por estado
 - Tabla dinámica filtrable por estado
 - Búsqueda en tiempo real
 - Modales de edición
 
 **Lógica JavaScript**:
javascript
// Recibe equipments_json desde backend
const equipments = JSON.parse('{{ equipments_json | safe }}');

// Filtra por estado para cada pestaña
function filterByStatus(status) {
    return equipments.filter(eq => eq.estado === status);
}
### Interacción con API
 
 **Patrón común**:
javascript
// Actualizar estado
fetch(`/api/equipment/${id}/update_status`, {
    method: 'POST',
    body: new FormData(form)
})
.then(res => res.json())
.then(data => {
    if (data.success) {
        location.reload();  // Recarga página
    } else {
        alert(data.error);
    }
});
⚠️ **Nota**: La mayoría de operaciones recargan la página completa (no SPA).
 
 ---
 
 ## 🔍 Flujos de Datos Críticos
 
 ### 1. Creación de Equipo
Usuario (Recepción) → [POST] /api/equipment/create
    ↓
API valida permisos (can_edit)
    ↓
EquipmentService.create_equipment(data)
    ↓
- Convierte campos a MAYÚSCULAS
- Asigna estado: "Espera de Diagnostico"
- Asigna encargado: "No asignado"
- Inserta en BD
    ↓
Retorna ID del equipo creado
    ↓
Frontend recarga página
### 2. Cambio de Estado (Con Validación)
Usuario (con can_edit) → [POST] /api/equipment/<id>/update_status
    ↓
API valida permisos (can_perform_action)
    ↓
EquipmentService.advance_to_next_state(id, user, new_status, additional_data)
    ↓
WorkflowEngine.validate_transition(current_state, new_status, user.role)
    ↓
Si es válida:
    - Actualiza estado del equipo
    - Actualiza campos adicionales (encargado, observaciones, etc.)
    - Crea registro en StatusHistory
    - Commit a BD
Si no es válida:
    - Retorna error con mensaje descriptivo
    ↓
Retorna (success, message, new_state)
    ↓
Frontend recarga página o muestra error
### 3. Visualización por Rol
Usuario autenticado → [GET] /
    ↓
Dashboard verifica rol
    ↓
EquipmentService.get_dashboard_config(user)
    ↓
EquipmentService.get_equipment_by_role(user)
    ↓
Si can_view_all:
    - Retorna todos los equipos activos
Si not can_view_all:
    - Filtra por relevant_statuses del rol
    ↓
Renderiza dashboard.html con equipos filtrados
### 4. Aprobación de Usuario
Admin → [POST] /auth/admin/users/set_access/<id>
    ↓
Recibe parámetro 'meses' (BLOCK, PERMANENT, <N>h, <N>)
    ↓
Según valor:
    - BLOCK: is_approved=False, expires_at=None
    - PERMANENT: is_approved=True, expires_at=None
    - <N>h: is_approved=True, expires_at=now+N horas
    - <N>: is_approved=True, expires_at=now+N meses
    ↓
Commit a BD
    ↓
Usuario puede hacer login (si aprobado y no expirado)
---
 
 ## ⚠️ Puntos Críticos y Consideraciones
 
 ### 1. ✅ Validación de Transiciones de Estado - IMPLEMENTADO
 
 **Estado**: ✅ **RESUELTO** mediante WorkflowEngine
 
 **Implementación**:
 - Máquina de estados completa con transiciones definidas
 - Validación de permisos por rol para cada transición
 - Estados terminales protegidos
 - Auditoría completa en StatusHistory
 
 **Beneficios**:
 - ✅ Integridad del flujo operativo garantizada
 - ✅ Imposible saltar pasos del proceso
 - ✅ Separación clara de responsabilidades por rol
 - ✅ Prevención de estados inconsistentes
 
 **Consideraciones**:
 - El método `_update_status_internal()` existe para uso interno pero NO debe llamarse directamente
 - Todos los cambios de estado deben pasar por `advance_to_next_state()`
 - El endpoint `/api/equipment/<id>/update_status` ahora valida todas las transiciones
 
 ### 2. Inicialización en Cada Request
 
 **Problema**: ensure_db() se ejecuta en cada request hasta que se complete.
 
 **Riesgo**:
 - Overhead en el primer request
 - Posibles race conditions en despliegues con múltiples workers
 
 **Recomendación**:
 - Usar comando de inicialización separado (Flask CLI)
 - Ejecutar db.create_all() solo en despliegue inicial
 
 ### 3. Sin Sistema de Migraciones
 
 **Problema**: No hay Alembic configurado.
 
 **Riesgo**:
 - Cambios en modelos requieren recrear BD (pérdida de datos)
 - Difícil sincronizar esquema entre desarrollo y producción
 
 **Recomendación**:
 - Configurar Flask-Migrate (Alembic)
 - Versionar esquema de base de datos
 
 ### 4. Contraseñas por Defecto
 
 **Problema**: Usuarios admin y Venllas se crean con contraseñas hardcodeadas.
 
 **Riesgo**:
 - Seguridad comprometida si no se cambian en producción
 
 **Recomendación**:
 - Forzar cambio de contraseña en primer login
 - Usar variables de entorno para contraseñas iniciales
 
 ### 5. Recarga de Página Completa
 
 **Problema**: La mayoría de operaciones recargan la página (location.reload()).
 
 **Impacto**:
 - Experiencia de usuario menos fluida
 - Mayor consumo de ancho de banda
 
 **Recomendación** (si se desea mejorar UX):
 - Implementar actualizaciones parciales con JavaScript
 - Usar AJAX para operaciones CRUD sin recargar
 
 ### 6. Búsqueda Limitada
 
 **Problema**: Búsqueda limitada a 100 resultados sin paginación.
 
 **Riesgo**:
 - En bases de datos grandes, resultados incompletos
 
 **Recomendación**:
 - Implementar paginación
 - Agregar filtros avanzados
 
 ### 7. Exportaciones en Disco
 
 **Problema**: Archivos de exportación se guardan en exports/ en el servidor.
 
 **Riesgo**:
 - Acumulación de archivos
 - Problemas en entornos serverless (Vercel)
 
 **Recomendación**:
 - Generar archivos en memoria y enviar directamente
 - Implementar limpieza automática de archivos antiguos
 
 ### 8. Permisos Basados en Rol Único
 
 **Problema**: Cada usuario tiene un solo rol.
 
 **Limitación**:
 - No se pueden combinar permisos (ej: Recepción + Almacén)
 
 **Recomendación** (si se requiere flexibilidad):
 - Implementar sistema de permisos basado en capacidades (capabilities)
 - Permitir múltiples roles por usuario
 
 ---
 
 ## 🔄 Reglas de Negocio Implícitas
 
 ### 1. Equipos Atrasados
 - **Definición**: Equipos no entregados con más de 5 días desde ingreso
 - **Cálculo**: fecha_ingreso < (now - 5 días)
 - **Uso**: Métrica en dashboard de admin
 
 ### 2. Tiempo Promedio de Servicio
 - **Cálculo**: Promedio de días entre fecha_ingreso y entrega
 - **Ventana**: Últimos 30 días
 - **Solo considera**: Equipos en estado "Entregado"
 
 ### 3. Normalización de Datos
 - **Campos de texto**: Se convierten a MAYÚSCULAS al crear equipo
 - **Propósito**: Consistencia en búsquedas y visualización
 
 ### 4. Encargado por Defecto
 - **Valor**: "No asignado"
 - **Cuándo**: Al crear equipo sin especificar encargado
 
 ### 5. Historial Inmutable
 - **Regla**: Cada cambio de estado crea un registro en StatusHistory
 - **No se puede**: Editar o eliminar historial (solo admin puede eliminar equipo completo)
 
 ### 6. Equipos Entregados
 - **Consideración especial**: Filtrados por defecto en vistas de "activos"
 - **Identificación**: Estado contiene "entregado" (case-insensitive)
 - **Excepción**: Panel de estados incluye pestaña de entregados
 
 ### 7. Roles y Visibilidad
 - **Almacén**: NO ve historial de entregados (preferencia del usuario)
 - **Visualizador**: Redirigido automáticamente a /panel (no usa dashboard principal)
 - **Admin**: Acceso total sin restricciones
 
 ---
 
 ## 📚 Dependencias Externas
 
 ### Dependencias Python (requirements.txt)
```
Flask==3.0.0                # Framework web
Flask-Login==0.6.3          # Gestión de sesiones
Flask-SQLAlchemy==3.1.1     # ORM
Werkzeug==3.0.1             # Utilidades (hashing de passwords)
pandas>=2.0.0               # Procesamiento de datos / exportación
openpyxl>=3.1.0             # Exportación a Excel
python-dateutil>=2.8.2      # Manipulación de fechas (relativedelta)
gspread>=5.10.0             # Integración con Google Sheets
oauth2client>=4.1.3         # OAuth para Google
psycopg2-binary>=2.9.9      # Driver PostgreSQL
```

**Nota**: `gspread` y `oauth2client` están incluidas en requirements.txt pero actualmente no se utilizan en el código. Estas dependencias pueden ser para funcionalidad futura o legacy que se mantuvo por compatibilidad.
 
 ---
 
 ## 🚀 Despliegue
 
 ### Configuración de Vercel
 
 **Archivo**: vercel.json
json
{
  "builds": [
    {
      "src": "wsgi.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "wsgi.py"
    }
  ]
}
**Punto de entrada**: wsgi.py
python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
### Variables de Entorno Requeridas
 
 **Producción**:
 - POSTGRES_URL o DATABASE_URL: URL de conexión a PostgreSQL
 - SECRET_KEY (opcional): Clave secreta de Flask (usa default si no se define)
 
 **Desarrollo**:
 - Ninguna (usa SQLite local)
 
 ---
 
 ## 🧪 Testing
 
 **Estado actual**: NO hay tests automatizados.
 
 **Recomendaciones para implementar**:
 1. **Unit tests**: Servicios (EquipmentService)
 2. **Integration tests**: Endpoints de API
 3. **E2E tests**: Flujos completos (registro → aprobación → login → crear equipo)
 
 ---
 
 ## 📖 Glosario de Términos del Negocio
 
 - **FR**: Código de identificación del equipo (Ficha de Recepción)
 - **Motosoldadora**: Tipo de equipo que se repara (soldadoras portátiles)
 - **Diagnóstico**: Evaluación técnica inicial del equipo
 - **Informe**: Documento técnico generado tras diagnóstico (campo numero_informe)
 - **Repuesto/Consumible**: Materiales necesarios para reparación
 - **Aprobación**: Autorización del cliente para proceder con reparación (generalmente tras cotización)
 - **Encargado**: Técnico responsable del equipo en su estado actual
 - **Entregado**: Estado final cuando el equipo es devuelto al cliente
 
 ---
 
 ## 🎯 Resumen para Nuevos Desarrolladores
 
 ### Para entender el sistema rápidamente:
 
 1. **Lee primero**:
 - app/core/workflow_engine.py ⚡ **CRÍTICO** (máquina de estados)
 - app/models/equipment.py (estados del equipo)
 - app/core/config.py (configuración de roles)
 - app/services/equipment_service.py (lógica de negocio)
 
 2. **Flujo principal**:
 - Usuario se registra → Admin aprueba → Usuario accede
 - Recepción crea equipo → Operaciones diagnostica → Almacén entrega repuestos → Operaciones repara → Recepción entrega
 - **IMPORTANTE**: Todos los cambios de estado pasan por WorkflowEngine
 
 3. **Puntos de entrada**:
 - manage.py (desarrollo local)
 - wsgi.py (producción Vercel)
 
 4. **Modificar permisos**:
 - Editar Config.DASHBOARD_ROLES en app/core/config.py
 - Editar WorkflowEngine.STATE_FLOW para permisos de transiciones
 
 5. **Agregar estado**:
 - Agregar constante en Equipment.Status
 - Agregar en WorkflowEngine.STATE_FLOW con transiciones y roles permitidos
 - Actualizar relevant_statuses de roles afectados en config.py
 - Actualizar WorkflowEngine.PENDING_LOGIC si es necesario
 - Actualizar templates si es necesario
 
 ### Para IAs que modificarán el código:
 
 - ✅ **SÍ hay validaciones de transiciones**: Implementadas en WorkflowEngine
 - ⚠️ **NO llamar _update_status_internal() directamente**: Usar advance_to_next_state()
 - **Recarga de página**: Patrón actual, considerar si se desea SPA
 - **Roles son excluyentes**: Un usuario = un rol
 - **Historial es auditoría**: No eliminar registros de StatusHistory
 - **Mayúsculas**: Campos de texto se normalizan a UPPER
 - **Filtrado por rol**: Lógica en EquipmentService.get_equipment_by_role()
 - **Workflow obligatorio**: Todos los cambios de estado deben validarse
 
 ---
 
 ## 📝 Notas Finales
 
 Este documento refleja el estado del código al momento del análisis. El sistema es funcional y cumple con los requisitos operativos actuales, pero tiene áreas de mejora identificadas en la sección de **Puntos Críticos**.
 
 **Filosofía del sistema**:
 - Simplicidad sobre complejidad
 - Confianza en usuarios capacitados
 - Auditoría completa de cambios
 - Permisos granulares por rol
 
 **Antes de hacer cambios**:
 1. Revisar impacto en roles y permisos
 2. Considerar historial de estados
 3. Validar con usuarios de cada área
 4. Probar flujo completo de un equipo
 
 ---
 
 **Documento actualizado**: 2026-01-28
 **Versión del sistema**: 2.0.0
 **Autor**: Análisis automatizado del código fuente real