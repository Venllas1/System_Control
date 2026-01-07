# Arreglo de Syntax Error (Etiqueta huérfana)

**El error:** `Encountered unknown tag 'endif'`.
**Causa:** Al cambiar de "Tarjetas" a "Tablas", eliminé un `{% if %}` condicional pero dejé su cierre `{% endif %}` por accidente. El sistema se confundió al encontrar un cierre sin apertura.

**Solución:**
Eliminé la línea sobrante (Línea 316). Ahora el código es simétrico y debería cargar perfectamente.

**Sube este cambio:**
```powershell
git add .
git commit -m "Fix syntax error dashboard"
git push origin dev
```

Esto debería desbloquear finalmente la vista.
