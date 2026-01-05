# Guía de Diagnóstico

No es normal que siga fallando si la prueba local funcionó. Posiblemente Vercel tenga bloqueada la conexión o haya un error oculto.

He creado una **herramienta de diagnóstico** dentro de tu propia página para ver qué está pasando.

## Paso 1: Actualizar
Sube este cambio:

```powershell
git add .
git commit -m "Agregar herramienta de diagnostico"
git push origin main
```

## Paso 2: Ejecutar Diagnóstico
1.  Espera 1 minuto a que se actualice.
2.  Entra a tu página web y añade **/debug_sync** al final de la dirección.
    *   Ejemplo: `https://pizarra-virtual.vercel.app/debug_sync`
3.  Verás una pantalla negra con letras verdes (tipo Matrix).
4.  **Dime qué error sale ahí** o copio el texto.

Ahí nos dirá exactamente si es un error de "Permiso denegado", "Timeout", o "Columna no encontrada".
