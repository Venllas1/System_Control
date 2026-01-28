# ANÁLISIS DEL FLUJO DE TRABAJO POST-APROBACIÓN

**Fecha de análisis**: 2026-01-28  
**Basado en**: Código fuente real del sistema

---

## 📋 Resumen Ejecutivo

Este documento describe el flujo de trabajo del sistema **después de que un equipo es aprobado**, basándose únicamente en la lógica implementada en el código fuente, sin suposiciones externas.

---

## 🔄 Flujo de Trabajo Después de la Aprobación

### Estado: "Aprobado"

**Archivo de referencia**: `app/core/workflow_engine.py` (líneas 41-46)

```python
'Aprobado': {
    'next': ['Inicio de Servicio'],
    'allowed_roles': ['admin', 'operaciones'],
    'requires_decision': False,
    'auto_fill': {'hora_aprobacion': 'now'}
}
```

### Características del Estado "Aprobado":

1. **Siguiente estado único**: `'Inicio de Servicio'`
   - No hay decisión que tomar (requires_decision: False)
   - Solo existe un camino posible

2. **Auto-fill automático**:
   - El campo `hora_aprobacion` se registra automáticamente con la hora actual
   - Implementado en `app/services/equipment_service.py` (líneas 265-273)

3. **Roles con control**:
   - **Admin**: Control total
   - **Operaciones**: Control total
   - Otros roles: Solo visualización

---

## 👥 Control del Equipo Post-Aprobación

### Análisis de Permisos por Rol

#### 1. **Rol: Admin**
**Permisos**:
- ✅ Puede avanzar el equipo de "Aprobado" a "Inicio de Servicio"
- ✅ Puede editar datos del equipo
- ✅ Puede eliminar el equipo
- ✅ Visualiza todos los equipos

**Acciones disponibles** (panel_estados.html, líneas 816-820):
```javascript
if (s === 'aprobado') {
    if (isOps) {  // isOps incluye admin
        actionsHtml += `<button onclick="startMaintenance(...)">Iniciar Mantenimiento</button>`;
    }
}
```

#### 2. **Rol: Operaciones**
**Permisos**:
- ✅ Puede avanzar el equipo de "Aprobado" a "Inicio de Servicio"
- ✅ Puede editar datos del equipo (según configuración)
- ❌ No puede eliminar equipos
- ✅ Visualiza equipos relevantes a su área

**Acciones disponibles**: Idénticas a Admin para este estado

#### 3. **Rol: Recepción**
**Permisos**:
- ❌ No puede avanzar el equipo desde "Aprobado"
- ❌ No tiene control sobre el equipo en este estado
- ✅ Solo visualización (si el equipo está en su lista)

**Razón**: El estado "Aprobado" solo permite roles 'admin' y 'operaciones' (workflow_engine.py)

#### 4. **Rol: Almacén**
**Permisos**:
- ❌ No puede avanzar el equipo desde "Aprobado"
- ❌ No tiene control sobre el equipo en este estado
- ✅ Solo visualización

#### 5. **Rol: Visualizador**
**Permisos**:
- ❌ No puede realizar ninguna acción
- ✅ Solo visualización completa

---

## 🎯 Acción Única Disponible: "Iniciar Mantenimiento"

### Implementación

**Frontend** (panel_estados.html, línea 818):
```javascript
actionsHtml += `<button class="btn btn-sm btn-primary" 
                onclick="startMaintenance(${item.id}, 'Inicio de Servicio')">
                Iniciar Mantenimiento
                </button>`;
```

**Función startMaintenance** (panel_estados.html, líneas 1113-1118):
```javascript
window.startMaintenance = function (id, status) {
    const encargado = prompt("ASIGNACIÓN DE TÉCNICO:\nPor favor, ingrese el nombre del encargado de mantenimiento:");
    if (encargado === null) return;
    if (!encargado.trim()) { alert("Debe asignar un encargado."); return; }
    updateStatus(id, status, null, { encargado_mantenimiento: encargado.trim() });
};
```

### Validaciones Aplicadas

1. **Solicitud de encargado**: El sistema solicita obligatoriamente el nombre del técnico
2. **Validación de campo vacío**: No permite continuar sin asignar un encargado
3. **Transición validada**: WorkflowEngine verifica que la transición sea válida

---

## 📊 Flujo Completo Post-Aprobación

```
┌─────────────────────────────────────────────────────────────┐
│ ESTADO: "Aprobado"                                          │
│ - hora_aprobacion se registra automáticamente               │
│ - Control: Admin y Operaciones                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ ÚNICA ACCIÓN DISPONIBLE
                            │ "Iniciar Mantenimiento"
                            │ (requiere asignar encargado)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ESTADO: "Inicio de Servicio"                                │
│ - encargado_mantenimiento se registra                        │
│ - hora_inicio_mantenimiento se registra automáticamente      │
│ - Control: Admin y Operaciones                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ TRANSICIÓN AUTOMÁTICA
                            │ (no requiere decisión)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ESTADO: "En servicio"                                        │
│ - Control: Admin y Operaciones                              │
│ - Opciones:                                                  │
│   1. "Terminar Mantenimiento" → "Entregado"                 │
│      (requiere observaciones_mantenimiento)                  │
│   2. "Pedir Repuestos" → "espera de repuestos"              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 Validaciones del Sistema

### Validación de Transiciones (workflow_engine.py)

```python
@staticmethod
def validate_transition(current_state, new_state, user_role):
    # 1. Verifica que el estado actual existe en el flujo
    # 2. Verifica que no es un estado terminal
    # 3. Verifica que new_state está en la lista de next_states
    # 4. Verifica que el rol del usuario está permitido
    return (is_valid, error_message)
```

### Auto-fill de Campos (equipment_service.py, líneas 265-273)

```python
# Handle Auto-fill fields if defined in workflow
target_info = WorkflowEngine.STATE_FLOW.get(target_state, {})
auto_fill = target_info.get('auto_fill', {})

for field, value in auto_fill.items():
    if value == 'now':
        additional_data[field] = datetime.now().strftime('%Y-%m-%d %H:%M')
```

**Campos con auto-fill**:
- `hora_aprobacion`: Al entrar a "Aprobado"
- `hora_inicio_diagnostico`: Al entrar a "en Diagnostico"
- `hora_inicio_mantenimiento`: Al entrar a "Inicio de Servicio"

---

## 📝 Conclusiones

### 1. Registro de hora_aprobacion
✅ **Funciona correctamente**:
- Se registra automáticamente al cambiar a estado "Aprobado"
- No es editable manualmente (campo readonly en gestion_general.html)
- Implementado mediante auto_fill en workflow_engine.py

### 2. Flujo de trabajo post-aprobación
✅ **Claramente definido**:
- Un solo camino: "Aprobado" → "Inicio de Servicio" → "En servicio"
- No hay acciones contradictorias
- Validaciones aplicadas en cada transición

### 3. Rol con control del equipo
✅ **Definido en código**:
- **Admin y Operaciones**: Control total
- **Recepción, Almacén, Visualizador**: Solo lectura
- Basado en `allowed_roles` en workflow_engine.py

### 4. Acciones disponibles
✅ **Una sola acción**:
- "Iniciar Mantenimiento" (requiere asignar encargado)
- No hay botón "Pedir Repuestos" en estado "Aprobado"
- Coherente con el flujo definido

---

## 🔍 Referencias de Código

| Aspecto | Archivo | Líneas |
|---------|---------|--------|
| Definición de flujo "Aprobado" | workflow_engine.py | 41-46 |
| Validación de transiciones | workflow_engine.py | 158-189 |
| Auto-fill de campos | equipment_service.py | 265-273 |
| Botón "Iniciar Mantenimiento" | panel_estados.html | 816-820 |
| Función startMaintenance | panel_estados.html | 1113-1118 |
| Campo hora_aprobacion (readonly) | gestion_general.html | 131-136 |
| Permisos por rol | config.py | DASHBOARD_ROLES |

---

**Documento generado automáticamente a partir del análisis del código fuente**  
**Sin suposiciones ni reglas impuestas manualmente**
