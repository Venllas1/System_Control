# Sincronización v3.0 (Reglas Estrictas)

**Requerimiento:** "Forzar valores por defecto (Sin FR, S/N, No Asignado) y asegurar texto en Serie/Accesorios".

**Solución:**
He actualizado el motor de importación. Ahora, si el Excel tiene celdas vacías, el sistema no pondrá "null" ni "sin info", sino exactamente lo que pediste:
*   Falta FR -> **"Sin FR"**
*   Falta Serie -> **"S/N"**
*   Falta Encargado -> **"No asignado"**
*   Falta Accesorios -> **"Sin accesorios"**

Además, me aseguré de que "Serie" y "Accesorios" se lean siempre como texto, para que no falte nada.

**Sube este cambio:**
```powershell
git add .
git commit -m "Update Excel Sync defaults"
git push origin dev
```

Y nuevamente, dale a **"Sincronizar Cloud"** para aplicar estas reglas a todos tus datos.
