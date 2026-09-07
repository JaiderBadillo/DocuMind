# 08 - MATRIZ DE TRAZABILIDAD DE REQUISITOS, FUNCIONALIDADES Y PRUEBAS
**PROYECTO INTEGRADOR: SISTEMA DE GESTIÓN DOCUMENTAL INTELIGENTE (DocuMind Enterprise)**  
**Asignatura:** Desarrollo de Aplicaciones Empresariales – VI Semestre  
**Institución:** Unidades Tecnológicas de Santander (UTS)  
**Docente:** Wilson Castaño Galviz  

---

## 1. Propósito de la Matriz de Trazabilidad
Esta matriz garantiza la correspondencia biunívoca y trazabilidad completa entre las necesidades del negocio, los requerimientos formales de ingeniería de software, los componentes de arquitectura, los archivos de código fuente implementados y los casos de prueba ejecutados.

---

## 2. Matriz Integral de Trazabilidad de Software

| ID Req. | Descripción del Requerimiento | Módulo / Componente de Diseño | Archivo de Código Fuente | Endpoint API / Interfaz | Caso de Prueba | Estado de Verificación |
|---|---|---|---|---|---|---|
| **RF-01** | Autenticación y Autorización con JWT | Capa de Seguridad y Criptografía | `backend/app/core/security.py`<br>`backend/app/api/auth_routes.py` | `POST /api/auth/register`<br>`POST /api/auth/login` | CP-01<br>CP-02 | **VALIDADO (100%)** |
| **RF-02** | Creación y administración de repositorios/carpetas | Gestor de Repositorios Relacional | `backend/app/api/repository_routes.py`<br>`frontend/js/app.js` | `GET /api/repositories`<br>`POST /api/repositories` | CP-03 | **VALIDADO (100%)** |
| **RF-03** | Carga, descarga, visualización y borrado de archivos | Gestor de Archivos y Storage | `backend/app/api/document_routes.py`<br>`frontend/js/components.js` | `POST /api/documents/upload`<br>`DELETE /api/documents/{id}` | CP-04<br>CP-05 | **VALIDADO (100%)** |
| **RF-04** | Extracción automática de contenido (PDF, DOCX, TXT) | Pipeline de Procesamiento Documental | `backend/app/services/document_parser.py` | Invocación interna en Background Task | CP-06<br>CP-08 | **VALIDADO (100%)** |
| **RF-05** | Clasificación automática en mínimo 3 categorías con IA | Motor de Inferencia y NLP | `backend/app/services/ai_engine.py` | Invocación en pipeline de IA | CP-06 | **VALIDADO (100%)** |
| **RF-06** | Generación de resumen ejecutivo por documento | Generador de Resúmenes Estructurados | `backend/app/services/ai_engine.py` | Campo `executive_summary` en visor | CP-06 | **VALIDADO (100%)** |
| **RF-07** | Extracción estructurada de información clave (3+ tipos) | Extractor de Entidades JSON | `backend/app/services/ai_engine.py`<br>`backend/app/models/schemas.py` | Campo `extracted_entities_json` | CP-07<br>CP-08 | **VALIDADO (100%)** |
| **RF-08** | Búsqueda dentro del contenido documental | Buscador Semántico e Índice Vectorial | `backend/app/services/vector_store.py`<br>`backend/app/api/search_routes.py` | `GET /api/search?q={term}` | CP-09 | **VALIDADO (100%)** |
| **RF-09** | Consultas en lenguaje natural con citas de fuentes (RAG) | Motor Conversacional RAG | `backend/app/services/vector_store.py`<br>`backend/app/api/search_routes.py` | `POST /api/rag/chat`<br>`frontend/js/app.js` | CP-10 | **VALIDADO (100%)** |
| **RF-10** | Dashboard con indicadores del repositorio | Agregador Analítico y KPIs | `backend/app/api/dashboard_routes.py`<br>`frontend/js/components.js` | `GET /api/dashboard/stats`<br>`GET /api/dashboard/logs` | CP-11 | **VALIDADO (100%)** |
| **RF-11** | Registro de estados de procesamiento y auditoría | Subordinador de Tareas y Auditoría | `backend/app/core/database.py`<br>`backend/app/api/dashboard_routes.py` | Tabla `audit_logs`<br>Campo `processing_status` | CP-12 | **VALIDADO (100%)** |
| **RF-12** | Resiliencia y soporte offline / Fallback IA | Inferencia Dual de IA | `backend/app/services/ai_engine.py` | Detección automática de conectividad | CP-06<br>CP-10 | **VALIDADO (100%)** |

---

## 3. Conclusión de Cumplimiento de Requisitos
La totalidad de los doce (12) requerimientos funcionales y seis (6) requerimientos no funcionales especificados en la fase de análisis se encuentran codificados, cubiertos por casos de prueba verificables y asociados a componentes auditables de la arquitectura de software.
