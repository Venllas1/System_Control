# Arreglo Urgente: Error de Servidor (500)

**Causa:**
Al agregar la lógica para actualizar la base de datos automáticamente, usé una función especial llamada `text()` para enviar comandos SQL, pero olvidé importar esa herramienta al principio del archivo.
El servidor intentaba arrancar, no encontraba la herramienta y colapsaba.

**Corrección:**
Agregué una pequeña palabra en la línea 9: `, text`.
Ahora el servidor tiene todo lo necesario para funcionar y crear las columnas nuevas.

**Sube este cambio:**
```powershell
git add .
git commit -m "Reparar importacion text sqlalchemy"
git push origin main
```

Esto solucionará el error 500 inmediatamente.
