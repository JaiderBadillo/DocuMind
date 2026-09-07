import os
import sys
import shutil
import uuid
from pathlib import Path

# Add project root and backend to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

from backend.app.core.config import STORAGE_DIR, DATABASE_PATH, DOCS_DIR
from backend.app.core.database import get_db, log_audit
from backend.app.services.document_parser import parse_document
from backend.app.services.ai_engine import process_document_ai
from backend.app.services.vector_store import save_document_chunks

def ingest_test_documents():
    """Batch imports and processes all 30 synthetic test documents into DocuMind Enterprise."""
    print("=========================================================================")
    print("      DOCUMIND ENTERPRISE - INGESTA DE DATASET DE 30 DOCUMENTOS         ")
    print("=========================================================================\n")
    
    if not DOCS_DIR.exists():
        print(f"[ERROR] No se encontró el directorio {DOCS_DIR}")
        return

    # Map subfolders to default repository IDs
    repo_mapping = {
        "contratos_legal": 1,          # Contratos y Acuerdos Legales
        "facturas_finanzas": 2,        # Facturación y Finanzas
        "talento_humano_informes": 3   # Talento Humano y Selección
    }

    # Get admin user ID
    admin_id = 1
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE role = 'ADMIN' LIMIT 1")
        row = cursor.fetchone()
        if row:
            admin_id = row["id"]

    all_files = list(DOCS_DIR.glob("**/*.*"))
    test_files = [f for f in all_files if f.suffix.lower() in [".pdf", ".docx", ".txt"]]
    print(f"Total de archivos de prueba detectados: {len(test_files)}\n")

    ingested = 0
    skipped = 0

    for fpath in test_files:
        filename = fpath.name
        ext = fpath.suffix.lower()
        subfolder = fpath.parent.name
        repo_id = repo_mapping.get(subfolder, 4)
        
        # If filename starts with 'Informe', put into repo 4 (Informes Técnicos)
        if filename.startswith("Informe_"):
            repo_id = 4

        # Check if already in DB
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM documents WHERE original_filename = ?", (filename,))
            existing = cursor.fetchone()
            if existing:
                print(f"  [OMITIDO] '{filename}' ya existe en la base de datos (ID: {existing['id']}).")
                skipped += 1
                continue

        # Copy to storage
        stored_filename = f"{uuid.uuid4().hex}{ext}"
        target_path = STORAGE_DIR / stored_filename
        shutil.copy2(fpath, target_path)
        file_size = fpath.stat().st_size

        # Insert document record
        mime = "application/pdf" if ext == ".pdf" else ("application/vnd.openxmlformats-officedocument.wordprocessingml.document" if ext == ".docx" else "text/plain")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO documents 
                (repository_id, original_filename, stored_filename, file_size_bytes, file_extension, mime_type, processing_status)
                VALUES (?, ?, ?, ?, ?, ?, 'PROCESSING')
                """,
                (repo_id, filename, stored_filename, file_size, ext, mime)
            )
            doc_id = cursor.lastrowid

        # Process text and AI
        try:
            parse_res = parse_document(target_path, ext)
            raw_text = parse_res["raw_text"]
            word_count = parse_res["word_count"]
            
            ai_res = process_document_ai(raw_text)
            
            with get_db() as conn:
                conn.execute(
                    "UPDATE documents SET raw_text = ?, processing_status = 'COMPLETED' WHERE id = ?",
                    (raw_text, doc_id)
                )
                conn.execute(
                    """
                    INSERT OR REPLACE INTO document_metadata 
                    (document_id, category, category_confidence, executive_summary, extracted_entities_json, word_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        doc_id,
                        ai_res["category"],
                        ai_res["category_confidence"],
                        ai_res["executive_summary"],
                        str(ai_res["extracted_entities"]),
                        word_count
                    )
                )
            
            save_document_chunks(doc_id, raw_text)
            print(f"  [OK] Ingestado: '{filename}' (ID: {doc_id}, Cat: {ai_res['category']}, Palabras: {word_count})")
            ingested += 1
        except Exception as e:
            print(f"  [ERROR] Procesando '{filename}': {e}")
            with get_db() as conn:
                conn.execute("UPDATE documents SET processing_status = 'FAILED' WHERE id = ?", (doc_id,))

    print(f"\nResumen: {ingested} documentos nuevos ingestados, {skipped} omitidos.")
    log_audit("DATASET_BATCH_INGEST", "SUCCESS", f"Ingesta masiva de {ingested} documentos de prueba", user_id=admin_id)

if __name__ == "__main__":
    ingest_test_documents()
