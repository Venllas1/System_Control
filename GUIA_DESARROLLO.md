# Asignación de Encargado en Mantenimiento

**Requerimiento:** "Pedir encargado al iniciar mantenimiento y mostrarlo en la tabla".

**Solución:**
1.  **Nuevo Prompt:** Ahora, al pulsar "Iniciar Mantenimiento" (desde el estado Aprobado), el sistema mostrará una ventana pidiendo el nombre del responsable.
2.  **Visualización:** Ese nombre se guardará y aparecerá en la columna "Encargado" de la tabla de Aprobados/En Servicio.
3.  **Tiempos:** Como ya activamos el historial, este cambio de estado (y quién lo hizo) quedará registrado con su hora exacta.

**Sube este cambio:**
```powershell
git add .
git commit -m "Prompt encargado maintenance"
git push origin dev
```

Prueba iniciar un mantenimiento y verás que ahora te pide el nombre.
