@echo off
chcp 65001 > nul
echo =========================================================================
echo       DETENIENDO SERVIDOR DOCUMIND ENTERPRISE (PUERTO 8000)
echo =========================================================================
echo.

:: Buscar proceso escuchando en el puerto 8000 y cerrarlo
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo Cerrando proceso PID: %%a ...
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo Servidor detenido exitosamente. Ya puedes cerrar esta ventana.
echo.
pause
