# Guía de Despliegue Final (Fix Base de Datos)

He reprogramado la sincronización para que sea **inteligente**.

Ahora el sistema:
1.  Busca específicamente la hoja **"CONTROL DE EQUIPOS CABELAB"**.
2.  Si por alguna razón el Excel exporta con otro nombre (ej. "Hoja1"), el sistema **busca automáticamente** la hoja que tenga las columnas "MARCA" y "MODELO", ignorando las demás.

Esto asegura que tus equipos aparezcan sí o sí.

## Paso Único: Actualizar
Sube este cambio final:

```powershell
git add .
git commit -m "Forzar lectura de hoja correcta"
git push origin main
```

**Nota:** Recuerda que la primera vez que entras tarda unos segundos en descargar los datos.
