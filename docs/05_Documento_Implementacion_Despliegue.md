# 05 - DOCUMENTO DE IMPLEMENTACIÓN Y DESPLIEGUE
**PROYECTO INTEGRADOR: SISTEMA DE GESTIÓN DOCUMENTAL INTELIGENTE (DocuMind Enterprise)**  
**Asignatura:** Desarrollo de Aplicaciones Empresariales – VI Semestre  
**Institución:** Unidades Tecnológicas de Santander (UTS)  
**Docente:** Wilson Castaño Galviz  

---

## 1. Descripción del Ambiente de Implementación
El sistema **DocuMind Enterprise** está diseñado para desplegarse con agilidad tanto en estaciones de trabajo locales para desarrollo y sustentación, como en servidores corporativos basados en contenedores Linux o plataformas en la nube.

### Requisitos Mínimos de Hardware y Software

| Recurso | Requisito Mínimo (Local / Desarrollo) | Requisito Recomendado (Producción Empresarial) |
|---|---|---|
| **Procesador (CPU)** | Intel Core i3 / AMD Ryzen 3 (2 núcleos) | Intel Core i5 / AMD Ryzen 5 o superior (4+ núcleos) |
| **Memoria RAM** | 4 GB | 8 GB o superior |
| **Almacenamiento** | 2 GB libres en disco | 50 GB SSD (para repositorios masivos) |
| **Sistema Operativo** | Windows 10/11, macOS o Linux (Ubuntu 20.04+) | Ubuntu Server 22.04 LTS / Debian 12 |
| **Runtime** | Python 3.10 o superior | Python 3.11+, Docker Engine 24+, Nginx |
| **Navegador Web** | Chrome 90+, Edge 90+, Firefox 90+ | Última versión con soporte Web Standards |

---

## 2. Variables de Entorno y Configuración Segura
El sistema utiliza un archivo `.env` en la raíz del backend para aislar configuraciones sensibles del control de versiones.

```bash
# ==========================================
# CONFIGURACIÓN GENERAL DEL SERVIDOR
# ==========================================
APP_NAME="DocuMind Enterprise"
APP_ENV="production"
PORT=8000
HOST="0.0.0.0"

# ==========================================
# SEGURIDAD Y TOKENS JWT
# ==========================================
SECRET_KEY="documind_enterprise_super_secret_key_change_in_production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=480

# ==========================================
# BASE DE DATOS Y ALMACENAMIENTO
# ==========================================
DATABASE_URL="sqlite:///./documind.db"
STORAGE_DIR="./storage"
MAX_FILE_SIZE_MB=25

# ==========================================
# SERVICIOS DE INTELIGENCIA ARTIFICIAL
# ==========================================
# Si se deja vacío, el sistema utilizará el motor de IA local offline automático
GEMINI_API_KEY=""
AI_FALLBACK_MODE=true
```

---

## 3. Proceso de Instalación y Ejecución Local Paso a Paso

### Paso 1: Clonar o descargar el repositorio
```bash
cd c:\Users\Jaider\Documents\Proyectos_antigravity\Proyecto_Integrador_Empresariales
```

### Paso 2: Crear y activar entorno virtual Python
```bash
python -m venv venv

# En Windows:
venv\Scripts\activate

# En Linux/macOS:
source venv/bin/activate
```

### Paso 3: Instalar dependencias requeridas
```bash
pip install -r backend/requirements.txt
```

### Paso 4: Inicializar la Base de Datos y Generar Documentos de Prueba
```bash
python backend/init_db.py
python backend/generate_test_docs.py
```

### Paso 5: Iniciar el Servidor de Aplicación
```bash
python backend/app/main.py
```
*O mediante el ejecutable directo en Windows:*  
Hacer doble clic en `run_server.bat`.

### Paso 6: Acceso a la Aplicación
Abrir el navegador web e ingresar a:  
👉 **`http://localhost:8000`**  
- **Credenciales por defecto del Administrador:**
  - **Correo:** `admin@documind.com`
  - **Contraseña:** `Admin123!`

---

## 4. Proceso de Despliegue en Producción (Docker)

Para ambientes de producción corporativa se provee la definición de contenedor:

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY frontend/ ./frontend/

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Comandos de despliegue con Docker:
```bash
docker build -t documind-enterprise .
docker run -d -p 8000:8000 --name documind-app -v documind_data:/app/backend/storage documind-enterprise
```

---

## 5. Estrategia de Respaldo y Recuperación (Disaster Recovery)

1. **Respaldo de Base de Datos:**  
   Al ser SQLite una base de datos ACID autocontenida, se puede realizar un snapshot en caliente mediante la utilidad `sqlite3`:
   ```bash
   sqlite3 documind.db ".backup './backups/documind_backup_$(date +%Y%m%d).db'"
   ```
2. **Respaldo de Archivos Físicos:**  
   Sincronización diaria del directorio `backend/storage/` mediante `rsync` o copia comprimida en almacenamiento seguro en frío.
3. **Plan de Restauración:**  
   En caso de fallo catastrófico, basta con restaurar el archivo `.db` y la carpeta `storage/` en un servidor nuevo y reejecutar el contenedor Docker.

---

## 6. Plan Básico de Mantenimiento
- **Monitoreo de Espacio en Disco:** Alertar cuando el uso del volumen de almacenamiento supere el 85%.
- **Limpieza de Archivos Temporales:** Tarea programada (Cron semanal) para purgar fragmentos huérfanos o archivos no asociados.
- **Rotación de Logs de Auditoría:** Purgar o archivar registros de auditoría con más de 180 días de antigüedad.
- **Actualización de Librerías:** Revisión mensual de parches de seguridad para dependencias de Python y FastAPI.
