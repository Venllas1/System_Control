# Modo Diagnóstico Activado

He envuelto la lógica del dashboard en un "Cazador de Errores".
En lugar de mostrar una página blanca de "Error 500", ahora mostrará en pantalla el texto exacto del error (Traceback).

Además, he reforzado la lógica de ordenamiento en el servidor (`app.py`) para que use una fecha por defecto (año 2000) si encuentra un equipo sin fecha, evitando el error de comparación.

**Sube esto para ver qué pasa:**
```powershell
git add .
git commit -m "Enable Debug Mode and Fix Sort"
git push origin dev
```

Si el error persiste, ahora por lo menos verás un texto técnico en pantalla. **Copia y pégame ese texto** para darte la solución final.
