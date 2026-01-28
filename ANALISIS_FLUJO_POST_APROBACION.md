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
    'next': ['En servicio'],
    'allowed_roles': ['admin', 'operaciones'],
    'requires_decision': False,
    'auto_fill': {'hora_aprobacion': 'now'}
}
```

### Características del Estado "Aprobado":

1. **Siguiente estado único**: `'En servicio'`
   - No hay decisión que tomar (requires_decision: False)
   - Solo existe un camino posible

2. **Auto-fill automático**:
   - El campo `hora_aprobacion` se registra automáticamente con la hora actual

3. **Roles con control**:
   - **Admin y Operaciones**: Control total

---

## 👥 Control del Equipo Post-Aprobación

### Análisis de Permisos por Rol

#### 1. **Rol: Admin / Operaciones**
**Permisos**:
- ✅ Puede avanzar el equipo de "Aprobado" a "En servicio"
- ✅ Puede editar datos del equipo

**Acciones disponibles** (panel_estados.html, líneas 825-829):
```javascript
if (s === 'aprobado') {
    if (isOps) {
        actionsHtml += `<button onclick="showAdvanceModal(..., 'En servicio')">Iniciar Servicio</button>`;
    }
}
```
*Nota: Se usa `showAdvanceModal` para activar los prompts de entrada (encargado) definidos en el estado destino.*

---

## 🎯 Acción Única Disponible: "Iniciar Servicio"

### Implementación

**Frontend**:
- Botón "Iniciar Servicio" en estado Aprobado.
- Llama a `showAdvanceModal`.

**Backend (WorkflowEngine)**:
- Estado destino "En servicio" tiene `enter_prompts: ['encargado_mantenimiento']`.
- Esto obliga al usuario a ingresar el nombre del técnico antes de cambiar de estado.
- Auto-fill de `hora_inicio_mantenimiento` al entrar a "En servicio".

### Validaciones Aplicadas

1. **Solicitud de encargado**: Obligatorio por `enter_prompts`.
2. **Hora de Aprobación**: Se guarda automáticamente al ENTRAR a "Aprobado".
3. **Hora Inicio Mantenimiento**: Se guarda automáticamente al ENTRAR a "En servicio".

---

## 📊 Flujo Completo Post-Aprobación

```
┌─────────────────────────────────────────────────────────────┐
│ ESTADO: "Aprobado"                                          │
│ - hora_aprobacion registrada automáticamente                │
│ - Control: Admin y Operaciones                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ ÚNICA ACCIÓN: "Iniciar Servicio"
                            │ (Prompt: encargado_mantenimiento)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ESTADO: "En servicio"                                       │
│ - hora_inicio_mantenimiento registrada automáticamente      │
│ - Control: Admin y Operaciones                              │
│ - Opciones:                                                 │
│   1. "Terminar Mantenimiento" → "Entregado"                 │
│      (Prompt: observaciones_mantenimiento)                  │
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
