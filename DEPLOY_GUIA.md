# Formulario de Recepción Modificado

Cumpliendo con la solicitud de personalizar el registro para Recepción.
He añadido los campos solicitados y actualizado la base de datos de manera segura.

**Cambios Realizados:**
1.  **Nuevos Campos:** Cliente, Número de Serie, Accesorios.
2.  **Base de Datos Inteligente:** Al reiniciar, el sistema añadirá automáticamente estas columnas sin borrar nada.
3.  **Formulario Actualizado:** El modal de registro ahora pide exactamente:
    *   FR, Cliente, Fecha (Auto), Marca, Modelo, Serie, Estado (Condición), Accesorios, Reporte.

**Sube estos cambios:**
```powershell
git add .
git commit -m "Personalizar formulario Recepcion y actualizar DB"
git push origin main
```

**Nota:** Es posible que la primera vez falle levemente si la DB está bloqueada, pero al reintentar o reiniciar debería ajustarse sola.
