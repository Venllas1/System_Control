# Arreglo Final: Persistencia y Flujos

Problema detectado: La "actualización de estructura" se quedó activada y borraba la tabla cada vez que el servidor se reiniciaba (o sea, muy seguido).
**¡Lo he desactivado!** Ahora tus datos son sagrados y no se tocarán.

## Mejoras Incluidas:
1.  **Botón Eliminar:** El usuario `Venllas` (y Admins) verán un tacho de basura rojo para borrar equipos.
2.  **Flujo Corregido:** He alineado los botones de Repuestos y Servicio para que coincidan con las reglas del sistema (Almacén entrega -> Operaciones retoma).

## Instrucciones
Sube este cambio crítico:

```powershell
git add .
git commit -m "Reparar persistencia y agregar eliminar"
git push origin main
```

**Importante:**
Como estábamos borrando la tabla, es probable que ahora mismo esté vacía o vieja.
Una vez que subas esto, **carga tus datos una última vez** con la herramienta secreta:
`.../debug_sync`

¡Y listo! A partir de ese momento, **nunca más** se borrará nada. Podrás cerrar sesión, volver mañana, y ahí estarán.
