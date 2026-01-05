# Guía de Despliegue Final

¡Excelente! Ya he configurado **Git** en tu carpeta y he creado el archivo de configuración para **Vercel**.
He realizado el primer "commit" con todos tus cambios.

Solo te falta conectar esto a GitHub:

## Paso 1: Crear Repositorio en GitHub
1.  Ve a [github.com/new](https://github.com/new).
2.  Ponle un nombre (ej: `pizarra-virtual`).
3.  **NO** marques "Initialize this repository with a README" (déjalo vacío).
4.  Dale a "Create repository".

## Paso 2: Subir tu código (Desde tu Terminal)
Copia y pega estos comandos en tu terminal (donde ya estás):

```powershell
git branch -M main
git remote add origin TU_URL_DEL_REPOSITORIO
git push -u origin main
```
*(Reemplaza `TU_URL_DEL_REPOSITORIO` por el link que te da GitHub, ej: `https://github.com/Usuario/pizarra-virtual.git`)*.

## Paso 3: Desplegar en Vercel
1.  Ve a [vercel.com/new](https://vercel.com/new).
2.  Importa el repositorio que acabas de subir (`pizarra-virtual`).
3.  Dale a **Deploy**.

¡Y listo! Tu aplicación estará en vivo.

### Verificación
*   **KPIs**: El orden es Diagnóstico -> Aprobados -> Pendientes -> Total.
*   **Aprobados**: No suma entregados en su tarjeta, pero sí en el Total.
*   **Base de Datos**: Se sincronizará con tu Excel de Google Drive cada vez que arranque.
