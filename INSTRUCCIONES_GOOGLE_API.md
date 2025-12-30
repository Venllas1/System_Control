# Guía de Configuración Google Sheets API

Sigue estos pasos para obtener el archivo `credentials.json` que necesitamos.

1.  **Ir a Google Cloud Console**:
    *   Entra a: [https://console.cloud.google.com/](https://console.cloud.google.com/)
    *   Inicia sesión con tu cuenta de Google.

2.  **Crear Proyecto**:
    *   Arriba a la izquierda, haz clic en el selector de proyectos y luego en **"Nuevo Proyecto"**.
    *   Ponle nombre (ej: `PizarraVirtual-Sync`) y dale a **Crear**. Selecciona el proyecto nuevo.

3.  **Activar APIs de Drive y Sheets**:
    *   En el menú (tres líneas) ve a **APIs y servicios > Biblioteca**.
    *   Busca **"Google Sheets API"** -> Ábrela y dale a **Habilitar**.
    *   Vuelve a la Biblioteca, busca **"Google Drive API"** -> Ábrela y dale a **Habilitar**.

4.  **Crear Cuenta de Servicio (El Robot)**:
    *   Ve a: **APIs y servicios > Credenciales**.
    *   Clic en **+ CREAR CREDENCIALES** > **Cuenta de servicio**.
    *   **Nombre**: ej. `lector-excel`.
    *   Dale a **Crear y Continuar**, luego **Listo** (puedes saltar los roles opcionales).

5.  **Descargar la Llave (JSON)**:
    *   En la lista de Cuentas de servicio (abajo), haz clic en el email raro que se creó (algo como `lector-excel@...iam.gserviceaccount.com`).
    *   Ve a la pestaña **CLAVES** (arriba).
    *   Clic en **Agregar clave > Crear clave nueva**.
    *   Selecciona **JSON** y dale a **Crear**.
    *   **¡Se descargará un archivo!** Guárdalo como `credentials.json` en la carpeta `Pizarra Virtual` en tu escritorio.

6.  **Compartir el Excel**:
    *   Abre tu archivo `credentials.json` con el bloc de notas y copia el **"client_email"** (el correo largo).
    *   Ve a tu Excel en Google Drive.
    *   Dale al botón **Compartir**.
    *   Pega el correo y dale permisos de **Lector**.

**Cuando termines:** Asegúrate de que `credentials.json` esté en la carpeta del proyecto.
