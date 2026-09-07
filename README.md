# DocuMind Enterprise - Sistema de Gestión Documental Inteligente con IA y RAG

[![UTS](https://img.shields.io/badge/UTS-Ingenier%C3%ADa%20de%20Sistemas-blue.svg)](https://www.uts.edu.co/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/Licencia-Acad%C3%A9mica-orange.svg)](#)

Proyecto Integrador de la asignatura **Desarrollo de Aplicaciones Empresariales – VI Semestre**, orientado por el docente **Wilson Castaño Galviz** en las **Unidades Tecnológicas de Santander (UTS)**.

---

## 🌟 1. Propósito y Reto Empresarial Resuelto
Las empresas suelen acumular miles de archivos heterogéneos (`.pdf`, `.docx`, `.txt`) en carpetas locales o unidades de red. Este almacenamiento opera de manera **pasiva**, ocasionando pérdidas de tiempo de hasta un 25% buscando cláusulas, fechas de vencimiento o montos facturados.

**DocuMind Enterprise** transforma ese repositorio estático en una **Base de Conocimiento Inteligente Corporativa** capaz de:
- Extraer texto íntegro de documentos PDF, Word (DOCX) y Texto Plano (TXT).
- Clasificar autónomamente los archivos en 4 categorías:
  1. *Contratos y Asuntos Legales*
  2. *Facturas, Comprobantes y Finanzas*
  3. *Talento Humano y Perfiles Laborales*
  4. *Informes Técnicos y Operativos*
- Generar un **Resumen Ejecutivo** estructurado en viñetas clave.
- Extraer **Entidades Estructuradas (JSON)**: montos, partes, vigencias, habilidades técnicas, IVA y números de factura.
- Búsqueda semántica vectorial por similitud coseno.
- Asistente conversacional **RAG (Retrieval-Augmented Generation)** que responde preguntas en lenguaje natural **citando exactamente el documento y párrafo fuente**.
- Dashboard en tiempo real con estadísticas del repositorio y logs de auditoría.
- **Resiliencia Total**: Arquitectura dual compatible con Google Gemini API y con un motor neuronal/heurístico local offline (ideal para sustentaciones sin dependencia de cuotas o internet).

---

## 📁 2. Estructura de Entregables Oficiales (Fases I a V)

Toda la documentación técnica exigida se encuentra detallada en la carpeta `docs/`:

| Entregable | Archivo de Documentación | Descripción |
|---|---|---|
| **01 – Análisis** | [`01_Documento_de_Analisis.md`](docs/01_Documento_de_Analisis.md) | Problema, objetivos, RF01-RF12, RNF01-RNF06, reglas de negocio, Historias de Usuario (Gherkin), casos de uso y riesgos. |
| **02 – Diseño** | [`02_Documento_de_Diseno.md`](docs/02_Documento_de_Diseno.md) | Arquitectura C4, modelo Entidad-Relación, diccionario de datos, diagramas de secuencia, API REST y seguridad. |
| **03 – Desarrollo** | [`03_Documento_de_Desarrollo.md`](docs/03_Documento_de_Desarrollo.md) | Memoria técnica, pipeline de IA, chunking, embeddings y estructura de código. |
| **04 – Pruebas** | [`04_Plan_y_Evidencias_de_Pruebas.md`](docs/04_Plan_y_Evidencias_de_Pruebas.md) | 12 casos de prueba documentados, trazabilidad requisito-prueba, tolerancia a fallos y defectos resueltos. |
| **05 – Despliegue** | [`05_Documento_Implementacion_Despliegue.md`](docs/05_Documento_Implementacion_Despliegue.md) | Variables de entorno, instalación paso a paso, Docker, respaldo y mantenimiento. |
| **06 – Manual de Usuario** | [`06_Manual_de_Usuario.md`](docs/06_Manual_de_Usuario.md) | Guía ilustrada de acceso, gestión de carpetas, carga drag-and-drop y chat RAG. |
| **07 – Manual Técnico** | [`07_Manual_Tecnico_Administracion.md`](docs/07_Manual_Tecnico_Administracion.md) | Operación de SQLite, logs de auditoría, gestión de API Keys y recuperación ante desastres. |
| **08 – Trazabilidad** | [`08_Matriz_de_Trazabilidad.md`](docs/08_Matriz_de_Trazabilidad.md) | Matriz biunívoca: Problema $\rightarrow$ Requisitos $\rightarrow$ Código $\rightarrow$ Pruebas. |
| **11 – Dataset 30 Docs** | `test_dataset_30_docs/` | 30 documentos sintéticos (.pdf, .docx, .txt) clasificados en 3 categorías sin datos personales reales. |
| **13 – Sustentación y Video**| [`13_Guion_Sustentacion_y_Video.md`](docs/13_Guion_Sustentacion_y_Video.md) | Guion para video de 5 minutos y diapositivas para la defensa técnica. |

---

## 🚀 3. Instrucciones de Instalación y Ejecución

### Opción A: Ejecución en un Clic (Recomendada para Windows)
Hacer doble clic sobre el archivo ejecutable:
```bat
run_server.bat
```
El script verificará Python, instalará las dependencias, inicializará la base de datos, generará los 30 documentos sintéticos y abrirá el servidor en `http://localhost:8000`.

### Opción B: Ejecución Manual Paso a Paso
1. **Crear entorno virtual (opcional pero recomendado):**
   ```bash
   python -m venv venv
   venv\Scripts\activate   # En Windows
   # source venv/bin/activate # En Linux/Mac
   ```
2. **Instalar dependencias:**
   ```bash
   pip install -r backend/requirements.txt
   ```
3. **Inicializar base de datos:**
   ```bash
   python backend/init_db.py
   ```
4. **Generar los 30 documentos de prueba:**
   ```bash
   python backend/generate_test_docs.py
   ```
5. **Iniciar el servidor FastAPI:**
   ```bash
   python backend/app/main.py
   ```
6. **Abrir en el navegador:**
   👉 **`http://localhost:8000`**

---

## 🔑 4. Credenciales de Acceso por Defecto
- **Correo Electrónico:** `admin@documind.com`
- **Contraseña:** `Admin123!`
*(También disponible mediante el botón "Acceso Rápido Sustentación" en la pantalla de inicio).*

---

## 🧪 5. Demostración para la Sustentación (Checklist)
1. Iniciar sesión con el usuario administrador.
2. Navegar a la carpeta "Contratos y Acuerdos Legales" o crear una nueva.
3. Arrastrar y soltar varios archivos de `test_dataset_30_docs/`.
4. Observar la barra de progreso pasando de *Pendiente* a *Procesando* y finalmente a *IA Listo*.
5. Abrir un contrato y una factura para ver el **Resumen Ejecutivo** y las **Entidades Extraídas** (total, IVA, partes, vigencias).
6. Ir a la pestaña **Chatbot RAG** y realizar las siguientes 3 preguntas:
   - *"¿Cuál es la penalidad por incumplimiento en el contrato de software?"*
   - *"¿Qué facturas fueron emitidas en marzo y cuál es su desglose de IVA?"*
   - *"¿Cuáles candidatos tienen experiencia en Python y desarrollo backend?"*
7. Ir a la pestaña **Dashboard** para revisar los gráficos de distribución por categoría y la tabla de auditoría.
