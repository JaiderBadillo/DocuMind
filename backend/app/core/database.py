import sqlite3
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from .config import DATABASE_PATH

_DB_INITIALIZED = False

def get_db_connection():
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_database():
    global _DB_INITIALIZED
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 1. Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'ADMIN',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 2. Repositories table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS repositories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)
        
        # 3. Documents table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repository_id INTEGER NOT NULL,
            original_filename TEXT NOT NULL,
            stored_filename TEXT NOT NULL,
            file_extension TEXT NOT NULL,
            file_size_bytes INTEGER NOT NULL,
            mime_type TEXT NOT NULL,
            processing_status TEXT DEFAULT 'PENDING',
            raw_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE
        )
        """)
        
        # 4. Document Metadata table (AI extraction)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER UNIQUE NOT NULL,
            category TEXT NOT NULL,
            category_confidence REAL NOT NULL,
            executive_summary TEXT NOT NULL,
            extracted_entities_json TEXT NOT NULL,
            token_count INTEGER DEFAULT 0,
            word_count INTEGER DEFAULT 0,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
        )
        """)
        
        # 5. Document Chunks table (RAG & Vector Search)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            chunk_index INTEGER NOT NULL,
            chunk_text TEXT NOT NULL,
            embedding_json TEXT,
            FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
        )
        """)
        
        # 6. Audit Logs table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            document_id INTEGER,
            action TEXT NOT NULL,
            status TEXT NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Automatically seed default admin if missing
        cursor.execute("SELECT id FROM users WHERE email = 'admin@documind.com'")
        if not cursor.fetchone():
            from .security import hash_password
            pwd = hash_password("Admin123!")
            cursor.execute(
                "INSERT INTO users (email, full_name, password_hash, role) VALUES (?, ?, ?, ?)",
                ("admin@documind.com", "Administrador DocuMind", pwd, "ADMIN")
            )
            admin_id = cursor.lastrowid
            default_repos = [
                ("Contratos y Acuerdos Legales", "Repositorio de minutas, contratos de prestación de servicios y confidencialidad."),
                ("Facturación y Finanzas", "Comprobantes fiscales, facturas electrónicas y órdenes de compra."),
                ("Talento Humano y Selección", "Hojas de vida de candidatos, perfiles de competencias y certificaciones."),
                ("Informes Técnicos de TI", "Arquitectura de software, planes de contingencia y manuales de operaciones.")
            ]
            for name, desc in default_repos:
                cursor.execute(
                    "INSERT INTO repositories (user_id, name, description) VALUES (?, ?, ?)",
                    (admin_id, name, desc)
                )
        conn.commit()
        _DB_INITIALIZED = True
    except Exception as e:
        conn.rollback()
        print(f"Error inicializando base de datos: {e}")
    finally:
        conn.close()

@contextmanager
def get_db():
    global _DB_INITIALIZED
    if not _DB_INITIALIZED:
        init_database()
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def log_audit(action: str, status: str, details: str = "", user_id: Optional[int] = None, document_id: Optional[int] = None):
    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO audit_logs (user_id, document_id, action, status, details) VALUES (?, ?, ?, ?, ?)",
                (user_id, document_id, action, status, details)
            )
    except Exception as e:
        print(f"Error logging audit event: {e}")
