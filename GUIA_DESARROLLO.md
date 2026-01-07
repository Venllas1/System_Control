# Error 500 Solucionado

**Causa:**
El servidor falló porque algunos equipos antiguos no tienen guardada la `fecha de ingreso`. Al intentar ordenarlos en la nueva vista de "Atención Prioritaria" de Recepción, el sistema intentaba formatear una fecha inexistente (`None`), provocando el error crítico.

**Solución:**
Agregué una protección en el código visual (`dashboard.html`) para que, si no hay fecha, muestre "N/A" en lugar de romperse.

**Sube este cambio:**
```powershell
git add .
git commit -m "Fix 500 error: handle null dates in dashboard"
git push origin dev
```

Ahora el sistema es robusto ante datos antiguos o incompletos.
