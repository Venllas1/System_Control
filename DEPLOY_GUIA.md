# Exclusión de Servicios Culminados en KPI

Solicitud: "Cuando termine mantenimiento, que ya no cuente como aprobado".

**Corrección:**
Ajusté el contador de "Aprobados".
Antes contaba todo lo que decía "Servicio".
Ahora cuenta "Servicio" **PERO** excluye específicamente "Servicio Culminado" y "Entregado".

Así, el número reflejará solo los equipos que están **actualmente en el taller**, y bajará automáticamente cuando se terminen.

**Sube este cambio:**
```powershell
git add .
git commit -m "Excluir servicios culminados de KPI aprobados"
git push origin main
```

El tablero ahora es un reflejo exacto de la carga de trabajo actual.
