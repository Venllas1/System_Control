#!/bin/bash
echo "==================================================="
echo "  Iniciando CABELAB 2025 - Control de Equipos"
echo "==================================================="

# Activar entorno virtual
# Nota: En Windows Git Bash la ruta usual es Scripts, en Linux puro es bin.
# Asumimos estructura Windows por el contexto.
if [ -f "sourceVenllas/Scripts/activate" ]; then
    source sourceVenllas/Scripts/activate
else
    source sourceVenllas/bin/activate
fi

# Abrir navegador
# Esto intenta usar el comando 'start' de Windows o 'explorer'
echo "Abriendo navegador..."
if command -v start &> /dev/null; then
    start http://localhost:5000
elif command -v explorer &> /dev/null; then
    explorer http://localhost:5000
else
    # Fallback para Linux/Mac puros si fuera el caso
    xdg-open http://localhost:5000 2>/dev/null
fi

# Ejecutar app
python app.py
