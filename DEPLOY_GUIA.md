# Guía de Despliegue Final (Anti-Duplicados)

La duplicación ocurría porque el servidor "se ponía nervioso" y arrancaba 2 o 3 veces a la vez, copiando los datos varias veces.

He implementado un **semáforo** (cooldown):
*   Ahora el sistema verifica si se actualizó hace menos de 3 minutos. Si es así, no hace nada (evita duplicados).
*   He mejorado la herramienta `/debug_sync` para que **FUERCE** una limpieza total y recarga fresca.

## Solución Definitiva
1.  Sube el cambio:

```powershell
git add .
git commit -m "Evitar duplicados y crear historial"
git push origin main
```

2.  Entra a: `https://TU-APP.vercel.app/debug_sync`
    *   Al entrar aquí, se borrarán todos los duplicados y se bajarán los datos limpios y nuevos de tu Excel.
    *   Si agregas un equipo nuevo en Excel, **recuerda esperar 2-3 minutos** (Google tarda un poco en publicar el cambio) y luego refresca tu página.
