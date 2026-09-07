import sys
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

import sqlite3
from backend.app.core.config import DATABASE_PATH, STORAGE_DIR, DOCS_DIR
from backend.app.services.document_parser import parse_document
from backend.app.services.ai_engine import process_document_ai
from backend.app.services.vector_store import save_document_chunks

def reprocess_failed():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, original_filename, stored_filename, file_extension, processing_status FROM documents WHERE processing_status = 'FAILED'")
    failed_docs = cursor.fetchall()
    print(f"Documentos con estado FAILED a reprocesar: {len(failed_docs)}")

    for doc_id, fname, sname, ext, status in failed_docs:
        print(f"Reprocesando ID {doc_id}: {fname}")
        found = list(DOCS_DIR.glob(f"**/{fname}"))
        if found:
            shutil.copy2(found[0], STORAGE_DIR / sname)
            res = parse_document(STORAGE_DIR / sname, ext)
            raw_text = res["raw_text"]
            wcount = res["word_count"]
            ai_res = process_document_ai(raw_text)
            
            cursor.execute("UPDATE documents SET raw_text = ?, processing_status = 'COMPLETED' WHERE id = ?", (raw_text, doc_id))
            cursor.execute("""
                INSERT OR REPLACE INTO document_metadata
                (document_id, category, category_confidence, executive_summary, extracted_entities_json, word_count)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (doc_id, ai_res["category"], ai_res["category_confidence"], ai_res["executive_summary"], str(ai_res["extracted_entities"]), wcount))
            save_document_chunks(doc_id, raw_text)
            print(f"  [OK] Completado: Cat={ai_res['category']}, Palabras={wcount}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    reprocess_failed()
