# Guía Final: Base de Datos Real (Postgres)

Para solucionar el problema de los usuarios que se borran, vamos a conectar el proyecto a una base de datos real en Vercel.

## Paso 1: Crear la Base de Datos (Web de Vercel)
1.  En la pantalla que me mostraste, selecciona **Neon (Serverless Postgres)**.
2.  Dale a **Create**.
3.  Te pedirá confirmar una región (acepta la que salga por defecto, ej: Washington DC).
4.  Dale a **Connect** (asegúrate de que esté seleccionada tu app "pizarra-virtual").
5.  Vercel añadirá automáticamente las "Environment Variables" (`POSTGRES_URL`, etc.). **No necesitas copiar nada**, se configuran solas.

## Paso 2: Actualizar el Código
He preparado el programa para que detecte automáticamente esta nueva base de datos. Solo sube los cambios:

```powershell
git add .
git commit -m "Activar soporte PostgreSQL"
git push origin main
```

## Paso 3: Disfrutar
1.  Vercel volverá a desplegar (tarda 1-2 mins).
2.  Entra a tu aplicación.
3.  Crea un usuario nuevo.
4.  Esta vez, **el usuario NUNCA se borrará**, porque ya está guardado en una base de datos profesional.
