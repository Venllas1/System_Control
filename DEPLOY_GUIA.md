# Guía de Despliegue Final (Fix Usuarios)

He actualizado el código para que cree automáticamente los usuarios **"Venllas"** y **"visualizador"** cuando arranque en Vercel, ya que la base de datos se crea desde cero.

**Contraseñas por defecto (Cámbialas al entrar si es posible):**
*   **Venllas**: `Venllas2025`
*   **visualizador**: `visualizador123`
*   **admin**: `admin123`

## Instrucciones para actualizar:
Ejecuta esto en tu terminal:

```powershell
git add .
git commit -m "Add Venllas and Visualizador users"
git push origin main
```

**Nota sobre los Equipos:**
Si no aparecen los equipos, espera unos 10-20 segundos después de iniciar sesión la primera vez, ya que el sistema los está descargando de Google Drive en segundo plano. Si siguen sin aparecer, verifica que el link de Google Sheet en `utils/excel_sync.py` siga siendo público y accesible.
