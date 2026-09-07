# 01 - DOCUMENTO DE ANÁLISIS DE REQUISITOS DE SOFTWARE
**PROYECTO INTEGRADOR: SISTEMA DE GESTIÓN DOCUMENTAL INTELIGENTE (DocuMind Enterprise)**  
**Asignatura:** Desarrollo de Aplicaciones Empresariales – VI Semestre  
**Institución:** Unidades Tecnológicas de Santander (UTS)  
**Docente:** Wilson Castaño Galviz  

---

## 1. Descripción del Problema y Contexto Empresarial
En el entorno empresarial contemporáneo, las organizaciones acumulan volúmenes exponenciales de información no estructurada en repositorios locales, servidores compartidos y servicios de almacenamiento en la nube. Esta información se encuentra dispersa en formatos heterogéneos como contratos (`.docx`), facturas de compras y servicios (`.pdf`), actas de reunión y notas de trabajo (`.txt`).

La problemática central radica en que este almacenamiento opera de forma **pasiva**:
1. **Pérdida de tiempo operativo:** El personal administrativo y operativo invierte hasta un 25% de su jornada laboral buscando cláusulas contractuales específicas, fechas de vencimiento de facturas o perfiles técnicos de colaboradores.
2. **Incapacidad de análisis a escala:** Los motores de búsqueda convencionales se limitan a coincidencias exactas por nombre de archivo o cadenas de texto superficiales, ignorando el contexto semántico y el significado de los documentos.
3. **Falta de gobernanza documental:** No existe un proceso automatizado que clasifique los documentos entrantes, genere resúmenes ejecutivos ni extraiga datos clave para la toma de decisiones.

## 2. Identificación de la Necesidad y Oportunidad de Negocio
Existe una oportunidad crítica de negocio para transformar ese "almacén muerto" en una **Base de Conocimiento Inteligente Corporativa**, permitiendo:
- Reducción drástica del tiempo de consulta documental mediante procesamiento de lenguaje natural (NLP) y búsqueda semántica (RAG).
- Catalogación y categorización autónoma sin intervención humana propensa a errores.
- Extracción estructurada de entidades (montos, partes legales, fechas de vencimiento, perfiles profesionales) para alimentar dashboards de inteligencia de negocios.
- Mayor cumplimiento legal y agilidad en auditorías contables y jurídicas.

## 3. Objetivos del Proyecto

### 3.1 Objetivo General
Diseñar, desarrollar, probar, documentar e implementar una solución web empresarial que gestione repositorios de documentos y aplique Inteligencia Artificial (procesamiento de lenguaje natural, clasificación, extracción y RAG) para transformar la información no estructurada en conocimiento útil, estructurado y consultable para la organización.

### 3.2 Objetivos Específicos
1. Desarrollar un módulo de gestión documental que permita autenticar usuarios, crear jerarquías de carpetas y administrar el ciclo de vida de archivos (`.pdf`, `.docx`, `.txt`).
2. Diseñar un pipeline de extracción y procesamiento de texto que normalice y segmente el contenido documental para su ingestión por modelos de lenguaje.
3. Implementar algoritmos de Inteligencia Artificial para la clasificación automática en al menos tres categorías corporativas, generación de resúmenes ejecutivos y extracción de entidades críticas.
4. Construir un motor de búsqueda semántica y un asistente conversacional basado en la arquitectura RAG (*Retrieval-Augmented Generation*) capaz de responder preguntas en lenguaje natural citando las fuentes documentales.
5. Desarrollar un dashboard analítico con indicadores en tiempo real sobre el volumen documental, categorías y estados de procesamiento del repositorio.
6. Aplicar el ciclo de vida completo de ingeniería de software con rigor metodológico, pruebas exhaustivas y despliegue automatizado.

## 4. Alcance y Exclusiones

### 4.1 Alcance del Sistema
- Plataforma web corporativa cliente-servidor responsiva.
- Soporte para extracción de texto en archivos PDF, Word (DOCX) y Texto Plano (TXT).
- Clasificación automatizada en 4 categorías:
  1. *Contratos y Asuntos Legales*
  2. *Facturas, Comprobantes y Finanzas*
  3. *Talento Humano y Perfiles Laborales*
  4. *Informes Técnicos y Operativos*
- Extracción de entidades estructuradas para facturas (montos, emisor, fecha, IVA), contratos (partes, cuantía, fechas de vigencia) y perfiles (nombre, experiencia, habilidades).
- Búsqueda híbrida (búsqueda léxica y búsqueda semántica vectorial).
- Asistente de preguntas y respuestas en lenguaje natural (RAG) con trazabilidad de páginas/fuentes.
- Dashboard de métricas y registro de auditoría de errores y transacciones.

### 4.2 Exclusiones
- Procesamiento de archivos de audio, video o diseño gráfico (DWG, CAD).
- Integración directa con sistemas ERP propietarios (SAP, Oracle) mediante conectores certificados (se proveen APIs abiertas estandarizadas).
- Reconocimiento óptico de caracteres (OCR) para manuscritos ilegibles o imágenes de bajísima resolución (el sistema procesa PDFs digitales y texto extraíble).

---

## 5. Identificación de Actores y Usuarios

| Actor | Descripción | Responsabilidades |
|---|---|---|
| **Administrador del Sistema** | Usuario con permisos totales de gestión y monitoreo. | Gestionar usuarios, ver métricas globales, consultar logs de auditoría, reintentar procesamientos fallidos. |
| **Gestor Documental / Analista** | Usuario operativo de áreas como Finanzas, Legal o RRHH. | Crear carpetas, cargar documentos masivos, visualizar análisis de IA, exportar resúmenes. |
| **Consultor / Auditor** | Usuario con permisos de consulta y lectura. | Realizar búsquedas semánticas, chatear con los documentos (RAG) y verificar citas de fuentes. |

### Perfiles de Usuario (User Personas)
- **Persona 1: Lic. Valeria Mendoza (Directora Jurídica)**  
  *Necesidad:* Necesita revisar rápidamente contratos de 30 páginas para saber qué contrapartes tienen cláusulas de penalización y cuáles son las fechas límite de renovación, sin tener que leerlos línea por línea.
- **Persona 2: Carlos Ortiz (Coordinador Contable)**  
  *Necesidad:* Recibe cientos de facturas en PDF mensualmente y requiere saber el total facturado por proveedor y si los comprobantes cuentan con el desglose del impuesto al valor agregado.
- **Persona 3: Diana Gómez (Líder de Talento Humano)**  
  *Necesidad:* Requiere filtrar decenas de currículums en formato DOCX y TXT buscando competencias específicas en desarrollo de software y años de experiencia.

---

## 6. Requerimientos del Sistema

### 6.1 Requerimientos Funcionales (RF)

| ID | Nombre | Descripción | Prioridad |
|---|---|---|---|
| **RF-01** | Autenticación y Autorización | El sistema debe permitir el registro e inicio de sesión de usuarios mediante credenciales seguras y generación de tokens JWT. | Alta |
| **RF-02** | Gestión de Repositorios / Carpetas | El sistema debe permitir crear, listar, renombrar y eliminar carpetas para organizar los documentos. | Alta |
| **RF-03** | Carga y CRUD de Documentos | El usuario debe poder cargar archivos en formatos `.pdf`, `.docx` y `.txt`, visualizarlos, descargarlos y eliminarlos. | Alta |
| **RF-04** | Extracción Automática de Contenido | El sistema debe extraer automáticamente el texto crudo estructurado de cualquier archivo PDF, DOCX o TXT admitido. | Alta |
| **RF-05** | Clasificación Automática con IA | El sistema debe clasificar el documento en una de al menos tres categorías (Legal, Finanzas, RRHH, Técnico) con un índice de confianza. | Alta |
| **RF-06** | Generación de Resumen Ejecutivo | El motor de IA debe generar una síntesis ejecutiva del documento destacando los puntos más importantes en viñetas. | Alta |
| **RF-07** | Extracción de Entidades Clave | El sistema debe extraer campos específicos en formato JSON estructurado según el tipo de documento (factura, contrato o currículum). | Alta |
| **RF-08** | Búsqueda Léxica y Semántica | El usuario debe poder realizar búsquedas sobre el contenido de los documentos encontrando términos por significado y similitud. | Alta |
| **RF-09** | Consultas en Lenguaje Natural (RAG) | El sistema debe responder preguntas complejas sobre la base documental usando RAG y citando explícitamente los archivos de soporte. | Alta |
| **RF-10** | Dashboard con Indicadores | Debe existir un panel visual con gráficos de distribución por categoría, formatos, volumen de archivos y estado de procesamiento. | Media |
| **RF-11** | Trazabilidad y Logs de Procesamiento | El sistema debe registrar el estado de cada documento (`PENDIENTE`, `PROCESANDO`, `COMPLETADO`, `ERROR`) y almacenar logs detallados. | Media |
| **RF-12** | Modo Offline / Resiliencia IA | El sistema debe ser capaz de operar con IA en la nube (API Gemini) o en modo heurístico local en caso de desconexión o límite de cuota. | Media |

### 6.2 Requerimientos No Funcionales (RNF)

| ID | Nombre | Especificación |
|---|---|---|
| **RNF-01** | Rendimiento y Latencia | El procesamiento y extracción de documentos menores a 10 MB no debe superar los 5 segundos en modo local y 10 segundos con API de IA externa. |
| **RNF-02** | Seguridad y Cifrado | Las contraseñas deben cifrarse con algoritmos de hash unidireccional con sal (`bcrypt`). Las rutas de API deben estar protegidas por JWT. |
| **RNF-03** | Usabilidad y Accesibilidad | La interfaz web debe ser moderna, intuitiva, con diseño adaptativo (responsive) para escritorio y tableta, con modo oscuro y claro. |
| **RNF-04** | Disponibilidad y Tolerancia a Fallos | Si un archivo está corrupto o protegido por contraseña, el sistema debe capturar la excepción, marcar el estado en `ERROR` y continuar operando sin caerse. |
| **RNF-05** | Modularidad y Mantenibilidad | El código debe separar estrictamente la capa de presentación (frontend), la capa de servicios de API (FastAPI) y los motores de IA/RAG. |
| **RNF-06** | Compatibilidad de Plataforma | La solución debe ser multiplataforma, pudiendo ejecutarse tanto en Windows como en Linux mediante contenedores Docker o entornos virtuales Python. |

---

## 7. Reglas de Negocio (RN)

- **RN-01 (Formatos Permitidos):** Únicamente se admiten archivos con extensiones `.pdf`, `.docx` y `.txt`. Cualquier otro formato debe ser rechazado inmediatamente con código HTTP 400.
- **RN-02 (Límite de Tamaño):** El tamaño máximo permitido por archivo individual es de 25 MB.
- **RN-03 (Unicidad y Versionamiento):** Dos archivos en la misma carpeta no pueden tener el mismo nombre exacto; si se carga uno con idéntico nombre, se debe generar una versión o sufijo de marca temporal.
- **RN-04 (Autonomía de Procesamiento):** Todo archivo cargado debe entrar inmediatamente en la cola de procesamiento en estado `PENDIENTE` y pasar a `PROCESANDO` de forma transparente.
- **RN-05 (Privacidad de Datos):** Las claves de API y credenciales de acceso a modelos externos no deben exponerse al cliente web bajo ninguna circunstancia.

---

## 8. Historias de Usuario (con Criterios de Aceptación Gherkin)

### HU-01: Carga y Procesamiento Inteligente de Contratos
**Como** Analista Legal  
**Quiero** subir un contrato en formato PDF o DOCX al repositorio  
**Para** que la IA lo clasifique automáticamente, me dé un resumen y extraiga las partes y el monto acordado.  
*Criterio de Aceptación:*
- **Dado** que un usuario autenticado está en la vista de su carpeta "Contratos 2026",
- **Cuando** arrastra y suelta el archivo `Contrato_Servicios_01.docx`,
- **Entonces** el sistema valida la extensión, extrae el texto, lo clasifica como "Legal / Contratos", genera el resumen en viñetas y extrae los campos `partes`, `cuantía` y `vigencia` en menos de 5 segundos.

### HU-02: Consulta en Lenguaje Natural sobre Facturas
**Como** Coordinador Contable  
**Quiero** hacer una pregunta en el chat como "¿Cuáles facturas tienen retención en la fuente o IVA superior a $500.000?"  
**Para** no tener que abrir cada archivo PDF manualmente.  
*Criterio de Aceptación:*
- **Dado** que existen 10 facturas procesadas en el sistema,
- **Cuando** el usuario ingresa la pregunta en la caja de chat RAG,
- **Entonces** el sistema busca los fragmentos semánticos más relevantes, genera una respuesta clara y concisa, y muestra una tarjeta con el enlace al archivo y párrafo correspondiente.

### HU-03: Dashboard de Control y Diagnóstico del Repositorio
**Como** Administrador del Sistema  
**Quiero** ver una pantalla con indicadores gráficos del repositorio  
**Para** conocer la salud del sistema, porcentaje de documentos por categoría y estado de las tareas de IA.  
*Criterio de Aceptación:*
- **Dado** que el usuario tiene permisos administrativos,
- **Cuando** accede a la sección de Dashboard,
- **Entonces** visualiza tarjetas con el total de archivos, gráficos de pastel por categoría, gráfico de barras por formato (`PDF`, `DOCX`, `TXT`) y una tabla con los últimos logs de procesamiento.

---

## 9. Casos de Uso del Sistema

```
                        +--------------------------------+
                        |     DocuMind Enterprise        |
                        +--------------------------------+
                                        |
       +--------------------------------+-------------------------------+
       |                                |                               |
[Iniciar Sesión / Registro]   [Administrar Carpetas]         [Cargar / Eliminar Docs]
       |                                |                               |
       +--------------------------------+-------------------------------+
                                        |
       +--------------------------------+-------------------------------+
       |                                |                               |
[Procesar Documento con IA]    [Buscar Semánticamente]         [Consultar Chat RAG]
       |                                |                               |
       +--------------------------------+-------------------------------+
                                        |
                               [Visualizar Dashboard]
```

### Especificación Caso de Uso Principal: CU-04 Procesamiento IA y Extracción
1. **Actor:** Gestor Documental / Sistema Background Worker.
2. **Precondición:** Archivo subido con éxito y almacenado en disco/servidor.
3. **Flujo Principal:**
   1. El sistema lee el archivo según su formato (`pypdf` para PDF, `python-docx` para DOCX, I/O para TXT).
   2. El sistema extrae el texto crudo y limpia caracteres anómalos.
   3. El sistema divide el texto en fragmentos (*chunks*) de 1.000 caracteres con solapamiento de 200.
   4. Se generan los vectores de embedding para cada fragmento.
   5. Se envía el texto completo o extracto principal al modelo de clasificación y resumen.
   6. Se ejecuta el extractor de entidades estructuradas según la categoría identificada.
   7. Se persisten los resultados en la base de datos relacional y se actualiza el estado a `COMPLETADO`.
4. **Flujo Alternativo (Error de lectura):**
   - Si el archivo está dañado o no contiene texto legible, el sistema marca el estado en `ERROR`, registra la traza en la tabla de logs y notifica en la interfaz sin interrumpir la experiencia de usuario.

---

## 10. Matriz de Riesgos del Proyecto

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| **R-01: Límite de cuota o indisponibilidad de API externa de IA** | Media | Alto | Implementación de arquitectura dual: fallback a motor local de clasificación, embeddings y resumen heurístico sin costo. |
| **R-02: Variabilidad en formatos PDF (escaneados vs digitales)** | Media | Medio | Detección previa de texto extraíble y advertencia en caso de requerir OCR suplementario. |
| **R-03: Inyección de archivos maliciosos en la carga** | Baja | Alto | Validación estricta de extensiones permitidas, sanitización de nombres de archivo y aislamiento en directorio de almacenamiento. |
| **R-04: Degradación del rendimiento por documentos muy extensos** | Media | Medio | Segmentación de texto en memoria mediante streaming y límites de lectura de tokens por documento. |
