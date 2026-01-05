# Guía de Migración: Base de Datos Nativa

¡Decisión correcta! Al usar la base de datos nativa (Postgres):
1.  **Cero duplicados.**
2.  **Cero "desapariciones" de datos.**
3.  **Velocidad máxima.**
4.  **Almacenamiento:** Tienes espacio para **décadas** de trabajo (0.5GB es inmenso para texto).

## Paso 1: Aplicar el Cambio
Sube este código para desconectar el Excel fallido:

```powershell
git add .
git commit -m "Migrar a Base de Datos Nativa"
git push origin main
```

## Paso 2: Importación Inicial (Solo una vez)
Si al entrar ves la lista vacía, usa esta herramienta secreta una última vez para "chupar" los datos del Excel y guardarlos en Postgres:

1.  Entra a `https://TITULO-DE-TU-APP.vercel.app/debug_sync`
2.  Espera a que termine.
3.  Vuelve al inicio. ¡Tus datos ya están ahí seguros!

## Paso 3: Nueva Forma de Trabajo
*   **¿Nuevo equipo?** -> Botón "Agregar Equipo" en la web.
*   **¿Reporte?** -> Botón "Exportar" (baja un Excel limpio).
*   **¿Excel antiguo?** -> Ya no se usa. Solo es un respaldo histórico.
