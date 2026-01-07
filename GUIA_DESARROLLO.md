# Renovación Visual del Dashboard

He transformado la vista de "Mis Tareas" para ser mucho más densa y útil, especialmente para Recepción.

**Mejoras Clave:**
1.  **Tablas en vez de Tarjetas:** Ahora verás el listado limpio para gestionar mejor el volumen de equipos.
2.  **Resumen de Estados:** Arriba verás insignias contando cuántos equipos hay en cada fase (Pendiente, Diagnóstico, Mantenimiento, etc.).
3.  **Para Recepción:** He añadido dos paneles críticos:
    *   🔴 **Veteranos:** Los equipos que llevan más tiempo esperando aprobación.
    *   🟢 **Recientes:** Los últimos que han llegado para aprobar.

**Sube estos cambios a rama DEV:**
```powershell
git add .
git commit -m "UI Refactor: Tablas y Resumenes por Rol"
git push origin dev
```

Revisa el link de **Preview** en Vercel para confirmar que te gusta el nuevo diseño antes de pasarlo a producción (`main`).
