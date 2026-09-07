# 07 - MANUAL TÉCNICO Y DE ADMINISTRACIÓN
**PROYECTO INTEGRADOR: SISTEMA DE GESTIÓN DOCUMENTAL INTELIGENTE (DocuMind Enterprise)**  
**Asignatura:** Desarrollo de Aplicaciones Empresariales – VI Semestre  
**Institución:** Unidades Tecnológicas de Santander (UTS)  
**Docente:** Wilson Castaño Galviz  

---

## 1. Responsabilidades del Administrador de Sistemas
El rol de **Administrador del Sistema** tiene el control operativo y técnico de la infraestructura de **DocuMind Enterprise**. Sus funciones principales comprenden:
- Monitoreo de disponibilidad y tiempos de respuesta de la API REST.
- Supervisión del espacio consumido en almacenamiento físico (`storage/`) y crecimiento de la base de datos relacional.
- Gestión de la vigencia de API Keys para proveedores de Inteligencia Artificial (Google Gemini).
- Ejecución de planes de contingencia, respaldo (backup) y restauración ante incidentes.
- Análisis de trazas de error en la consola de auditoría.

---

## 2. Configuración de Servicios y Proveedores de IA

El motor de IA está desacoplado mediante el patrón *Strategy* en `ai_engine.py`:

### Configuración con Google Gemini API
1. Obtenga una API Key válida en [Google AI Studio](https://aistudio.google.com/).
2. Abra el archivo de variables de entorno `.env` en la raíz del backend:
   ```env
   GEMINI_API_KEY="AIzaSyYourSecretKeyHere..."
   ```
3. Reinicie el servidor de FastAPI. El sistema detectará automáticamente la llave y utilizará `gemini-1.5-flash` para clasificación semántica de alta precisión y respuestas RAG enriquecidas.

### Configuración en Modo Autónomo / Offline (Fallback)
Si el servidor opera en una red cerrada sin acceso a internet o se agotaron las cuotas gratuitas:
- Deje la variable `GEMINI_API_KEY=""`.
- El sistema activará de forma transparente el **Motor Semántico Local**:
  - Clasificador Bayesiano / Léxico basado en ontologías empresariales preentrenadas.
  - Generador de resúmenes sintéticos por relevancia de oraciones núcleo.
  - Motor de extracción de expresiones regulares estructuradas para facturas, contratos y hojas de vida.
  - Calculador de similitud coseno vectorial en memoria con persistencia SQLite.

---

## 3. Administración de la Base de Datos SQLite

### Inspección Directa por Línea de Comandos
```bash
sqlite3 documind.db
```
Comandos útiles de diagnóstico:
```sql
-- Verificar conteo de documentos por estado
SELECT processing_status, COUNT(*) FROM documents GROUP BY processing_status;

-- Verificar distribución de categorías detectadas por IA
SELECT category, COUNT(*) FROM document_metadata GROUP BY category;

-- Consultar los últimos 10 errores registrados
SELECT timestamp, action, details FROM audit_logs WHERE status = 'ERROR' ORDER BY timestamp DESC LIMIT 10;
```

### Script de Inicialización y Reseteo (`init_db.py`)
Para reconstruir el esquema limpio o crear el usuario administrador inicial:
```bash
python backend/init_db.py
```

---

## 4. Gestión de Logs y Diagnóstico de Errores

Los logs se emiten simultáneamente a dos canales:
1. **Salida estándar (Consola stdout):** Nivel `INFO` con marcas de tiempo formateadas mediante `uvicorn`.
2. **Tabla relacional `audit_logs`:** Registro persistente de cada evento crítico:
   - `DOCUMENT_UPLOAD`: Carga de archivo completada.
   - `EXTRACTION_ERROR`: Archivo no legible o dañado.
   - `AI_INFERENCE_SUCCESS`: Clasificación y resumen generados.
   - `RAG_QUERY`: Pregunta efectuada por el usuario en el chat.

---

## 5. Procedimiento de Respaldo y Restauración en Caliente

### Generación de Respaldo (Backup)
1. Ejecute el siguiente comando en PowerShell o Bash:
   ```powershell
   # Windows PowerShell
   Copy-Item documind.db -Destination ".\backups\documind_$(Get-Date -Format 'yyyyMMdd_HHmmss').db"
   Compress-Archive -Path .\backend\storage -DestinationPath ".\backups\storage_$(Get-Date -Format 'yyyyMMdd_HHmmss').zip"
   ```
2. Asegúrese de que el directorio `backups/` se encuentre en un medio de almacenamiento secundario.

### Restauración
1. Detenga el servicio de FastAPI.
2. Reemplace `documind.db` con la copia de seguridad.
3. Descomprima el archivo `storage_*.zip` en la carpeta `backend/storage`.
4. Reinicie el servicio: `python backend/app/main.py`.
