import math
import json
import re
from typing import List, Dict, Any, Optional
from ..core.database import get_db
from ..core.config import get_gemini_api_key, get_best_gemini_model, generate_with_gemini_fallback

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Divides text into sliding windows with overlap to preserve semantic continuity."""
    if not text:
        return []
        
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= text_len:
            break
        start += (chunk_size - overlap)
        
    return chunks

def compute_sparse_embedding(text: str, dimension: int = 128) -> List[float]:
    """
    Computes a normalized sparse vector embedding using hashing trick and term frequencies.
    Captures lexical and contextual word distributions without external model weight files.
    """
    vector = [0.0] * dimension
    words = re.findall(r'\b[a-zA-ZáéíóúÁÉÍÓÚñÑ]{3,}\b', text.lower())
    
    if not words:
        return vector
        
    for word in words:
        # Hash into vector bucket
        idx = hash(word) % dimension
        vector[idx] += 1.0
        
    # L2 normalize
    norm = math.sqrt(sum(v * v for v in vector))
    if norm > 0:
        vector = [v / norm for v in vector]
        
    return vector

def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calculates cosine similarity between two normalized vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    return sum(a * b for a, b in zip(vec_a, vec_b))

def save_document_chunks(document_id: int, text: str):
    """Chunks the document, computes embeddings and stores them in SQLite."""
    chunks = chunk_text(text)
    with get_db() as conn:
        # Clear previous chunks if any
        conn.execute("DELETE FROM document_chunks WHERE document_id = ?", (document_id,))
        for idx, chunk in enumerate(chunks):
            embedding = compute_sparse_embedding(chunk)
            conn.execute(
                "INSERT INTO document_chunks (document_id, chunk_index, chunk_text, embedding_json) VALUES (?, ?, ?, ?)",
                (document_id, idx, chunk, json.dumps(embedding))
            )

STOPWORDS_ES = {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "al", "a",
    "en", "para", "por", "con", "sin", "sobre", "entre", "tras", "durante", "hasta",
    "que", "quien", "quién", "quienes", "quiénes", "cual", "cuál", "cuales", "cuáles",
    "donde", "dónde", "cuando", "cuándo", "como", "cómo", "es", "son", "fue", "será",
    "hay", "tiene", "tienen", "tenia", "este", "esta", "estos", "estas", "ese", "esa",
    "y", "o", "u", "e", "pero", "mas", "más", "me", "se", "te", "le", "les", "nos",
    "dime", "cuenta", "sabes", "sobre", "acerca", "favor"
}

def extract_informative_terms(text: str) -> List[str]:
    """Extracts non-stopword, meaningful keywords from user query."""
    clean = re.sub(r'[^\w\s]', ' ', text.lower())
    words = clean.split()
    return [w for w in words if len(w) > 2 and w not in STOPWORDS_ES]

def search_similar_chunks(
    query: str, 
    repository_id: Optional[int] = None, 
    category: Optional[str] = None,
    file_extension: Optional[str] = None,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Discriminative semantic & keyword retrieval:
    Gives heavy weight to rare, informative query terms (e.g. 'director', 'penalidad', 'iva')
    and deduplicates adjacent overlapping chunks.
    """
    query_vector = compute_sparse_embedding(query)
    info_terms = extract_informative_terms(query)
    query_clean_lower = query.strip().lower()
    
    candidates = []
    
    with get_db() as conn:
        sql = """
        SELECT c.id, c.document_id, c.chunk_index, c.chunk_text, c.embedding_json,
               d.original_filename, d.file_extension, m.category
        FROM document_chunks c
        JOIN documents d ON c.document_id = d.id
        LEFT JOIN document_metadata m ON d.id = m.document_id
        WHERE d.processing_status = 'COMPLETED'
        """
        params = []
        if repository_id:
            sql += " AND d.repository_id = ?"
            params.append(repository_id)
        if category:
            sql += " AND m.category = ?"
            params.append(category)
        if file_extension:
            sql += " AND LOWER(d.file_extension) = ?"
            params.append(file_extension.lower())
            
        cursor = conn.cursor()
        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall()
        
        for row in rows:
            chunk_text = row["chunk_text"]
            chunk_lower = chunk_text.lower()
            
            # Base cosine similarity
            sim = 0.0
            if row["embedding_json"]:
                chunk_vec = json.loads(row["embedding_json"])
                sim = cosine_similarity(query_vector, chunk_vec)
                
            # Score discriminative terms
            term_score = 0.0
            matched_terms_count = 0
            for term in info_terms:
                if term in chunk_lower:
                    matched_terms_count += 1
                    term_score += 1.5
                    # Extra boost if it appears near beginning of chunk or with colon
                    if re.search(rf'\b{term}\s*[:\-]', chunk_lower):
                        term_score += 3.0

            # Exact multi-term or phrase boost
            if len(info_terms) >= 2 and all(t in chunk_lower for t in info_terms):
                term_score += 4.0
            if query_clean_lower in chunk_lower:
                term_score += 6.0

            final_score = (sim * 0.25) + term_score

            if final_score > 0.1:
                candidates.append({
                    "document_id": row["document_id"],
                    "document_name": row["original_filename"],
                    "file_extension": row["file_extension"],
                    "category": row["category"] or "General",
                    "chunk_index": row["chunk_index"],
                    "relevance_score": round(min(0.99, 0.40 + (final_score * 0.12)), 2),
                    "excerpt": chunk_text,
                    "matched_count": matched_terms_count
                })

    # Sort descending by relevance
    candidates.sort(key=lambda x: (x["matched_count"], x["relevance_score"]), reverse=True)
    
    # Deduplicate adjacent overlapping chunks from the same document
    deduped = []
    seen_regions = set()
    
    for c in candidates:
        key = (c["document_id"], c["chunk_index"] // 2)
        if key not in seen_regions:
            seen_regions.add(key)
            deduped.append(c)
        if len(deduped) >= top_k:
            break
            
    return deduped

def extract_snippet(text: str, query: str, max_length: int = 220) -> str:
    """Extracts a readable context snippet centered on matching query terms."""
    if not text:
        return ""
    terms = extract_informative_terms(query)
    text_lower = text.lower()
    
    match_pos = -1
    query_lower = query.strip().lower()
    if query_lower in text_lower:
        match_pos = text_lower.find(query_lower)
    else:
        for t in terms:
            pos = text_lower.find(t)
            if pos != -1:
                match_pos = pos
                break
                
    if match_pos == -1:
        snippet = text[:max_length].strip().replace('\n', ' ')
        return snippet + ("..." if len(text) > max_length else "")
        
    start = max(0, match_pos - 60)
    end = min(len(text), match_pos + max_length - 60)
    snippet = text[start:end].strip().replace('\n', ' ')
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(text) else ""
    return f"{prefix}{snippet}{suffix}"

def hybrid_search_documents(
    query: str,
    repository_id: Optional[int] = None,
    category: Optional[str] = None,
    file_extension: Optional[str] = None,
    top_k: int = 20
) -> List[Dict[str, Any]]:
    """
    Hybrid Search combining:
    1. Lexical and exact keyword matching across full document text and filenames.
    2. Vector & term similarity retrieval from document chunks.
    Filters by repository, category, and file format.
    """
    if not query or not query.strip():
        return []
        
    terms = extract_informative_terms(query)
    query_lower = query.strip().lower()
    
    # 1. Retrieve matching chunks from vector & semantic scoring
    chunk_results = search_similar_chunks(
        query=query,
        repository_id=repository_id,
        category=category,
        file_extension=file_extension,
        top_k=top_k * 2
    )
    
    # Map document_id -> highest chunk score and chunk excerpt
    chunk_map: Dict[int, Dict[str, Any]] = {}
    for c in chunk_results:
        doc_id = c["document_id"]
        if doc_id not in chunk_map or c["relevance_score"] > chunk_map[doc_id]["relevance_score"]:
            chunk_map[doc_id] = c

    # 2. Query full documents table to combine lexical matching
    doc_results: Dict[int, Dict[str, Any]] = {}
    
    with get_db() as conn:
        sql = """
        SELECT d.id, d.repository_id, d.original_filename, d.file_extension, d.raw_text,
               m.category, m.executive_summary
        FROM documents d
        LEFT JOIN document_metadata m ON d.id = m.document_id
        WHERE d.processing_status = 'COMPLETED'
        """
        params = []
        if repository_id:
            sql += " AND d.repository_id = ?"
            params.append(repository_id)
        if category:
            sql += " AND m.category = ?"
            params.append(category)
        if file_extension:
            sql += " AND LOWER(d.file_extension) = ?"
            params.append(file_extension.lower())
            
        cursor = conn.cursor()
        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall()
        
        for row in rows:
            doc_id = row["id"]
            filename = row["original_filename"] or ""
            filename_lower = filename.lower()
            raw_text = row["raw_text"] or ""
            raw_text_lower = raw_text.lower()
            summary = row["executive_summary"] or ""
            doc_cat = row["category"] or "General"
            
            # Score lexical presence
            lexical_score = 0.0
            
            # Filename match (very high priority)
            if query_lower in filename_lower:
                lexical_score += 4.0
            elif any(t in filename_lower for t in terms):
                lexical_score += 2.0
                
            # Exact phrase match in text
            if query_lower in raw_text_lower:
                lexical_score += 3.5
                
            # Individual term matches in text
            matches_count = sum(1 for t in terms if t in raw_text_lower)
            if terms:
                lexical_score += (matches_count / len(terms)) * 3.0
                
            # Chunk score if present
            chunk_info = chunk_map.get(doc_id)
            chunk_score = (chunk_info["relevance_score"] * 3.0) if chunk_info else 0.0
            
            total_score = lexical_score + chunk_score
            
            # If there is meaningful relevance
            if total_score > 0.4:
                # Determine snippet
                if chunk_info and chunk_info.get("excerpt"):
                    snippet = extract_snippet(chunk_info["excerpt"], query)
                else:
                    snippet = extract_snippet(raw_text or summary, query)
                    
                # Calculate normalized relevance between 0.40 and 0.99
                relevance = round(min(0.99, 0.45 + (total_score * 0.09)), 2)
                
                doc_results[doc_id] = {
                    "document_id": doc_id,
                    "document_name": filename,
                    "file_extension": row["file_extension"],
                    "category": doc_cat,
                    "snippet": snippet,
                    "relevance": relevance,
                    "score": total_score
                }

    # Also include any chunk hits not yet captured
    for doc_id, c in chunk_map.items():
        if doc_id not in doc_results:
            doc_results[doc_id] = {
                "document_id": doc_id,
                "document_name": c["document_name"],
                "file_extension": c["file_extension"],
                "category": c["category"],
                "snippet": extract_snippet(c["excerpt"], query),
                "relevance": c["relevance_score"],
                "score": c["relevance_score"] * 3.0
            }

    # Sort descending by score / relevance
    sorted_results = sorted(doc_results.values(), key=lambda x: x["score"], reverse=True)
    return sorted_results[:top_k]

def extract_answer_from_context(query: str, chunks: List[Dict[str, Any]]) -> Optional[str]:
    """
    NLP Extractive Q&A: Scans sentences in chunks to pinpoint the direct factual answer.
    """
    info_terms = extract_informative_terms(query)
    if not info_terms:
        return None
        
    query_lower = query.lower()
    is_who = any(w in query_lower for w in ["quien", "quién", "persona", "nombre", "director", "autor", "candidato"])
    is_value = any(w in query_lower for w in ["cuanto", "cuánto", "valor", "precio", "costo", "total", "iva", "monto"])
    is_penalty = "penalidad" in query_lower or "sancion" in query_lower or "multa" in query_lower

    best_sentence = ""
    highest_match = 0
    
    for c in chunks:
        # Split chunk into clean sentences
        sentences = re.split(r'[\n\.\?!]+', c["excerpt"])
        for s in sentences:
            s_clean = s.strip()
            if len(s_clean) < 12:
                continue
            s_lower = s_clean.lower()
            
            # Count target keyword matches in this specific sentence
            matches = sum(1 for term in info_terms if term in s_lower)
            
            # Priority boosts for targeted interrogative types
            if is_who and any(k in s_lower for k in ["director", "asesor", "tutor", "autor", "ing.", "lic.", "dr.", "candidato", "suscrito"]):
                matches += 2
            if is_value and any(k in s_lower for k in ["$", "cop", "pesos", "total", "subtotal", "iva"]):
                matches += 2
            if is_penalty and any(k in s_lower for k in ["%", "penalidad", "incumplimiento", "sancion"]):
                matches += 3

            if matches > highest_match:
                highest_match = matches
                best_sentence = s_clean

    if highest_match >= 2 and best_sentence:
        return best_sentence
    return None

def answer_rag_query(query: str, repository_id: Optional[int] = None) -> Dict[str, Any]:
    """Generates an accurate augmented answer based on top matching chunks."""
    top_chunks = search_similar_chunks(query, repository_id=repository_id, top_k=4)
    
    if not top_chunks:
        return {
            "query": query,
            "answer": "No se encontró información relevante en los documentos procesados para responder a esta consulta.",
            "sources": [],
            "model_used": "Sistema de Recuperación Semántica DocuMind"
        }
        
    # Build augmented context
    context_text = "\n\n---\n\n".join([
        f"[Documento: {c['document_name']} | Sección {c['chunk_index']}]:\n{c['excerpt']}"
        for c in top_chunks
    ])
    
    # Check if Gemini API is available
    api_key = get_gemini_api_key()
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            prompt = f"""
            Eres el Asistente Inteligente DocuMind Enterprise. Responde de forma DIRECTA, PRECISA y CONCISA a la pregunta del usuario basándote ESTRICTAMENTE en el siguiente contexto documental.
            Si el contexto contiene la respuesta específica (por ejemplo un nombre, cargo, valor o cláusula), menciónalo claramente de primero.
            Cita de manera explícita el nombre del documento de donde extrajiste la información.
            
            CONTEXTO:
            {context_text}
            
            PREGUNTA:
            {query}
            """
            answer_text, _ = generate_with_gemini_fallback(genai, prompt)
            return {
                "query": query,
                "answer": answer_text,
                "sources": [
                    {
                        "document_id": c["document_id"],
                        "document_name": c["document_name"],
                        "category": c["category"],
                        "chunk_index": c["chunk_index"],
                        "relevance_score": c["relevance_score"],
                        "excerpt": c["excerpt"][:280] + "..."
                    }
                    for c in top_chunks
                ],
                "model_used": f"Google Gemini ({selected_model}) (RAG)"
            }
        except Exception as e:
            print(f"Fallback RAG local: {e}")
            
    # Enhanced Local Extractive RAG
    primary_source = top_chunks[0]
    extracted_sentence = extract_answer_from_context(query, top_chunks)
    
    if extracted_sentence:
        answer_text = (
            f"Basado en el análisis directo del documento **{primary_source['document_name']}**:\n\n"
            f"📌 **Dato encontrado:**\n"
            f"> *\"{extracted_sentence}\"*\n\n"
            f"🔍 **Ubicación:** Sección #{primary_source['chunk_index']} con una pertinencia calculada del {int(primary_source['relevance_score']*100)}%."
        )
    else:
        clean_sample = primary_source['excerpt'].strip().replace('\n', ' ')
        answer_text = (
            f"De acuerdo con la información localizada en **{primary_source['document_name']}** (relevancia {int(primary_source['relevance_score']*100)}%):\n\n"
            f"• **Fragmento relevante:** *\"{clean_sample[:300]}...\"*\n\n"
            f"💡 Te sugerimos verificar los detalles completos en el documento fuente citado abajo."
        )
    
    return {
        "query": query,
        "answer": answer_text,
        "sources": [
            {
                "document_id": c["document_id"],
                "document_name": c["document_name"],
                "category": c["category"],
                "chunk_index": c["chunk_index"],
                "relevance_score": c["relevance_score"],
                "excerpt": c["excerpt"][:280] + "..."
            }
            for c in top_chunks
        ],
        "model_used": "Motor Local Semántico DocuMind (Extractive QA)"
    }
