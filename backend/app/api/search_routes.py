from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from ..models.schemas import SearchResponse, RagQueryRequest, RagQueryResponse
from ..services.vector_store import hybrid_search_documents, answer_rag_query
from ..core.database import log_audit
from .auth_routes import get_current_user

router = APIRouter(tags=["Búsqueda y RAG"])

@router.get("/search", response_model=SearchResponse)
def search_documents(
    q: str = Query(..., min_length=2, description="Término o frase de búsqueda"),
    repository_id: Optional[int] = None,
    category: Optional[str] = None,
    format: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    ext = format
    if ext and not ext.startswith("."):
        ext = f".{ext}"
        
    results_raw = hybrid_search_documents(
        query=q,
        repository_id=repository_id,
        category=category,
        file_extension=ext,
        top_k=20
    )
    
    results = [
        {
            "document_id": r["document_id"],
            "document_name": r["document_name"],
            "category": r["category"],
            "snippet": r["snippet"],
            "relevance": r["relevance"]
        }
        for r in results_raw
    ]
    
    log_audit("SEARCH_QUERY", "SUCCESS", f"Búsqueda: '{q}' (cat={category}, fmt={format}, {len(results)} resultados)", user_id=current_user["user_id"])
    
    return {
        "query": q,
        "total_results": len(results),
        "results": results
    }

@router.post("/rag/chat", response_model=RagQueryResponse)
def rag_chat(request: RagQueryRequest, current_user: dict = Depends(get_current_user)):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="La consulta no puede estar vacía")
        
    answer_data = answer_rag_query(request.query, repository_id=request.repository_id)
    log_audit("RAG_QUERY", "SUCCESS", f"Consulta RAG: '{request.query[:80]}'", user_id=current_user["user_id"])
    
    return answer_data
