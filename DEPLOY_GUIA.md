# Guía de Despliegue Final (Actualizada para Vercel)

El error "Internal Server Error" ocurría porque en Vercel no se puede guardar nada en la carpeta principal, solo en la carpeta temporal `/tmp`.

He modificado el código para arreglar esto automáticamente. Sigue estos pasos para subir la corrección:

## Paso Único: Actualizar en GitHub
Copia y pega estos comandos en tu terminal:

```powershell
git add .
git commit -m "Fix Vercel deployment: use temp DB and init on request"
git push origin main
```

**¿Qué pasará?**
1.  Vercel detectará el nuevo cambio y volverá a construir la app (esto tarda 1-2 minutos).
2.  Cuando termine, el error desaparecerá.
3.  Al entrar la primera vez, **tardará unos segundos extra** porque estará descargando tu Excel de Google Drive.

¡Con esto debería funcionar el login de Admin perfectamente!
