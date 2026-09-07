# 13 - GUION DE VIDEO (5 MINUTOS) Y ESTRUCTURA DE SUSTENTACIÓN
**PROYECTO INTEGRADOR: SISTEMA DE GESTIÓN DOCUMENTAL INTELIGENTE (DocuMind Enterprise)**  
**Asignatura:** Desarrollo de Aplicaciones Empresariales – VI Semestre  
**Institución:** Unidades Tecnológicas de Santander (UTS)  
**Docente:** Wilson Castaño Galviz  

---

## 1. Guion Técnico para el Video Demostrativo (Duración Máxima: 5:00 min)

| Minutaje | Sección del Video | Acción en Pantalla | Guion / Diálogo Técnico |
|---|---|---|---|
| **00:00 - 00:40** | **Introducción y Reto Empresarial** | Pantalla de inicio de sesión con branding empresarial. | *"Cordial saludo. Presentamos DocuMind Enterprise, una solución que transforma carpetas pasivas de documentos en bases de conocimiento activas usando Inteligencia Artificial. Cumplimos el ciclo de ingeniería de software con arquitectura basada en FastAPI, procesamiento multiformato y RAG."* |
| **00:41 - 01:25** | **Autenticación y Repositorios** | Ingreso con credenciales `admin@documind.com`. Creación de la carpeta "Operaciones y Finanzas 2026". | *"Iniciamos sesión con autenticación JWT y contraseñas cifradas en bcrypt. Creamos un nuevo repositorio donde organizaremos la documentación corporativa con separación lógica."* |
| **01:26 - 02:20** | **Carga y Procesamiento IA en Vivo** | Arrastrar y soltar 3 archivos simultáneos: 1 PDF (Factura), 1 DOCX (Contrato), 1 TXT (Hoja de Vida). Mostrar indicador de procesamiento. | *"Cargamos tres formatos diferentes. En milisegundos, el backend extrae el texto con PyPDF y python-docx, genera chunks y embeddings, e infiere la categoría. Vemos cómo pasa de 'Procesando' a 'Completado' en tiempo real."* |
| **02:21 - 03:15** | **Demostración de Clasificación, Resumen y Extracción** | Clic en el contrato: mostrar panel con categoría 'Legal/Contratos', 3 viñetas de resumen y JSON con partes y valor. Luego clic en la factura para ver total e IVA. | *"Al abrir el documento, no vemos un simple visor: la IA clasificó el contrato con 94% de confianza, generó una síntesis ejecutiva y extrajo en campos estructurados las partes, el objeto y la cuantía contractual."* |
| **03:16 - 04:10** | **Búsqueda Semántica y Chatbot RAG (3 Preguntas)** | Pestaña de Chat. Realizar 3 preguntas consecutivas y mostrar las citas de fuente. | *"Probamos el motor RAG. Pregunta 1: '¿Cuál es el valor del contrato de prestación de servicios?'. El sistema responde con el monto exacto y cita la cláusula. Pregunta 2: '¿Qué candidatos dominan Python y FastAPI?'. Identifica el currículum. Pregunta 3: '¿Cuál es el total de la factura 102?'."* |
| **04:11 - 05:00** | **Dashboard, Métricas y Conclusión** | Vista del Dashboard con gráficos de pastel, barras de formatos y log de auditoría. | *"En el dashboard vemos los KPIs en tiempo real: distribución por categorías, almacenamiento consumido y registro de auditoría. La solución es 100% reproducible, resiliente y lista para producción. Muchas gracias."* |

---

## 2. Diapositivas y Estructura de Sustentación Presencial / Virtual

### Diapositiva 1: Portada
- **Título:** DocuMind Enterprise: Transformación de Repositorios Pasivos en Bases de Conocimiento Inteligentes.
- **Integrantes del Equipo y Programa:** Ingeniería de Sistemas / Desarrollo de Aplicaciones Empresariales – VI Semestre – UTS.
- **Docente:** Wilson Castaño Galviz.

### Diapositiva 2: El Problema Empresarial
- Almacenamiento pasivo: carpetas repletas de PDFs, Word y notas de texto sin indexar.
- 25% del tiempo de los colaboradores desperdiciado en búsquedas manuales.
- Ausencia de resúmenes ejecutivos y extracción de datos para auditorías y finanzas.

### Diapositiva 3: Arquitectura Técnica y Flujo de IA
- **Frontend:** SPA Empresarial responsiva con visualizadores de metadatos y consola RAG.
- **Backend:** Python FastAPI asíncrono con base de datos relacional SQLite y almacenamiento seguro de archivos.
- **Pipeline de IA:** Extracción $\rightarrow$ Chunking con solapamiento $\rightarrow$ Embeddings vectoriales $\rightarrow$ Similitud Coseno $\rightarrow$ Clasificador $\rightarrow$ Extractor de entidades $\rightarrow$ Contexto RAG.
- **Resiliencia:** Compatibilidad dual con Google Gemini API y motor heurístico local offline.

### Diapositiva 4: Demostración en Vivo (Checklist de la Guía de Evaluación)
1. ✅ Demostrar autenticación y control de acceso.
2. ✅ Cargar documentos en formatos PDF, DOCX y TXT.
3. ✅ Mostrar clasificación automática en al menos 3 categorías.
4. ✅ Mostrar generación de resumen por documento.
5. ✅ Mostrar extracción de entidades estructuradas (Contratos, Facturas, Hojas de Vida).
6. ✅ Realizar búsqueda semántica en el contenido.
7. ✅ Formular mínimo tres (3) preguntas en lenguaje natural (RAG) con citas de fuentes.
8. ✅ Mostrar dashboard con indicadores y trazabilidad de logs de error.

### Diapositiva 5: Ciclo de Vida y Pruebas
- 12 Casos de prueba documentados con 100% de aprobación.
- Matriz de trazabilidad extremo a extremo (Problema $\rightarrow$ Requisitos $\rightarrow$ Código $\rightarrow$ Pruebas).
- Despliegue reproducible con un solo comando.
