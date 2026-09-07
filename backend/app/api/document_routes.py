import os
import uuid
import json
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse

from ..core.config import STORAGE_DIR, MAX_FILE_SIZE_BYTES, ALLOWED_EXTENSIONS
from ..core.database import get_db, log_audit
from ..models.schemas import DocumentResponse, DocumentDetailResponse
from ..services.document_parser import parse_document
from ..services.ai_engine import process_document_ai
from ..services.vector_store import save_document_chunks
from .auth_routes import get_current_user

router = APIRouter(prefix="/documents", tags=["Documentos"])

def execute_ai_pipeline(doc_id: int, stored_path: Path, ext: str, user_id: int):
    """Background task to extract text, run AI classification/summaries and create vector embeddings."""
    try:
        # 1. Update status to PROCESSING
        with get_db() as conn:
            conn.execute("UPDATE documents SET processing_status = 'PROCESSING' WHERE id = ?", (doc_id,))
            
        # 2. Extract text from PDF / DOCX / TXT
        parse_res = parse_document(stored_path, ext)
        raw_text = parse_res["raw_text"]
        word_count = parse_res["word_count"]
        
        if not raw_text.strip():
            raise ValueError("El documento no contiene texto legible.")
            
        # 3. AI Classification, Summary & Entity Extraction
        ai_res = process_document_ai(raw_text)
        
        # 4. Save metadata & chunks to DB
        with get_db() as conn:
            conn.execute("UPDATE documents SET raw_text = ?, processing_status = 'COMPLETED' WHERE id = ?", (raw_text, doc_id))
            
            # Save or replace metadata
            conn.execute("DELETE FROM document_metadata WHERE document_id = ?", (doc_id,))
            conn.execute(
                """
                INSERT INTO document_metadata 
                (document_id, category, category_confidence, executive_summary, extracted_entities_json, word_count)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    doc_id,
                    ai_res["category"],
                    ai_res["category_confidence"],
                    ai_res["executive_summary"],
                    json.dumps(ai_res["extracted_entities"]),
                    word_count
                )
            )
            
        # 5. Build vector embeddings for RAG
        save_document_chunks(doc_id, raw_text)
        log_audit("DOCUMENT_PROCESSED", "SUCCESS", f"Doc #{doc_id} procesado con éxito en categoría {ai_res['category']}", user_id=user_id, document_id=doc_id)

    except Exception as e:
        err_msg = str(e)
        print(f"Error procesando documento #{doc_id}: {err_msg}")
        with get_db() as conn:
            conn.execute("UPDATE documents SET processing_status = 'FAILED' WHERE id = ?", (doc_id,))
        log_audit("DOCUMENT_PROCESS_FAILED", "ERROR", f"Fallo procesando Doc #{doc_id}: {err_msg}", user_id=user_id, document_id=doc_id)

@router.post("/upload", response_model=List[DocumentResponse])
async def upload_documents(
    background_tasks: BackgroundTasks,
    repository_id: int = Form(...),
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user)
):
    created_docs = []
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM repositories WHERE id = ?", (repository_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Repositorio no encontrado")

    for file in files:
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"Extensión '{ext}' no permitida. Formatos válidos: .pdf, .docx, .txt"
            )
            
        # Read file contents
        content = await file.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(status_code=400, detail=f"El archivo {file.filename} excede el límite de 25MB")
            
        stored_filename = f"{uuid.uuid4().hex}{ext}"
        stored_path = STORAGE_DIR / stored_filename
        
        with open(stored_path, "wb") as f:
            f.write(content)
            
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO documents 
                (repository_id, original_filename, stored_filename, file_extension, file_size_bytes, mime_type, processing_status)
                VALUES (?, ?, ?, ?, ?, ?, 'PENDING')
                """,
                (repository_id, file.filename, stored_filename, ext, len(content), file.content_type or "application/octet-stream")
            )
            doc_id = cursor.lastrowid
            
            created_docs.append({
                "id": doc_id,
                "repository_id": repository_id,
                "original_filename": file.filename,
                "file_extension": ext,
                "file_size_bytes": len(content),
                "mime_type": file.content_type or "application/octet-stream",
                "processing_status": "PENDING",
                "created_at": "Justo ahora"
            })
            
        log_audit("DOCUMENT_UPLOAD", "SUCCESS", f"Archivo {file.filename} subido", user_id=current_user["user_id"], document_id=doc_id)
        background_tasks.add_task(execute_ai_pipeline, doc_id, stored_path, ext, current_user["user_id"])
        
    return created_docs

@router.get("", response_model=List[DocumentResponse])
def list_documents(
    repository_id: Optional[int] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    with get_db() as conn:
        cursor = conn.cursor()
        sql = """
        SELECT d.id, d.repository_id, d.original_filename, d.file_extension,
               d.file_size_bytes, d.mime_type, d.processing_status, d.created_at,
               m.category, m.executive_summary
        FROM documents d
        LEFT JOIN document_metadata m ON d.id = m.document_id
        WHERE 1=1
        """
        params = []
        if repository_id:
            sql += " AND d.repository_id = ?"
            params.append(repository_id)
        if category:
            sql += " AND m.category = ?"
            params.append(category)
        if status:
            sql += " AND d.processing_status = ?"
            params.append(status)
            
        sql += " ORDER BY d.created_at DESC"
        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall()
        
        return [
            {
                "id": r["id"],
                "repository_id": r["repository_id"],
                "original_filename": r["original_filename"],
                "file_extension": r["file_extension"],
                "file_size_bytes": r["file_size_bytes"],
                "mime_type": r["mime_type"],
                "processing_status": r["processing_status"],
                "created_at": str(r["created_at"]),
                "category": r["category"],
                "summary": r["executive_summary"]
            }
            for r in rows
        ]

@router.get("/{doc_id}", response_model=DocumentDetailResponse)
def get_document_detail(doc_id: int, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT d.id, d.repository_id, d.original_filename, d.file_extension,
               d.file_size_bytes, d.mime_type, d.processing_status, d.created_at, d.raw_text,
               m.category, m.category_confidence, m.executive_summary, m.extracted_entities_json,
               m.token_count, m.word_count, m.processed_at
        FROM documents d
        LEFT JOIN document_metadata m ON d.id = m.document_id
        WHERE d.id = ?
        """, (doc_id,))
        r = cursor.fetchone()
        
        if not r:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
            
        meta = None
        if r["category"]:
            try:
                entities = json.loads(r["extracted_entities_json"])
            except Exception:
                entities = {}
                
            meta = {
                "category": r["category"],
                "category_confidence": r["category_confidence"] or 0.0,
                "executive_summary": r["executive_summary"] or "",
                "extracted_entities": entities,
                "token_count": r["token_count"] or 0,
                "word_count": r["word_count"] or 0,
                "processed_at": str(r["processed_at"])
            }
            
        return {
            "id": r["id"],
            "repository_id": r["repository_id"],
            "original_filename": r["original_filename"],
            "file_extension": r["file_extension"],
            "file_size_bytes": r["file_size_bytes"],
            "mime_type": r["mime_type"],
            "processing_status": r["processing_status"],
            "created_at": str(r["created_at"]),
            "category": r["category"],
            "summary": r["executive_summary"],
            "raw_text": r["raw_text"],
            "metadata": meta
        }

@router.get("/{doc_id}/download")
def download_document(doc_id: int, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT stored_filename, original_filename, mime_type FROM documents WHERE id = ?", (doc_id,))
        r = cursor.fetchone()
        if not r:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
            
        file_path = STORAGE_DIR / r["stored_filename"]
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="El archivo físico no se encuentra en el servidor")
            
        return FileResponse(
            path=str(file_path),
            filename=r["original_filename"],
            media_type=r["mime_type"]
        )

@router.delete("/{doc_id}")
def delete_document(doc_id: int, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT stored_filename, original_filename FROM documents WHERE id = ?", (doc_id,))
        r = cursor.fetchone()
        if not r:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
            
        # Delete from disk
        file_path = STORAGE_DIR / r["stored_filename"]
        if file_path.exists():
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error eliminando archivo físico: {e}")
                
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        log_audit("DOCUMENT_DELETE", "SUCCESS", f"Documento '{r['original_filename']}' eliminado", user_id=current_user["user_id"], document_id=doc_id)
        return {"message": "Documento y metadatos eliminados correctamente"}

@router.post("/{doc_id}/reprocess")
def reprocess_document(
    doc_id: int,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT stored_filename, file_extension FROM documents WHERE id = ?", (doc_id,))
        r = cursor.fetchone()
        if not r:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
            
        file_path = STORAGE_DIR / r["stored_filename"]
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Archivo físico no encontrado")
            
        background_tasks.add_task(execute_ai_pipeline, doc_id, file_path, r["file_extension"], current_user["user_id"])
        return {"message": f"Reprocesamiento iniciado para documento #{doc_id}"}
