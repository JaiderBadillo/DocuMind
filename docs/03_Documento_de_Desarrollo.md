# 03 - DOCUMENTO DE DESARROLLO Y MEMORIA TÉCNICA
**PROYECTO INTEGRADOR: SISTEMA DE GESTIÓN DOCUMENTAL INTELIGENTE (DocuMind Enterprise)**  
**Asignatura:** Desarrollo de Aplicaciones Empresariales – VI Semestre  
**Institución:** Unidades Tecnológicas de Santander (UTS)  
**Docente:** Wilson Castaño Galviz  

---

## 1. Descripción del Entorno de Desarrollo
El proyecto **DocuMind Enterprise** ha sido desarrollado bajo estándares de código limpio (Clean Code), tipado estricto y separación de responsabilidades:

- **Sistema Operativo Base:** Windows 10/11 / Linux Ubuntu 22.04 LTS.
- **Lenguaje de Programación Backend:** Python 3.10 / 3.11 / 3.12.
- **Framework Web Backend:** FastAPI 0.110+ con servidor asíncrono Uvicorn.
- **Lenguaje Frontend:** HTML5 semántico, CSS3 corporativo y JavaScript moderno (ES6+ Modules, Fetch API).
- **Gestor de Paquetes:** `pip` con fijación de versiones en `requirements.txt`.
- **Librerías de Procesamiento Documental:**
  - `pypdf` (v4.0+) para extracción de texto y metadatos de documentos PDF.
  - `python-docx` (v1.1+) para análisis y extracción de archivos Word DOCX.
- **Librerías de Criptografía y Seguridad:** `passlib[bcrypt]`, `python-jose[cryptography]`.

---

## 2. Estructura Completa del Código Fuente

```
Proyecto_Integrador_Empresariales/
│
├── backend/                               # Servidor de Aplicación y Motor IA
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth_routes.py             # Endpoints de login, registro y tokens
│   │   │   ├── repository_routes.py       # CRUD de carpetas
│   │   │   ├── document_routes.py         # Subida, descarga, visor y borrado
│   │   │   ├── search_routes.py           # Búsqueda semántica y chat RAG
│   │   │   └── dashboard_routes.py        # Métricas, KPIs y logs
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py                  # Variables de entorno y ajustes
│   │   │   ├── database.py                # Conexión SQLite y creación de tablas
│   │   │   └── security.py                # Hashing de contraseñas y JWT
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py                 # Esquemas Pydantic de entrada/salida
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── document_parser.py         # Extracción de PDF, DOCX y TXT
│   │   │   ├── ai_engine.py               # Clasificación, resumen y entidades
│   │   │   └── vector_store.py            # Chunker, embeddings y similitud coseno
│   │   └── main.py                        # Instancia FastAPI y orquestación
│   ├── storage/                           # Almacén de archivos físicos (aislado)
│   ├── requirements.txt                   # Dependencias Python
│   ├── init_db.py                         # Inicialización y sembrado de BD
│   └── generate_test_docs.py              # Generador de 30 documentos sintéticos
│
├── frontend/                              # Interfaz de Usuario Web
│   ├── index.html                         # SPA Empresarial Unificada
│   ├── css/
│   │   └── styles.css                     # Tokens de diseño, Glassmorphism, temas
│   └── js/
│       ├── api.js                         # Cliente HTTP y manejo de JWT
│       ├── app.js                         # Controladores de vista y eventos UI
│       └── components.js                  # Modales, gráficos y renderizadores
│
├── docs/                                  # Entregables Oficiales de Software (Fases I-V)
│   ├── 01_Documento_de_Analisis.md
│   ├── 02_Documento_de_Diseno.md
│   ├── 03_Documento_de_Desarrollo.md
│   ├── 04_Plan_y_Evidencias_de_Pruebas.md
│   ├── 05_Documento_Implementacion_Despliegue.md
│   ├── 06_Manual_de_Usuario.md
│   ├── 07_Manual_Tecnico_Administracion.md
│   ├── 08_Matriz_de_Trazabilidad.md
│   └── 13_Guion_Sustentacion_y_Video.md
│
├── test_dataset_30_docs/                  # Dataset Oficial de 30 Archivos de Prueba
│   ├── contratos_legal/                   # 10 archivos (PDF, DOCX, TXT)
│   ├── facturas_finanzas/                 # 10 archivos (PDF, DOCX, TXT)
│   └── talento_humano_informes/           # 10 archivos (PDF, DOCX, TXT)
│
├── run_server.bat                         # Lanzador en un clic para Windows
└── README.md                              # Guía rápida del repositorio
```

---

## 3. Implementación del Pipeline de Procesamiento de Documentos

### 3.1 Extracción Multiformato (`document_parser.py`)
El servicio cuenta con manejadores especializados según el MIME type o extensión del archivo:
- **Archivos `.pdf`:** Se utiliza `pypdf.PdfReader` para iterar sobre el árbol de páginas, extrayendo los bloques de texto codificados y descartando elementos gráficos binarios para optimizar memoria.
- **Archivos `.docx`:** Se utiliza `docx.Document` para recorrer la colección de párrafos y tablas internas, garantizando que el texto en celdas de contratos o facturas no se pierda.
- **Archivos `.txt`:** Se procesa con detección de codificación universal (UTF-8 con fallback a Latin-1) para soportar tildes, caracteres especiales del castellano y saltos de línea.

### 3.2 Motor de Inteligencia Artificial (`ai_engine.py`)
El motor de IA resuelve tres tareas centrales:
1. **Clasificación en 4 Categorías Corporativas:**
   - `LEGAL_CONTRACTS` (Contratos, acuerdos de confidencialidad, convenios, minutas).
   - `FINANCE_INVOICES` (Facturas electrónicas, cuentas de cobro, comprobantes fiscales).
   - `HR_PROFILES` (Hojas de vida, currículums vitae, perfiles de competencias).
   - `TECH_REPORTS` (Informes de proyectos, especificaciones de arquitectura, manuales técnicos).
   *Mecanismo de Inferencia:* Análisis semántico y frecuencias de vocabulario especializado (*terminología legal, balances fiscales, roles laborales*) con ponderación bayesiana o llamada a Google Gemini API para obtener la categoría y su índice de confianza (0.0 a 1.0).
2. **Generación de Resumen Ejecutivo:**
   - Extracción de oraciones núcleo y síntesis en formato estructurado (Contexto, Puntos Clave, Obligaciones o Conclusiones).
3. **Extracción Estructurada de Entidades Clave (JSON):**
   - Para Facturas: `{"numero_factura": "...", "emisor": "...", "cliente": "...", "fecha": "...", "subtotal": "...", "iva": "...", "total": "..."}`
   - Para Contratos: `{"partes": ["...", "..."], "objeto": "...", "valor": "...", "vigencia": "...", "jurisdiccion": "..."}`
   - Para Hojas de Vida: `{"candidato": "...", "profesion": "...", "experiencia_anos": "...", "habilidades": ["...", "..."]}`

---

## 4. Implementación del Motor RAG y Búsqueda Semántica (`vector_store.py`)

1. **Chunking Estratégico:**  
   El texto extraído se divide en fragmentos continuos de 1.000 caracteres con un solapamiento (*overlap*) de 200 caracteres. Esto previene que una cláusula o valor importante quede cortado entre dos fragmentos.
2. **Representación Vectorial:**  
   Se genera un vector numérico de alta dimensionalidad para cada fragmento, capturando la semántica del texto mediante embeddings.
3. **Búsqueda por Similitud Coseno:**  
   Cuando el usuario formula una pregunta en el chat, esta se convierte en un vector de consulta y se calcula la similitud coseno contra todos los fragmentos del repositorio:
   $$\text{Similitud}(u, v) = \frac{u \cdot v}{\|u\| \|v\|}$$
4. **Respuesta Aumentada con Citas:**  
   Los $K$ fragmentos con mayor puntuación (Top-3 / Top-5) se inyectan en el prompt del LLM como contexto factual estricto, ordenándole generar la respuesta citando el archivo de origen y absteniéndose de alucinar información.

---

## 5. Gestión de Errores, Logs y Seguridad
- **Manejo Centralizado de Excepciones:** Los endpoints de FastAPI capturan excepciones no controladas y devuelven respuestas JSON estandarizadas (`{"detail": "Mensaje legible"}`).
- **Tabla de Auditoría:** Cada acción (carga, fallo de extracción, consulta RAG) se registra en la tabla `audit_logs` con fecha, usuario y mensaje de error si aplica.
- **Variables de Entorno:** Configurables en archivo `.env` para `SECRET_KEY`, `GEMINI_API_KEY` y rutas de almacenamiento físico, asegurando que ninguna clave quede quemada en el código.
