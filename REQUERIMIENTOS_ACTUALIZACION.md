# Documento de Especificación de Requerimientos Técnicos y Funcionales

**Proyecto:** Sistema de Gestión de Equipos - CABELAB  
**Estado:** Por Implementar  
**Analista/Desarrollador:** Antigravity AI  

---

## 1. Automatización de Auditoría de Entrega
### Requerimiento Funcional
El sistema debe registrar de forma automática e irrevocable el momento exacto en que un equipo pasa al estado final de "ENTREGADO". Esto permitirá realizar auditorías precisas sobre el tiempo de ciclo total del servicio.

### Especificación Técnica
- **Campo de Datos:** Adición de la columna `hora_entregado` (Tipo: DateTime) en la entidad `Equipment`.
- **Lógica de Negocio:** 
  - Al detectar una transición de estado hacia "Entregado" o "Entregado - Devolución", el sistema deberá asignar el valor actual de `get_local_now()` (Hora Perú) a la propiedad `hora_entregado`.
  - Este registro debe ocurrir a nivel de persistencia de datos (Service Layer).

---

## 2. Restricción Temporal del Módulo de Auditoría
### Requerimiento Funcional
Para garantizar que el módulo de Auditoría muestre datos relevantes de la gestión actual y evitar la carga de registros históricos obsoletos, se establece un filtro temporal obligatorio.

### Especificación Técnica
- **Filtrado de Consultas:** El endpoint de la vista de Auditoría (`/auditoria`) aplicará un filtro en la base de datos para recuperar únicamente registros donde `fecha_ingreso >= '2026-02-01'`.
- **Impacto:** Menor consumo de recursos y mayor coherencia en los gráficos de rendimiento mensual.

---

## 3. Identificación Visual de Estados Críticos
### Requerimiento Funcional
Optimizar la legibilidad del "Panel de Estados" mediante la diferenciación cromática de las fases iniciales del flujo de trabajo, permitiendo al personal de operaciones identificar cuellos de botella de un vistazo.

### Especificación Técnica (UI/UX)
Se asignarán los siguientes estilos visuales (Badges):
- **ESPERA DE DIAGNÓSTICO:** Color **Warning/Naranja** (Representa equipo en espera/cola).
- **EN DIAGNÓSTICO:** Color **Info/Cian** (Representa trabajo en progreso).
- **Otros estados:** Mantendrán su codificación estándar.

---

## 4. Ordenamiento Inteligente de la Tabla de Diagnóstico
### Requerimiento Funcional
La tabla de "Equipos en Diagnóstico" debe presentarse de forma organizada para priorizar el flujo operativo, evitando el desorden visual por fechas de ingreso aleatorias.

### Especificación Técnica
Los criterios de ordenamiento (Sorting) serán:
1. **Criterio Primario:** Alfabético por Código **FR** (Ascendente).
2. **Criterio Secundario:** Prioridad de Estado según el siguiente flujo lógico:
   - 1°: **ESPERA DE DIAGNÓSTICO** (Prioridad alta para iniciar).
   - 2°: **EN DIAGNÓSTICO** (Trabajo activo).
   - 3°: **ESPERA DE REPUESTOS** (Pendiente de suministros).

---

## 5. Sistema de Idempotencia y Prevención de Duplicados
### Requerimiento Funcional
Robustecer la interfaz de usuario para prevenir fallos técnicos causados por la impaciencia del usuario (clics múltiples) o reenvíos de formularios que generen registros duplicados en la base de datos.

### Especificación Técnica
- **Control de UI:** Bloqueo (Disabling) inmediato de botones de acción tras el primer clic.
- **Feedback Visual:** Inserción de estados de "Carga" (Spinners) mientras se espera la respuesta del servidor.
- **Backend Sync:** Implementación de validaciones a nivel de servicio para omitir transiciones de estado que ya han sido procesadas o sean redundantes.
