# Guía de Despliegue (GitHub y Vercel)

Como tu equipo no tiene `git` instalado/configurado en la consola, sigue estos pasos para subir tu proyecto:

## 1. Preparar Archivos
He creado el archivo `vercel.json` necesario para que Vercel reconozca tu aplicación Python.

## 2. Opción A: Usar GitHub Desktop (Recomendado)
1.  Descarga e instala **[GitHub Desktop](https://desktop.github.com/)**.
2.  Inicia sesión con tu cuenta de GitHub.
3.  Ve a **File > Add Local Repository**.
4.  Selecciona la carpeta `C:\Users\User\Desktop\Pizarra Virtual`.
5.  Si te pregunta si quieres crear un repositorio, dile que **SÍ**.
6.  En la pestaña "Changes", escribe un título (ej: "Versión Final V1") y dale a **Commit**.
7.  Dale al botón **Publish repository** (esto lo subirá a GitHub).

## 3. Opción B: Subida Manual (Web)
1.  Ve a [github.com/new](https://github.com/new) y crea un repositorio vacio.
2.  En la página del repo, busca la opción **"uploading an existing file"**.
3.  Arrastra todos los archivos de tu carpeta `Pizarra Virtual` ahí.
4.  Dale a "Commit changes".

## 4. Conectar a Vercel
1.  Ve a [vercel.com](https://vercel.com) e inicia sesión (con tu cuenta de GitHub es más fácil).
2.  Dale a **"Add New..."** -> **"Project"**.
3.  Selecciona el repositorio que acabas de subir a GitHub ("Import").
4.  En la configuración:
    *   **Framework Preset**: Other (o Flask si sale).
    *   **Root Directory**: ./
    *   **Environment Variables**: Si usaras API keys privadas, irían aqui. Como usas un Link Público de Drive, no necesitas configurar nada extra.
5.  Dale a **Deploy**.

## Nota Importante sobre la Base de Datos
En Vercel, el sistema de archivos es "efímero" (se borra cada vez que se reinicia).
*   **Tu App Actual**: Usa SQLite (`equipos.db`).
*   **En Vercel**: Cada vez que se vuelva a desplegar, la base de datos se reiniciará.
*   **Solución**: Como has configurado que al inicio se **descargue el Excel de Google Drive**, esto no es un problema grave: cada vez que arranque, leerá el Excel actualizado. ¡Así que funcionará bien!

**Solo recuerda**: Si haces cambios manuales en la web (si habilitaras editar), esos cambios se perderían. Pero como tu fuente de verdad es el Excel de Google Drive, estarás bien.
