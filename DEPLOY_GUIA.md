# Organización Visual Correcta

El usuario reportó que los equipos "saltaban" de tabla incorrectamente al pedir repuestos.

**Causa:**
El filtrado visual no distinguía entre pedir un repuesto para *Diagnóstico* (fase inicial) o para *Mantenimiento* (fase final). Ambos tienen la palabra "repuesto".

**Solución:**
He ajustado los filtros del panel "Visualizador":
1.  **Tabla Diagnóstico:** Ahora retiene los equipos si el estado es "Diagnóstico", "Consumible" o "Repuesto" (singular, que corresponde a esta etapa).
2.  **Tabla Aprobados/Servicio:** Ahora retiene los equipos si el estado es "Aprobado", "Servicio" o "Repuestos" (plural, que corresponde a mantenimiento).

**Sube este cambio:**
```powershell
git add .
git commit -m "Corregir filtros visuales repuestos"
git push origin main
```

Ahora cada equipo se quedará en su carril correspondiente hasta terminar la fase.
