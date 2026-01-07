# Recuperación de Datos (Cliente y Observaciones)

**El problema:** "Se perdió la información de Cliente y Observaciones en la importación inicial".
**La causa:** El "mapa de traducción" del sistema no sabía que la columna "CLIENTE" del Excel correspondía al campo "cliente" de la base de datos, así que la ignoraba.

**La solución:**
1.  **Mapeo de Cliente:** He enseñado al sistema que busque columnas llamadas "CLIENTE", "NOMBRE" o "PROPIETARIO" y guarde esa info.
2.  **Mapeo de Observaciones:** Ya existía, pero con la nueva limpieza (`clean_text`) nos aseguramos de que no se guarde como vacío si hay espacios ocultos.

**Para arreglar tu base de datos (Neon):**
1.  Sube este cambio:
    ```powershell
    git add .
    git commit -m "Fix excel mapping for Cliente"
    git push origin dev
    ```
2.  **IMPORTANTE:** Una vez subido, ve a tu Dashboard y pulsa el botón **"Sincronizar Cloud"** (arriba a la derecha). Esto borrará los datos incompletos actuales y traerá todo de nuevo desde el Excel, esta vez incluyendo al Cliente y con la limpieza activada.

*Nota: Solo necesitas hacerlo una vez.*
