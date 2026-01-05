# Guía de Despliegue Final (Sync Robusto)

He reforzado el código de sincronización para asegurar que pueda leer el Excel correctamente en el servidor de Vercel.

**Datos de Acceso Confirmados:**
*   **Usuario**: `Venllas`
*   **Contraseña**: `Venllas2025`
    *(Asegúrate de escribir la V mayúscula)*.

## Instrucciones para actualizar:
Ejecuta esto en tu terminal por última vez:

```powershell
git add .
git commit -m "Mejorar lecturas de excel"
git push origin main
```

Una vez desplegado:
1.  Espera 1-2 minutos a que Vercel termine.
2.  Entra a la web.
3.  Inicia sesión (puede tardar 5-10 segundos en entrar la primera vez mientras descarga los datos).
4.  Si ves "No hay equipos", **recarga la página** o usa el botón de "Refrescar".
