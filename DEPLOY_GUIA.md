# Arreglo Final: KPIs y Mayúsculas

Había un detalle visual: Los contadores (esas tarjetas de colores arriba) solo se calculaban para el "Visualizador". Por eso Recepción veía ceros.

**Corrección Aplicada:**
1.  **KPIs Globales:** He movido la calculadora de estados para que funcione para TODOS los roles. Ahora Recepción verá "Pendientes: 5" (o los que sean) al entrar.
2.  **Todo Mayúsculas:** He forzado que Marca y Modelo también se vean en mayúsculas, además de los Estados.

**Sube este cambio:**
```powershell
git add .
git commit -m "Activar KPIs para todos y mayusculas"
git push origin main
```

Con esto, el panel de Recepción debería reflejar la realidad inmediatamente.
