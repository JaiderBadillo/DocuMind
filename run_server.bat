@echo off
chcp 65001 > nul
cls
echo =========================================================================
echo       DOCUMIND ENTERPRISE - SISTEMA DE GESTION DOCUMENTAL CON IA
echo   Proyecto Integrador - VI Semestre UTS - Docente: Wilson Castano Galviz
echo =========================================================================
echo.

:: 1. Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no se encuentra en el PATH.
    echo Por favor instale Python 3.10 o superior.
    pause
    exit /b 1
)

:: 2. Instalar dependencias si no se han instalado
echo [1/4] Verificando e instalando dependencias en backend...
pip install -r backend/requirements.txt

:: 3. Inicializar Base de Datos SQLite
echo [2/4] Inicializando base de datos SQLite y usuario admin...
python backend/init_db.py

:: 4. Generar los 30 documentos de prueba sinteticos
echo [3/4] Generando 30 documentos sinteticos de prueba (PDF, DOCX, TXT)...
python backend/generate_test_docs.py

:: 5. Iniciar Servidor FastAPI
echo [4/4] Iniciando Servidor Web DocuMind Enterprise en http://localhost:8000 ...
echo.
echo Presione Ctrl+C para detener el servidor en cualquier momento.
echo.
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

pause
