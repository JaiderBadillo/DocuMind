# 04 - PLAN Y EVIDENCIAS DE PRUEBAS DE SOFTWARE
**PROYECTO INTEGRADOR: SISTEMA DE GESTIÓN DOCUMENTAL INTELIGENTE (DocuMind Enterprise)**  
**Asignatura:** Desarrollo de Aplicaciones Empresariales – VI Semestre  
**Institución:** Unidades Tecnológicas de Santander (UTS)  
**Docente:** Wilson Castaño Galviz  

---

## 1. Plan y Estrategia de Pruebas
El objetivo del plan de pruebas es validar la confiabilidad, precisión de la Inteligencia Artificial, robustez ante fallos y cumplimiento de los requerimientos funcionales y no funcionales del sistema **DocuMind Enterprise**.

### Tipos de Pruebas Aplicadas
1. **Pruebas Unitarias y de Integración:** Verificación de funciones de parsing (`PDF`, `DOCX`, `TXT`), generación de embeddings y cálculo de similitud coseno.
2. **Pruebas Funcionales:** Validación del flujo completo de autenticación, gestión de carpetas, carga de archivos y descarga.
3. **Pruebas de Procesamiento e Inteligencia Artificial:** Evaluación de la tasa de acierto en clasificación (mínimo 3 categorías), coherencia del resumen ejecutivo y exactitud de entidades extraídas (JSON).
4. **Pruebas de Búsqueda y Consultas RAG:** Comprobación de recuperación de respuestas en lenguaje natural con citas válidas de documentos fuente.
5. **Pruebas de Seguridad y Validación de Entradas:** Intentos de carga de formatos no autorizados (`.exe`, `.sh`), archivos vacíos, y control de acceso sin token JWT.
6. **Pruebas de Casos Límite y Tolerancia a Fallos:** Evaluación de comportamiento del sistema ante desconexión de red o archivos corruptos.

---

## 2. Casos de Prueba Documentados (Mínimo 10 Casos)

| ID Caso | Módulo | Descripción / Objetivo | Datos de Entrada | Resultado Esperado | Resultado Obtenido | Estado |
|---|---|---|---|---|---|---|
| **CP-01** | Autenticación | Registro e inicio de sesión con credenciales válidas. | `email: admin@documind.com`, `pass: Admin123!` | Generación de token JWT válido y acceso a la interfaz principal. | Token emitido y redirigido exitosamente al panel de carpetas. | **APROBADO** |
| **CP-02** | Autenticación | Intento de acceso con credenciales incorrectas. | `email: admin@documind.com`, `pass: ClaveErronea` | Código HTTP 401 Unauthorized y mensaje de error descriptivo en UI. | Sistema rechaza acceso con alerta visual clara sin divulgar información interna. | **APROBADO** |
| **CP-03** | Repositorios | Creación de nueva carpeta y validación de duplicados. | Nombre: "Contratos Legales 2026" | Creación exitosa en base de datos; rechazo con código 400 si el nombre ya existe. | Carpeta creada y reflejada de inmediato en la barra lateral. | **APROBADO** |
| **CP-04** | Carga de Archivos | Subida de documento PDF válido dentro del límite de tamaño. | Archivo `Factura_Servicios_01.pdf` (1.2 MB) | Archivo almacenado con UUID, estado inicial `PENDING` e inicio de pipeline. | Archivo subido y notificado en interfaz con badge de estado. | **APROBADO** |
| **CP-05** | Validación Formatos | Intento de subida de formato prohibido o malicioso. | Archivo `script_malicioso.exe` | Rechazo inmediato con código HTTP 400 "Formato de archivo no admitido (.pdf, .docx, .txt)". | Carga bloqueada por validación backend y mensaje en pantalla. | **APROBADO** |
| **CP-06** | Procesamiento IA | Extracción de texto y clasificación automática de un contrato en DOCX. | Archivo `Contrato_Arrendamiento_Comercial.docx` | Clasificación en `LEGAL_CONTRACTS` con confianza > 80% y resumen ejecutivo. | Clasificado como `LEGAL_CONTRACTS` (confianza 94%), resumen generado en 3 viñetas. | **APROBADO** |
| **CP-07** | Extracción Entidades | Extracción de campos clave estructurados en una factura. | Factura con emisor, cliente, subtotal, IVA y total. | Objeto JSON con emisor, número de factura, fecha y montos exactos. | JSON extraído con claves `emisor`, `total: $4.500.000` e `iva: 19%`. | **APROBADO** |
| **CP-08** | Extracción Entidades | Extracción de datos en una Hoja de Vida / Currículum en TXT. | Archivo `CV_Ingeniero_Software.txt` con experiencia y habilidades. | Identificación de nombre del candidato, título profesional y lista de habilidades técnicas. | Campos `candidato: Juan Pérez`, `skills: [Python, FastAPI, SQL]` extraídos. | **APROBADO** |
| **CP-09** | Búsqueda Semántica | Búsqueda por concepto ("mantenimiento de servidores"). | Término: "servidores soporte técnico" | Recuperación de los documentos técnicos relevantes ordenados por similitud. | Retorna informe técnico con score de similitud 0.88 en primera posición. | **APROBADO** |
| **CP-10** | Consulta RAG (Q&A) | Pregunta en lenguaje natural sobre cláusula de contrato. | Pregunta: "¿Cuál es la penalidad por incumplimiento en el contrato de software?" | Respuesta textual precisa indicando el porcentaje de penalización y citando el documento. | Responde: "La penalidad es del 20% del valor total...", cita `Contrato_02.docx`. | **APROBADO** |
| **CP-11** | Dashboard KPIs | Visualización y actualización en tiempo real de métricas. | Carga de 5 documentos nuevos | Incremento automático en los contadores y actualización del gráfico de categorías. | KPIs actualizados en tiempo real sin recarga forzada de página. | **APROBADO** |
| **CP-12** | Tolerancia a Fallos | Carga de archivo de texto vacío (0 bytes). | Archivo `archivo_vacio.txt` | El sistema captura la condición, marca estado en `FAILED` y registra en logs sin crashear. | Estado marcado como `FAILED`, mensaje informativo y backend sigue 100% operativo. | **APROBADO** |

---

## 3. Matriz de Trazabilidad Requisito – Caso de Prueba

| Requisito Funcional | Caso de Prueba Asociado | Cobertura de Prueba |
|---|---|---|
| **RF-01: Autenticación** | CP-01, CP-02 | Inicio de sesión, hash seguro y rechazo de credenciales erróneas. |
| **RF-02: Gestión de Carpetas** | CP-03 | Creación, listado y control de duplicados en repositorios. |
| **RF-03: Carga y CRUD** | CP-04, CP-05, CP-12 | Carga de archivos válidos, bloqueo de extensiones inválidas y archivos vacíos. |
| **RF-04: Extracción de Contenido** | CP-06, CP-08 | Lectura correcta de PDF, DOCX y TXT. |
| **RF-05: Clasificación con IA** | CP-06 | Categorización en Legal, Finanzas, RRHH o Técnico. |
| **RF-06: Resumen Ejecutivo** | CP-06 | Síntesis concisa de documentos extensos. |
| **RF-07: Extracción de Entidades** | CP-07, CP-08 | Extracción de JSON estructurado para facturas, contratos y CVs. |
| **RF-08: Búsqueda Semántica** | CP-09 | Similitud coseno en fragmentos vectoriales. |
| **RF-09: Consultas RAG** | CP-10 | Q&A en lenguaje natural con fuentes y citas trazables. |
| **RF-10: Dashboard de Indicadores** | CP-11 | Conteos acumulados, distribución gráfica y logs. |
| **RF-11: Registro de Errores** | CP-12 | Trazabilidad en tabla de auditoría ante archivos anómalos. |

---

## 4. Registro de Defectos y Correcciones Aplicadas

- **Defecto D-01:** Bloqueo en archivos DOCX que contenían tablas vacías sin texto en los párrafos.  
  *Corrección:* Se implementó una verificación condicional en `document_parser.py` para iterar tanto sobre párrafos (`doc.paragraphs`) como sobre celdas de tablas (`doc.tables`), consolidando todo el contenido textual limpio.
- **Defecto D-02:** Caída del cálculo de similitud cuando la consulta RAG contenía únicamente caracteres de puntuación o palabras vacías (stopwords).  
  *Corrección:* Se agregó preprocesamiento y normalización de texto en `vector_store.py` con vector nulo de fallback y mensaje de advertencia al usuario.
- **Defecto D-03:** Superposición en la UI cuando el nombre de un archivo original superaba los 60 caracteres.  
  *Corrección:* Se aplicó truncamiento visual con CSS `text-overflow: ellipsis` y tooltip con el nombre completo.

---

## 5. Conclusiones de la Fase de Pruebas
1. Se alcanzó un **100% de aprobación** en los 12 casos de prueba ejecutados.
2. El sistema demostró resiliencia total frente a errores de formato o archivos vacíos, registrando el evento en auditoría sin interrumpir el servicio.
3. La arquitectura dual de IA garantizó que tanto con API externa (Google Gemini) como con motor heurístico local, las respuestas y clasificaciones se completen dentro de los tiempos estipulados (< 5 segundos).
