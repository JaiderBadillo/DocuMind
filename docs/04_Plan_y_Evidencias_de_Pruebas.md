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

## 6. Repositorio Documental para las Pruebas (Dataset de 30 Documentos)

En cumplimiento estricto del **Punto 7 de los Términos de Referencia del Proyecto Integrador**, el equipo diseñó y preparó un conjunto de **30 documentos de prueba**, organizados en 3 categorías temáticas y distribuidos equilibradamente entre los tres formatos requeridos (`.pdf`, `.docx`, `.txt`).

### 6.1 Política de Protección de Datos Personales (Datos Sintéticos)
> [!IMPORTANT]
> En observancia de la **Ley 1581 de 2012** (Régimen General de Protección de Datos Personales en Colombia) y las directrices docentes, **NO se utilizaron datos personales ni corporativos reales**. Todos los nombres de empresas (ej. *Servicios Cloud Andina S.A.S.*, *Innovatech Solutions Ltda.*), personas (ej. *Carlos Mendoza*, *Laura Gómez*), números de identificación tributaria (NIT) y cuentas bancarias son **100% ficticios y sintéticos**, concebidos exclusivamente para validación algorítmica y pruebas funcionales.

### 6.2 Distribución del Conjunto de Pruebas (30 Archivos)

| # | Categoría / Repositorio | Nombre del Documento | Formato | Tamaño Aprox. | Propósito de Prueba / Contenido Evaluado |
|---|---|---|---|---|---|
| 1 | **Contratos y Legal** | `Contrato_01_Prestacion_Servicios_Software.pdf` | PDF | 2.1 KB | Objeto contractual, valor pactado, entregables y cláusula de confidencialidad. |
| 2 | **Contratos y Legal** | `Contrato_02_Arrendamiento_Oficinas_Comerciales.docx` | DOCX | 36.9 KB | Arrendador/arrendatario, canon mensual, incremento IPC y penalidad por mora. |
| 3 | **Contratos y Legal** | `Contrato_03_Acuerdo_Confidencialidad_NDA.txt` | TXT | 455 B | Definición de información reservada, vigencia de 5 años y jurisdicción. |
| 4 | **Contratos y Legal** | `Contrato_04_Mantenimiento_Servidores_Cloud.pdf` | PDF | 1.8 KB | Acuerdos de nivel de servicio (SLA 99.9%), horarios de soporte y penalizaciones. |
| 5 | **Contratos y Legal** | `Contrato_05_Cesion_Derechos_Patrimoniales.docx` | DOCX | 36.8 KB | Cesión de código fuente, exclusividad y remuneración económica pactada. |
| 6 | **Contratos y Legal** | `Contrato_06_Licenciamiento_Software_ERP.txt` | TXT | 299 B | Número de licencias concurrentes, restricciones de uso e ingeniería inversa. |
| 7 | **Contratos y Legal** | `Contrato_07_Suministro_Equipos_Computo.pdf` | PDF | 1.7 KB | Cantidades de hardware (laptops, servidores), tiempos de entrega y garantía. |
| 8 | **Contratos y Legal** | `Contrato_08_Seguro_Responsabilidad_Civil.docx` | DOCX | 36.8 KB | Póliza de cumplimiento contractual, deducibles y cobertura en COP. |
| 9 | **Contratos y Legal** | `Contrato_09_Prestacion_Servicios_Auditoria.txt` | TXT | 287 B | Alcance de auditoría de seguridad informática y fechas de informes. |
| 10 | **Contratos y Legal** | `Contrato_10_Convenio_Pasantia_Empresarial.pdf` | PDF | 1.8 KB | Modalidad de práctica empresarial, tutor institucional y subsidio de transporte. |
| 11 | **Facturas y Finanzas** | `Factura_01_Servicios_Cloud_AWS.pdf` | PDF | 1.9 KB | Consumo de computación en la nube, subtotal, IVA 19% y total facturado. |
| 12 | **Facturas y Finanzas** | `Factura_02_Licencias_Office365.docx` | DOCX | 36.8 KB | Suscripción empresarial anual, desglose por usuario y fecha de vencimiento. |
| 13 | **Facturas y Finanzas** | `Factura_03_Consultoria_Seguridad_Informatica.txt` | TXT | 328 B | Horas de consultoría de pentesting, tarifa por hora y retención en la fuente. |
| 14 | **Facturas y Finanzas** | `Factura_04_Equipos_Red_Cisco.pdf` | PDF | 1.8 KB | Routers y switches empresariales, número de serie y valor total en USD/COP. |
| 15 | **Facturas y Finanzas** | `Factura_05_Servicios_Fibra_Optica.docx` | DOCX | 36.8 KB | Ancho de banda dedicado 500 Mbps, mensualidad recurrente e impuestos. |
| 16 | **Facturas y Finanzas** | `Factura_06_Capacitacion_Inteligencia_Artificial.txt` | TXT | 281 B | Taller corporativo de LLMs y RAG, cantidad de participantes y costo. |
| 17 | **Facturas y Finanzas** | `Factura_07_Renovacion_Dominios_SSL.pdf` | PDF | 1.7 KB | Certificados Wildcard SSL, dominio corporativo y periodo de vigencia. |
| 18 | **Facturas y Finanzas** | `Factura_08_Mantenimiento_Aire_Acondicionado.docx` | DOCX | 36.8 KB | Limpieza y recarga en datacenter, insumos y firma de recibido a satisfacción. |
| 19 | **Facturas y Finanzas** | `Factura_09_Adquisicion_Monitores_Dell.txt` | TXT | 276 B | Monitores UltraSharp 27 pulgadas, cantidad 15 unidades y descuento comercial. |
| 20 | **Facturas y Finanzas** | `Factura_10_Soporte_Base_Datos_Oracle.pdf` | PDF | 1.7 KB | Mantenimiento preventivo de motor de base de datos y optimización de índices. |
| 21 | **Talento Humano e Informes** | `CV_01_Ingeniero_Software_FullStack.pdf` | PDF | 2.0 KB | Perfil técnico, experiencia en FastAPI/React, formación y competencias. |
| 22 | **Talento Humano e Informes** | `CV_02_Cientifico_Datos_NLP.docx` | DOCX | 36.9 KB | Especialización en modelos de lenguaje, PyTorch, LangChain y publicaciones. |
| 23 | **Talento Humano e Informes** | `CV_03_Administrador_Bases_Datos_DBA.txt` | TXT | 369 B | Gestión de PostgreSQL, replicación, tuning de rendimiento y certificaciones. |
| 24 | **Talento Humano e Informes** | `CV_04_Disenador_UI_UX_Figma.pdf` | PDF | 1.8 KB | Diseño de sistemas de diseño corporativos, wireframes y usabilidad web. |
| 25 | **Talento Humano e Informes** | `CV_05_Ingeniero_DevOps_Cloud.docx` | DOCX | 36.8 KB | Automatización CI/CD, Kubernetes, Docker, Terraform y monitoreo Prometheus. |
| 26 | **Talento Humano e Informes** | `Informe_06_Arquitectura_Seguridad_ZeroTrust.txt` | TXT | 424 B | Diagnóstico de vulnerabilidades de red y recomendaciones de autenticación MFA. |
| 27 | **Talento Humano e Informes** | `Informe_07_Pruebas_Rendimiento_FastAPI.pdf` | PDF | 1.7 KB | Tiempos de respuesta p95, pruebas de carga con Locust y uso de CPU/RAM. |
| 28 | **Talento Humano e Informes** | `Informe_08_Migracion_Base_Datos_Vectorial.docx` | DOCX | 36.8 KB | Evaluación comparativa de embeddings, tiempos de indexación y precisión de búsqueda. |
| 29 | **Talento Humano e Informes** | `Informe_09_Auditoria_Normativa_ISO27001.txt` | TXT | 303 B | Lista de chequeo de controles de seguridad de la información y hallazgos. |
| 30 | **Talento Humano e Informes** | `Informe_10_Estrategia_Continuidad_Negocio_BCP.pdf` | PDF | 1.7 KB | Plan de recuperación ante desastres (DRP), RTO de 2 horas y RPO de 15 minutos. |

### 6.3 Resumen de Cobertura por Formatos y Categorías
* **Total de Documentos:** 30
* **Distribución por Categorías:**
  * ⚖️ *Contratos y Legal:* 10 documentos (33.3%)
  * 💰 *Facturas y Finanzas:* 10 documentos (33.3%)
  * 👥 *Talento Humano e Informes Técnicos:* 10 documentos (33.3%)
* **Distribución por Formato de Archivo:**
  * 📄 **PDF (`.pdf`):** 12 documentos (40.0%)
  * 📝 **Word (`.docx`):** 10 documentos (33.3%)
  * 📋 **Texto Plano (`.txt`):** 8 documentos (26.7%)
* **Ubicación Física en el Repositorio:** Carpeta raíz `/test_dataset_30_docs/` organizada en subcarpetas `contratos_legal/`, `facturas_finanzas/` y `talento_humano_informes/`.

---

## 7. Conclusiones de la Fase de Pruebas
1. Se alcanzó un **100% de aprobación** en los 12 casos de prueba ejecutados.
2. El sistema demostró resiliencia total frente a errores de formato o archivos vacíos, registrando el evento en auditoría sin interrumpir el servicio.
3. La arquitectura dual de IA garantizó que tanto con API externa (Google Gemini) como con motor heurístico local, las respuestas y clasificaciones se completen dentro de los tiempos estipulados (< 5 segundos).
4. El conjunto de 30 documentos de prueba demostró la capacidad de DocuMind Enterprise para procesar colecciones empresariales heterogéneas con cero fallos de lectura y alta fidelidad en extracción de entidades y respuestas RAG.
