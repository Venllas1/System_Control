# 🏥 CABELAB 2025 - Sistema de Control de Equipos

Sistema profesional de gestión y control de equipos con sistema de licencias integrado.

## 🚀 Características

- ✅ **Dashboard interactivo** con estadísticas en tiempo real
- ✅ **Sistema de licencias** híbrido (local + online)
- ✅ **Control remoto** de licencias desde panel admin
- ✅ **Exportación** de datos (CSV, Excel)
- ✅ **Búsqueda avanzada** y filtros
- ✅ **Tema dark** profesional y responsive

---

## 📋 Requisitos

- Python 3.8 o superior
- Conexión a internet (opcional - funciona offline 24h)
- Navegador web moderno

---

## ⚡ Instalación Rápida

### 1. Clonar/Descargar el proyecto

```bash
cd CABELAB_2025
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

### 4. Configurar Firebase (opcional - para licencias online)

Ver: `docs/FIREBASE_SETUP.md`

### 5. Ejecutar aplicación

```bash
python app.py
```

Acceder a: `http://localhost:5000`

---

## 🔐 Sistema de Licencias

### Para Usuarios (Clientes)

1. **Obtener Hardware ID:**
   - Ejecutar la app por primera vez
   - Ir a: `http://localhost:5000/license/activate`
   - Copiar Hardware ID
   - Enviar al administrador

2. **Activar Licencia:**
   - Recibir clave de licencia del administrador
   - Pegar en formulario de activación
   - ¡Listo! Ya puedes usar la app

### Para Administradores

#### Opción A: Panel Web (Online - Recomendado)

```bash
python admin/admin_panel.py
```

Acceder a: `http://localhost:5001/admin`  
Password: `admin123` (cambiar en producción)

#### Opción B: Script CLI (Local)

```bash
python scripts/generate_license.py
```

---

## 📁 Estructura del Proyecto

```
CABELAB_2025/
├── app.py                    # Servidor principal
├── config.py                 # Configuración
├── requirements.txt          # Dependencias
├── utils/                    # Módulos Python
├── static/                   # CSS, JS, imágenes
├── templates/                # HTML
├── admin/                    # Panel administrador
├── scripts/                  # Scripts utilidad
├── keys/                     # Claves RSA
├── logs/                     # Logs de sistema
└── exports/                  # Exportaciones
```

---

## ⚙️ Configuración

### Editar ruta del Excel

`config.py` línea 16:
```python
EXCEL_PATH = r"C:\ruta\a\tu\archivo.xlsx"
```

### Cambiar puerto

`app.py` línea 362:
```python
app.run(port=5000)  # Cambiar 5000 por tu puerto
```

### Configurar Firebase

`utils/firebase_license.py` líneas 22-23:
```python
self.firebase_url = "https://tu-proyecto.firebaseio.com"
self.api_key = "TU_API_KEY"
```

---

## 🎨 Personalización

### Cambiar colores

`static/css/dashboard.css` líneas 11-20:
```css
:root {
    --primary: #6366f1;    /* Tu color */
    --secondary: #8b5cf6;
}
```

### Cambiar logo

`templates/dashboard.html` línea 19:
```html
<i class="fas fa-tu-icono"></i>
```

O usar imagen:
```html
<img src="{{ url_for('static', filename='img/logo.png') }}" height="60">
```

---

## 📊 Uso

### Dashboard Principal

- **Estadísticas:** 5 métricas principales
- **Tablas:** Equipos por estado
- **Pestañas:** Resumen, Detalle, Herramientas
- **Exportar:** CSV o Excel desde pestaña Herramientas

### Panel Administrador

- **Ver todas las licencias** activas
- **Aprobar solicitudes** pendientes
- **Revocar acceso** instantáneamente
- **Renovar licencias** con 1 click
- **Estadísticas** en tiempo real

---

## 🔧 Solución de Problemas

### Error: "Archivo Excel no encontrado"
**Solución:** Verificar ruta en `config.py`

### Error: "Licencia no válida"
**Solución:** Activar licencia en `/license/activate`

### Error: "Puerto ya en uso"
**Solución:** Cambiar puerto en `app.py` o matar proceso:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

### La app no se conecta a Firebase
**Solución:** Verificar URL y reglas en Firebase Console

---

## 🛡️ Seguridad

### Archivos NUNCA compartir:
- ❌ `keys/private.pem`
- ❌ `license.dat`
- ❌ Archivos `.log`

### Cambiar contraseña admin:
`admin/admin_panel.py` línea 14:
```python
ADMIN_PASSWORD = "tu_password_seguro"
```

---

## 📝 Logs

### Ver logs de la app:
```bash
cat logs/cabelab.log
```

### Ver intentos de licencia:
```bash
cat logs/license_attempts.log
```

---

## 🔄 Actualización

```bash
# Activar entorno virtual
venv\Scripts\activate

# Actualizar dependencias
pip install --upgrade -r requirements.txt

# Reiniciar app
python app.py
```

---

## 📞 Soporte

Para problemas o consultas:
- 📧 Email: soporte@cabelab.com
- 📱 WhatsApp: +51 XXX XXX XXX

---

## 📄 Licencia

Uso exclusivo de CABELAB 2025.  
Prohibida la distribución sin autorización.

---

## 👨‍💻 Desarrollado por

**CABELAB 2025**  
Sistema de Control de Equipos v2.0

---

## 📅 Changelog

### v2.0.0 (2025-05-12)
- ✅ Sistema de licencias online con Firebase
- ✅ Panel de administración web
- ✅ Tema dark profesional
- ✅ Exportación de datos
- ✅ Búsqueda avanzada

### v1.0.0 (2025-01-15)
- ✅ Versión inicial
- ✅ Dashboard básico
- ✅ Lectura de Excel


### Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
### .\sourceVenllas\Scripts\Activate