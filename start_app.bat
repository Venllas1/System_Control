@echo off
TITLE CABELAB 2025 Server
echo ===================================================
echo   Iniciando CABELAB 2025 - Control de Equipos
echo ===================================================
echo.

:: Abrir navegador (espera 2 segundos para dar tiempo al server)
timeout /t 2 /nobreak >nul
start http://localhost:5000

:: Activar entorno virtual
echo Activando entorno virtual (sourceVenllas)...
call sourceVenllas\Scripts\activate

:: Ejecutar aplicacion
echo Iniciando servidor...
python app.py

pause
