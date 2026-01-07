# Restaurar Botón de Sincronización

**El problema:** "No encuentro el botón".
**La causa:** Se había borrado de la pantalla (HTML), aunque su cerebro (código JS) seguía ahí.

**Solución:**
He vuelto a colocar el botón **"Sincronizar Cloud"** en la cabecera del Panel de Administrador (junto a "Backup DB").

**Ruta para verlo:**
1.  Debes entrar con un usuario **Administrador** (como `admin` o `Venllas`).
2.  Verás el botón verde arriba a la derecha.

**Sube este cambio:**
```powershell
git add .
git commit -m "Restore Sync Cloud Button"
git push origin dev
```

Una vez aparezca, púlsalo para traer los clientes y aplicar la limpieza.
