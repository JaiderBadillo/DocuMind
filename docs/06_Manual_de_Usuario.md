# 06 - MANUAL DE USUARIO FINAL
**PROYECTO INTEGRADOR: SISTEMA DE GESTIÓN DOCUMENTAL INTELIGENTE (DocuMind Enterprise)**  
**Asignatura:** Desarrollo de Aplicaciones Empresariales – VI Semestre  
**Institución:** Unidades Tecnológicas de Santander (UTS)  
**Docente:** Wilson Castaño Galviz  

---

## 1. Introducción y Bienvenida
Bienvenido a **DocuMind Enterprise**, la solución integral que transforma sus archivos tradicionales en un repositorio inteligente con Inteligencia Artificial. Con esta plataforma usted podrá:
- Clasificar automáticamente sus documentos legales, contables, técnicos y de personal.
- Obtener resúmenes ejecutivos instantáneos sin leer documentos de decenas de páginas.
- Extraer montos de facturas, partes de contratos y perfiles laborales en formato estructurado.
- Chatear en lenguaje natural con sus documentos (RAG) y verificar exactamente de qué página y archivo proviene cada dato.

---

## 2. Acceso al Sistema (Inicio de Sesión y Registro)

1. Abra su navegador web e ingrese a la dirección asignada (por ejemplo: `http://localhost:8000`).
2. En la pantalla principal observará el formulario de autenticación segura.
3. Si ya posee una cuenta corporativa:
   - Ingrese su **Correo Electrónico** (Ej: `admin@documind.com`).
   - Ingrese su **Contraseña** (Ej: `Admin123!`).
   - Haga clic en el botón **"Iniciar Sesión"**.
4. Si es un usuario nuevo:
   - Haga clic en **"Crear Cuenta"**.
   - Diligencie su nombre completo, correo electrónico y contraseña.
   - El sistema validará sus datos y le otorgará acceso inmediato.

---

## 3. Navegación Principal y Módulos
Al autenticarse, accederá a la consola principal organizada en una barra de navegación superior y lateral:
- 📁 **Repositorio / Carpetas:** Explorador de archivos con visualización en cuadrícula o lista.
- ⚡ **Subida Rápida:** Zona interactiva de arrastrar y soltar para carga masiva de archivos.
- 💬 **Asistente RAG (Chat Inteligente):** Consola de preguntas y respuestas sobre el contenido documental.
- 📊 **Dashboard y Métricas:** Estadísticas en tiempo real del repositorio y salud del sistema.
- 👤 **Perfil y Sesión:** Información del usuario conectado y botón de cierre seguro de sesión.

---

## 4. Gestión de Carpetas y Carga de Archivos

### 4.1 Crear una Nueva Carpeta
1. En la vista de Repositorios, presione el botón **"+ Nueva Carpeta"**.
2. Escriba un nombre claro (por ejemplo: `Contratos de Proveedores 2026`).
3. Agregue una breve descripción opcional y presione **"Guardar"**.

### 4.2 Cargar Documentos
1. Seleccione la carpeta de destino donde desea alojar los archivos.
2. Arrastre los archivos desde el explorador de su computadora hasta la zona punteada marcada como **"Arrastra y suelta tus archivos aquí (PDF, DOCX, TXT)"** o haga clic sobre ella para seleccionarlos manualmente.
3. Puede cargar múltiples archivos simultáneamente.
4. Observe la barra de progreso:
   - El archivo se sube al servidor.
   - El indicador cambiará a **"Procesando con IA..."** mientras se extrae el texto, se generan vectores y se categoriza.
   - Al finalizar, el documento se marcará con una etiqueta verde: **"Completado"**.

---

## 5. Visualización del Análisis de Inteligencia Artificial

Al hacer clic en cualquier documento de la lista:
1. Se abrirá el **Visor Inteligente** con dos paneles:
   - **Panel Izquierdo:** Vista previa y metadatos generales (nombre original, tamaño, fecha de subida, extensión).
   - **Panel Derecho (Resultados de IA):**
     - **Categoría Detectada:** (Ej: `Legal y Contratos` con 95% de certidumbre).
     - **Resumen Ejecutivo:** Puntos clave sintetizados en viñetas comprensibles.
     - **Entidades Estructuradas:** Tabla con los campos clave identificados (por ejemplo, en facturas: emisor, cliente, subtotal, IVA y valor total).
2. Botones de Acción:
   - 📥 **Descargar Archivo Original:** Descarga el binario directo a su equipo.
   - 🔄 **Reprocesar con IA:** Vuelve a ejecutar los algoritmos si se actualizó el modelo.
   - 🗑️ **Eliminar:** Borra el archivo y sus metadatos del repositorio de manera permanente.

---

## 6. Uso del Asistente Documental RAG (Chat Inteligente)

1. Diríjase a la pestaña **"Chat Inteligente (RAG)"**.
2. Escriba su consulta en lenguaje natural en la barra inferior. Ejemplos de preguntas:
   - *"¿Cuál es el valor total del contrato de soporte técnico con TechCorp?"*
   - *"¿Qué facturas fueron emitidas en el mes de mayo y cuál es su desglose de impuestos?"*
   - *"¿Qué candidatos tienen experiencia en Python y bases de datos relacionales?"*
3. Presione la tecla **Enter** o el botón de enviar.
4. El asistente responderá de manera sintetizada y mostrará tarjetas con las **Fuentes Citadas**:
   - Nombre del archivo de soporte.
   - Párrafo relevante extraído que sustenta la respuesta.

---

## 7. Preguntas Frecuentes (FAQ)

- **¿Qué pasa si subo un archivo en formato Excel o imagen?**  
  El sistema le mostrará una notificación informándole que solo se admiten documentos en formato PDF, Word (DOCX) y Texto Plano (TXT).
- **¿Mis archivos o contraseñas están seguros?**  
  Sí. El sistema aplica algoritmos criptográficos modernos (`bcrypt` para credenciales y tokens JWT firmados digitalmente para cada sesión).
