from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
import re
from ..core.database import get_db, log_audit
from ..core.config import get_gemini_api_key, get_best_gemini_model, generate_with_gemini_fallback
from ..models.schemas import NotebookQueryRequest, NotebookResponse, NotebookSourceItem, NotebookCitation
from .auth_routes import get_current_user

router = APIRouter(prefix="/notebook", tags=["NotebookLM Studio"])

@router.get("/sources", response_model=List[NotebookSourceItem])
def get_notebook_sources(
    repository_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user)
):
    """Returns all ready documents formatted as selectable sources for the Notebook Studio."""
    sources = []
    with get_db() as conn:
        sql = """
        SELECT d.id, d.original_filename, d.file_extension,
               COALESCE(m.category, 'General') as category,
               COALESCE(m.word_count, 0) as word_count,
               COALESCE(m.executive_summary, SUBSTR(d.raw_text, 1, 150)) as summary
        FROM documents d
        LEFT JOIN document_metadata m ON d.id = m.document_id
        WHERE d.processing_status = 'COMPLETED'
        """
        params = []
        if repository_id:
            sql += " AND d.repository_id = ?"
            params.append(repository_id)
            
        sql += " ORDER BY d.created_at DESC"
        cursor = conn.cursor()
        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall()
        
        for r in rows:
            summary_raw = r["summary"] or ""
            snippet = summary_raw[:140].strip().replace("\n", " ")
            if len(summary_raw) > 140:
                snippet += "..."
            sources.append({
                "id": r["id"],
                "original_filename": r["original_filename"],
                "category": r["category"],
                "file_extension": r["file_extension"],
                "word_count": r["word_count"],
                "summary_snippet": snippet
            })
            
    return sources

def clean_and_tokenize(text: str) -> List[str]:
    """Cleans text, strips punctuation, and filters non-informative stopwords."""
    clean = re.sub(r'[^\w\s]', ' ', text.lower())
    stopwords = {
        "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "al", "a",
        "en", "para", "por", "con", "sin", "sobre", "entre", "tras", "durante", "hasta",
        "que", "quien", "quién", "quienes", "quiénes", "cual", "cuál", "cuales", "cuáles",
        "donde", "dónde", "cuando", "cuándo", "como", "cómo", "es", "son", "fue", "será",
        "hay", "tiene", "tienen", "este", "esta", "estos", "estas", "ese", "esa", "dio",
        "y", "o", "u", "e", "pero", "mas", "más", "me", "se", "te", "le", "les", "nos",
        "dime", "cuenta", "sabes", "sobre", "acerca", "favor", "este", "esta", "estos"
    }
    return [w for w in clean.split() if len(w) > 2 and w not in stopwords]

def get_synonym_keywords(query: str) -> List[str]:
    """Expands user queries with domain synonyms for students, authors, directors, budgets, etc."""
    query_clean = re.sub(r'[^\w\s]', ' ', query.lower())
    words = clean_and_tokenize(query)
    expanded = list(words)
    
    # Students / Authors / Team / Developers
    if any(k in query_clean for k in ["quien", "quién", "estudiante", "integran", "integrante", "autor", "equipo", "alumno", "participante", "desarrollador", "responsable", "personas"]):
        expanded.extend(["estudiante", "estudiantes", "autor", "autores", "integrante", "integrantes", "elaborado por", "presentado por", "candidato", "alumnos", "investigador", "investigadores"])
        
    # Director / Advisor / Tutor / Professor
    if any(k in query_clean for k in ["director", "directora", "asesor", "asesora", "tutor", "tutora", "docente", "profesor"]):
        expanded.extend(["director", "directora", "asesor", "asesora", "tutor", "tutora", "docente", "docente asesor", "director de proyecto", "ing.", "lic.", "dr."])
        
    # Budget / Costs / Price / Amount / Finance
    if any(k in query_clean for k in ["presupuesto", "cuanto", "cuánto", "costo", "costos", "valor", "inversion", "inversión", "precio", "monto", "total", "financiero", "rubro"]):
        expanded.extend(["presupuesto", "costo", "costos", "inversión", "inversion", "valor", "subtotal", "total", "recursos", "pesos", "$", "cop"])
        
    # Dates / Schedule / Deliverables
    if any(k in query_clean for k in ["cuando", "cuándo", "fecha", "plazo", "tiempo", "cronograma", "duracion", "duración"]):
        expanded.extend(["cronograma", "fecha", "plazo", "meses", "dias", "días", "vigencia", "inicio", "entrega"])
        
    # Objectives / Scope
    if any(k in query_clean for k in ["objetivo", "alcance", "proposito", "propósito", "meta"]):
        expanded.extend(["objetivo general", "objetivos específicos", "propósito", "alcance", "meta"])
        
    return list(set(expanded))

def find_most_relevant_context(query: str, text: str, max_chars: int = 1500) -> Optional[Dict[str, Any]]:
    """Scans full document content to pinpoint the exact paragraph or table answering the question."""
    if not text:
        return None
        
    target_terms = get_synonym_keywords(query)
    if not target_terms:
        return None
        
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if len(p.strip()) > 15]
    if not paragraphs:
        paragraphs = [text[:1200]]
        
    best_paragraph = ""
    highest_score = 0
    query_clean = re.sub(r'[^\w\s]', ' ', query.lower()).strip()
    
    for p in paragraphs:
        p_lower = p.lower()
        score = 0
        
        # Exact multi-word query match
        if query_clean and len(query_clean) > 5 and query_clean in p_lower:
            score += 18.0
            
        matched_terms = 0
        for term in target_terms:
            if term in p_lower:
                matched_terms += 1
                weight = 3.5 if " " in term else 1.5
                # Boost if followed by colon or title pattern (e.g. "Autor: Jaider", "Presupuesto: $")
                if re.search(rf'\b{re.escape(term)}\s*[:\-]', p_lower):
                    weight += 6.0
                score += weight
                
        if matched_terms >= 2:
            score += 4.0
            
        if score > highest_score:
            highest_score = score
            best_paragraph = p
            
    if highest_score >= 2.0 and best_paragraph:
        return {
            "score": highest_score,
            "text": best_paragraph[:max_chars]
        }
    return None

def build_mode_instructions(mode: str, query: str) -> str:
    """Configures explicit task directives mirroring Google NotebookLM feature sets."""
    if mode == "study_guide":
        return (
            "TAREA: Genera una GUÍA DE ESTUDIO Y RESUMEN EJECUTIVO exhaustivo a partir de las fuentes.\n"
            "Estructura la respuesta en Markdown con:\n"
            "1. 📌 **Objetivo y Contexto General** de las fuentes analizadas.\n"
            "2. 🔑 **Conceptos, Cláusulas y Hallazgos Principales** (detallados y explicados).\n"
            "3. 📊 **Entidades, Fechas o Cifras Críticas** extraídas textualmente.\n"
            "4. 💡 **Conclusiones y Recomendaciones Clave**.\n"
            "Incluye citas explícitas entre corchetes [Fuente: NombreDocumento] en cada punto."
        )
    elif mode == "faq":
        return (
            "TAREA: Genera una lista de PREGUNTAS FRECUENTES (FAQ) esenciales basadas estrictamente en las fuentes.\n"
            "Plantea entre 4 y 7 preguntas altamente pertinentes que cualquier lector o auditor se haría sobre estos documentos, "
            "y responde cada una con precisión matemática y citas directas [Fuente: NombreDocumento]."
        )
    elif mode == "comparison":
        return (
            "TAREA: Genera una MATRIZ COMPARATIVA de las fuentes analizadas.\n"
            "Crea una tabla en Markdown contrastando:\n"
            "• Documento y Propósito\n"
            "• Partes o Actores involucrados\n"
            "• Condiciones, Montos o Hitos clave\n"
            "• Similitudes y Discrepancias principales observadas."
        )
    elif mode == "briefing":
        return (
            "TAREA: Genera un BRIEFING EJECUTIVO / GUION DE AUDIO (Estilo Audio Overview de NotebookLM).\n"
            "Redacta un resumen conversacional, dinámico, profesional y altamente pedagógico "
            "como si dos analistas o expertos estuvieran explicando los puntos más fascinantes y relevantes "
            "de estos documentos a un director de empresa."
        )
    elif mode == "timeline":
        return (
            "TAREA: Genera una CRONOLOGÍA DETALLADA de eventos, plazos, fechas de vencimiento o hitos presentes en las fuentes.\n"
            "Organiza cronológicamente con viñetas indicando fecha exacta, acontecimiento y fuente citada."
        )
    else:
        return (
            f"TAREA: Responde de forma directa, rigurosa y completa a la siguiente consulta del usuario:\n"
            f"PREGUNTA DEL USUARIO: \"{query}\"\n"
            "Respalda cada afirmación citando explícitamente el documento de donde proviene con [Fuente: NombreDocumento]."
        )

@router.post("/chat", response_model=NotebookResponse)
def notebook_chat_query(
    request: NotebookQueryRequest,
    current_user: dict = Depends(get_current_user)
):
    if not request.document_ids:
        raise HTTPException(status_code=400, detail="Debe seleccionar al menos un documento como fuente.")
    if not request.query.strip() and request.mode == "chat":
        raise HTTPException(status_code=400, detail="La consulta no puede estar vacía.")

    # Retrieve full document contents
    docs_data = []
    total_words = 0
    with get_db() as conn:
        placeholders = ",".join(["?"] * len(request.document_ids))
        sql = f"""
        SELECT d.id, d.original_filename, d.file_extension, d.raw_text,
               COALESCE(m.category, 'General') as category,
               COALESCE(m.executive_summary, '') as summary
        FROM documents d
        LEFT JOIN document_metadata m ON d.id = m.document_id
        WHERE d.id IN ({placeholders}) AND d.processing_status = 'COMPLETED'
        """
        cursor = conn.cursor()
        cursor.execute(sql, tuple(request.document_ids))
        rows = cursor.fetchall()
        
        for r in rows:
            text = r["raw_text"] or ""
            words = len(text.split())
            total_words += words
            docs_data.append({
                "id": r["id"],
                "filename": r["original_filename"],
                "category": r["category"],
                "summary": r["summary"],
                "text": text,
                "word_count": words
            })

    if not docs_data:
        raise HTTPException(status_code=404, detail="No se encontraron documentos válidos para las fuentes seleccionadas.")

    mode = request.mode or "chat"
    query = request.query.strip()
    mode_instructions = build_mode_instructions(mode, query)

    # Build grounded context package
    context_blocks = []
    citations: List[Dict[str, Any]] = []
    
    for idx, doc in enumerate(docs_data, start=1):
        sample_text = doc["text"][:25000]
        context_blocks.append(
            f"=== FUENTE [{idx}]: \"{doc['filename']}\" (Categoría: {doc['category']}) ===\n"
            f"Resumen previo: {doc['summary']}\n\n"
            f"Contenido completo:\n{sample_text}\n"
        )
        first_quote = doc["text"][:160].strip().replace("\n", " ") + "..."
        citations.append({
            "citation_id": idx,
            "document_id": doc["id"],
            "document_name": doc["filename"],
            "quote": first_quote
        })

    full_context_text = "\n\n-----------------------------------------\n\n".join(context_blocks)
    api_key = get_gemini_api_key()
    gemini_error = None
    
    # 1. Google Gemini integration with automatic modern model fallback
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            system_prompt = (
                "Eres DocuMind NotebookLM Studio, un sistema de inteligencia artificial especializado "
                "en análisis documental corporativo. Tu objetivo es operar como Google NotebookLM:\n"
                "1. Fundamenta tus respuestas ESTRICTAMENTE en las fuentes documentales proporcionadas a continuación.\n"
                "2. NO inventes información, datos ni cifras que no provengan explícitamente de las fuentes.\n"
                "3. Añade citas claras del documento de origen indicando el nombre del archivo entre corchetes, por ejemplo [Fuente: archivo.pdf].\n"
                "4. Utiliza formato Markdown elegante (negritas, viñetas, tablas, encabezados claros y organizados).\n\n"
                f"FUENTES DOCUMENTALES DISPONIBLES ({len(docs_data)} fuentes seleccionadas, ~{total_words} palabras):\n"
                f"{full_context_text}\n\n"
                f"INSTRUCCIÓN DE LA SESIÓN:\n"
                f"{mode_instructions}"
            )
            
            answer_text, used_model = generate_with_gemini_fallback(genai, system_prompt)
            
            log_audit(
                "NOTEBOOK_LM_QUERY",
                "SUCCESS",
                f"NotebookLM Gemini ({used_model}): Modo={mode} ({len(docs_data)} fuentes, {total_words} palabras)",
                user_id=current_user["user_id"]
            )
            
            return {
                "query": query or mode.upper(),
                "mode": mode,
                "answer": answer_text,
                "citations": citations,
                "sources_used": [d["filename"] for d in docs_data],
                "model_used": f"Google Gemini ({used_model}) (Grounded)",
                "total_words_analyzed": total_words
            }
        except Exception as e:
            gemini_error = str(e)
            print(f"Error llamando a Gemini NotebookLM: {gemini_error}. Activando fallback local.")

    # 2. Local Extractive NotebookLM Engine (Offline fallback)
    local_answer_parts = []
    local_answer_parts.append(f"### 📓 NotebookLM Studio (Análisis Grounded)")
    
    if gemini_error:
        local_answer_parts.append(
            f"> ⚠️ **Fallo al invocar Google Gemini API:** `{gemini_error}`\n"
            f"> *Se activó el motor semántico local de contingencia. Verifica si tu API Key es válida o si la cuota está activa.*"
        )
    elif not api_key:
        local_answer_parts.append(
            "> ⚡ **Modo Local Offline Activo:** La API Key de Gemini no está configurada actualmente. "
            "Para activar respuestas generativas avanzadas con **Google Gemini 1.5 Flash**, "
            "haz clic en el botón de tuerca **⚙️** arriba a la izquierda e ingresa tu API Key gratuita de Google AI Studio."
        )

    local_answer_parts.append(
        f"*Análisis fundamentado en **{len(docs_data)} fuentes activas** "
        f"con un volumen analizado de **{total_words:,} palabras**.*\n"
    )
    
    if mode == "study_guide":
        local_answer_parts.append("#### 📌 1. Resumen Ejecutivo Integrado")
        for d in docs_data:
            local_answer_parts.append(f"- **{d['filename']}** ({d['category']}): {d['summary']}")
        local_answer_parts.append("\n#### 🔑 2. Hallazgos y Cláusulas Centrales")
        for d in docs_data:
            clean = d['text'].strip().replace('\n', ' ')
            sample = clean[:260] + "..." if len(clean) > 260 else clean
            local_answer_parts.append(f"• **{d['filename']}**: *\"{sample}\"* [Fuente: {d['filename']}]")
        local_answer_parts.append("\n#### 💡 3. Conclusión Sintética")
        local_answer_parts.append("Las fuentes seleccionadas configuran el marco operativo y contractual de la organización para auditoría y toma de decisiones.")

    elif mode == "faq":
        local_answer_parts.append("#### ❓ Preguntas Frecuentes Detectadas en las Fuentes")
        for idx, d in enumerate(docs_data, 1):
            local_answer_parts.append(f"**P{idx}: ¿Cuál es el objeto o propósito central de {d['filename']}?**")
            local_answer_parts.append(f"**R:** {d['summary']} [Fuente: {d['filename']}]\n")
            if "contrato" in d['filename'].lower() or d['category'] == "LEGAL_CONTRACTS":
                local_answer_parts.append(f"**P{idx}.1: ¿Qué penalidades o cláusulas rigen este acuerdo?**")
                local_answer_parts.append(f"**R:** Rigen las estipuladas en las cláusulas de incumplimiento del texto contractual [Fuente: {d['filename']}].\n")

    elif mode == "comparison":
        local_answer_parts.append("#### 📋 Matriz Comparativa de Fuentes Seleccionadas\n")
        local_answer_parts.append("| Documento | Categoría | Volumen | Propósito Principal |")
        local_answer_parts.append("| :--- | :--- | :--- | :--- |")
        for d in docs_data:
            brief = d['summary'][:80].replace("|", "/") + "..."
            local_answer_parts.append(f"| **{d['filename']}** | `{d['category']}` | {d['word_count']} palabras | {brief} |")

    elif mode == "briefing":
        local_answer_parts.append("#### 🎙️ Briefing Ejecutivo (Audio Overview Script)\n")
        local_answer_parts.append(f"**Locutor A:** Bienvenidos al informe ejecutivo de DocuMind. Hoy estamos revisando {len(docs_data)} documentos de alto impacto.")
        local_answer_parts.append(f"**Locutor B:** Así es. Revisando específicamente **{docs_data[0]['filename']}**, destaca su rol estratégico en la gestión corporativa.")
        for d in docs_data[1:]:
            local_answer_parts.append(f"**Locutor A:** Y complementando esto, el archivo **{d['filename']}** aporta el sustento documental indispensable.")
        local_answer_parts.append(f"**Locutor B:** En conclusión, ambos documentos están alineados y listos para toma de decisiones ejecutivas.")

    elif mode == "timeline":
        local_answer_parts.append("#### ⏱️ Cronología e Hitos Clave de las Fuentes")
        for d in docs_data:
            dates_found = re.findall(r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4})\b', d['text'])
            unique_dates = list(set(dates_found))[:3]
            dates_str = ", ".join(unique_dates) if unique_dates else "Fechas referenciadas en el cuerpo del texto"
            local_answer_parts.append(f"- **{d['filename']}**: Referencias temporales detectadas: `{dates_str}` [Fuente: {d['filename']}]")

    else:
        # Chat mode - advanced semantic context extraction across all selected sources
        best_match = None
        best_doc = None
        
        for d in docs_data:
            res = find_most_relevant_context(query, d['text'])
            if res and (best_match is None or res['score'] > best_match['score']):
                best_match = res
                best_doc = d
                
        if best_match and best_doc:
            clean_text = best_match['text'].strip()
            local_answer_parts.append(f"De acuerdo con la información localizada en **{best_doc['filename']}**:\n")
            local_answer_parts.append(f"> {clean_text}\n")
            local_answer_parts.append(f"[Fuente: {best_doc['filename']}]")
        else:
            local_answer_parts.append(
                f"Tras escanear rigurosamente las fuentes seleccionadas, no se halló un fragmento explícito sobre \"{query}\". "
                "Te recomendamos verificar si el término está formulado de otra forma o activar **Google Gemini 1.5 Flash** con tu API Key en el menú ⚙️ para comprensión generativa completa."
            )

    log_audit(
        "NOTEBOOK_LM_QUERY",
        "SUCCESS",
        f"NotebookLM Local: Modo={mode} ({len(docs_data)} fuentes)",
        user_id=current_user["user_id"]
    )

    return {
        "query": query or mode.upper(),
        "mode": mode,
        "answer": "\n\n".join(local_answer_parts),
        "citations": citations,
        "sources_used": [d["filename"] for d in docs_data],
        "model_used": "Motor Local Grounded DocuMind (NotebookLM)",
        "total_words_analyzed": total_words
    }
