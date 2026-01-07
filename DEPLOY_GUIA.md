# Solución Error: "Transición Desconocida"

**Problema:**
Algunos equipos (probablemente importados o antiguos) tienen el estado "Espera Diagnostico" (sin la preposición "de"), mientras que el sistema espera estrictamente "Espera **de** Diagnostico".
Al intentar iniciar diagnóstico, el sistema dice "No reconozco este estado actual" y bloquea el cambio.

**Corrección:**
Agregué una regla al "Cerebro" del sistema (`workflow_logic.py`) para que entienda que "Espera Diagnostico" es lo mismo que "Espera de Diagnostico" y permita avanzar.

**Sube este cambio:**
```powershell
git add .
git commit -m "Permitir transicion Espera Diagnostico legacy"
git push origin main
```

Ahora podrás iniciar el diagnóstico de ese equipo Lincoln.
