# 🏥 Sistema de Control de Equipos CABELAB

Sistema web profesional de gestión y seguimiento de equipos de motosoldadoras con control de flujo operativo entre diferentes áreas de la empresa.

## 🚀 Características Principales

- ✅ **Sistema de roles y permisos** - Control de acceso granular (Admin, Recepción, Operaciones, Almacén, Visualizador)
- ✅ **Flujo de trabajo validado** - Máquina de estados que garantiza transiciones correctas
- ✅ **Dashboard interactivo** - Visualización diferenciada según rol del usuario
- ✅ **Panel de estados** - Seguimiento detallado del ciclo de vida de equipos
- ✅ **Historial completo** - Auditoría de todos los cambios de estado
- ✅ **Gestión de usuarios** - Sistema de aprobación y permisos temporales/permanentes
- ✅ **Exportación de datos** - CSV y Excel con filtros personalizados
- ✅ **Búsqueda avanzada** - Búsqueda por múltiples criterios
- ✅ **Tema dark profesional** - Interfaz moderna y responsive

---

## 📋 Requisitos

- Python 3.8 o superior
- PostgreSQL (producción) o SQLite (desarrollo)
- Navegador web moderno

---

## ⚡ Instalación y Configuración

### 1. Clonar/Descargar el proyecto

```bash
cd "Pizarra Virtual"
```

### 2. Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos

**Desarrollo (SQLite - automático):**
No requiere configuración adicional. Se creará automáticamente `cabelab.db`.

**Producción (PostgreSQL):**
Configurar variable de entorno:
```bash
# Windows
set POSTGRES_URL=postgresql://usuario:password@host:puerto/database

# Linux/Mac
export POSTGRES_URL=postgresql://usuario:password@host:puerto/database
```

### 5. Ejecutar aplicación

```bash
python manage.py
```

Acceder a: `http://localhost:5000`

---

## 🔐 Usuarios por Defecto

El sistema crea automáticamente dos usuarios administradores:

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| admin | admin123 | Administrador |
| Venllas | Venllas2025 | Super Administrador |

⚠️ **IMPORTANTE**: Cambiar estas contraseñas en producción.

---

## 👥 Sistema de Roles

### Roles Disponibles

1. **Admin** - Acceso total al sistema
   - Ve todos los equipos
   - Gestiona usuarios
   - Exporta datos
   - Elimina equipos

2. **Recepción** - Gestión de ingreso y entrega
   - Registra nuevos equipos
   - Gestiona aprobaciones de clientes
   - Entrega equipos culminados

3. **Operaciones** - Diagnóstico y reparación
   - Realiza diagnósticos
   - Ejecuta reparaciones
   - Solicita repuestos
   - Actualiza estado de servicio

4. **Almacén** - Gestión de repuestos
   - Ve equipos que requieren repuestos
   - Registra entrega de materiales

5. **Visualizador** - Solo lectura
   - Visualiza información sin editar
   - Acceso completo a consultas

### Gestión de Usuarios

**Para Usuarios Nuevos:**
1. Registrarse en `/auth/register`
2. Esperar aprobación del administrador
3. Recibir notificación de acceso aprobado

**Para Administradores:**
1. Acceder a `/auth/admin/users`
2. Aprobar usuarios pendientes
3. Asignar rol operativo
4. Configurar acceso:
   - **PERMANENT**: Acceso permanente
   - **BLOCK**: Bloquear usuario
   - **Nh** (ej: 24h): N horas de acceso
   - **N** (ej: 6): N meses de acceso

---

## 🔄 Flujo de Trabajo de Equipos

### Estados del Ciclo de Vida

1. **Espera de Diagnostico** → Equipo recién ingresado
2. **en Diagnostico** → Técnico evaluando
3. **espera de repuesto o consumible** → Requiere materiales
4. **Repuesto entregado** → Almacén entregó materiales
5. **Pendiente de aprobacion** → Esperando aprobación del cliente
6. **Aprobado** → Cliente aprobó el servicio
7. **Inicio de Servicio** → Comienza reparación
8. **espera de repuestos** → Requiere más repuestos
9. **En servicio** → Reparación en curso
10. **Servicio culminado** → Reparación completada
11. **Entregado** → Equipo devuelto al cliente (estado final)

### Validación de Transiciones

El sistema implementa un **WorkflowEngine** que:
- ✅ Valida todas las transiciones de estado
- ✅ Verifica permisos por rol
- ✅ Previene saltos de estados
- ✅ Registra historial completo
- ✅ Protege estados terminales

---

## 📁 Estructura del Proyecto

```
Pizarra Virtual/
├── app/                    # Aplicación principal
│   ├── blueprints/        # Módulos de rutas (auth, api, dashboard)
│   ├── models/            # Modelos de datos (Equipment, User)
│   ├── services/          # Lógica de negocio (EquipmentService)
│   ├── core/              # Configuración y WorkflowEngine
│   ├── templates/         # Plantillas HTML
│   └── static/            # CSS, JS, imágenes
├── scripts/               # Scripts de utilidad
├── manage.py              # Punto de entrada desarrollo
├── wsgi.py                # Punto de entrada producción
├── requirements.txt       # Dependencias
└── vercel.json            # Configuración Vercel
```

---

## 🎨 Características del Frontend

- **Templates**: Jinja2
- **CSS**: Vanilla CSS (sin frameworks)
- **JavaScript**: Vanilla JS
- **Diseño**: Responsive y tema dark
- **Componentes**:
  - Dashboard con estadísticas
  - Panel de estados con pestañas
  - Modales de edición
  - Búsqueda en tiempo real
  - Tablas dinámicas

---

## 📊 Uso del Sistema

### Dashboard Principal

**Acceso**: `/`

- Muestra equipos según rol del usuario
- Estadísticas del sistema (solo admin)
- Tabla de equipos activos
- Historial de entregados
- Botones de acción según permisos

### Panel de Estados

**Acceso**: `/panel`

- Vista completa por estados
- Pestañas dinámicas
- Filtrado en tiempo real
- Búsqueda avanzada
- Gestión de equipos

### Panel de Gestión General

**Acceso**: `/general`

- Vista de gestión general del sistema
- Herramientas administrativas

### Panel de Gestión Excel

**Acceso**: `/excel`

- Gestión de datos Excel
- Importación de informes

### Gestión de Usuarios (Admin)

**Acceso**: `/auth/admin/users`

- Lista de todos los usuarios
- Aprobación de usuarios nuevos
- Asignación de roles
- Configuración de accesos temporales
- Eliminación de usuarios

---

## 🔧 API REST

### Endpoints Principales

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/stats` | GET | Estadísticas del sistema |
| `/api/equipment/create` | POST | Crear nuevo equipo |
| `/api/equipment/<id>/update_status` | POST | Cambiar estado (validado) |
| `/api/equipment/<id>/update_data` | POST | Actualizar datos generales |
| `/api/equipment/<id>/details` | GET | Detalles de equipo |
| `/api/equipment/<id>/delete` | POST | Eliminar equipo (admin) |
| `/api/equipment/<id>/next_state` | GET | Info de siguiente estado |
| `/api/search?q=<query>` | GET | Búsqueda de equipos |
| `/api/export/<formato>` | GET | Exportar datos (csv/xlsx) |
| `/api/pending_tasks` | GET | Tareas pendientes del usuario |

---

## 🚀 Despliegue

### Desarrollo Local

```bash
python manage.py
```

### Producción (Vercel)

1. Configurar variables de entorno:
   - `POSTGRES_URL` o `DATABASE_URL`
   - `SECRET_KEY` (opcional)

2. Desplegar:
```bash
vercel --prod
```

El archivo `vercel.json` ya está configurado para usar `wsgi.py` como punto de entrada.

---

## � Seguridad

### Buenas Prácticas Implementadas

- ✅ Contraseñas hasheadas con Werkzeug
- ✅ Autenticación con Flask-Login
- ✅ Protección de rutas con decoradores
- ✅ Validación de permisos por rol
- ✅ Sistema de aprobación de usuarios
- ✅ Accesos temporales con expiración
- ✅ Usuarios protegidos (no eliminables)

### Recomendaciones

- Cambiar contraseñas por defecto
- Usar HTTPS en producción
- Configurar SECRET_KEY fuerte
- Revisar accesos periódicamente
- Mantener dependencias actualizadas

---

## 📝 Mantenimiento

### Backup de Base de Datos

**SQLite (desarrollo):**
```bash
# Descargar desde la interfaz
/admin/db/backup
```

**PostgreSQL (producción):**
```bash
pg_dump -U usuario -h host database > backup.sql
```

### Importar Números de Informe

1. Preparar CSV con formato:
```
FR;No DIAG
FR001;DIAG-2024-001
FR002;DIAG-2024-002
```

2. Importar desde `/admin/import_informes`

---

## � Solución de Problemas

### Error: "Puerto ya en uso"

```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

### Error: "Base de datos no encontrada"

Verificar que la aplicación se ejecutó al menos una vez para crear las tablas automáticamente.

### Error: "Licencia no válida" / "Permiso denegado"

Verificar que el usuario esté aprobado y su acceso no haya expirado.

---

## � Documentación Adicional

- **ARQUITECTURA_DEL_SISTEMA.md** - Documentación técnica completa
- **DEPLOY_GUIA.md** - Guía de despliegue
- **GUIA_DESARROLLO.md** - Guía para desarrolladores

---

## � Changelog

### v2.0.0 (2026-01-28)
- ✅ Sistema de roles y permisos completo
- ✅ WorkflowEngine para validación de estados
- ✅ Panel de estados mejorado
- ✅ Gestión de usuarios con accesos temporales
- ✅ Exportación de datos
- ✅ Búsqueda avanzada
- ✅ Tema dark profesional
- ✅ Despliegue en Vercel con PostgreSQL

---

## 👨‍💻 Desarrollado para

**CABELAB**  
Sistema de Control de Equipos de Motosoldadoras

---

## 📄 Licencia

Uso exclusivo de CABELAB.  
Prohibida la distribución sin autorización.

---

## 📞 Soporte Técnico

Para consultas sobre el sistema, contactar al administrador del sistema.

---

**Última actualización**: 2026-01-28  
**Versión**: 2.0.0