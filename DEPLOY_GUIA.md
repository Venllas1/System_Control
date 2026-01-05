# Arreglo: Ciclo de Repuestos (Devoluciones)

He habilitado el "bucle de repuestos".
Antes, una vez que iniciabas el servicio, el sistema asumía que ya tenías todo.
Ahora, si el repuesto es incorrecto o falta otro, puedes volver a pedirlo.

**Logica Nueva:**
*   `En Servicio` -> Permite volver a `Espera de Repuestos`.
*   Almacén entrega -> Vuelves a `En Servicio`.

**Sube este cambio:**
```powershell
git add .
git commit -m "Permitir rebote de repuestos"
git push origin main
```
